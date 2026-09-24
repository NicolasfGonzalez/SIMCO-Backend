import uuid
from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base

class Client(Base):
    __tablename__ = "client"

    id_client = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)

    # Relación con Invernaderos
    greenhouses = relationship("Greenhouse", back_populates="client", cascade="all, delete-orphan")