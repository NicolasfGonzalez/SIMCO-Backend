from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base

class AlertRule(Base):
    __tablename__ = "alert_rule"
    __table_args__ = {'extend_existing': True}

    id_alert_rule = Column(Integer, primary_key=True, autoincrement=True)
    id_sensor_type = Column(Integer, ForeignKey("sensor_type.id_sensor_type"), nullable=False)
    id_greenhouse = Column(UUID(as_uuid=True), ForeignKey("greenhouse.id_greenhouse", ondelete="CASCADE"), nullable=True)
    
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(String(200), nullable=True)

    # Relaciones
    sensor_type = relationship("SensorType")
    greenhouse = relationship("Greenhouse")