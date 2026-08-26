from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.even_task import EventTaskModel
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate
from app.services.event import get_staff


def create_task(db: Session, event_id: int, data: EventTaskCreate) -> EventTaskModel:
    # Nếu có gán assignee thì assignee phải là thành viên (staff) của event
    if data.assignee_id is not None:
        if not get_staff(db, event_id, data.assignee_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Assignee phải là thành viên của sự kiện",)

    task = EventTaskModel(
        event_id=event_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        priority=data.priority,
        assignee_id=data.assignee_id,
        status="TODO",
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    event_id: int,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    page: int = 1,
    size: int = 10,
) -> list[EventTaskModel]:
    # Lọc task theo event, rồi áp thêm các filter tùy chọn (status/priority/assignee/search)
    query = db.query(EventTaskModel).filter(EventTaskModel.event_id == event_id)

    if status_filter:
        query = query.filter(EventTaskModel.status == status_filter)
    if priority_filter:
        query = query.filter(EventTaskModel.priority == priority_filter)
    if assignee_id:
        query = query.filter(EventTaskModel.assignee_id == assignee_id)
    if search:
        query = query.filter(EventTaskModel.title.ilike(f"%{search}%"))
    sort_column = EventTaskModel.due_date if sort_by == "due_date" else EventTaskModel.created_at
    query = query.order_by(sort_column)
    # Phân trang
    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()

def get_task_or_404(db: Session, task_id: int) -> EventTaskModel:
    task = db.query(EventTaskModel).filter(EventTaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Công việc không tồn tại")
    return task

def update_task(db: Session, task: EventTaskModel, data: EventTaskUpdate) -> EventTaskModel:
    # exclude_unset=True: chỉ lấy field client thật sự gửi lên, tránh ghi đè bằng None
    update_data = data.model_dump(exclude_unset=True)

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        if not get_staff(db, task.event_id, update_data["assignee_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee phải là thành viên của sự kiện",
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: EventTaskModel) -> None:
    db.delete(task)
    db.commit()