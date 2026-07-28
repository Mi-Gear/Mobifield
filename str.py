import json
from typing import Optional, Dict, Any
from aiogram.fsm.storage.base import BaseStorage, StorageKey

import aiosqlite

class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str = "bot_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Создаёт таблицу, если её нет (синхронно при инициализации)"""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fsm_states (
                    chat_id INTEGER,
                    user_id INTEGER,
                    state TEXT,
                    data TEXT,
                    PRIMARY KEY (chat_id, user_id)
                )
            """)

    async def set_state(self, key: StorageKey, state: Optional[str] = None) -> None:
        # Преобразуем объект State в строку, если это не строка и не None
        if state is not None and hasattr(state, 'state'):
            state_str = state.state
        else:
            state_str = state
        
        print(f"[DB] set_state: chat={key.chat_id}, user={key.user_id}, state={state_str}")
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO fsm_states (chat_id, user_id, state, data) "
                "VALUES (?, ?, ?, COALESCE((SELECT data FROM fsm_states WHERE chat_id=? AND user_id=?), '{}'))",
                (key.chat_id, key.user_id, state_str, key.chat_id, key.user_id)
            )
            await conn.commit()
            print(f"[DB] set_state выполнен для chat={key.chat_id}")

    async def get_state(self, key: StorageKey) -> Optional[str]:
        print(f"[DB] get_state: chat={key.chat_id}, user={key.user_id}")
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute(
                "SELECT state FROM fsm_states WHERE chat_id=? AND user_id=?",
                (key.chat_id, key.user_id)
            ) as cursor:
                row = await cursor.fetchone()
                result = row[0] if row else None
                print(f"[DB] get_state вернул: {result}")
                return result

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        print(f"[DB] set_data: chat={key.chat_id}, user={key.user_id}, data={data}")
        json_data = json.dumps(data, ensure_ascii=False)
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO fsm_states (chat_id, user_id, state, data) "
                "VALUES (?, ?, COALESCE((SELECT state FROM fsm_states WHERE chat_id=? AND user_id=?), ''), ?)",
                (key.chat_id, key.user_id, key.chat_id, key.user_id, json_data)
            )
            await conn.commit()
            print(f"[DB] set_data выполнен для chat={key.chat_id}")

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        print(f"[DB] get_data: chat={key.chat_id}, user={key.user_id}")
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute(
                "SELECT data FROM fsm_states WHERE chat_id=? AND user_id=?",
                (key.chat_id, key.user_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    result = json.loads(row[0])
                    print(f"[DB] get_data вернул: {result}")
                    return result
                print(f"[DB] get_data вернул пустой словарь")
                return {}

    async def close(self) -> None:
        """Закрытие соединений (если есть пул)"""
        pass

    async def clear(self) -> None:
        """Очистка всей таблицы"""
        print("[DB] clear: удаление всех записей")
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("DELETE FROM fsm_states")
            await conn.commit()
            print("[DB] clear выполнен")