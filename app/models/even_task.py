from app.db.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, VARCHAR, Text
from sqlalchemy.orm import relationship
from enum import Enum
class EventTaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
class EventTaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
class EventTaskModel(Base):
    __tablename__ = "event_tasks"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer,ForeignKey("events.id"),nullable=False)
    title = Column(VARCHAR(255), nullable=False)
    description = Column(Text)
    assignee_id = Column(Integer,ForeignKey("users.id"))
    status = Column(String(255), nullable=False)
    priority = Column(String(255), nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime,nullable=False,default=datetime.now)
    event = relationship("EventModel",back_populates="tasks")
    assignee = relationship("UserModel",back_populates="assigned_tasks")