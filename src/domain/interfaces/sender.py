from abc import ABC, abstractmethod


class ISender(ABC):
    @abstractmethod
    def send_response(self, external_id: str, text: str) -> bool:
        ...
