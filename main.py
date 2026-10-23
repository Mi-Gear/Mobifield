import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiogram import Dispatcher

from utils.str import SQLiteStorage
from help import bot
from routers.reg_router import reg
from routers.town_router import twn
from routers.outside_router import out


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

storage = SQLiteStorage("utils/db.sqlite")
dp = Dispatcher(bot=bot, storage=storage)

dp.include_router(reg)
reg.include_router(twn)
twn.include_router(out)


async def on_startup() -> None:
    logger.info("Бот запускается")


async def on_shutdown() -> None:
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
