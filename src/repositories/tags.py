import logging
from typing import Any

from src.domain.entities import Item, Tag
from src.domain.enums import Emotion, Intent, ItemType, Marketplace, Responsibility, ResponseTone, Sentiment, Urgency
from src.domain.interfaces import ITagRepository
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class TagRepository(BaseRepository[Tag], ITagRepository):
    table = "tags"

    def _row_to_entity(self, row: dict[str, Any]) -> Tag:
        return Tag(
            id=row["id"],
            item_id=row["item_id"],
            sentiment=Sentiment(row["sentiment"]) if row["sentiment"] else None,
            topic=row["topic"],
            subtopic=row.get("subtopic"),
            emotion=Emotion(row["emotion"]) if row.get("emotion") else None,
            product_issue=row.get("product_issue"),
            intent=Intent(row["intent"]) if row.get("intent") else None,
            keywords=row.get("keywords"),
            response_tone=ResponseTone(row["response_tone"]) if row.get("response_tone") else None,
            responsibility=Responsibility(row["responsibility"]) if row.get("responsibility") else None,
            urgency=Urgency(row["urgency"]),
            requires_response=row["requires_response"],
            extra=row["extra"],
            model_name=row["model_name"],
            tagged_at=row["tagged_at"],
        )

    def insert(self, tag: Tag) -> int:
        sql = """
            INSERT INTO tags (item_id, sentiment, topic, subtopic, emotion,
                              product_issue, intent, keywords, response_tone,
                              responsibility, urgency, requires_response, extra, model_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (item_id) DO NOTHING
            RETURNING id
        """
        result = self._insert(sql, (
            tag.item_id,
            tag.sentiment.value if tag.sentiment else None,
            tag.topic,
            tag.subtopic,
            tag.emotion.value if tag.emotion else None,
            tag.product_issue,
            tag.intent.value if tag.intent else None,
            tag.keywords,
            tag.response_tone.value if tag.response_tone else None,
            tag.responsibility.value if tag.responsibility else None,
            tag.urgency.value,
            tag.requires_response,
            self._json_dumps(tag.extra),
            tag.model_name,
        ))
        tag.id = result
        return result

    def get_by_item_id(self, item_id: int) -> Tag | None:
        sql = "SELECT * FROM tags WHERE item_id = %s"
        with self._db.cursor() as cur:
            cur.execute(sql, (item_id,))
            row = cur.fetchone()
            return self._row_to_entity(row) if row else None

    def get_items_needing_response(self) -> list[tuple[Item, Tag]]:
        sql = """
            SELECT i.*, t.id as tag_id, t.item_id as t_item_id,
                   t.sentiment, t.topic, t.subtopic, t.emotion,
                   t.product_issue, t.intent, t.keywords, t.response_tone, t.responsibility,
                   t.urgency, t.requires_response,
                   t.extra as tag_extra, t.model_name as tag_model, t.tagged_at
            FROM tags t
            JOIN items i ON i.id = t.item_id
            LEFT JOIN responses r ON r.item_id = t.item_id
            WHERE t.requires_response = TRUE AND r.id IS NULL
            ORDER BY t.tagged_at ASC
        """
        with self._db.cursor() as cur:
            cur.execute(sql)
            results = []
            for row in cur.fetchall():
                item = Item(
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
                tag = Tag(
                    id=row["tag_id"],
                    item_id=row["t_item_id"],
                    sentiment=Sentiment(row["sentiment"]) if row["sentiment"] else None,
                    topic=row["topic"],
                    subtopic=row.get("subtopic"),
                    emotion=Emotion(row["emotion"]) if row.get("emotion") else None,
                    product_issue=row.get("product_issue"),
                    intent=Intent(row["intent"]) if row.get("intent") else None,
                    keywords=row.get("keywords"),
                    response_tone=ResponseTone(row["response_tone"]) if row.get("response_tone") else None,
                    responsibility=Responsibility(row["responsibility"]) if row.get("responsibility") else None,
                    urgency=Urgency(row["urgency"]),
                    requires_response=row["requires_response"],
                    extra=row["tag_extra"],
                    model_name=row["tag_model"],
                    tagged_at=row["tagged_at"],
                )
                results.append((item, tag))
            return results
