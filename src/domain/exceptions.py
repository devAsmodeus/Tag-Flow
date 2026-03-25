class TagFlowException(Exception):
    """Base exception for all Tag-Flow errors."""

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(message)


class CollectionError(TagFlowException):
    """Failed to collect items from a marketplace."""


class MarketplaceAPIError(TagFlowException):
    """Marketplace API returned an error."""

    def __init__(self, marketplace: str, message: str) -> None:
        self.marketplace = marketplace
        super().__init__(f"[{marketplace}] {message}")


class TaggingError(TagFlowException):
    """Failed to tag an item."""


class LLMError(TagFlowException):
    """LLM service error (connection, timeout, etc.)."""


class LLMParseError(LLMError):
    """Failed to parse LLM response."""


class ResponseGenerationError(TagFlowException):
    """Failed to generate a response."""


class SendingError(TagFlowException):
    """Failed to send a response to marketplace."""


class DatabaseError(TagFlowException):
    """Database operation failed."""


class MigrationError(TagFlowException):
    """Database migration failed."""
