from help import *
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router



reg = Router()
twn = Router()
out = Router()

class Reg(StatesGroup):
    goto_hub = State()


@prn
async def on_enter(message:Pepe, state: FSMContext):
    await state.set_state(Reg.goto_hub)
    photo = FSInputFile("guildmaster.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Воин",callback_data="class_warrior")],[InlineKeyboardButton(text = "Стрелок",callback_data="class_archer")],[InlineKeyboardButton(text = "Маг",callback_data="class_mage")]])
    msg = await message.send_photo(caption=dialog["1"].format(name=message._get_user().first_name),photo=photo,reply_markup = kb)
    add_to_trash(message.get_user_id(),msg.message_id)
@prn
async def class_handler(call: Pepe, state: FSMContext):
    msg = await call.send_message(dialog["2"])
    await asyncio.sleep(5)
    data = call._get_callback_data()
    player = pl()
    player.id,player.name,player.cls = call. _get_user().id,call._get_user().first_name, data.split("class_")[1]
    add_player(player)
    await delete_messages(call.get_user_id())
    add_to_trash(call.get_user_id(),msg.message_id)
    await state.clear()
    await enter(call,state)

class Town(StatesGroup):
    street = State()
    sword_shop = State()
    ranger_shop = State()
    mage_shop = State()

@prn
async def enter(event: Pepe,state:FSMContext):
    await delete_messages(event.get_user_id())
    photo = FSInputFile("town.png")
    call = event
    kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Лицензия гильдии",callback_data="profile")],
            [InlineKeyboardButton(text="За город",callback_data="outside")],
            [InlineKeyboardButton(text="Кузница",callback_data="smelt"),InlineKeyboardButton(text="В Яблочко!",callback_data="archer_shop"),InlineKeyboardButton(text = "Вжух!",callback_data="mage_shop")]
        ]
    )
    await state.set_state(Town.street)
    await call.send_photo(caption="Мрачные улицы, крысы, грязь и вечная суета. Здесь особо нечего ловить. Разве что у тебя есть золотишко..",photo=photo,reply_markup=kb)


class Outside(StatesGroup):
    crossroads = State()
    forest = State()
    field = State()

@prn
async def crossroads(ev:Pepe,state:FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=
            [
                [InlineKeyboardButton(text="Лес",callback_data="enter_forest")],
                [InlineKeyboardButton(text="Поля",callback_data="enter_fields")],
                [InlineKeyboardButton(text="Назад",callback_data="town")]
            ]
        )
    await ev.send_message(text = dialog["5"], reply_markup=kb)
    
@prn
async def enter_forest(ev:Pepe,state=FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Обыск",callback_data="search_forest")],
            [InlineKeyboardButton(text="Назад",callback_data="cross")]
        ]
    )
    await ev.send_message(text = dialog["3"], reply_markup=kb)

