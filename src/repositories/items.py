import logging
from typing import Any

from src.domain.entities import Item
from src.domain.enums import ItemType, Marketplace
from src.domain.interfaces import IItemRepository
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ItemRepository(BaseRepository[Item], IItemRepository):
    table = "items"

    def _row_to_entity(self, row: dict[str, Any]) -> Item:
        return Item(
            id=row["id"],
            marketplace=Marketplace(row["marketplace"]),
            item_type=ItemType(row["item_type"]),
            external_id=row["external_id"],
            product_id=row["product_id"],
            author_name=row["author_name"],
            rating=row["rating"],
            text=row["text"],
            raw_json=row["raw_json"],
            fetched_at=row["fetched_at"],
        )

    def insert(self, item: Item) -> int | None:
        sql = """
            INSERT INTO items (marketplace, item_type, external_id, product_id,
                               author_name, rating, text, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (marketplace, external_id) DO NOTHING
            RETURNING id
        """
        result = self._insert(sql, (
            item.marketplace.value,
            item.item_type.value,
            item.external_id,
            item.product_id,
            item.author_name,
            item.rating,
            item.text,
            self._json_dumps(item.raw_json),
        ))
        if result is not None:
            item.id = result
        return result

    def get_untagged(self) -> list[Item]:
        sql = """
            SELECT i.* FROM items i
            LEFT JOIN tags t ON t.item_id = i.id
            WHERE t.id IS NULL
            ORDER BY i.fetched_at ASC
        """
        with self._db.cursor() as cur:
            cur.execute(sql)
            return [self._row_to_entity(row) for row in cur.fetchall()]
