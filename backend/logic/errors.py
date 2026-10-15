class AppError(Exception):
    pass
class AuthenticationError(AppError):
    pass

class DoesNotExistError(AppError):
    pass