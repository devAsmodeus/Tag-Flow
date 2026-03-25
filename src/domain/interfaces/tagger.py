from abc import ABC, abstractmethod

from src.domain.entities import Item, Tag


class ITagger(ABC):
    @abstractmethod
    def tag(self, item: Item) -> Tag:
        ...
