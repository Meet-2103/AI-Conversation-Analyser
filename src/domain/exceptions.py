class AppError(Exception):
    """Base exception for all domain-level application errors."""
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

class LLMProviderError(AppError):
    """Raised when the LLM provider fails to generate a response or raises an API error."""
    pass

class DataIngestionError(AppError):
    """Raised when there is an issue parsing, reading, or processing data."""
    pass

class VectorStoreError(AppError):
    """Raised when there is an issue communicating with the vector database."""
    pass
