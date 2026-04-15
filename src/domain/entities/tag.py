from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from src.domain.enums import Emotion, Intent, Responsibility, ResponseTone, Sentiment, Urgency


class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    sentiment: Sentiment | None = None
    topic: str | None = None
    subtopic: str | None = None
    emotion: Emotion | None = None
    product_issue: str | None = None
    intent: Intent | None = None
    keywords: list[str] | None = None
    response_tone: ResponseTone | None = None
    responsibility: Responsibility | None = None
    urgency: Urgency = Urgency.LOW
    requires_response: bool = True
    extra: dict[str, Any] | None = None
    model_name: str | None = None
    id: int | None = None
    tagged_at: datetime | None = None
