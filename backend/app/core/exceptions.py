"""Centralized application exceptions and HTTP error mapping.

All API errors should raise `AppException` (or subclasses) so they are handled
consistently by the global exception handler in `app.main`.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception with an HTTP status code and error code."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: Any) -> None:
        super().__init__(
            status_code=404,
            error_code="not_found",
            message=f"{resource} with id {resource_id} not found",
            details={"resource": resource, "resource_id": str(resource_id)},
        )


class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=400,
            error_code="validation_error",
            message=message,
            details=details or {},
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=409,
            error_code="conflict",
            message=message,
            details=details or {},
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(
            status_code=401,
            error_code="unauthorized",
            message=message,
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Not enough permissions") -> None:
        super().__init__(
            status_code=403,
            error_code="forbidden",
            message=message,
        )
