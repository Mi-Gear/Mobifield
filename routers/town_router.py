from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from utils.functions import *
from states.states import Town

twn = Router()



@prn
@twn.callback_query(StateFilter("town"))
async def enter(call: Pepe,state:FSMContext):
    bot.delete_message()
    await delete_messages(call.get_user_id())
    photo = FSInputFile("images/town.png")
    kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Лицензия гильдии",callback_data="profile")],
            [InlineKeyboardButton(text="За город",callback_data="outside")],
            [InlineKeyboardButton(text="Кузница",callback_data="smelt"),InlineKeyboardButton(text="В Яблочко!",callback_data="archer_shop"),InlineKeyboardButton(text = "Вжух!",callback_data="mage_shop")]
        ]
    )
    await call.send_photo(caption="Мрачные улицы, крысы, грязь и вечная суета. Здесь особо нечего ловить. Разве что у тебя есть золотишко..",photo=photo,reply_markup=kb)