from fastapi import HTTPException
from starlette import status


class Http404(HTTPException):
    """Not found 404."""

    def __init__(self, detail: str = "Record not found"):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail
