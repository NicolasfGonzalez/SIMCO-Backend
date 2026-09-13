import uuid

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    ForeignKey,
    text,
    TIMESTAMP
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from core.database import Base


class Greenhouse(Base):

    __tablename__ = "greenhouse"

    id_greenhouse = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(100),
        nullable=False
    )

    id_client = Column(
        ForeignKey("client.id_client"),
        nullable=False
    )

    location = Column(
        String(200),
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )

    client = relationship(
        "Client",
        back_populates="greenhouses"
    )

    assignments = relationship(
        "Assignment",
        backref="greenhouse",
        cascade="all, delete-orphan"
    )