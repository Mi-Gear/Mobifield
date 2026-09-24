from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
from help import dialog,bot
import json
import asyncio
from routers.town_router import enter
from aiogram import F, Router
from states.states import Reg

from utils.functions import *

reg = Router()
reg_dialog = dialog["registration"]



@prn
@reg.message(Command("start"))
@pepe_handler
async def on_enter(message:Pepe, state: FSMContext):
    await state.set_state("reg_0")
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Я хочу вступить в гильдию!",callback_data="123")]])
    msg = await message.send_photo(caption=reg_dialog[0].format(name=message._get_user().first_name),photo=photo,reply_markup = kb)

@prn
@reg.callback_query(StateFilter("reg_0"))
@pepe_handler
async def reg_1(message:Pepe, state: FSMContext):
    print(message.callback_message.text)
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("reg_1")
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="{name}".format(name=message._get_user().first_name), callback_data="123")]])
    msg = await message.send_photo(caption=reg_dialog[1],photo=photo,reply_markup = kb)
    
@reg.callback_query(Reg.goto_hub)
@pepe_handler
@prn
async def class_handler(call: Pepe, state: FSMContext):
    msg = await call.send_message(dialog["2"])
    await asyncio.sleep(5)
    data = call._get_callback_data()
    player = pl()
    player.id,player.name,player.cls = call. _get_user().id,call._get_user().first_name, data.split("class_")[1]
    add_player(player)
    await delete_messages(call.get_user_id())
    add_to_trash(call.get_user_id(),msg.message_id)
    await state.clear()
    await enter(call,state)

