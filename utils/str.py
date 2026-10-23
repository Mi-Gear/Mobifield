import json
import logging
from typing import Any

import aiosqlite
from aiogram.fsm.storage.base import BaseStorage, StorageKey

logger = logging.getLogger(__name__)


class SQLiteStorage(BaseStorage):
    """Асинхронное SQLite-хранилище состояний и данных FSM aiogram."""

    def __init__(self, db_path: str = "bot_state.db") -> None:
        self.db_path = db_path
        self._initialized = False
        self._init_lock = __import__("asyncio").Lock()

    async def _ensure_db(self) -> None:
        """Асинхронно создаёт таблицу при первом обращении к хранилищу."""
        if self._initialized:
            return

        async with self._init_lock:
            if self._initialized:
                return

            async with aiosqlite.connect(self.db_path, timeout=5) as conn:
                await conn.execute("PRAGMA busy_timeout = 5000")
                await conn.execute("PRAGMA journal_mode = WAL")
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS fsm_states (
                        chat_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        state TEXT,
                        data TEXT NOT NULL DEFAULT '{}',
                        PRIMARY KEY (chat_id, user_id)
                    )
                    """
                )
                await conn.commit()

            self._initialized = True
            logger.debug("SQLite FSM storage initialized: %s", self.db_path)

    async def _connect(self):
        """Открывает короткоживущее соединение после инициализации БД."""
        await self._ensure_db()
        conn = await aiosqlite.connect(self.db_path, timeout=5)
        await conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    async def set_state(
        self,
        key: StorageKey,
        state: str | None = None,
    ) -> None:
        # В aiogram обычно передаётся строка состояния или None.
        state_value = getattr(state, "state", state)

        async with await self._connect() as conn:
            await conn.execute(
                """
                INSERT INTO fsm_states (chat_id, user_id, state, data)
                VALUES (?, ?, ?, '{}')
                ON CONFLICT(chat_id, user_id)
                DO UPDATE SET state = excluded.state
                """,
                (key.chat_id, key.user_id, state_value),
            )
            await conn.commit()

        logger.debug(
            "FSM state updated: chat_id=%s user_id=%s state=%s",
            key.chat_id,
            key.user_id,
            state_value,
        )

    async def get_state(self, key: StorageKey) -> str | None:
        async with await self._connect() as conn:
            async with conn.execute(
                "SELECT state FROM fsm_states WHERE chat_id = ? AND user_id = ?",
                (key.chat_id, key.user_id),
            ) as cursor:
                row = await cursor.fetchone()

        result = row[0] if row else None
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

        async with await self._connect() as conn:
            await conn.execute(
                """
                INSERT INTO fsm_states (chat_id, user_id, state, data)
                VALUES (?, ?, NULL, ?)
                ON CONFLICT(chat_id, user_id)
                DO UPDATE SET data = excluded.data
                """,
                (key.chat_id, key.user_id, json_data),
            )
            await conn.commit()

        logger.debug(
            "FSM data updated: chat_id=%s user_id=%s",
            key.chat_id,
            key.user_id,
        )

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        async with await self._connect() as conn:
            async with conn.execute(
                "SELECT data FROM fsm_states WHERE chat_id = ? AND user_id = ?",
                (key.chat_id, key.user_id),
            ) as cursor:
                row = await cursor.fetchone()

        if not row or not row[0]:
            return {}

        try:
            result = json.loads(row[0])
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
        """Соединения не хранятся постоянно, поэтому закрывать нечего."""
        return None

    async def clear(self) -> None:
        """Удаляет все состояния и данные FSM."""
        async with await self._connect() as conn:
            await conn.execute("DELETE FROM fsm_states")
            await conn.commit()

        logger.info("All FSM state and data cleared")
