from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from help import *
import json
from aiogram import F, Router
from utils.functions import *

outside_dialog = dialog["outside"]
out = Router()
cr_kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Лес",callback_data="enter_forest")],
                [InlineKeyboardButton(text="Поля",callback_data="enter_fields")],
                [InlineKeyboardButton(text="Назад",callback_data="back_town")]
            ]
        )
@prn
@out.callback_query(StateFilter("town") and F.data=="outside")
@pepe_handler
async def crossroads(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("crossroads")
    await message.send_message(text = outside_dialog["crossroads"], reply_markup=cr_kb)

@prn
@out.callback_query(StateFilter("crossroads") and F.data.startswith("back_"))
@out.callback_query(StateFilter("crossroads") and F.data.startswith("enter_"))
@pepe_handler
async def enter_(message:Pepe,state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    cbd = message.get_callback_data()
    await state.set_state(cbd)
    kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Обыск",callback_data=f"search_{cbd.split("enter_")}")],
                [InlineKeyboardButton(text="Назад",callback_data="back_crossroads")]
            ]
        )
    await message.send_message(text = outside_dialog[cbd.split("enter_")[1]], reply_markup=kb)
    
@prn
@out.callback_query(F.data.startswith("back_"))
@pepe_handler
async def back_(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    call = message.callback_data.split("back_")
    match call:
        case "town":
            await state.set_state("back_town")
            photo = FSInputFile("images/town.png")
            await message.send_photo(caption=dialog["town"][0],photo=photo,reply_markup=town_kb)
        case "crossroads":
            await state.set_state("back_crossroads")
            await message.send_message(text=dialog["town"][0],reply_markup=cr_kb)


@prn
@out.callback_query(F.data.startswith("search_"))
@pepe_handler
async def search(message:Pepe,state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    data = await state.get_state()
    await globals()[message._get_callback_data()](message,state)