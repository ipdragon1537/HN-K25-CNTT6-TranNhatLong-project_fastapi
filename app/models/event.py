from app.db.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
class RoleStaff(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
class EventModel(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    owner = relationship("UserModel",back_populates="owned_events",foreign_keys=[owner_id])
    staff = relationship("EventStaffModel",back_populates="event",cascade="all,delete-orphan")
    tasks = relationship("EventTaskModel",back_populates="event")
class EventStaffModel(Base):
    __tablename__ = "event_staff"
    event_id = Column(Integer,ForeignKey("events.id",ondelete="CASCADE"),primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    role = Column(String(20), nullable=False)
    joined_at = Column(DateTime, nullable=False,default=datetime.now)
    event = relationship("EventModel",back_populates="staff")
    user = relationship("UserModel",back_populates="event_staff")
