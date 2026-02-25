from pathlib import Path
import math

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.file_permission import ActivityLog, FilePermission, PermissionLevel
from models.user import User
from routers.auth import get_current_user
from services.permission_service import check_file_permission
from services.provenance_service import log_file_access, record_file_upload

import sys
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from data_manager import DataManager

router = APIRouter(prefix="/files", tags=["Files"])
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
dm = DataManager(str(settings.DATA_DIR))


def _sanitize_json_value(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_json_value(v) for v in value]
    return value


@router.get("/list")
def list_files(
    path: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    full_path = settings.DATA_DIR / path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Directory not found")

    files = []
    for item in full_path.iterdir():
        rel = str(item.relative_to(settings.DATA_DIR))
        if item.is_dir() or check_file_permission(db, current_user.id, rel, PermissionLevel.VIEW):
            stat = item.stat()
            files.append(
                {
                    "name": item.name,
                    "type": "folder" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": stat.st_mtime,
                    "path": rel,
                }
            )
    return {"path": path, "files": files}


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    path: str = Query(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    save_path = settings.DATA_DIR / path / file.filename
    save_path.parent.mkdir(parents=True, exist_ok=True)

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    rel_path = str(save_path.relative_to(settings.DATA_DIR))
    existing = db.query(FilePermission).filter(
        FilePermission.file_path == rel_path, FilePermission.user_id == current_user.id
    ).first()
    if existing and not check_file_permission(db, current_user.id, rel_path, PermissionLevel.EDIT):
        raise HTTPException(status_code=403, detail="No permission to upload here")

    with open(save_path, "wb") as f:
        f.write(contents)

    if not existing:
        perm = FilePermission(
            file_path=rel_path,
            user_id=current_user.id,
            permission=PermissionLevel.ADMIN,
            granted_by=current_user.id,
        )
        db.add(perm)

    db.add(
        ActivityLog(
            user_id=current_user.id,
            action="file.upload",
            resource_type="file",
            resource_id=rel_path,
            ip_address=request.client.host if request.client else None,
        )
    )
    record_file_upload(
        db=db,
        file_path=rel_path,
        user_id=current_user.id,
        transformation_details={"size": len(contents), "filename": file.filename},
    )
    log_file_access(
        db=db,
        file_path=rel_path,
        user_id=current_user.id,
        action="upload",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"filename": file.filename, "size": len(contents)},
    )
    db.commit()

    return {"message": "File uploaded", "path": rel_path}


@router.get("/preview/{file_path:path}")
def preview_file(
    request: Request,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.VIEW):
        raise HTTPException(status_code=403, detail="No permission to view this file")
    try:
        df = dm.load(file_path)
        columns = [
            {
                "name": str(col),
                "dtype": str(dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
            }
            for col, dtype in df.dtypes.items()
        ]
        log_file_access(
            db=db,
            file_path=file_path,
            user_id=current_user.id,
            action="view",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        db.commit()
        response = {
            "columns": columns,
            "data": df.head(100).to_dict(orient="records"),
            "total_rows": len(df),
            "metadata": {},
        }
        return _sanitize_json_value(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/download/{file_path:path}")
def download_file(
    request: Request,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.VIEW):
        raise HTTPException(status_code=403, detail="No permission to download")

    full_path = settings.DATA_DIR / file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    log_file_access(
        db=db,
        file_path=file_path,
        user_id=current_user.id,
        action="download",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    return FileResponse(full_path, filename=full_path.name)


@router.delete("/{file_path:path}")
def delete_file(
    request: Request,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, file_path, PermissionLevel.ADMIN):
        raise HTTPException(status_code=403, detail="No permission to delete")

    full_path = settings.DATA_DIR / file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    full_path.unlink()
    db.query(FilePermission).filter(FilePermission.file_path == file_path).delete()
    db.add(
        ActivityLog(
            user_id=current_user.id,
            action="file.delete",
            resource_type="file",
            resource_id=file_path,
            ip_address=request.client.host if request.client else None,
        )
    )
    log_file_access(
        db=db,
        file_path=file_path,
        user_id=current_user.id,
        action="delete",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()

    return {"message": "File deleted"}
