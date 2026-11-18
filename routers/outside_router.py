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
@wrk
async def crossroads(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    await state.set_state("crossroads")
    await message.send_message(text = outside_dialog["crossroads"], reply_markup=outside_keyboard((await get_player(message.get_user_id())).lvl))

@prn
@out.callback_query(F.data.startswith("enter_"))
@pepe_handler
@profile_message
@wrk
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
@wrk
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
@wrk
async def run_(message:Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id)
    state_ = await state.get_state()
    location = state_.split("enter_")[1]
    type = message.callback_query.data.split("run_")[1]
    loot = await get_run_loot(location, type)

    items = [i.id for i in loot]
    weights = [i.weights for i in loot]
    seconds = 300
    match type:
        case "fishing":
            prt = "Ты устраиваешься у воды. Рыба пока не проявляет интереса к твоей персоне. Взаимность — редкое явление.\n\n"
        case "hunting":
            prt = "Ты идёшь по следу. Лес молчит, и это молчание постепенно начинает казаться осмысленным.\n\n"
        case "choping":
            prt = "Ты принимаешься за деревья. Они не возражают, но и сотрудничеством это назвать трудно.\n\n"
        case "mining":
            prt = "Ты разбираешь породу. Камень хранит молчание лучше большинства людей.\n\n"
        case "searching":
            prt = "Ты осматриваешь окрестности. Обычно ценное лежит там, где его никто не ищет, — или там, где уже кто-то умер.\n\n"
    await state.set_state("exploring")
    msg = await message.send_message(text=prt + make_bar("xp", 0,10)+" 0%",parse_mode="html")

    arr = {}

    try:
        for _ in range(math.floor(seconds / 30)):
            await asyncio.sleep(math.floor(seconds / 10))

            item_base = await get_item(random.choices(items,weights))
            arr[item_base] = arr.get(item_base, 0) + 1

            res_text = prt + make_bar("xp", _+1,seconds/30)+f"{(_+1)*10}%\n\n"
            for item, count in arr.items():
                res_text += f"+{count} {item.name}\n"

            await msg.edit_text(res_text,parse_mode="html")

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
