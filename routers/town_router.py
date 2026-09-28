from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from utils.functions import *

twn = Router()


@prn
@twn.callback_query(F.data =="back_town")
@twn.callback_query(F.data == "enter_town")
@pepe_handler
async def enter(message: Pepe,state:FSMContext):
    profile_text = "Авантюрист: {name}\n\nУровень: 1\nЗолото: 0\nРепутация: 0\n"
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    
    prof = profile(message.get_user_id())
    data = await state.get_data()
    if data.get("inv_id",None) is None:  
        inv = await message.send_message(text=profile_text.format(name=prof[0]))
        await state.update_data({"inv_id":f"{inv.message_id}"})
    else:
        await edit_profile_message(message.get_user_id(),data.get("inv_id"),profile_text.format(name=prof[0]))
        
    
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