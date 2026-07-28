import asyncio
from utils.config import TOKEN
from utils.str import SQLiteStorage
from routers.reg_router import reg
from routers.town_router import twn
from routers.outside_router import out
from aiogram import Bot, Dispatcher

storage = SQLiteStorage("utils/db.sqlite")

bot = Bot(token = TOKEN())
dp = Dispatcher(bot = bot)

dp.include_router(reg)
reg.include_router(twn)
twn.include_router(out)


async def main():
    dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())