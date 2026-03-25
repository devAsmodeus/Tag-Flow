from abc import ABC, abstractmethod

from src.domain.entities import Item


class ICollector(ABC):
    @abstractmethod
    def fetch_new_items(self) -> list[Item]:
        ...
