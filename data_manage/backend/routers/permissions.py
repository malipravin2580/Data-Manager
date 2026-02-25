from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.file_permission import FilePermission, PermissionLevel
from models.user import User
from routers.auth import get_current_user
from services.permission_service import check_file_permission
from services.provenance_service import log_permission_change

router = APIRouter(prefix="/permissions", tags=["Permissions"])


class GrantPermissionRequest(BaseModel):
    file_path: str
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    permission: PermissionLevel


class PermissionResponse(BaseModel):
    id: int
    file_path: str
    user_id: Optional[int]
    team_id: Optional[int]
    permission: PermissionLevel

    class Config:
        from_attributes = True


@router.get("/file/{file_path:path}")
def get_file_permissions(
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.ADMIN):
        raise HTTPException(status_code=403, detail="No permission to view permissions")

    perms = db.query(FilePermission).filter(FilePermission.file_path == file_path).all()
    return [PermissionResponse.model_validate(p) for p in perms]


@router.post("/grant")
def grant_permission(
    request: GrantPermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, request.file_path, PermissionLevel.ADMIN):
        raise HTTPException(status_code=403, detail="No permission to grant permissions")

    if not request.user_id and not request.team_id:
        raise HTTPException(status_code=400, detail="Either user_id or team_id required")

    existing = (
        db.query(FilePermission)
        .filter(
            FilePermission.file_path == request.file_path,
            FilePermission.user_id == request.user_id,
            FilePermission.team_id == request.team_id,
        )
        .first()
    )

    if existing:
        old_permission = existing.permission.value
        existing.permission = request.permission
        action = "update"
    else:
        old_permission = None
        action = "grant"
        db.add(
            FilePermission(
                file_path=request.file_path,
                user_id=request.user_id,
                team_id=request.team_id,
                permission=request.permission,
                granted_by=current_user.id,
            )
        )

    log_permission_change(
        db=db,
        file_path=request.file_path,
        action=action,
        performed_by=current_user.id,
        target_user_id=request.user_id,
        target_team_id=request.team_id,
        old_permission=old_permission,
        new_permission=request.permission.value,
    )
    db.commit()
    return {"message": "Permission granted"}


@router.delete("/revoke/{permission_id}")
def revoke_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    perm = db.query(FilePermission).filter(FilePermission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    if not check_file_permission(db, current_user.id, perm.file_path, PermissionLevel.ADMIN):
        raise HTTPException(status_code=403, detail="No permission to revoke")

    log_permission_change(
        db=db,
        file_path=perm.file_path,
        action="revoke",
        performed_by=current_user.id,
        target_user_id=perm.user_id,
        target_team_id=perm.team_id,
        old_permission=perm.permission.value,
        new_permission=None,
    )
    db.delete(perm)
    db.commit()
    return {"message": "Permission revoked"}
