from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import UserModel
from app.schemas.event import EventCreate,EventUpdate,AddMember,EventResponse
from app.services.event import create_event,get_current,get_events,update_event,delete_event,add_member,delete_staff,get_event_members
from app.dependencies.auth import get_current_user
router = APIRouter(prefix="/event",tags=["Events"])
@router.post("",response_model=EventResponse,status_code=status.HTTP_201_CREATED)
def create(data:EventCreate,db:Session = Depends(get_db),current_user:UserModel = Depends(get_current_user)):
    return create_event(db,data,current_user)
@router.get("")
def get_all(seach:str |None = None,db:Session = Depends(get_db),current_user:UserModel = Depends(get_current_user)):
    return get_current(db,current_user,seach)
@router.get("/{event_id}")
def detail(event_id:int,db:Session = Depends(get_db),current_user:UserModel = Depends(get_current_user)):
    event = get_events(db,event_id,current_user)
    if not event:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bạn ko phải thành viên của sự kiện")
    return event
@router.put("/{event_id}")
def update(event_id: int,data: EventUpdate,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    result = update_event(db,event_id,data,current_user)
    if result == "NOT_OWNER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Chỉ OWNER mới được sửa sự kiện")
    if result == "EVENT_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Sự kiện không tồn tại")
    return result
@router.delete("/{event_id}")
def delete(event_id: int,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    result = delete_event(db,event_id,current_user)
    if result == "NOT_OWNER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Chỉ OWNER mới được xóa sự kiện")
    if result == "EVENT_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Sự kiện không tồn tại")
    return {"message": "Xóa sự kiện thành công"}
@router.post("/{event_id}/members")
def add(event_id: int,data: AddMember,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    result = add_member(db,event_id,data.user_id,current_user)
    if result == "NOT_OWNER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Chỉ OWNER mới được thêm thành viên")
    if result == "EVENT_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Sự kiện không tồn tại")
    if result == "USER_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User không tồn tại")
    if result == "ALREADY_MEMBER":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User đã là thành viên")
    return {"message": "Thêm thành viên thành công"}
@router.delete("/{event_id}/members/{user_id}")
def remove_member(event_id: int,user_id: int,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    result = delete_staff(db,event_id,user_id,current_user)
    if result == "NOT_OWNER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Chỉ OWNER mới được xóa thành viên")
    if result == "MEMBER_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Thành viên không tồn tại")
    if result == "CANNOT_DELETE_OWNER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Không được xóa OWNER")
    return {"message": "Xóa thành viên thành công"}
@router.get("/{event_id}/members")
def members(event_id: int,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    result = get_event_members(db,event_id,current_user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bạn không phải thành viên của sự kiện")
    return [
        {
            "user_id": staff.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": staff.role,
            "joined_at": staff.joined_at
        }
        for staff, user in result
    ]