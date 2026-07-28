from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
import json
from functions import *

twn = twn



@prn
@twn.callback_query(F.data == "profile")
@pepe_handler
async def proflle(event:Pepe):
    await profile_function(event)

@prn
@twn.callback_query(F.data == "inventory")
@pepe_handler
async def proflle(event:Pepe):
    await inventory(event)


    
