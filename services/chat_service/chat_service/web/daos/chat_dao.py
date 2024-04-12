from uuid import UUID
from chat_service.core.base_dao import BaseDAORO, BaseDAOWO
from chat_service.db.models import Chat
from chat_service.web.dtos.chat_dtos import ChatInputDTO
import sqlalchemy as sa


class ChatReadDAO(BaseDAORO[Chat]):
    """Class for accessing Chat table READ."""

    async def get_chat(self, user_id_1: UUID, user_id_2: UUID) -> Chat | None:
        """Get chat by users."""

        query = sa.select(self.model).where(
            sa.and_(
                self.model.user_id_1 == user_id_1,
                self.model.user_id_2 == user_id_2,
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class ChatWriteDAO(ChatReadDAO, BaseDAOWO[Chat, ChatInputDTO]):
    """Class for accessing Chat table WRITE."""


# class ChatDAO(BaseDAO[Chat, ChatInputDTO]): ...
