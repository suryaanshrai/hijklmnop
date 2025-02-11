from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.schemas import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, index=True, default=uuid.uuid4)
    
    username = Column(String(32), unique=True, index=True, nullable=False)
    password = Column(String(256), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    todos = relationship("Todo", back_populates="user", cascade="all, delete-orphan")