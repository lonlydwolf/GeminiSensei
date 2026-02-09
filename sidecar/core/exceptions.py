class BaseAppException(Exception):
    """Base exception for all application errors."""

    message: str
    code: str
    details: dict[str, object]

    def __init__(self, message: str, code: str, details: dict[str, object] | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ExternalAPIError(BaseAppException):
    """Raised when an external API (like Google Gemini) fails."""

    def __init__(self, message: str, details: dict[str, object] | None = None):
        super().__init__(message=message, code="EXTERNAL_API_ERROR", details=details)


class QuotaExceededError(BaseAppException):
    """Raised when an API quota is exceeded."""

    def __init__(self, message: str = "Quota exceeded", details: dict[str, object] | None = None):
        super().__init__(message=message, code="QUOTA_EXCEEDED", details=details)


class LessonError(Exception):
    """Base exception for lesson-related errors."""

    pass


class LessonNotFoundError(LessonError):
    """Raised when a lesson is not found."""

    pass
