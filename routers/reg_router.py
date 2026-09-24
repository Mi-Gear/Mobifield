from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
from help import dialog
import json
import asyncio
from routers.town_router import enter
from aiogram import F, Router
from states.states import Reg

from utils.functions import *

reg = Router()



@prn
@reg.message(Command("start"))
@pepe_handler
async def on_enter(message:Pepe, state: FSMContext):
    reg_dialog = dialog["registration"]
    await state.set_state(Reg.goto_hub)
    photo = FSInputFile("images/guildmaster.jpg")
    #kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Воин",callback_data="class_warrior")],[InlineKeyboardButton(text = "Стрелок",callback_data="class_archer")],[InlineKeyboardButton(text = "Маг",callback_data="class_mage")]])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Я хочу вступить в гильдию!",callback_data="123")]])
    msg = await message.send_photo(caption=reg_dialog[0].format(name=message._get_user().first_name),photo=photo,reply_markup = kb)
    add_to_trash(message.get_user_id(),msg.message_id)

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

