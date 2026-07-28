from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
import json
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from utils.functions import *
from states import Town

twn = Router()



@prn
async def enter(event: Pepe,state:FSMContext):
    await delete_messages(event.get_user_id())
    photo = FSInputFile("town.png")
    call = event
    kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Лицензия гильдии",callback_data="profile")],
            [InlineKeyboardButton(text="За город",callback_data="outside")],
            [InlineKeyboardButton(text="Кузница",callback_data="smelt"),InlineKeyboardButton(text="В Яблочко!",callback_data="archer_shop"),InlineKeyboardButton(text = "Вжух!",callback_data="mage_shop")]
        ]
    )
    await state.set_state(Town.street)
    await call.send_photo(caption="Мрачные улицы, крысы, грязь и вечная суета. Здесь особо нечего ловить. Разве что у тебя есть золотишко..",photo=photo,reply_markup=kb)