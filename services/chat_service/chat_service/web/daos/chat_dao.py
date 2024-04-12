from chat_service.core.base_dao import BaseDAORO
from chat_service.db.models import Chat


class ChatReadDAO(BaseDAORO[Chat]):
    """Class for accessing Chat table."""
