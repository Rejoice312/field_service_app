"""Custom application exceptions used across the backend.

These error types let the API layer translate data access and authentication
failures into clear HTTP responses without coupling every module to FastAPI.
"""


class AppError(Exception):
    """Base exception used by backend domain logic.

    Subclasses represent expected application failures such as validation,
    authentication, and missing-resource conditions.
    """

    pass


class AuthenticationError(AppError):
    """Raised when credentials are missing, invalid, or rejected."""

    pass


class DoesNotExistError(AppError):
    """Raised when a requested record cannot be found in the database."""

    pass


class AlreadyExistsError(AppError):
    """Raised when a create action conflicts with existing persisted data."""

    pass