from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.domain.enums import Marketplace, SendStatus


class SendLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    response_id: int
    marketplace: Marketplace
    external_id: str
    status: SendStatus = SendStatus.PENDING
    error_message: str | None = None
    attempts: int = 0
    sent_at: datetime | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
