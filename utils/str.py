import json
import logging
from typing import Any

from aiogram.fsm.storage.base import BaseStorage, StorageKey
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from utils.database import FSMModel, Session

logger = logging.getLogger(__name__)


class SQLiteStorage(BaseStorage):
    """Асинхронное SQLAlchemy-хранилище состояний и данных FSM aiogram."""

    async def set_state(
        self,
        key: StorageKey,
        state: str | None = None,
    ) -> None:
        state_value = getattr(state, "state", state)
        async with Session() as session:
            record = await session.get(FSMModel, (key.chat_id, key.user_id))
            if record is None:
                record = FSMModel(
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    state=state_value,
                    data="{}",
                )
                session.add(record)
            else:
                record.state = state_value
            await session.commit()

        logger.debug(
            "FSM state updated: chat_id=%s user_id=%s state=%s",
            key.chat_id,
            key.user_id,
            state_value,
        )

    async def get_state(self, key: StorageKey) -> str | None:
        async with Session() as session:
            record = await session.get(FSMModel, (key.chat_id, key.user_id))
            result = record.state if record else None

        logger.debug(
            "FSM state read: chat_id=%s user_id=%s state=%s",
            key.chat_id,
            key.user_id,
            result,
        )
        return result

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        try:
            json_data = json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError):
            logger.exception("Failed to serialize FSM data")
            raise

        async with Session() as session:
            record = await session.get(FSMModel, (key.chat_id, key.user_id))
            if record is None:
                record = FSMModel(
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    state=None,
                    data=json_data,
                )
                session.add(record)
            else:
                record.data = json_data
            await session.commit()

        logger.debug(
            "FSM data updated: chat_id=%s user_id=%s",
            key.chat_id,
            key.user_id,
        )

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        async with Session() as session:
            record = await session.get(FSMModel, (key.chat_id, key.user_id))
            raw_data = record.data if record else "{}"

        try:
            result = json.loads(raw_data or "{}")
        except json.JSONDecodeError:
            logger.exception(
                "Invalid JSON in FSM data for chat_id=%s user_id=%s",
                key.chat_id,
                key.user_id,
            )
            return {}

        if not isinstance(result, dict):
            logger.error(
                "FSM data must be a JSON object (chat_id=%s user_id=%s)",
                key.chat_id,
                key.user_id,
            )
            return {}
        return result

    async def close(self) -> None:
        # Соединениями управляет общий SQLAlchemy engine.
        return None

    async def clear(self) -> None:
        async with Session() as session:
            await session.execute(delete(FSMModel))
            await session.commit()
        logger.info("All FSM state and data cleared")
