from fastapi import status


class AppError(Exception):
    """Базовая ошибка приложения - от него наследуются все доменные исключения"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_SERVER_ERROR"

    def __init__(
            self,
            message: str | None = None,
            status_code: int | None = None,
            error_code: str | None = None,
            details: dict | list | None = None,
    ):
        self.message = message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "DATABASE_ERROR"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "RESOURCE_NOT_FOUND"


class InvariantViolationError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "INVARIANT_VIOLATION"


class InvalidStateError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "INVALID_STATE"


class AlreadyExistsError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "ALREADY_EXISTS"


class EmailSendingFailedError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "EMAIL_SENDING_FAILED"


class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"


class UnsupportedOperationError(AppError):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    error_code = "UNSUPPORTED_OPERATION"
