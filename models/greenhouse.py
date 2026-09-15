import uuid
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base

class Greenhouse(Base):
    __tablename__ = "greenhouse"

    id_greenhouse = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_client = Column(UUID(as_uuid=True), ForeignKey("client.id_client", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    
    # Nombres exactos de la base de datos
    address = Column(String(200), nullable=True) 
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)

    client = relationship("Client", back_populates="greenhouses")
    assignments = relationship("Assignment", backref="greenhouse", cascade="all, delete-orphan")