from enum import StrEnum


class Marketplace(StrEnum):
    WB = "wb"
    OZON = "ozon"
    YANDEX = "yandex"


class ItemType(StrEnum):
    REVIEW = "review"
    QUESTION = "question"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Urgency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SendStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
