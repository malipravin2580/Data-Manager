from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.file_provenance import FileAccessLog
from models.user import User, UserRole
from routers.auth import get_current_user

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get("/feed")
def get_activity_feed(
    user_id: Optional[int] = None,
    file_path: Optional[str] = None,
    action: Optional[str] = None,
    days: int = 7,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(FileAccessLog)

    cutoff = datetime.utcnow() - timedelta(days=days)
    query = query.filter(FileAccessLog.created_at >= cutoff)

    if user_id and (current_user.role == UserRole.ADMIN or user_id == current_user.id):
        query = query.filter(FileAccessLog.user_id == user_id)
    elif current_user.role != UserRole.ADMIN:
        query = query.filter(FileAccessLog.user_id == current_user.id)

    if file_path:
        query = query.filter(FileAccessLog.file_path == file_path)

    if action:
        query = query.filter(FileAccessLog.action == action)

    logs = (
        query.order_by(FileAccessLog.created_at.desc(), FileAccessLog.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "file_path": log.file_path,
            "user": log.user.username if log.user else None,
            "action": log.action,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/my-activity")
def get_my_activity(
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_activity_feed(
        user_id=current_user.id,
        days=days,
        limit=limit,
        current_user=current_user,
        db=db,
    )
