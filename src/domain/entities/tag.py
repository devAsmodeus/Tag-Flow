from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from src.domain.enums import Sentiment, Urgency


class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    sentiment: Sentiment | None = None
    topic: str | None = None
    urgency: Urgency = Urgency.LOW
    requires_response: bool = True
    extra: dict[str, Any] | None = None
    model_name: str | None = None
    id: int | None = None
    tagged_at: datetime | None = None
