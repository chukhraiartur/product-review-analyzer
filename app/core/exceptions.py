"""Custom exception classes for the application."""


class ReviewAnalyzerException(Exception):
    """Base exception for the Review Analyzer application."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ScrapingException(ReviewAnalyzerException):
    """Raised when web scraping fails."""

    pass


class LLMException(ReviewAnalyzerException):
    """Raised when LLM API calls fail."""

    pass


class StorageException(ReviewAnalyzerException):
    """Raised when storage operations fail."""

    pass


class VectorDBException(ReviewAnalyzerException):
    """Raised when vector database operations fail."""

    pass


class ConfigurationException(ReviewAnalyzerException):
    """Raised when configuration is invalid."""

    pass
