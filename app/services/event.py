from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import EventModel, EventStaffModel
from app.schemas.event import EventCreate, EventUpdate

def create_event(db: Session, owner_id: int, data: EventCreate) -> EventModel:
    event = EventModel(name=data.name, description=data.description, owner_id=owner_id,)
    db.add(event)
    db.commit()
    db.refresh(event)
    staff = EventStaffModel(event_id=event.id, user_id=owner_id, role="OWNER")
    db.add(staff)
    db.commit()
    return event


def list_events_for_user(db: Session, user_id: int, keyword: Optional[str] = None) -> list[EventModel]:
    query = (
        db.query(EventModel)
        .join(EventStaffModel, EventStaffModel.event_id == EventModel.id)
        .filter(EventStaffModel.user_id == user_id)
    )
    if keyword:
        query = query.filter(EventModel.name.ilike(f"%{keyword}%"))
    return query.order_by(EventModel.id).all()


def get_event_or_404(db: Session, event_id: int) -> EventModel:
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sự kiện không tồn tại")
    return event


def get_staff(db: Session, event_id: int, user_id: int) -> Optional[EventStaffModel]:
    return (db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id, EventStaffModel.user_id == user_id).first())


def require_member(db: Session, event_id: int, user_id: int) -> EventStaffModel:
    staff = get_staff(db, event_id, user_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên sự kiện này")
    return staff


def require_owner(db: Session, event_id: int, user_id: int) -> EventStaffModel:
    staff = require_member(db, event_id, user_id)
    if staff.role != "OWNER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ Owner mới có quyền thực hiện")
    return staff


def update_event(db: Session, event: EventModel, data: EventUpdate) -> EventModel:
    if data.name is not None:
        event.name = data.name
    if data.description is not None:
        event.description = data.description
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: EventModel) -> None:
    db.delete(event)
    db.commit()


def add_member(db: Session, event_id: int, user_id: int) -> EventStaffModel:
    existing = get_staff(db, event_id, user_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người dùng đã là thành viên sự kiện")
    staff = EventStaffModel(event_id=event_id, user_id=user_id, role="MEMBER")
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def list_members(db: Session, event_id: int,) -> list[EventStaffModel]:
    return db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.role == "MEMBER").all()

def remove_member(db: Session, event_id: int, user_id: int) -> None:
    staff = get_staff(db, event_id, user_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thành viên không tồn tại")
    if staff.role == "OWNER":
        owner_count = (db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id, EventStaffModel.role == "OWNER").count())
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa owner cuối cùng của sự kiện",
            )
    db.delete(staff)
    db.commit()