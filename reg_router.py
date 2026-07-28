from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
import json, town
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from functions import *
import functions

reg = reg

@prn
@reg.message(Command("start"))
@pepe_handler
async def f1(message:Pepe, state: FSMContext):
    await on_enter(message = message, state=state)

@prn
@reg.callback_query(Reg.goto_hub)
@pepe_handler
async def f2(msg:Pepe, state: FSMContext):
    await class_handler(call = msg,state=state)

