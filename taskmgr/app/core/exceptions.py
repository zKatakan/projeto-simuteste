from fastapi import HTTPException

class DomainError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

class NotFoundError(DomainError):
    pass

class ValidationError(DomainError):
    pass

def http_error_from_domain(e: DomainError) -> HTTPException:
    status = 422 if isinstance(e, ValidationError) else 404 if isinstance(e, NotFoundError) else 400
    return HTTPException(status_code=status, detail={"code": e.code, "message": e.message})
