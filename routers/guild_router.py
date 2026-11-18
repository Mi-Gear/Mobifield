from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from help import *
import json, math
from aiogram import F, Router
from utils.functions import *

guild = Router()

@guild.callback_query(F.data == "guild")
@pepe_handler
@profile_message
@wrk
@prn
async def enter_guild(msg:Pepe,state:FSMContext):
    await bot.delete_message(
        chat_id=msg.callback_from.id,
        message_id=msg.callback_message.message_id,
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Доска объявлений",callback_data="taskboard")],
        [InlineKeyboardButton(text="Торговец",callback_data="guild_merchant")],
        [InlineKeyboardButton(text="Выйти",callback_data="back_town")],
        
    ])
    await msg.answer(text="""
Вы входите в гильдию приключенцев. Вам в нос вдарил запах хлеба, выпивки, пота и крови. В воздухе витают смех, музыка и всевозможные тосты за выживших и не очень.

Это место наполнено духом приключений. Лишь бы ты не испустил дух...

В другом конце зала сидит торговец снаряжением и одним своим видом его прилавок выделяется из всей этой суматохи.
""",
    reply_markup=kb)

@guild.callback_query(F.data == "guild_merchant")
@pepe_handler
@profile_message
@wrk
@prn
async def enter_guild(msg:Pepe,state:FSMContext):
    await bot.delete_message(
        chat_id=msg.callback_from.id,
        message_id=msg.callback_message.message_id,
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выйти",callback_data="guild")],
        
    ])
    await msg.answer(text="""
Динах, тут нет нихуя, далбаёб нищий


""",
    reply_markup=kb)

@guild.callback_query(F.data == "taskboard")
@pepe_handler
@profile_message
@wrk
@prn
async def show_taskboard(msg:Pepe, state:FSMContext):
    await bot.delete_message(
            chat_id=msg.callback_from.id,
            message_id=msg.callback_message.message_id,
       )
    await msg.answer(text="""
Вы подходите к доске с кучей опрятно вырисованных листов заданий. Вы присматриваетесь...
    """,
        reply_markup=await taskboard_kb((await get_player(msg.get_user_id())).lvl))


@guild.callback_query(F.data.startswith("task_"))
@pepe_handler
@profile_message
@wrk
@prn
async def show_task(msg:Pepe, state:FSMContext):
    await bot.delete_message(
        chat_id=msg.callback_from.id,
        message_id=msg.callback_message.message_id,
    )
    callback_data = msg.callback_query.data.split("task_")[1]
    tasks = await get_tasks((await get_player(msg.get_user_id())).lvl)
    for i in tasks:
        if i.id == callback_data:
            task = i
    req = ''
    req_arr = json.loads(task.requirements)
    for i in req_arr:
        print(i)
        item = await get_item(i)
        req += item.name+': '+str(req_arr[i])
    markdown = f"{task.description}\n\nПредоставить: {req}"
    await msg.answer(
                    text=markdown,
                    reply_markup=await task_kb(task.id,msg.get_user_id())
    )        

@guild.callback_query(F.data.startswith("reward_"))
@pepe_handler
@profile_message
@wrk
@prn
async def show_task(msg:Pepe, state:FSMContext):
    await bot.delete_message(
        chat_id=msg.callback_from.id,
        message_id=msg.callback_message.message_id,
    )
    callback_data = msg.callback_query.data.split("reward_")[1]
    tasks = await get_tasks((await get_player(msg.get_user_id())).lvl)
    for i in tasks:
        if i.id == callback_data:
            task = i
            break
    req_arr = json.loads(task.requirements)
    for i in req_arr:
        await change_inventory(msg.get_user_id(),i,-req_arr[i])
    await change_xp(msg.get_user_id(),task.exp_reward)
    await add_gold(msg.get_user_id(),task.gold_reward)
    await msg.answer(
                    text="Вы получили по ебалу",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Выйти",callback_data="task_"+callback_data)]])
    )        

@guild.callback_query(F.data=="123")
@pepe_handler
@profile_message
@wrk
@prn
async def sex(msg:Pepe, state:FSMContext):
    pass