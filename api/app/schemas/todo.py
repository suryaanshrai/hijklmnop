from sqlalchemy import Column, String, DateTime, Boolean, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.schemas import Base


class Todo(Base):
    __tablename__ = 'todos'

    id = Column(String(36), primary_key=True, index=True, default=uuid.uuid4)

    task = Column(String(256), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="todos")