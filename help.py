import json, functools
from aiogram.types import Update, CallbackQuery
from aiogram import Bot
from utils.config import TOKEN
from functools import wraps
from typing import Callable, Optional,Dict, Any
from aiogram.types import CallbackQuery, Message, User,Chat
import sqlite3
from utils.player import player as pl
from typing import Union, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputRichMessage
bot = Bot(token = TOKEN())

town_kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Лицензия гильдии",callback_data="profile")],
            [InlineKeyboardButton(text="За город",callback_data="outside")],
            [InlineKeyboardButton(text="Кузница",callback_data="smelt"),InlineKeyboardButton(text="В Яблочко!",callback_data="archer_shop"),InlineKeyboardButton(text = "Вжух!",callback_data="mage_shop")]
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
    Оборачивает Message или CallbackQuery в Pepe и передаёт обработчику.

    Не отвечает на callback автоматически: обработчик сам решает, когда
    вызвать event.answer_callback(), чтобы не мешать alert-ответам и
    не отвечать дважды на один callback.
    """
    @wraps(func)
    async def wrapper(source: Message | CallbackQuery, *args, **kwargs):
        return await func(Pepe(source), *args, **kwargs)

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



conn = sqlite3.connect('utils/db.sqlite')
cursor = conn.cursor()

def get_player(id):
    player = pl()
    cursor.execute(f"select * from players where ID = {id}")
    data = cursor.fetchone()
    if data is None:
        return None
    player.id = data[0]
    player.name = data[1]
    player.lvl = data[2]
    player.exp = data[3]
    player.gold = data[4]
    return player

def outside_keyboard(lvl):
    kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Лес",callback_data="enter_forest")],
            ]
        )
    if lvl >= 5:
        kb.inline_keyboard.append([InlineKeyboardButton(text="Поля",callback_data="enter_field")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="Назад",callback_data="back_town")])
    return kb


def add_player(player: pl):
    print(player.id)
    cursor.execute(f"select * from players where ID = {player.id}")
    data = cursor.fetchone()
    if data is None:
        cursor.execute(f"INSERT INTO players (ID, name,exp,level,gold) values (?, ?, ?, ?, ?)",(player.id,player.name,player.exp,player.lvl,player.gold))
        conn.commit()

async def delete_messages(id):
    cursor.execute(f"select * from trash where ID = {id}")
    data = cursor.fetchall()
    for i in data:
        print(isinstance(i[1],int))
        await bot.delete_message(i[0],i[1])
        cursor.execute(f"DELETE FROM TRASH WHERE msg_id = ?",(i[1],))
        conn.commit()

def profile(id):
    return get_player(id)
        

def add_to_trash(id,msg_id):
    cursor.execute("insert into trash values (?, ?)",(id,msg_id))
    conn.commit()

def get_inventory(id):
    cursor.execute(f"SELECT * FROM INVENTORY WHERE PL_ID = ?",(id,))
    return cursor.fetchall()

@prn
async def inventory(event:Pepe):
    inv = get_inventory(event.get_user_id())
    kbt = []
    for i in inv:
        kbt.append([InlineKeyboardButton(text = i[5] +" "+ i[3],callback_data="inv_item_"+i[1])])
    kb = InlineKeyboardMarkup(inline_keyboard=kbt)
    await event.send_message("Моя сумка полна всяких интересностей. Ну-ка...",reply_markup=kb)

            
