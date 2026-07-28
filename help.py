import json, asyncio,functools
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Update, CallbackQuery
from functools import wraps
from typing import Callable, Optional,Dict, Any
from aiogram.types import CallbackQuery, Message, User,Chat
import sqlite3
from player import player as pl
from typing import Union, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

bt = Bot(token = "8732639893:AAHW1v_eRfcB_nwwBFYkZBYquU577QtZNTQ")
class Pepe:

    """
    Унифицированный класс для работы с Message и CallbackQuery
    """
    
    def __init__(self, source: Union[Message, CallbackQuery]):
        self._source = source
        self._is_callback = isinstance(source, CallbackQuery)
        
        # Основные поля
        self.user: User = self._get_user()
        self.chat: Optional[Chat] = self._get_chat()
        self.message_id: int = self._get_message_id()
        self.text: Optional[str] = self._get_text()
        self.original_message: Optional[Message] = self._get_original_message()
        
        # Дополнительные поля для callback
        self.callback_data: Optional[str] = self._get_callback_data()
        self.callback_id: Optional[str] = self._get_callback_id()
        self.callback_from: Optional[User] = self._get_callback_from()
        self.callback_message: Optional[Message] = self._get_callback_message()
        self.callback_chat_instance: Optional[str] = self._get_callback_chat_instance()
        
        # Данные из callback (если есть)
        self.data: Optional[Any] = self._parse_callback_data()
        
        # Дополнительные параметры
        self.inline_message_id: Optional[str] = self._get_inline_message_id()
        self.guild_id: Optional[int] = self._get_guild_id()
        
    def _get_user(self) -> User:
        """Получить пользователя"""
        if self._is_callback:
            return self._source.from_user
        return self._source.from_user
    
    def _get_chat(self) -> Optional[Chat]:
        """Получить чат"""
        if self._is_callback:
            return self._source.message.chat if self._source.message else None
        return self._source.chat
    
    def _get_message_id(self) -> int:
        """Получить ID сообщения"""
        if self._is_callback:
            return self._source.message.message_id if self._source.message else 0
        return self._source.message_id
    
    def _get_text(self) -> Optional[str]:
        """Получить текст сообщения или callback_data"""
        if self._is_callback:
            return self._source.data
        return self._source.text
    
    def _get_original_message(self) -> Optional[Message]:
        """Получить оригинальное сообщение (для callback)"""
        if self._is_callback:
            return self._source.message
        return self._source
    
    def _get_callback_data(self) -> Optional[str]:
        """Получить данные callback"""
        if self._is_callback:
            return self._source.data
        return None
    
    def _get_callback_id(self) -> Optional[str]:
        """Получить ID callback"""
        if self._is_callback:
            return self._source.id
        return None
    
    def _get_callback_from(self) -> Optional[User]:
        """Получить пользователя, вызвавшего callback"""
        if self._is_callback:
            return self._source.from_user
        return None
    
    def _get_callback_message(self) -> Optional[Message]:
        """Получить сообщение, к которому привязан callback"""
        if self._is_callback:
            return self._source.message
        return None
    
    def _get_callback_chat_instance(self) -> Optional[str]:
        """Получить экземпляр чата callback"""
        if self._is_callback:
            return self._source.chat_instance
        return None
    
    def _get_inline_message_id(self) -> Optional[str]:
        """Получить ID инлайн сообщения"""
        if self._is_callback:
            return self._source.inline_message_id
        return None
    
    def _get_guild_id(self) -> Optional[int]:
        """Получить ID гильдии (для Telegram)"""
        # Для совместимости с другими платформами
        return None
    
    def _parse_callback_data(self) -> Optional[Any]:
        """
        Парсинг данных callback.
        Можно переопределить для поддержки JSON или других форматов.
        """
        if not self._is_callback or not self._source.data:
            return None
        
        try:
            import json
            # Пробуем парсить как JSON
            return json.loads(self._source.data)
        except (json.JSONDecodeError, TypeError):
            # Если не JSON, возвращаем как есть
            return self._source.data
    
    # Унифицированные методы
    
    async def answer(self, text: str, **kwargs):
        """
        Ответить на сообщение
        """
        if self._is_callback:
            if kwargs.get('show_alert', False):
                await self._source.answer(text, show_alert=True, **kwargs)
            else:
                await self._source.message.answer(text, **kwargs)
        else:
            await self._source.answer(text, **kwargs)
    
    async def reply(self, text: str, **kwargs):
        """
        Ответить с reply
        """
        if self._is_callback:
            await self._source.message.reply(text, **kwargs)
        else:
            await self._source.reply(text, **kwargs)
    
    async def edit(self, text: str, **kwargs):
        """
        Отредактировать сообщение
        """
        if self._is_callback:
            await self._source.message.edit_text(text, **kwargs)
        else:
            await self._source.edit_text(text, **kwargs)
    
    async def delete(self):
        """Удалить сообщение"""
        if self._is_callback:
            if self._source.message:
                await self._source.message.delete()
        else:
            await self._source.delete()
    
    async def send_photo(self, photo, caption: str = "", **kwargs):
        """Отправить фото"""
        if self._is_callback:
            return await self._source.message.answer_photo(photo, caption=caption, **kwargs)
        return await self._source.answer_photo(photo, caption=caption, **kwargs)
    
    async def send_document(self, document, caption: str = "", **kwargs):
        """Отправить документ"""
        if self._is_callback:
            return await self._source.message.answer_document(document, caption=caption, **kwargs)
        return await self._source.answer_document(document, caption=caption, **kwargs)
    
    async def answer_callback(self, text: str = "", show_alert: bool = False, **kwargs):
        """Ответить на callback (только для callback)"""
        if self._is_callback:
            await self._source.answer(text, show_alert=show_alert, **kwargs)
    
    async def send_message(self, text: str, **kwargs):
        """Отправить сообщение в тот же чат"""
        if self._is_callback:
            return await self._source.message.answer(text, **kwargs)
        return await self._source.answer(text, **kwargs)
    
    # Дополнительные полезные методы
    
    def get_user_id(self) -> int:
        """Получить ID пользователя"""
        return self.user.id
    
    def is_callback(self) -> bool:
        """Проверить, является ли источник callback'ом"""
        return self._is_callback
    
    def is_message(self) -> bool:
        """Проверить, является ли источник сообщением"""
        return not self._is_callback
    
    def get_source(self) -> Union[Message, CallbackQuery]:
        """Получить оригинальный источник"""
        return self._source
    
    def get_callback_data(self) -> Optional[Any]:
        """Получить данные callback в распарсенном виде"""
        return self.data
    
    def get_raw_callback_data(self) -> Optional[str]:
        """Получить сырые данные callback"""
        return self.callback_data
    
    def is_inline(self) -> bool:
        """Проверить, является ли сообщение инлайн"""
        if self._is_callback:
            return self._source.inline_message_id is not None
        return False
    
    async def edit_reply_markup(self, reply_markup=None):
        """Изменить клавиатуру"""
        if self._is_callback and self._source.message:
            await self._source.message.edit_reply_markup(reply_markup=reply_markup)
        else:
            await self._source.edit_reply_markup(reply_markup=reply_markup)
    
    # Метод для получения данных в виде словаря
    
    def to_dict(self) -> Dict[str, Any]:
        """Представить объект в виде словаря"""
        return {
            "user_id": self.user.id,
            "user_name": self.user.full_name,
            "chat_id": self.chat.id if self.chat else None,
            "message_id": self.message_id,
            "text": self.text,
            "is_callback": self._is_callback,
            "callback_data": self.callback_data,
            "callback_id": self.callback_id,
            "data": self.data,
        }
    
    # Магические методы
    
    def __str__(self):
        callback_info = f", callback_data={self.callback_data}" if self._is_callback else ""
        return f"Pepe(user_id={self.user.id}, text={self.text}{callback_info})"
    
    def __repr__(self):
        return self.__str__()



