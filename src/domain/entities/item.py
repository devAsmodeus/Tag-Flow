from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from src.domain.enums import ItemType, Marketplace


class Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    marketplace: Marketplace
    item_type: ItemType
    external_id: str
    text: str
    id: int | None = None
    product_id: str | None = None
    author_name: str | None = None
    rating: int | None = None
    raw_json: dict[str, Any] | None = None
    fetched_at: datetime | None = None
