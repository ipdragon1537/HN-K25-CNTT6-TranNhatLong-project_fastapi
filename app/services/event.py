from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import UserModel
from app.models.event import EventModel,EventStaffModel
from app.models.even_task import EventTaskModel
def create_event(db:Session,data,current_user:UserModel):
    event = EventModel(
        name = data.name,
        description = data.description,
        owner_id = current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    staff = EventStaffModel(
        event_id = event.id,
        user_id = current_user.id,
        role = "OWNER",
        joined_at = datetime.now()
    )
    db.add(staff)
    db.commit()
    return event
def get_current(db:Session,current_user:UserModel,search:str | None = None):
    list_current = db.query(EventModel).join(EventStaffModel,EventModel.id == EventStaffModel.event_id)
    if search:
        list_current = list_current.filter(EventModel.name.ilike(f"%{search}%"))
    return list_current.all()
def get_events(db:Session,event_id:int,current_user:UserModel):
    staff = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == current_user.id).first()
    if not staff:
        return None
    return db.query(EventModel).filter(EventModel.id == event_id).first()
def update_event(db:Session,event_id:int,data,current_user:UserModel):
    list_current = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == current_user.id,EventStaffModel.role == "OWNER").first()
    if not list_current:
        return "NOT_OWNER"
    event_user = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event_user:
        return "EVENT_NOT_FOUND"
    if data.name is not None:
        data.name == event_user.name
    if data.description is not None:
        event_user.description = data.description
    db.commit()
    db.refresh(event_user)
    return event_user
def delete_event(db:Session,event_id:int,current_id:UserModel):
    list_current = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == current_id.id,EventStaffModel.role == "OWNER").first()
    if not list_current:
        return "NOT_OWNER"
    event_user = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event_user:
        return "EVENT_NOT_FOUND"
    db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id).delete()
    db.query(EventTaskModel).filter(EventTaskModel.event_id == event_id).delete()
    db.delete(event_user)
    db.commit()
    return True
def add_member(db:Session,event_id:int,user_id:int,current_user:UserModel):
    list_current = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == current_user.id,EventStaffModel.role == "OWNER").first()
    if not list_current:
        return "NOT_OWNER"
    event_user = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event_user:
        return "EVENT_NOT_FOUND"
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return "USER_NOT_FOUND"
    staff = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == user_id).first()
    if staff:
        return "ALREADY_MEMBER"
    staff = EventStaffModel(event_id = event_id,user_id = user_id,role = "MEMBER",joined_at = datetime.now())
    db.add(staff)
    db.commit()
    return staff
def delete_staff(db:Session,event_id:int,user_id:int,current_user:UserModel):
    request = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == current_user.id).first()
    if not request or request.role.upper() != "OWNER":
        return "NOT_OWNER"
    staff = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == user_id).first()
    if not staff:
        return "MEMBER_NOT_FOUND"
    if staff.role.upper() == "OWNER":
        count = db.query(func.count(EventStaffModel.event_id)).filter(EventStaffModel.event_id == event_id,EventStaffModel.role == "OWNER").scalar()
        if count <= 1:
            return "CANNOT_DELETE_OWNER"
    db.delete(staff)
    db.commit()
    return True
def get_event_members(db:Session,event_id:int,current_user :UserModel):
    current_staff = db.query(EventStaffModel).filter(EventStaffModel.event_id == event_id,EventStaffModel.user_id == current_user.id).first()
    if not current_staff:
        return None
    return db.query(EventStaffModel,UserModel).join(UserModel,EventStaffModel.user_id == UserModel.id).filter(EventStaffModel.event_id == event_id).all()
