import logging
from typing import Any

from src.domain.entities import SendLogEntry
from src.domain.enums import Marketplace, SendStatus
from src.domain.interfaces import ISendLogRepository
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class SendLogRepository(BaseRepository[SendLogEntry], ISendLogRepository):
    table = "send_log"

    def _row_to_entity(self, row: dict[str, Any]) -> SendLogEntry:
        return SendLogEntry(
            id=row["id"],
            response_id=row["response_id"],
            marketplace=Marketplace(row["marketplace"]),
            external_id=row["external_id"],
            status=SendStatus(row["status"]),
            error_message=row["error_message"],
            attempts=row["attempts"],
            sent_at=row["sent_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def insert(self, entry: SendLogEntry) -> int:
        sql = """
            INSERT INTO send_log (response_id, marketplace, external_id,
                                  status, error_message, attempts, sent_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self._insert(sql, (
            entry.response_id,
            entry.marketplace.value,
            entry.external_id,
            entry.status.value,
            entry.error_message,
            entry.attempts,
            entry.sent_at,
        ))
        entry.id = result
        return result

    def update_status(
        self, entry_id: int, status: SendStatus, error_message: str | None = None
    ) -> None:
        sql = """
            UPDATE send_log
            SET status = %s, error_message = %s, attempts = attempts + 1,
                sent_at = CASE WHEN %s = 'sent' THEN NOW() ELSE sent_at END,
                updated_at = NOW()
            WHERE id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (status.value, error_message, status.value, entry_id))

    def get_failed_for_retry(self, max_retries: int) -> list[SendLogEntry]:
        sql = """
            SELECT * FROM send_log
            WHERE status = 'failed' AND attempts < %s
            ORDER BY updated_at ASC
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (max_retries,))
            return [self._row_to_entity(row) for row in cur.fetchall()]
