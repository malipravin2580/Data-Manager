from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.file_provenance import PermissionAuditLog
from models.user import User, UserRole
from routers.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/permissions")
def get_permission_audit_feed(
    file_path: Optional[str] = None,
    user_id: Optional[int] = None,
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin permission required")

    query = db.query(PermissionAuditLog)

    cutoff = datetime.utcnow() - timedelta(days=days)
    query = query.filter(PermissionAuditLog.created_at >= cutoff)

    if file_path:
        query = query.filter(PermissionAuditLog.file_path == file_path)

    if user_id:
        query = query.filter(PermissionAuditLog.performed_by == user_id)

    logs = (
        query.order_by(PermissionAuditLog.created_at.desc(), PermissionAuditLog.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "file_path": log.file_path,
            "action": log.action,
            "target_user": log.target_user.username if log.target_user else None,
            "target_team_id": log.target_team_id,
            "old_permission": log.old_permission,
            "new_permission": log.new_permission,
            "performed_by": log.performer.username if log.performer else None,
            "created_at": log.created_at,
        }
        for log in logs
    ]
