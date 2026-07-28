from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
import json, town
import asyncio
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from functions import *
import functions

out = out

@prn
@out.callback_query(Town.street and F.data=="outside")
@pepe_handler
async def cross(msg:Pepe, state: FSMContext):
    await state.set_state(Outside.crossroads)
    await crossroads(msg,state)

@prn
@out.callback_query(Outside.crossroads and F.data.startswith("enter_"))
@pepe_handler
async def enter_(msg:Pepe,state: FSMContext):
    await state.set_state("Outside:"+msg._get_callback_data().split("enter_")[1])
    await globals()[msg._get_callback_data()](msg,state)

@prn
@out.callback_query(F.data.startswith("search_"))
@pepe_handler
async def search(msg:Pepe,state: FSMContext):
    data = await state.get_state()
    await globals()[msg._get_callback_data()](msg,state)

@prn
@out.callback_query(Outside.crossroads and F.data.startswith("enter_"))
@pepe_handler
async def enter_(msg:Pepe,state: FSMContext):