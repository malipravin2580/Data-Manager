from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from models.file_provenance import FileAccessLog, FileProvenance, PermissionAuditLog


def record_file_upload(
    db: Session,
    file_path: str,
    user_id: int,
    source_file_path: Optional[str] = None,
    transformation_details: Optional[dict[str, Any]] = None,
) -> FileProvenance:
    provenance = FileProvenance(
        file_path=file_path,
        source_file_path=source_file_path,
        transformation_type="upload",
        transformation_details=transformation_details or {},
        created_by=user_id,
    )
    db.add(provenance)
    return provenance


def record_file_transformation(
    db: Session,
    output_file_path: str,
    input_file_paths: Sequence[str],
    user_id: int,
    transformation_type: str,
    transformation_details: Optional[dict[str, Any]] = None,
) -> None:
    for input_path in input_file_paths:
        db.add(
            FileProvenance(
                file_path=output_file_path,
                source_file_path=input_path,
                transformation_type=transformation_type,
                transformation_details=transformation_details or {},
                created_by=user_id,
            )
        )


def log_file_access(
    db: Session,
    file_path: str,
    user_id: int,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> FileAccessLog:
    access_log = FileAccessLog(
        file_path=file_path,
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {},
    )
    db.add(access_log)
    return access_log


def log_permission_change(
    db: Session,
    file_path: str,
    action: str,
    performed_by: int,
    target_user_id: Optional[int] = None,
    target_team_id: Optional[int] = None,
    old_permission: Optional[str] = None,
    new_permission: Optional[str] = None,
) -> PermissionAuditLog:
    audit_log = PermissionAuditLog(
        file_path=file_path,
        action=action,
        target_user_id=target_user_id,
        target_team_id=target_team_id,
        old_permission=old_permission,
        new_permission=new_permission,
        performed_by=performed_by,
    )
    db.add(audit_log)
    return audit_log


def get_file_lineage(db: Session, file_path: str, depth: int = 5) -> dict[str, Any]:
    lineage_rows = (
        db.query(FileProvenance)
        .filter(FileProvenance.file_path == file_path)
        .order_by(FileProvenance.created_at.asc(), FileProvenance.id.asc())
        .all()
    )

    ancestors = []
    seen_sources = set()
    for row in lineage_rows:
        if not row.source_file_path or row.source_file_path in seen_sources:
            continue
        seen_sources.add(row.source_file_path)
        ancestors.append(
            {
                "file_path": row.source_file_path,
                "transformation_type": row.transformation_type,
                "created_at": row.created_at,
                "created_by": row.creator.username if row.creator else None,
            }
        )

    descendants_rows = (
        db.query(FileProvenance)
        .filter(FileProvenance.source_file_path == file_path)
        .order_by(FileProvenance.created_at.desc(), FileProvenance.id.desc())
        .all()
    )

    descendants = []
    seen_descendants = set()
    for row in descendants_rows:
        if row.file_path in seen_descendants:
            continue
        seen_descendants.add(row.file_path)
        descendants.append(
            {
                "file_path": row.file_path,
                "transformation_type": row.transformation_type,
                "created_at": row.created_at,
                "created_by": row.creator.username if row.creator else None,
            }
        )

    # Best-effort depth cap for direct ancestors list in this schema.
    ancestors = ancestors[-max(depth, 0) :]

    return {
        "current_file": file_path,
        "ancestors": ancestors,
        "descendants": descendants,
    }


def get_file_access_history(db: Session, file_path: str, limit: int = 100) -> list[dict[str, Any]]:
    logs = (
        db.query(FileAccessLog)
        .filter(FileAccessLog.file_path == file_path)
        .order_by(FileAccessLog.created_at.desc(), FileAccessLog.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "user": log.user.username if log.user else None,
            "action": log.action,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
            "details": log.details,
        }
        for log in logs
    ]


def get_permission_audit_history(db: Session, file_path: str, limit: int = 100) -> list[dict[str, Any]]:
    logs = (
        db.query(PermissionAuditLog)
        .filter(PermissionAuditLog.file_path == file_path)
        .order_by(PermissionAuditLog.created_at.desc(), PermissionAuditLog.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
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
