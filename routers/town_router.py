from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from help import *
import json
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from utils.functions import *

twn = Router()


@prn
@twn.callback_query(F.data =="back_town")
@twn.callback_query(F.data == "enter_town")
@pepe_handler
async def enter(message: Pepe,state:FSMContext):
    await bot.delete_message(chat_id=message.callback_from.id, message_id=message.callback_message.message_id) 
    prof = profile(message.get_user_id())
    print(prof.name)
    with open("profile_text.txt", "r", encoding="utf-8") as f:
        profile_text = f.read()
    
    
    data = await state.get_data()
    with open("level.json", "r", encoding="utf-8") as f:
        need_xp = json.load(f)[str(prof.lvl)]
    xp_bar = "🟨" * (prof.exp // (need_xp // 10)) + "⬛" * (10 - (prof.exp // (need_xp // 10)))
    if data.get("inv_id",None) is None:  
        inv = await message.bot.send_rich_message(
            chat_id=message.get_user_id(),
            rich_message=InputRichMessage(markdown=profile_text.format(name=prof.name, exp=prof.exp, lvl=prof.lvl, gold=prof.gold,need_xp=need_xp, bar=xp_bar)),            
            )
        await state.update_data({"inv_id":f"{inv.message_id}"})
    else:
        try:
            await message.bot.edit_message_text(rich_message=InputRichMessage(markdown=profile_text.format(name=prof.name, exp=prof.exp, lvl=prof.lvl, gold=prof.gold,need_xp=need_xp, bar=xp_bar)),chat_id=message.get_user_id(),message_id=data.get("inv_id"))
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                pass
        
    
    await state.set_state("town")
    photo = FSInputFile("images/town.png")
    await message.send_photo(caption=dialog["town"][0],photo=photo,reply_markup=town_kb)