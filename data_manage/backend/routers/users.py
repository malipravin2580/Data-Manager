from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


class UserListResponse(BaseModel):
    id: int
    username: str
    full_name: str | None
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[UserListResponse])
def list_users(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.username.asc()).all()
    return [UserListResponse.model_validate(user) for user in users]
