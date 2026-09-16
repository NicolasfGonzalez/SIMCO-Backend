import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base

class Device(Base):
    __tablename__ = "device"
    __table_args__ = {'extend_existing': True}

    id_device = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_greenhouse = Column(UUID(as_uuid=True), ForeignKey("greenhouse.id_greenhouse", ondelete="CASCADE"), nullable=False)
    id_pile = Column(UUID(as_uuid=True), ForeignKey("pile.id_pile", ondelete="SET NULL"), nullable=True)
    
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    registered_at = Column(TIMESTAMP, server_default=text("NOW()"), nullable=False)

    # Relaciones ORM
    greenhouse = relationship("Greenhouse", backref="devices")
    pile = relationship("Pile", back_populates="devices")
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")