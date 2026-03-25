from abc import ABC, abstractmethod

from src.domain.entities import Item, Tag


class IResponder(ABC):
    @abstractmethod
    def generate(self, item: Item, tag: Tag) -> str:
        ...
