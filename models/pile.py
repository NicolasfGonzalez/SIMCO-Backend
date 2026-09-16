import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base

class Pile(Base):
    __tablename__ = "pile"

    id_pile = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_greenhouse = Column(
        UUID(as_uuid=True),
        ForeignKey("greenhouse.id_greenhouse", ondelete="CASCADE"),
        nullable=False
    )
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    process_start_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)

    # Relaciones
    greenhouse = relationship("Greenhouse", backref="piles")
    devices = relationship("Device", back_populates="pile")