from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
import json
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from states import Town, Outside

out = Router()

@prn
@out.callback_query(Town.street and F.data=="outside")
@pepe_handler
async def crossroads(ev:Pepe,state:FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Лес",callback_data="enter_forest")],
                [InlineKeyboardButton(text="Поля",callback_data="enter_fields")],
                [InlineKeyboardButton(text="Назад",callback_data="town")]
            ]
        )
    await ev.send_message(text = dialog["5"], reply_markup=kb)

@prn
@out.callback_query(Outside.crossroads and F.data.startswith("enter_"))
@pepe_handler
async def enter_(msg:Pepe,state: FSMContext):
    await state.set_state("Outside:"+msg._get_callback_data().split("enter_")[1])
    await globals()[msg._get_callback_data()](msg,state)

func = {
    

}
@prn
async def enter_forest(ev:Pepe,state=FSMContext):
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
async def search(msg:Pepe,state: FSMContext):
    data = await state.get_state()
    await globals()[msg._get_callback_data()](msg,state)