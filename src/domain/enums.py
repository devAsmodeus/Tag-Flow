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


class Emotion(StrEnum):
    ANGER = "anger"
    DISAPPOINTMENT = "disappointment"
    FRUSTRATION = "frustration"
    SURPRISE = "surprise"
    GRATITUDE = "gratitude"
    INDIFFERENCE = "indifference"


class Intent(StrEnum):
    RETURN = "return"
    EXCHANGE = "exchange"
    COMPLAINT = "complaint"
    INFO = "info"
    GRATITUDE = "gratitude"


class ResponseTone(StrEnum):
    APOLOGY = "apology"
    GRATITUDE = "gratitude"
    CLARIFICATION = "clarification"
    INFORMATIONAL = "informational"


class Responsibility(StrEnum):
    SELLER = "seller"
    MARKETPLACE = "marketplace"
    BOTH = "both"
    NONE = "none"


class SendStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
