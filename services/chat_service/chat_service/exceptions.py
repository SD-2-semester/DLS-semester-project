from fastapi import HTTPException
from starlette import status


class Http403(HTTPException):
    """Not found 404."""

    def __init__(self, detail: str = "Forbidden."):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = detail


class Http404(HTTPException):
    """Not found 404."""

    def __init__(self, detail: str = "Record not found"):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail
