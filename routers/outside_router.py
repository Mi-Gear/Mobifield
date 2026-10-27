from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from help import *
import json, math
from aiogram import F, Router
from utils.functions import *

outside_dialog = dialog["outside"]
out = Router()

@prn
@out.callback_query(StateFilter("town"), F.data == "outside")
@pepe_handler
@profile_message
async def crossroads(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("crossroads")
    await message.send_message(text = outside_dialog["crossroads"], reply_markup=outside_keyboard((await get_player(message.get_user_id())).lvl))

@prn
@out.callback_query(F.data.startswith("enter_"))
@pepe_handler
@profile_message
async def enter_(message:Pepe,state: FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    cbd = message.get_callback_data()
    await state.set_state(cbd)
    kb = await location_keyboard(cbd.split("enter_")[1],(await get_player(message.get_user_id())).lvl)
    await message.send_message(text = outside_dialog[cbd.split("enter_")[1]], reply_markup=kb)
    
@prn
@out.callback_query(F.data.startswith("back_"))
@pepe_handler
@profile_message
async def back_(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    call = message.callback_data.split("back_")
    match call[1]:
        case "town":
            await state.set_state("back_town")
            photo = FSInputFile("images/town.png")
            await message.send_photo(caption=dialog["town"][0],photo=photo,reply_markup=town_kb)
        case "crossroads":
            await state.set_state("crossroads")
            await message.send_message(text=outside_dialog["crossroads"],reply_markup=outside_keyboard((await get_player(message.get_user_id())).lvl))


@prn
@out.callback_query(F.data.startswith("run_"))
@pepe_handler
@profile_message
async def run_(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    state_ = await state.get_state()
    location = state_.split("enter_")[1]
    type = message.callback_query.data.split("run_")[1]
    loot = await get_run_loot(location,type)
    common, rare, epic, legendary = [],[],[],[]
    for item in loot:
        match item.rarity:
            case 'common': common.append(item)
            case 'rare': rare.append(item)
            case 'epic': epic.append(item)
            case 'legendary': legendary.append(item)
    seconds = 300
    prt = "Вы рыбачите...\n\n"
    await state.set_state('exploring')
    msg = await message.send_message(text=prt)
    try:
        arr = dict()
        text = msg.text
        for i in range(math.floor(seconds/30)):
            await asyncio.sleep(math.floor(seconds/10))
            result = None
            match random.choice(range(1,5)):
                case 1: result = random.choice(common)
                case 2: result = random.choice(rare)
                case 3: result = random.choice(epic)
                case 4: result = random.choice(legendary)
            result.count = arr.get(result, 0) + 1
            arr[result] = result.count
            res_text = prt
            for i in arr.keys():
                res_text += i.name + " + " + str(arr[i])+"\n"
            await msg.edit_text(res_text)
    finally:
        res = {}
        for i in arr:
            res[i.id] = i.count
        await add_to_inventory(message.get_user_id(),res)
        await state.set_state(state_)
        await msg.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Завершить", callback_data=state_)]]))

