import aiosqlite
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import DATABASE_PATH


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_dir()

    def _ensure_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS api_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    api_url TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    api_pass TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            await conn.commit()

    async def add_api(
        self, name: str, api_url: str, api_key: str, api_pass: str
    ) -> bool:
        encoded_pass = base64.b64encode(api_pass.encode()).decode()
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM api_configs")
            count = (await cursor.fetchone())[0]
            is_default = 1 if count == 0 else 0

            await conn.execute(
                "INSERT INTO api_configs (name, api_url, api_key, api_pass, is_default) VALUES (?, ?, ?, ?, ?)",
                (name, api_url, api_key, encoded_pass, is_default),
            )
            await conn.commit()
            return True

    async def get_api(self, name: str) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT * FROM api_configs WHERE name = ?", (name,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_default_api(self) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT * FROM api_configs WHERE is_default = 1"
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def list_apis(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM api_configs ORDER BY name")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_api(self, name: str) -> bool:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "DELETE FROM api_configs WHERE name = ?", (name,)
            )
            await conn.commit()
            return cursor.rowcount > 0

    async def set_default(self, name: str) -> bool:
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("UPDATE api_configs SET is_default = 0")
            cursor = await conn.execute(
                "UPDATE api_configs SET is_default = 1 WHERE name = ?", (name,)
            )
            await conn.commit()
            return cursor.rowcount > 0

    async def api_exists(self, name: str) -> bool:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT 1 FROM api_configs WHERE name = ?", (name,)
            )
            return await cursor.fetchone() is not None

    async def api_exists_case_insensitive(self, name: str) -> bool:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT 1 FROM api_configs WHERE LOWER(name) = LOWER(?)", (name,)
            )
            return await cursor.fetchone() is not None


db = Database()
