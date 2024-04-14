from typing import Annotated
from uuid import UUID

import sqlalchemy as sa
from fastapi import Depends

from chat_service import exceptions
from chat_service.db.models import Chat
from chat_service.utils.daos import ReadDAOs


async def get_chat_by_id(chat_id: UUID, r_daos: ReadDAOs) -> Chat:
    """Get chat by id."""

    return await r_daos.chat.get_by_id_or_error(chat_id)


GetChat = Annotated[Chat, Depends(get_chat_by_id)]


async def get_chat_if_participant(
    chat: GetChat, user_id: UUID, r_daos: ReadDAOs
) -> Chat:
    """Get chat if user is a participant."""

    existing_chat = await r_daos.chat.get_chat_if_participant(chat.id, user_id)

    if existing_chat is None:
        raise exceptions.Http404("User is not a participant of this chat.")

    return chat


GetChatIfParticipant = Annotated[Chat, Depends(get_chat_if_participant)]
