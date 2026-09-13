import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class Assignment(Base):
    __tablename__ = "assignment"

    id_assignment = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )
    id_user = Column(UUID(as_uuid=True), ForeignKey("user.id_user"), nullable=False)
    id_greenhouse = Column(UUID(as_uuid=True), ForeignKey("greenhouse.id_greenhouse"), nullable=False)