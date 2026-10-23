from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
from help import dialog, bot
import json
from aiogram import F, Router
from utils.functions import *
from utils.database import (
    initialize_player_stats,
    get_player_stats,
    allocate_stat_point,
)

reg = Router()
reg_dialog = dialog["registration"]

STAT_LABELS = {
    "strength": "💪 Сила",
    "agility": "🏃 Ловкость",
    "endurance": "❤️ Выносливость",
    "luck": "🍀 Удача",
}


def stats_keyboard(stats: dict[str, int]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{STAT_LABELS[key]}: {stats[key]}  ➕",
            callback_data=f"stat_add_{key}",
        )]
        for key in STAT_LABELS
    ]
    buttons.append([
        InlineKeyboardButton(
            text=f"Готово ({stats['points']} очк.)",
            callback_data="stat_done",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def stats_caption(stats: dict[str, int]) -> str:
    return (
        "Распределение характеристик\n\n"
        "У тебя есть 10 очков. Нажимай на характеристику, чтобы "
        "повысить её на 1. Каждое нажатие тратит одно очко.\n\n"
        f"💪 Сила: {stats['strength']}\n"
        f"🏃 Ловкость: {stats['agility']}\n"
        f"❤️ Выносливость: {stats['endurance']}\n"
        f"🍀 Удача: {stats['luck']}\n\n"
        f"Свободных очков: {stats['points']}"
    )


async def update_stats_screen(message: Pepe, stats: dict[str, int]) -> None:
    await bot.edit_message_caption(
        chat_id=message.callback_from.id,
        message_id=message.callback_message.message_id,
        caption=stats_caption(stats),
        reply_markup=stats_keyboard(stats),
    )


@prn
@reg.message(Command("start"))
@pepe_handler
async def on_enter(message: Pepe, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if await get_player(message.get_user_id()) is not None and message.get_user_id() != 658742998:
        await message.send_message(
            text="Повторная попытка регистрации в гильдии нарушает законы Мобифилда. Вам отказано!"
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
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=message._get_user().first_name,
            callback_data="123",
        )
    ]])
    await message.send_photo(caption=reg_dialog[1], photo=photo, reply_markup=kb)


@prn
@reg.callback_query(StateFilter("reg_1"))
@pepe_handler
async def class_handler(message: Pepe, state: FSMContext):
    await bot.delete_message(
        chat_id=message.callback_from.id,
        message_id=message.callback_message.message_id,
    )

    player = pl()
    player.id = message._get_user().id
    player.name = message._get_user().first_name
    await add_player(player)
    await initialize_player_stats(player.id, points=10)

    stats = await get_player_stats(player.id)
    await state.set_state("reg_stats")
    photo = FSInputFile("images/guildmaster.jpg")
    sent = await message.send_photo(
        caption=stats_caption(stats),
        photo=photo,
        reply_markup=stats_keyboard(stats),
    )
    await state.update_data(stats_message_id=sent.message_id)


@prn
@reg.callback_query(StateFilter("reg_stats"), F.data.startswith("stat_add_"))
@pepe_handler
async def stat_add(message: Pepe, state: FSMContext):
    stat_name = message.callback_data.removeprefix("stat_add_")
    stats = await allocate_stat_point(message.get_user_id(), stat_name)
    await update_stats_screen(message, stats)


@prn
@reg.callback_query(StateFilter("reg_stats"), F.data == "stat_done")
@pepe_handler
async def stat_done(message: Pepe, state: FSMContext):
    stats = await get_player_stats(message.get_user_id())
    if stats["points"] > 0:
        await update_stats_screen(message, stats)
        await message.send_message(
            text=f"Сначала распредели все очки. Осталось: {stats['points']}."
        )
        return

    await bot.delete_message(
        chat_id=message.callback_from.id,
        message_id=message.callback_message.message_id,
    )
    await state.set_state("back_town")
    photo = FSInputFile("images/guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Спасибо!", callback_data="back_town")
    ]])
    await message.send_photo(caption=reg_dialog[2], photo=photo, reply_markup=kb)
