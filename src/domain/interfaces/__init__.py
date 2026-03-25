from .collector import ICollector
from .repository import IItemRepository, IResponseRepository, ISendLogRepository, ITagRepository
from .responder import IResponder
from .sender import ISender
from .tagger import ITagger

__all__ = [
    "ICollector",
    "ISender",
    "ITagger",
    "IResponder",
    "IItemRepository",
    "ITagRepository",
    "IResponseRepository",
    "ISendLogRepository",
]