def pepe_handler(func: Callable) -> Callable:
    """
    Декоратор для обработчиков сообщений и callback'ов.
    Автоматически оборачивает Message или CallbackQuery в объект Pepe.
    Автоматически отвечает на callback, если это CallbackQuery.
    
    Пример использования:
    @pepe_handler
    async def start_command(pepe: Pepe):
        await pepe.answer("Привет!")
    
    @pepe_handler
    async def button_callback(pepe: Pepe):
        await pepe.edit("Текст изменен")
    """
    @wraps(func)
    async def wrapper(source: Union[Message, CallbackQuery], *args, **kwargs) -> Any:
        # Создаем объект Pepe из источника
        pepe = Pepe(source)
        
        # Если это callback - автоматически отвечаем на него
        if isinstance(source, CallbackQuery):
            try:
                await source.answer()
            except Exception as e:
                print(f"Ошибка при answer callback: {e}")
        
        # Вызываем функцию с Pepe
        return await func(pepe, *args, **kwargs)
    
    return wrapper

def prn(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Вызвана функция: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

dialog = {}
with open("dialog.json","r",encoding="utf-8") as file:
    dialog = json.load(file)



conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

def get_player(id):
    player = pl()
    cursor.execute(f"select * from players where ID = {id}")
    data = cursor.fetchone()
    if data is None:
        return None
    player.id = data[0]
    player.name = data[1]
    player.cls = data[2]
    return player

def add_player(player: pl):
    print(player.id)
    cursor.execute(f"select * from players where ID = {player.id}")
    data = cursor.fetchone()
    if data is None:
        cursor.execute(f"INSERT INTO players values (?, ?, ?)",(player.id,player.name,player.cls))
        conn.commit()

async def delete_messages(id):
    cursor.execute(f"select * from trash where ID = {id}")
    data = cursor.fetchall()
    for i in data:
        print(isinstance(i[1],int))
        await bt.delete_message(i[0],i[1])
        cursor.execute(f"DELETE FROM TRASH WHERE msg_id = ?",(i[1],))
        conn.commit()

def add_to_trash(id,msg_id):
    cursor.execute("insert into trash values (?, ?)",(id,msg_id))
    conn.commit()

@prn
async def profile_function(call:Pepe):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = "Рюкзак",callback_data = "inventory")]])
    player = get_player(call.get_user_id())
    await call.send_message(f"Имя: {player.name}\nЗолото: 0\nКласс: {player.cls}",reply_markup=kb)

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

            
