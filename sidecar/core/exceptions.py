class LessonError(Exception):
    """Base exception for lesson-related errors."""
    pass


class LessonNotFoundError(LessonError):
    """Raised when a lesson is not found."""
    pass
