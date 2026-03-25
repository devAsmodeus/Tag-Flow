import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.infrastructure.database import Database

logger = logging.getLogger(__name__)


class BaseRepository[T: BaseModel](ABC):
    table: str

    def __init__(self, db: Database) -> None:
        self._db = db

    @abstractmethod
    def _row_to_entity(self, row: dict[str, Any]) -> T:
        ...

    def get_by_id(self, entity_id: int) -> T | None:
        sql = f"SELECT * FROM {self.table} WHERE id = %s"  # noqa: S608
        with self._db.cursor() as cur:
            cur.execute(sql, (entity_id,))
            row = cur.fetchone()
            return self._row_to_entity(row) if row else None

    def _insert(self, sql: str, params: tuple) -> int | None:
        with self._db.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return row["id"] if row else None

    @staticmethod
    def _json_dumps(data: dict | None) -> str | None:
        if data is None:
            return None
        return json.dumps(data, ensure_ascii=False)
