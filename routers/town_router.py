from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
from aiogram import F, Router
from utils.functions import *

twn = Router()


async def show_town(message: Pepe, state: FSMContext):
    await state.set_state("town")
    photo = FSInputFile("images/town.png")
    await message.send_photo(
        caption=dialog["town"][0],
        photo=photo,
        reply_markup=town_kb,
    )


@prn
@twn.callback_query(F.data == "back_town")
@twn.callback_query(F.data == "enter_town")
@pepe_handler
@profile_message
async def enter(message: Pepe, state: FSMContext):
    await bot.delete_message(
        chat_id=message.callback_from.id,
        message_id=message.callback_message.message_id,
    )
    await show_town(message, state)


@prn
@twn.message(Command("respawn"))
@pepe_handler
@profile_message
async def respawn(message: Pepe, state: FSMContext):
    await show_town(message, state)
