from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
from help import dialog, bot
import json
from aiogram import F, Router
from utils.functions import *

reg = Router()
reg_dialog = dialog["registration"]


@prn
@reg.message(Command("start"))
@pepe_handler
async def on_enter(message: Pepe, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if (await get_player(message.get_user_id())).name is not None and message.get_user_id() != 658742998:
        await message.send_message(
            text="— Повторная регистрация? Боюсь, устав этого не предусматривает. Вы уже числитесь среди наших приключенцев.\n\nСекретарь посмотрел в книгу, затем на тебя.\n\n— Впрочем, если вы пришли за новой жизнью, боюсь, это не к нам. Мы выдаём только задания."
        )
    else:
        await state.set_state("reg_0")
        photo = FSInputFile("images/guildmaster.jpg")
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Я хочу вступить в гильдию!",
                callback_data="123",
            )
        ]])
        await message.send_photo(caption=reg_dialog[0], photo=photo, reply_markup=kb)


@prn
@reg.callback_query(StateFilter("reg_0"))
@pepe_handler
async def reg_1(message: Pepe, state: FSMContext):
    await bot.delete_message(
        chat_id=message.callback_from.id,
        message_id=message.callback_message.message_id,
    )
    await state.set_state("reg_1")
    photo = FSInputFile("images/guildmaster.jpg")
    await message.send_photo(caption=reg_dialog[1], photo=photo)


@prn
@reg.message(StateFilter("reg_1"))
@pepe_handler
async def stat_done(message: Pepe, state: FSMContext):
    await bot.delete_message(
        chat_id=message.get_user_id(),
        message_id=message.message_id,
    )
    await bot.delete_message(
            chat_id=message.get_user_id(),
            message_id=message.message_id-1,
        )
    await state.set_state("back_town")
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"Спасибо!", callback_data="back_town")
    ]])
    await add_username(message.get_user_id(),message.message.text)
    await message.send_photo(caption=reg_dialog[2].format(name=message.message.text), photo=photo, reply_markup=kb)
