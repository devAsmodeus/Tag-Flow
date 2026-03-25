from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    response_text: str
    model_name: str | None = None
    id: int | None = None
    generated_at: datetime | None = None
