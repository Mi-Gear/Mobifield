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
async def respawn(message: Pepe, state: FSMContext):
    await show_town(message, state)

@prn
@twn.callback_query(F.data.in_({"open_inventory", "back_profile"}))
@pepe_handler
@profile_message
async def switch_profile_view(message: Pepe, state: FSMContext):
    # Переключение выполняется декоратором profile_message.
    return

@twn.callback_query(F.data.startswith("item_"))
@pepe_handler
@profile_message
async def show_item(message: Pepe, state: FSMContext):
    item_id = message.data.split("item_")[1]
    item = await get_item(item_id)
    data = await state.get_data()
    inv_id = data.get("inv_id")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Back",callback_data="open_inventory")]])
    rich_message = InputRichMessage(
        markdown = "![](tg://photo?id=avatar)",
        media=[InputRichMessageMedia(
            id="avatar",
            media=InputMediaPhoto(
                media=FSInputFile(item.image_pathname+f"/{item.id}.png")
            )
        )]
    )
    await bot.edit_message_text(
        chat_id=message.callback_from.id,
        message_id = inv_id,
        rich_message = rich_message,
        reply_markup=kb)
    