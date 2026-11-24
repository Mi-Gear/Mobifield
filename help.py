import json, functools
from aiogram.types import Update, CallbackQuery
from aiogram import Bot
from utils.config import TOKEN
from functools import wraps
from typing import Callable, Optional,Dict, Any
from aiogram.types import CallbackQuery, Message, User, Chat, InputMediaPhoto, InputRichMessageMedia
from utils.player import player as pl
import asyncio, random
from utils.database import *
from utils.database import delete_messages as _delete_messages
from typing import Union, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputRichMessage, DisabledButton, WebAppInfo
from aiogram.fsm.context import FSMContext
bot = Bot(token = TOKEN())

town_kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Гильдия",callback_data='guild')],
            [InlineKeyboardButton(text="За город",callback_data="outside")],
        ]
    )

class Pepe:
    """
    Обёртка над aiogram.types.Message или CallbackQuery.

    is_message / is_callback — булевы поля, определяющие тип события.
    message / callback_query — исходный объект только соответствующего типа.
    Поля остальных типов не подменяются искусственными значениями.
    """

    def __init__(self, source: Message | CallbackQuery):
        if isinstance(source, Message):
            self.is_message = True
            self.is_callback = False
        elif isinstance(source, CallbackQuery):
            self.is_message = False
            self.is_callback = True
        else:
            raise TypeError(
                "Pepe ожидает aiogram.types.Message или CallbackQuery, "
                f"получено {type(source).__name__}"
            )

        self._source = source
        self.bot = source.bot

    @property
    def source(self) -> Message | CallbackQuery:
        """Исходный объект Telegram без изменений."""
        return self._source

    @property
    def message(self) -> Message | None:
        """Исходное Message; None, если событие — CallbackQuery."""
        return self._source if self.is_message else None

    @property
    def callback_query(self) -> CallbackQuery | None:
        """Исходное CallbackQuery; None, если событие — Message."""
        return self._source if self.is_callback else None

    def __getattr__(self, name: str) -> Any:
        """
        Прозрачно проксирует поля и методы к исходному объекту.
        Поэтому Message.text доступно для Message, а CallbackQuery.data —
        для CallbackQuery. Несуществующие у типа поля вызовут AttributeError.
        """
        return getattr(self._source, name)

    @property
    def user(self) -> User:
        return self._source.from_user

    @property
    def user_id(self) -> int:
        return self.user.id

    @property
    def chat(self) -> Chat | None:
        if self.is_message:
            return self._source.chat
        callback = self._source
        return callback.message.chat if callback.message else None

    @property
    def chat_id(self) -> int | None:
        chat = self.chat
        return chat.id if chat else None

    @property
    def message_id(self) -> int | None:
        if self.is_message:
            return self._source.message_id
        callback = self._source
        return callback.message.message_id if callback.message else None

    # Совместимость с существующими обработчиками проекта.

    @property
    def original_message(self) -> Message | None:
        if self.is_message:
            return self._source
        return self._source.message

    @property
    def callback_data(self) -> str | None:
        return self._source.data if self.is_callback else None

    @property
    def callback_id(self) -> str | None:
        return self._source.id if self.is_callback else None

    @property
    def callback_from(self) -> User | None:
        return self._source.from_user if self.is_callback else None

    @property
    def callback_message(self) -> Message | None:
        return self._source.message if self.is_callback else None

    @property
    def callback_chat_instance(self) -> str | None:
        return self._source.chat_instance if self.is_callback else None

    @property
    def inline_message_id(self) -> str | None:
        return self._source.inline_message_id if self.is_callback else None

    @property
    def data(self) -> Any:
        """JSON из callback_data, если оно является корректным JSON; иначе строка."""
        if not self.is_callback or not self._source.data:
            return None

        try:
            return json.loads(self._source.data)
        except (json.JSONDecodeError, TypeError):
            return self._source.data

    def get_user_id(self) -> int:
        return self.user_id

    def get_source(self) -> Message | CallbackQuery:
        return self._source

    def get_callback_data(self) -> Any:
        return self.data

    def get_raw_callback_data(self) -> str | None:
        return self.callback_data

    def is_inline(self) -> bool:
        return self.is_callback and self._source.inline_message_id is not None

    async def answer_callback(
        self,
        text: str = "",
        show_alert: bool = False,
        **kwargs,
    ):
        """Ответить на CallbackQuery и закрыть индикатор загрузки."""
        if not self.is_callback:
            raise TypeError("answer_callback доступен только для CallbackQuery")
        return await self._source.answer(
            text,
            show_alert=show_alert,
            **kwargs,
        )

    async def answer(self, text: str = "", **kwargs):
        """
        Для Message — отправить ответ на сообщение.
        Для CallbackQuery — отправить новое сообщение в привязанный чат.
        Для ответа на сам callback используйте answer_callback().
        """
        if self.is_message:
            return await self._source.answer(text, **kwargs)
        if self._source.message:
            return await self._source.message.answer(text, **kwargs)
        raise TypeError(
            "У inline CallbackQuery нет обычного чата; "
            "для отправки сообщения используйте bot.send_message с chat_id"
        )

    async def send_message(self, text: str, **kwargs):
        return await self.answer(text, **kwargs)

    async def reply(self, text: str, **kwargs):
        if self.is_message:
            return await self._source.reply(text, **kwargs)
        if self._source.message:
            return await self._source.message.reply(text, **kwargs)
        raise TypeError("У inline CallbackQuery нет обычного сообщения для reply")

    async def send_photo(self, photo, caption: str = "", **kwargs):
        if self.is_message:
            return await self._source.answer_photo(
                photo=photo, caption=caption, **kwargs
            )
        if self._source.message:
            return await self._source.message.answer_photo(
                photo=photo, caption=caption, **kwargs
            )
        raise TypeError("У inline CallbackQuery нет обычного чата для отправки фото")

    async def send_document(self, document, caption: str = "", **kwargs):
        if self.is_message:
            return await self._source.answer_document(
                document=document, caption=caption, **kwargs
            )
        if self._source.message:
            return await self._source.message.answer_document(
                document=document, caption=caption, **kwargs
            )
        raise TypeError(
            "У inline CallbackQuery нет обычного чата для отправки документа"
        )

    async def edit(self, text: str, **kwargs):
        if self.is_message:
            return await self._source.edit_text(text, **kwargs)
        if self._source.message:
            return await self._source.message.edit_text(text, **kwargs)
        raise TypeError("У inline CallbackQuery нет обычного сообщения для редактирования")

    async def delete(self):
        if self.is_message:
            return await self._source.delete()
        if self._source.message:
            return await self._source.message.delete()
        raise TypeError("У inline CallbackQuery нет обычного сообщения для удаления")

    async def edit_reply_markup(self, reply_markup=None):
        if self.is_message:
            return await self._source.edit_reply_markup(reply_markup=reply_markup)
        if self._source.message:
            return await self._source.message.edit_reply_markup(
                reply_markup=reply_markup
            )
        raise TypeError(
            "У inline CallbackQuery нет обычного сообщения для редактирования"
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
            "is_message": self.is_message,
            "is_callback": self.is_callback,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "message_id": self.message_id,
        }
        if self.is_message:
            result["text"] = self._source.text
        else:
            result["callback_data"] = self._source.data
            result["callback_id"] = self._source.id
        return result

    def __repr__(self) -> str:
        event_type = "Message" if self.is_message else "CallbackQuery"
        details = (
            f"text={self._source.text!r}"
            if self.is_message
            else f"data={self._source.data!r}"
        )
        return f"Pepe(type={event_type}, user_id={self.user_id}, {details})"


