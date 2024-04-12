from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from chat_service.db.meta import meta
import uuid
import sqlalchemy as sa
from datetime import datetime, timezone


class Base(DeclarativeBase):
    """Base model for all other models."""

    metadata = meta

    __tablename__: str

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )


class Server(Base):
    """Server model."""

    __tablename__ = "server"

    title: Mapped[str] = mapped_column(sa.String(255))
    owner_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
    )


class ServerMember(Base):
    """Server Member model."""

    __tablename__ = "server_member"

    server_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("server.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True))

    server: Mapped["Server"] = relationship(
        "Server",
        foreign_keys=[server_id],
        uselist=False,
    )


class Chat(Base):
    """Chat model."""

    __tablename__ = "chat"

    user_id_1: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True))
    user_id_2: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True))


class ChatMessage(Base):
    """Chat Message model."""

    __tablename__ = "chat_message"

    chat_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("chat.id", ondelete="CASCADE")
    )
    message: Mapped[uuid.UUID] = mapped_column(sa.String(1024))

    chat: Mapped["Chat"] = relationship(
        "Chat",
        foreign_keys=[chat_id],
        uselist=False,
    )


class ServerMessage(Base):
    """Server Message model."""

    __tablename__ = "server_message"

    server_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("server.id", ondelete="CASCADE")
    )
    message: Mapped[uuid.UUID] = mapped_column(sa.String(1024))

    server: Mapped["Server"] = relationship(
        "Server",
        foreign_keys=[server_id],
        uselist=False,
    )
