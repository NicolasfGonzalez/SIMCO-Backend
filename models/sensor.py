import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class SensorType(Base):
    __tablename__ = "sensor_type"
    __table_args__ = {'extend_existing': True}

    id_sensor_type = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False) # Ej: Temperatura Interna, pH
    unit = Column(String(20), nullable=False)               # Ej: °C, pH, %

    # Relaciones
    sensors = relationship("Sensor", back_populates="sensor_type")


class Sensor(Base):
    __tablename__ = "sensor"
    __table_args__ = {'extend_existing': True}

    id_sensor = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_device = Column(
        UUID(as_uuid=True), 
        ForeignKey("device.id_device", ondelete="CASCADE"), 
        nullable=False
    )
    id_sensor_type = Column(
        Integer, 
        ForeignKey("sensor_type.id_sensor_type"), 
        nullable=False
    )
    code = Column(String(50), unique=True, nullable=False)  # Ej: SENS-TEMP-01
    location = Column(String(100), nullable=True)          # Ej: Centro de la Pila
    is_active = Column(Boolean, default=True, nullable=False)

    # Relaciones
    device = relationship("Device", back_populates="sensors")
    sensor_type = relationship("SensorType", back_populates="sensors")