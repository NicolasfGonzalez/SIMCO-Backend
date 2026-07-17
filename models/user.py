import uuid

from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "user"

    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))

    id_role = Column(ForeignKey("role.id_role"), nullable=False)
    id_client = Column(ForeignKey("client.id_client"))

    role = relationship("Role", back_populates="users")
    client = relationship("Client", back_populates="users")