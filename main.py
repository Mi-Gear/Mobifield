import asyncio
from utils.str import SQLiteStorage
from help import bot
from routers.reg_router import reg
from routers.town_router import twn
from routers.outside_router import out
from aiogram import Dispatcher

storage = SQLiteStorage("utils/db.sqlite")

dp = Dispatcher(bot = bot,storage=storage)

dp.include_router(reg)
reg.include_router(twn)
twn.include_router(out)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())