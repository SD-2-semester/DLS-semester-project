from chat_service.core.base_dao import BaseDAORO, BaseDAOWO
from chat_service.db.models import ChatMessage
from chat_service.web.dtos.chat_message_dtos import ChatMessageInputDTO


class ChatMessageReadDAO(BaseDAORO[ChatMessage]):
    """Class for accessing ChatMessage table READ."""


class ChatMessageWriteDAO(
    ChatMessageReadDAO, BaseDAOWO[ChatMessage, ChatMessageInputDTO]
):
    """Class for accessing ChatMessage table WRITE."""
