import logging
from typing import Any

from src.domain.entities import Item, Response
from src.domain.enums import ItemType, Marketplace
from src.domain.interfaces import IResponseRepository
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ResponseRepository(BaseRepository[Response], IResponseRepository):
    table = "responses"

    def _row_to_entity(self, row: dict[str, Any]) -> Response:
        return Response(
            id=row["id"],
            item_id=row["item_id"],
            response_text=row["response_text"],
            model_name=row["model_name"],
            generated_at=row["generated_at"],
        )

    def insert(self, response: Response) -> int:
        sql = """
            INSERT INTO responses (item_id, response_text, model_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (item_id) DO NOTHING
            RETURNING id
        """
        result = self._insert(sql, (
            response.item_id,
            response.response_text,
            response.model_name,
        ))
        response.id = result
        return result

    def get_unsent(self) -> list[tuple[Response, Item]]:
        sql = """
            SELECT r.id as resp_id, r.item_id, r.response_text, r.model_name, r.generated_at,
                   i.id as item_db_id, i.marketplace, i.item_type, i.external_id,
                   i.product_id, i.author_name, i.rating, i.text, i.raw_json, i.fetched_at
            FROM responses r
            JOIN items i ON i.id = r.item_id
            LEFT JOIN send_log sl ON sl.response_id = r.id AND sl.status = 'sent'
            WHERE sl.id IS NULL
            ORDER BY r.generated_at ASC
        """
        with self._db.cursor() as cur:
            cur.execute(sql)
            results = []
            for row in cur.fetchall():
                response = Response(
                    id=row["resp_id"],
                    item_id=row["item_id"],
                    response_text=row["response_text"],
                    model_name=row["model_name"],
                    generated_at=row["generated_at"],
                )
                item = Item(
                    id=row["item_db_id"],
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
                results.append((response, item))
            return results
