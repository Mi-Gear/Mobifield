from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message


class ExplorationLockMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        state = data.get("state")

        if state and await state.get_state() == 'exploring':
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⏳ Ты сейчас исследуешь локацию!",
                    show_alert=True,
                )
            elif isinstance(event, Message):
                await event.answer(
                    "⏳ Сначала закончи исследование!"
                )

            return

        return await handler(event, data)