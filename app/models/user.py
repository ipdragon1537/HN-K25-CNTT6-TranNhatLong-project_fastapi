from app.db.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="USER")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    owned_events = relationship("EventModel",back_populates="owner",foreign_keys="EventModel.owner_id")
    event_staff = relationship("EventStaffModel",back_populates="user")
    assigned_tasks = relationship("EventTaskModel",back_populates="assignee")