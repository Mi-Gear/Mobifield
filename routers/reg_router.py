from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
from help import dialog,bot
import json
import asyncio
from routers.town_router import enter
from aiogram import F, Router
from utils.functions import *

reg = Router()
reg_dialog = dialog["registration"]


@prn
@reg.message(Command("start"))
@pepe_handler
async def on_enter(message:Pepe, state: FSMContext):
    await bot.delete_message(chat_id=message.get_user_id(), message_id=message.message_id)
    if get_player((message.get_user_id())) != None:
        if message.get_user_id() == 658742998: print("Тебе можно!")
        msg = await message.send_message(text="Повторная попытка регистрации в гильдии нарушает законы Мобифилда. Вам отказано!")
    else:
        await state.set_state("reg_0")
        photo = FSInputFile("images/guildmaster.jpg")
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Я хочу вступить в гильдию!",callback_data="123")]])
        msg = await message.send_photo(caption=reg_dialog[0],photo=photo,reply_markup = kb)

@prn
@reg.callback_query(StateFilter("reg_0"))
@pepe_handler
async def reg_1(message:Pepe, state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("reg_1")
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="{name}".format(name=message._get_user().first_name), callback_data="123")]])
    msg = await message.send_photo(caption=reg_dialog[1],photo=photo,reply_markup = kb)

@prn
@reg.callback_query(StateFilter("reg_1"))
@pepe_handler
async def reg_1(message:Pepe, state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("reg_2")
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Воин", callback_data="class_warrior")],[InlineKeyboardButton(text="Лучник", callback_data="class_ranger")],[InlineKeyboardButton(text="Колдун", callback_data="class_mage")]])
    msg = await message.send_photo(caption=reg_dialog[2],photo=photo,reply_markup = kb)

@prn
@reg.callback_query(StateFilter("reg_2"))
@pepe_handler
async def class_handler(message: Pepe, state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("enter_town")
    data = message._get_callback_data()
    player = pl()
    player.id,player.name,player.cls = message. _get_user().id,message._get_user().first_name, data.split("class_")[1]
    add_player(player)
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Спасибо!", callback_data="123")]])
    msg = await message.send_photo(caption=reg_dialog[3],photo=photo,reply_markup = kb)