def pepe_handler(func: Callable) -> Callable:
    """
    Оборачивает Message или CallbackQuery в Pepe.

    Для CallbackQuery автоматически вызывает callback.answer() перед
    запуском обработчика, чтобы Telegram убирал индикатор загрузки.
    Обработчик при необходимости может вызвать answer_callback() повторно
    с текстом/alert, но Telegram может уже считать callback отвеченным.
    """
    @wraps(func)
    async def wrapper(source: Message | CallbackQuery, *args, **kwargs):
        if isinstance(source, CallbackQuery):
            try:
                await source.answer()
            except Exception as e:
                # Не блокируем обработчик, если callback уже подтверждён
                # или Telegram не смог принять answer.
                print(f"Ошибка при автоматическом answer callback: {e}")

        return await func(Pepe(source), *args, **kwargs)

    return wrapper

async def taskboard_kb(lvl):
    buttons = []
    tasks = await get_tasks(lvl)
    tab=[]
    counter = 0
    for i in range(0,len(tasks)):
        tab.append(InlineKeyboardButton(text=tasks[i].name,callback_data="task_"+tasks[i].id))
        if (counter==2):
            buttons.append(tab)
            tab=[]
            counter = 0
        counter+=1
    buttons.append(tab)
    buttons.append([InlineKeyboardButton(text="Вернуться", callback_data="guild")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def outside_keyboard(lvl):
    buttons = []
    if lvl >= 1:
        buttons.append([InlineKeyboardButton(text="Поля",callback_data="enter_field")])
    if lvl >= 10:
        buttons.append([InlineKeyboardButton(text="Лес",callback_data="enter_forest")])
    if lvl >= 20:
        buttons.append([InlineKeyboardButton(text="Руины",callback_data="enter_ruins")])
    if lvl >= 30:
        buttons.append([InlineKeyboardButton(text="Темнолесье",callback_data="enter_darkforest")])            

    buttons.append([InlineKeyboardButton(text="Назад",callback_data="back_town")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def location_keyboard(location, lvl):
    loc = await get_loc_requir(location)
    buttons = []
    if lvl >= loc['fishing'] and loc['fishing']!=-1:
        buttons.append([InlineKeyboardButton(text="🎣 Рыбалка",callback_data="run_fishing")])
    if lvl >= loc['choping'] and loc['choping']!=-1:
        buttons.append([InlineKeyboardButton(text="🪓 Рубка",callback_data="run_choping")])
    if lvl >= loc['searching'] and loc['searching']!=-1:
        buttons.append([InlineKeyboardButton(text="🔎 Исследование",callback_data="run_searching")])
    if lvl >= loc['hunting'] and loc['hunting']!=-1:
        buttons.append([InlineKeyboardButton(text="🏹 Охота",callback_data="run_hunting")])            
    if lvl >= loc['mining'] and loc['mining']!=-1:
        buttons.append([InlineKeyboardButton(text="⛏️ Добыча",callback_data="run_mining")])  

    buttons.append([InlineKeyboardButton(text="Назад",callback_data="back_crossroads")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def profile_keyboard():
    buttons = [[InlineKeyboardButton(text="Инвентарь",web_app=WebAppInfo(url="https://mobifield.duckdns.org"))]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def inventory_keyboard(player_id):
    inventory = await get_inventory(player_id)
    buttons = []
    for item in inventory:
        buttons.append([InlineKeyboardButton(text=f"{item.base.name} x{item.count}",callback_data=f"item_{item.id}",icon_custom_emoji_id=item.base.emoji_id)])
    buttons.append([InlineKeyboardButton(text="Назад",callback_data="back_profile")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def task_kb(task_id, player_id):
    buttons = []
    tasks = await get_tasks((await get_player(player_id)).lvl)
    try:
        for i in tasks:
                if i.id == task_id:
                    task = i
        req = json.loads(task.requirements)
        for i in req:
            item = await get_item_from_inventory(player_id,i)
            if item is None or item.count < req[i]:
                raise ValueError
    except ValueError as e:
        buttons.append([InlineKeyboardButton(text="Не выполнены условия",callback_data="123",style="danger")])
    if len(buttons) == 0:
        buttons.append([InlineKeyboardButton(text="Выполнить",callback_data=f"reward_{task_id}", style="danger")])
    buttons.append([InlineKeyboardButton(text="Назад",callback_data="taskboard")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
    

def make_bar(type: str, current,purpose):
    progress = max(0, min(100, current/ purpose * 100))
    filled = int(progress // 10)

    repres = [1 if x <= filled else 0 for x in range(1, 11)]
    typo = {
        "xp":{
            "left_filled":5424864752243354510,
            "left_empty":5424762574971383104,
            "middle_filled":5424824959371355055,
            "middle_empty":5425077709606791595,
            "right_filled":5424658336115105531,
            "right_empty":5427227061565562800
            }
        }
    emoji_set = typo[type]
    for i in range(len(repres)):
        match i:
            case 0:
                repres[i] = (
                    f'<tg-emoji emoji-id="{emoji_set["left_filled"]}">🟨</tg-emoji>'
                    if repres[i] else
                    f'<tg-emoji emoji-id="{emoji_set["left_empty"]}">⬛</tg-emoji>'
                )
            case 9:
                repres[i] = (
                    f'<tg-emoji emoji-id="{emoji_set["middle_filled"]}">🟨</tg-emoji>'
                    if repres[i] else
                    f'<tg-emoji emoji-id="{emoji_set["middle_empty"]}">⬛</tg-emoji>'
                )
            case _:
                repres[i] = (
                    f'<tg-emoji emoji-id="{emoji_set["right_filled"]}">🟨</tg-emoji>'
                    if repres[i] else
                    f'<tg-emoji emoji-id="{emoji_set["right_empty"]}">⬛</tg-emoji>'
                )
    return "".join(repres)

                
def wrk(func:Callable) -> Callable:
    @wraps(func)
    async def wrapper(message: Pepe, state: FSMContext, *args, **kwargs):
        data = await state.get_data()
        data["_"] = message.message_id
        await state.set_data(data)
        result = await func(message, state, *args, **kwargs)
        return result
    return wrapper
    
def profile_message(func: Callable) -> Callable:
    """Создаёт карточку профиля и переключает её содержимое на инвентарь."""

    @wraps(func)
    async def wrapper(message: Pepe, state: FSMContext, *args, **kwargs):

        # Сначала выполняем основной обработчик

        callback_data = message.get_raw_callback_data()
        if message.is_message and message.message.text == "/respawn":
            await bot.delete_message(message.get_user_id(),message.message_id)
        data = await state.get_data()

        # Определяем отображаемый экран
        if callback_data == "open_inventory":
            data["inv_state"] = "inventory"
        elif callback_data == "back_profile":
            data["inv_state"] = "profile"
        elif callback_data and callback_data.startswith("item_"):
            data["inv_state"] = "item"

        view = data.get("inv_state", "profile")

        player_id = message.get_user_id()
        await add_level(str(player_id))

        player = await profile(player_id, message.user.first_name)

        with open("profile_text.txt", "r", encoding="utf-8") as file:
            profile_text = file.read()

        with open("level.json", "r", encoding="utf-8") as file:
            levels = json.load(file)


        bar = make_bar("xp",player.exp,levels[str(player.lvl)])


        rich_message = InputRichMessage(
            markdown=profile_text.format(
                name=player.name,
                exp=player.exp,
                lvl=player.lvl,
                gold=player.gold,
                need_xp=levels[str(player.lvl)],
                bar=bar,
            )
        )

        from aiogram.exceptions import TelegramBadRequest

        profile_message_id = data.get("inv_id")

        try:
            if message.message.text == "/respawn":
                data.pop("inv_id")
                data.pop("inv_state")
                await state.set_data(data)
                await bot.delete_message(message.get_user_id(),profile_message_id)
                profile_message_id = None
        except:
            pass

        if profile_message_id is None:
            sent = await message.bot.send_rich_message(
                chat_id=player_id,
                rich_message=rich_message,
                reply_markup=profile_keyboard(),
            )
            profile_message_id = str(sent.message_id)
            await state.update_data(inv_id=profile_message_id)


        try:
            if view == "item":
                # Карточку предмета уже обработал основной обработчик
                pass

            elif view == "inventory":
                await message.bot.edit_message_text(
                    chat_id=player_id,
                    message_id=int(profile_message_id),
                    text="Ваш инвентарь:",
                    reply_markup=await inventory_keyboard(player_id),
                )

            else:
                await message.bot.edit_message_text(
                    chat_id=player_id,
                    message_id=int(profile_message_id),
                    rich_message=rich_message,
                    reply_markup=profile_keyboard(),
                )

        except TelegramBadRequest as error:
            if "message is not modified" not in error.message:
                raise

        await state.update_data(inv_state=view)
        result = await func(message, state, *args, **kwargs)

        return result

    return wrapper

def prn(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Вызвана функция: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

dialog = {}
with open("utils/dialog.json","r",encoding="utf-8") as file:
    dialog = json.load(file)



async def delete_messages(player_id):
    await _delete_messages(player_id, bot)


async def profile(player_id,name):
    return await get_player(player_id,name)

            
