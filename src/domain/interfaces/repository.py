from abc import ABC, abstractmethod

from src.domain.entities import Item, Response, SendLogEntry, Tag
from src.domain.enums import SendStatus


class IItemRepository(ABC):
    @abstractmethod
    def insert(self, item: Item) -> int | None:
        """Insert item, return id. Return None if duplicate."""
        ...

    @abstractmethod
    def get_untagged(self) -> list[Item]:
        ...

    @abstractmethod
    def get_by_id(self, item_id: int) -> Item | None:
        ...


class ITagRepository(ABC):
    @abstractmethod
    def insert(self, tag: Tag) -> int:
        ...

    @abstractmethod
    def get_by_item_id(self, item_id: int) -> Tag | None:
        ...

    @abstractmethod
    def get_items_needing_response(self) -> list[tuple[Item, Tag]]:
        """Items with requires_response=True and no response yet."""
        ...


class IResponseRepository(ABC):
    @abstractmethod
    def insert(self, response: Response) -> int:
        ...

    @abstractmethod
    def get_unsent(self) -> list[tuple[Response, Item]]:
        """Responses without a successful send_log entry."""
        ...


class ISendLogRepository(ABC):
    @abstractmethod
    def insert(self, entry: SendLogEntry) -> int:
        ...

    @abstractmethod
    def update_status(
        self, entry_id: int, status: SendStatus, error_message: str | None = None
    ) -> None:
        ...

    @abstractmethod
    def get_failed_for_retry(self, max_retries: int) -> list[SendLogEntry]:
        ...
