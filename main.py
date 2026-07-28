from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from str import SQLiteStorage
from functions import *
from help import dialog, get_player,bt
import reg_router, town,outside
import asyncio


# Инициализация хранилища
storage = SQLiteStorage("db.sqlite")

dp = Dispatcher(storage = storage)
bot = bt

reg.include_router(twn)
dp.include_router(reg)
twn.include_router(out)
@dp.message(Command("start"))
@prn
@pepe_handler
async def start_registration(message: Pepe, state: FSMContext):
    if await state.get_state() == None:
        await on_enter(message,state)

async def main():
    await dp.start_polling(bot)

@dp.message(Command("respawn"))
@prn
@pepe_handler
async def respawn(msg:Pepe,state:FSMContext):
    await globals()["enter"](msg,state)



if __name__ == "__main__":
    asyncio.run(main())