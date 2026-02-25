from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.file_permission import PermissionLevel
from models.user import User
from routers.auth import get_current_user
from services.permission_service import check_file_permission
from services.provenance_service import (
    get_file_access_history,
    get_file_lineage,
    get_permission_audit_history,
    log_file_access,
)

router = APIRouter(prefix="/provenance", tags=["Provenance"])


@router.get("/lineage/{file_path:path}")
def get_file_lineage_endpoint(
    request: Request,
    file_path: str,
    depth: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.VIEW):
        raise HTTPException(status_code=403, detail="No permission to view this file")

    log_file_access(
        db,
        file_path,
        current_user.id,
        "view.lineage",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()

    return get_file_lineage(db, file_path, depth)


@router.get("/access-history/{file_path:path}")
def get_file_access_history_endpoint(
    file_path: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.ADMIN):
        raise HTTPException(status_code=403, detail="Admin permission required")

    return get_file_access_history(db, file_path, limit)


@router.get("/permission-audit/{file_path:path}")
def get_permission_audit_history_endpoint(
    file_path: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.ADMIN):
        raise HTTPException(status_code=403, detail="Admin permission required")

    return get_permission_audit_history(db, file_path, limit)
