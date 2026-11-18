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
    await msg.answer(text="""Гильдия встретила тебя шумом, который, вероятно, считался дружелюбным. За длинными столами спорили, играли в кости и с серьёзным видом объясняли друг другу, почему вчерашняя неудача была на самом деле почти победой.

Пахло хлебом, мокрой шерстью и горячим железом. У стены дремал человек в доспехах. Никто не пытался его разбудить: возможно, он был опасен, а возможно, просто давно не платил за комнату.

У стойки висела доска объявлений. В дальнем углу торговец раскладывал товар и время от времени пересчитывал его, словно надеялся, что за время подсчёта появится что-нибудь новое.

В этом месте каждый был занят важным делом. По крайней мере, так было написано над входом.""",
    reply_markup=kb)

@guild.callback_query(F.data == "guild_merchant")
@pepe_handler
@profile_message
@wrk
@prn
async def enter_guild_merchant(msg:Pepe,state:FSMContext):
    await bot.delete_message(
        chat_id=msg.callback_from.id,
        message_id=msg.callback_message.message_id,
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выйти",callback_data="guild")],
    ])
    await msg.answer(text="""Торговец поднял глаза от прилавка.

— Снаряжение интересует? Прекрасно. У меня как раз есть всё, что нужно человеку, который ещё не понял, насколько опасно его положение.

Он оглядел твои вещи, потом прилавок, потом снова тебя.

— Хотя, если честно, сегодня ассортимент не тот. Поставки задерживаются, поставщики пропадают, а те, кто не пропадает, требуют предоплату. Торговля — это искусство сохранять оптимизм при полном отсутствии товара.

Он аккуратно сложил пустой лист бумаги и убрал его под прилавок. Видимо, это и был весь сегодняшний запас.""",
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
    await msg.answer(text="""Доска объявлений была покрыта листами разного размера и степени древности. Некоторые задания написали красивым почерком, некоторые — углём, а одно, судя по запаху, кровью. Впрочем, в гильдии не принято задавать лишних вопросов к документам.

Ты пробежал глазами по объявлениям. Каждое обещало работу, опасность и вознаграждение. Иногда в таком порядке, иногда в обратном.""",
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
    markdown = f"{task.description}\n\nТребуется предоставить:\n{req}\n\nГильдия обещает оплату по завершении. Гильдия также оставляет за собой право определить, что именно считается завершением."
    await msg.answer(
                    text=markdown,
                    reply_markup=await task_kb(task.id,msg.get_user_id())
    )

@guild.callback_query(F.data.startswith("reward_"))
@pepe_handler
@profile_message
@wrk
@prn
async def claim_task_reward(msg:Pepe, state:FSMContext):
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
                    text="Служащий гильдии пересчитал принесённое, сверился с записью и поставил печать.\n\n— Всё верно. Вот ваше вознаграждение. Не благодарите. Благодарность, как известно, не входит в смету.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Вернуться к заданию",callback_data="task_"+callback_data)]])
    )

@guild.callback_query(F.data=="123")
@pepe_handler
@profile_message
@wrk
@prn
async def unavailable_task(msg:Pepe, state:FSMContext):
    await msg.answer("Пока это действие недоступно.")
