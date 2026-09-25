from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from utils.functions import *

twn = Router()
def profile(id):
    user = get_player(id)
    return [user.name]

@prn
@twn.callback_query(F.data =="back_town")
@twn.callback_query(F.data == "enter_town")
@pepe_handler
async def enter(message: Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    
    prof = profile(message.get_user_id())
    await message.send_message(text=f"Авантюрист: {prof[0]}\n\nУровень: 1\nЗолото: 0\nРепутация: 0\n")
    
    await state.set_state("town")
    photo = FSInputFile("images/town.png")
    kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Лицензия гильдии",callback_data="profile")],
            [InlineKeyboardButton(text="За город",callback_data="outside")],
            [InlineKeyboardButton(text="Кузница",callback_data="smelt"),InlineKeyboardButton(text="В Яблочко!",callback_data="archer_shop"),InlineKeyboardButton(text = "Вжух!",callback_data="mage_shop")]
        ]
    )
    await message.send_photo(caption="Мрачные улицы, крысы, грязь и вечная суета. Здесь особо нечего ловить. Разве что у тебя есть золотишко...",photo=photo,reply_markup=kb)