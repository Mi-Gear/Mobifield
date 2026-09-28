from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
import asyncio
from aiogram import F, Router

out = Router()

@prn
@out.callback_query(StateFilter("town") and F.data=="outside")
@pepe_handler
async def crossroads(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("crossroads")
    kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Лес",callback_data="enter_forest")],
                [InlineKeyboardButton(text="Поля",callback_data="enter_fields")],
                [InlineKeyboardButton(text="Назад",callback_data="back_town")]
            ]
        )
    await message.send_message(text = dialog["5"], reply_markup=kb)

@prn
@out.callback_query(StateFilter("crossroads") and F.data.startswith("enter_"))
@pepe_handler
async def enter_(message:Pepe,state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    cbd = message.get_callback_data()
    await state.set_state(cbd)
    kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Обыск",callback_data=f"search_{cbd.split("enter_")}")],
                [InlineKeyboardButton(text="Назад",callback_data="cross")]
            ]
        )
    await message.send_message(text = dialog["3"], reply_markup=kb)

@prn
async def search(ev:Pepe,state=FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Обыск",callback_data="search_forest")],
            [InlineKeyboardButton(text="Назад",callback_data="cross")]
        ]
    )
    await ev.send_message(text = dialog["3"], reply_markup=kb)

@prn
@out.callback_query(F.data.startswith("search_"))
@pepe_handler
async def search(message:Pepe,state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    data = await state.get_state()
    await globals()[message._get_callback_data()](message,state)