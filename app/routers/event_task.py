from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.event_task import EventTaskCreate, EventTaskResponse, EventTaskUpdate
from app.services.event import get_event_or_404, require_member
from app.services.event_task import (
    create_task,
    delete_task,
    get_task_or_404,
    list_tasks,
    update_task,
)

router = APIRouter(tags=["Event Tasks"])


@router.post(
    "/events/{event_id}/event-tasks",
    response_model=EventTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    event_id: int,
    data: EventTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_event_or_404(db, event_id)
    require_member(db, event_id, current_user.id)
    return create_task(db, event_id, data)


@router.get("/events/{event_id}/event-tasks", response_model=list[EventTaskResponse])
def list_tasks_endpoint(
    event_id: int,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|due_date)$"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_event_or_404(db, event_id)
    require_member(db, event_id, current_user.id)
    return list_tasks(
        db,
        event_id,
        status_filter=status_filter,
        priority_filter=priority,
        assignee_id=assignee_id,
        search=search,
        sort_by=sort_by,
        page=page,
        size=size,
    )


@router.get("/event-tasks/{task_id}", response_model=EventTaskResponse)
def get_task_endpoint(
    task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    task = get_task_or_404(db, task_id)
    require_member(db, task.event_id, current_user.id)
    return task


@router.patch("/event-tasks/{task_id}", response_model=EventTaskResponse)
def update_task_endpoint(
    task_id: int,
    data: EventTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_or_404(db, task_id)
    require_member(db, task.event_id, current_user.id)
    return update_task(db, task, data)


@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    task = get_task_or_404(db, task_id)
    require_member(db, task.event_id, current_user.id)
    delete_task(db, task)