from uuid import UUID

import sqlalchemy as sa

from chat_service.core.base_dao import BaseDAORO, BaseDAOWO
from chat_service.db.models import Chat
from chat_service.web.dtos.chat_dtos import ChatInputDTO


class ChatReadDAO(BaseDAORO[Chat]):
    """Class for accessing Chat table READ."""

    async def get_chat_if_participant(
        self, chat_id: UUID, user_id: UUID
    ) -> Chat | None:
        """Get chat if participant."""

        query = (
            sa.select(self.model)
            .where(
                sa.or_(
                    self.model.user_id_1 == user_id,
                    self.model.user_id_2 == user_id,
                )
            )
            .where(self.model.id == chat_id)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class ChatWriteDAO(ChatReadDAO, BaseDAOWO[Chat, ChatInputDTO]):
    """Class for accessing Chat table WRITE."""
