from typing import Annotated
from uuid import UUID

from fastapi import Depends

from chat_service import exceptions
from chat_service.db.models import Server
from chat_service.utils.daos import ReadDAOs
