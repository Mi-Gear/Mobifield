import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from utils.LockMiddleware import ExplorationLockMiddleware
from aiogram import Dispatcher
from aiogram.filters import Command
from utils.web_inventory import WEB_URL, create_login_token, start_inventory_web
from utils.database import init_db, close_db

from utils.str import SQLiteStorage
from help import bot
from routers.reg_router import reg
from routers.town_router import twn
from routers.outside_router import out
from routers.guild_router import guild


# Логи пишутся в консоль и в logs/bot.log.
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_DIR / "bot.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("mobifield")

web_runner = None


async def inventory_web_login(message):
    token = create_login_token(message.from_user.id)
    await message.answer(
        "Ссылка для входа в веб-инвентарь (действует 10 минут и открывается один раз):\n"
        f"{WEB_URL}/#token={token}"
    )

storage = SQLiteStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Middleware должен получать конкретные Message и CallbackQuery,
# а не общий объект Update. Иначе исключения для кнопок инвентаря
# во время exploring не могут корректно сработать.
exploration_lock = ExplorationLockMiddleware()
dp.message.outer_middleware(exploration_lock)
dp.callback_query.outer_middleware(exploration_lock)

dp.message.register(inventory_web_login, Command("web_inventory"))

dp.include_router(reg)
reg.include_router(twn)
twn.include_router(out)
twn.include_router(guild)


async def on_startup() -> None:
    global web_runner
    await init_db()
    web_runner = await start_inventory_web()
    logger.info("Веб-инвентарь запущен на 127.0.0.1:8765")
    logger.info("Бот запускается")


async def on_shutdown() -> None:
    global web_runner
    if web_runner is not None:
        await web_runner.cleanup()
        web_runner = None
    await close_db()
    logger.info("Бот останавливается")
    
async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Критическая ошибка при работе бота")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger("mobifield").info("Бот остановлен вручную")
