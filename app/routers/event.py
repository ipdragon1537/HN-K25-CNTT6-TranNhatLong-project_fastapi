from typing import Optional

from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import UserModel
from app.schemas.event import EventCreate, EventResponse, EventUpdate, MemberAdd, MemberResponse
from app.services.event import (
    add_member,
    create_event,
    delete_event,
    get_event_or_404,
    list_events_for_user,
    list_members,
    remove_member,
    require_member,
    require_owner,
    update_event,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event_endpoint(
    data: EventCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    if current_user.role == "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="ADMIM ko đc tạo sự kiện")
    return create_event(db, current_user.id, data)


@router.get("", response_model=list[EventResponse])
def list_events(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return list_events_for_user(db, current_user.id, search)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    event = get_event_or_404(db, event_id)
    require_member(db, event_id, current_user.id)   
    return event


@router.patch("/{event_id}", response_model=EventResponse)
def update_event_endpoint(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    event = get_event_or_404(db, event_id)
    require_owner(db, event_id, current_user.id)
    return update_event(db, event, data)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_endpoint(
    event_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    event = get_event_or_404(db, event_id)
    require_owner(db, event_id, current_user.id)
    delete_event(db, event)


@router.post("/{event_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def add_member_endpoint(
    event_id: int,
    data: MemberAdd,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    get_event_or_404(db, event_id)
    require_owner(db, event_id, current_user.id)
    return add_member(db, event_id, data.user_id)


@router.get("/{event_id}/members", response_model=list[MemberResponse])
def list_members_endpoint(
    event_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    get_event_or_404(db, event_id)
    require_member(db, event_id, current_user.id)
    return list_members(db, event_id)


@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member_endpoint(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    get_event_or_404(db, event_id)
    require_owner(db, event_id, current_user.id)
    remove_member(db, event_id, user_id)