from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message


class ExplorationLockMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        state = data.get("state")

        if state and await state.get_state() == 'exploring':
            # Во время исследования разрешаем только открыть инвентарь
            # или вернуться к карточке профиля. Само исследование продолжается.
            if isinstance(event, CallbackQuery) and event.data in {
                "open_inventory",
                "back_profile",
            }:
                return await handler(event, data)

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