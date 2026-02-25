from typing import Optional

from sqlalchemy.orm import Session

from models.file_permission import FilePermission, PermissionLevel


_RANK = {
    PermissionLevel.VIEW: 1,
    PermissionLevel.EDIT: 2,
    PermissionLevel.ADMIN: 3,
}


def check_file_permission(
    db: Session,
    user_id: int,
    file_path: str,
    required_permission: PermissionLevel,
) -> bool:
    perms = (
        db.query(FilePermission)
        .filter(FilePermission.file_path == file_path, FilePermission.user_id == user_id)
        .all()
    )
    if not perms:
        return False
    best = max((_RANK[p.permission] for p in perms), default=0)
    return best >= _RANK[required_permission]


def get_user_permission(db: Session, user_id: int, file_path: str) -> Optional[PermissionLevel]:
    perms = (
        db.query(FilePermission)
        .filter(FilePermission.file_path == file_path, FilePermission.user_id == user_id)
        .all()
    )
    if not perms:
        return None
    if any(p.permission == PermissionLevel.ADMIN for p in perms):
        return PermissionLevel.ADMIN
    if any(p.permission == PermissionLevel.EDIT for p in perms):
        return PermissionLevel.EDIT
    return PermissionLevel.VIEW
