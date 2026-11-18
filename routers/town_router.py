from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
from aiogram import F, Router
from utils.functions import *

twn = Router()


async def show_town(message: Pepe, state: FSMContext):
    await state.set_state("town")
    photo = FSInputFile("images/town.png")
    await message.send_photo(
        caption=dialog["town"][0],
        photo=photo,
        reply_markup=town_kb,
    )


@prn
@twn.callback_query(F.data == "back_town")
@twn.callback_query(F.data == "enter_town")
@pepe_handler
@profile_message
@wrk
async def enter(message: Pepe, state: FSMContext):
    await bot.delete_message(
        chat_id=message.callback_from.id,
        message_id=message.callback_message.message_id,
    )
    await show_town(message, state)


@prn
@twn.message(Command("respawn"))
@pepe_handler
@profile_message
@wrk
async def respawn(message: Pepe, state: FSMContext):
    data = await state.get_data()
    if not data.get("_") is None:
        try:
            await bot.delete_message(message.get_user_id(),data.get("_"))
        except:
            pass
        data.pop("_")
        await state.set_data(data)
    await show_town(message, state)


@prn
@twn.callback_query(F.data.in_({"open_inventory", "back_profile"}))
@pepe_handler
@profile_message
@wrk
async def switch_profile_view(message: Pepe, state: FSMContext):
    return


@twn.callback_query(F.data.startswith("item_"))
@pepe_handler
@profile_message
@wrk
async def show_item(message: Pepe, state: FSMContext):
    item_id = message.data.split("item_")[1]
    item = await get_item(item_id)
    data = await state.get_data()
    inv_id = data.get("inv_id")
    try:
        image_path = item.image_pathname+f"/{item.id}.png"
    except:
        image_path = "./images/placeholder.png"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад",callback_data="open_inventory")]])
    description = "Описание этого предмета пока не внесено. В гильдии обещали заполнить карточку, как только найдут человека, который умеет писать и согласен работать за еду."
    rich_message = InputRichMessage(
        markdown = "![](tg://photo?id=img)" + (description if item.description is None else item.description),
        media=[InputRichMessageMedia(
            id="img",
            media=InputMediaPhoto(
                media=FSInputFile(image_path)
            )
        )]
    )
    await bot.edit_message_text(
        chat_id=message.callback_from.id,
        message_id = inv_id,
        rich_message = rich_message,
        reply_markup=kb)
