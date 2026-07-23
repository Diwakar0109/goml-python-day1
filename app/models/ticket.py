import uuid

from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    priority = Column(
        Enum(
            "low",
            "medium",
            "high",
            name="priority_enum",
        ),
        default="medium",
    )

    status = Column(
        Enum(
            "open",
            "in_progress",
            "resolved",
            "closed",
            name="status_enum",
        ),
        default="open",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    assignee_email = Column(
        String(255),
        nullable=True,
    )