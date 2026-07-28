from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from help import *
import json
import asyncio
from town_router import enter
from aiogram import F, Router
from states import Reg

from utils.functions import *

reg = Router()



@prn
@reg.message(Command("start"))
@pepe_handler
async def on_enter(message:Pepe, state: FSMContext):
    await state.set_state(Reg.goto_hub)
    photo = FSInputFile("guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Воин",callback_data="class_warrior")],[InlineKeyboardButton(text = "Стрелок",callback_data="class_archer")],[InlineKeyboardButton(text = "Маг",callback_data="class_mage")]])
    msg = await message.send_photo(caption=dialog["1"].format(name=message._get_user().first_name),photo=photo,reply_markup = kb)
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

