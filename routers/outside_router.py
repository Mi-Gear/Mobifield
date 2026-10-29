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
    loot = await get_run_loot(location, type)

    common, rare, epic, legendary = [], [], [], []

    for item in loot:
        match item.rarity:
            case "common":
                common.append(item)
            case "rare":
                rare.append(item)
            case "epic":
                epic.append(item)
            case "legendary":
                legendary.append(item)

    rarity_items = {
        "common": common,
        "rare": rare,
        "epic": epic,
        "legendary": legendary,
    }

    # Оставляем только редкости, в которых есть предметы
    available_rarities = [
        rarity
        for rarity, items in rarity_items.items()
        if items
    ]

    if not available_rarities:
        await message.send_message(
            text="Здесь пока нечего найти. Попробуйте исследовать другое место."
        )
        return

    seconds = 300
    match type:
        case "fishing":
            prt = "Вы рыбачите...\n\n"
        case "hunting":
            prt = "Вы охотитесь...\n\n"
        case "choping":
            prt = "Вы рубите деревья...\n\n"
        case "mining":
            prt = "Вы добываете руду...\n\n"
        case "searching":
            prt = "Вы ищете что-то интересное...\n\n"
    await state.set_state("exploring")
    msg = await message.send_message(text=prt)

    arr = {}

    try:
        for _ in range(math.floor(seconds / 30)):
            await asyncio.sleep(math.floor(seconds / 10))

            match random.choice(available_rarities):
                case "common":
                    result = random.choice(common)
                case "rare":
                    result = random.choice(rare)
                case "epic":
                    result = random.choice(epic)
                case "legendary":
                    result = random.choice(legendary)

            arr[result] = arr.get(result, 0) + 1

            res_text = prt
            for item, count in arr.items():
                res_text += f"+{count} {item.name}\n"

            await msg.edit_text(res_text)

    finally:
        res = {
            item.id: count
            for item, count in arr.items()
        }

        if res:
            await add_to_inventory(message.get_user_id(), res)

        await state.set_state(state_)
        await msg.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Завершить",
                            callback_data=state_,
                        )
                    ]
                ]
            )
        )

