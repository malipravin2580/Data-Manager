from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.file_permission import PermissionLevel
from models.share_link import ShareLink
from models.user import User
from routers.auth import get_current_user
from services.permission_service import check_file_permission
from services.share_service import create_share_link, get_shareable_url, validate_share_link

router = APIRouter(prefix="/share", tags=["Share"])


class CreateShareRequest(BaseModel):
    file_path: str
    permission: str = "view"
    expires_days: int = settings.SHARE_LINK_EXPIRE_DAYS
    password: Optional[str] = None
    max_views: Optional[int] = None


class ShareLinkResponse(BaseModel):
    id: int
    token: str
    file_path: str
    permission: str
    expires_at: datetime
    max_views: Optional[int]
    view_count: int
    url: str


@router.post("/create", response_model=ShareLinkResponse)
def create_share(
    request: CreateShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_file_permission(db, current_user.id, request.file_path, PermissionLevel.VIEW):
        raise HTTPException(status_code=403, detail="No permission to share this file")

    try:
        share = create_share_link(
            db=db,
            file_path=request.file_path,
            creator_id=current_user.id,
            permission=request.permission,
            expires_days=request.expires_days,
            password=request.password,
            max_views=request.max_views,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ShareLinkResponse(
        id=share.id,
        token=share.token,
        file_path=share.file_path,
        permission=share.permission,
        expires_at=share.expires_at,
        max_views=share.max_views,
        view_count=share.view_count,
        url=get_shareable_url(share.token),
    )


@router.get("/validate/{token}")
def validate_share(token: str, password: Optional[str] = None, db: Session = Depends(get_db)):
    share = validate_share_link(db, token, password)
    if not share:
        raise HTTPException(status_code=404, detail="Invalid or expired share link")

    return {
        "valid": True,
        "file_path": share.file_path,
        "permission": share.permission,
        "expires_at": share.expires_at,
        "view_count": share.view_count,
    }


@router.get("/my-links")
def get_my_share_links(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shares = db.query(ShareLink).filter(ShareLink.creator_id == current_user.id).all()
    return [
        ShareLinkResponse(
            id=s.id,
            token=s.token,
            file_path=s.file_path,
            permission=s.permission,
            expires_at=s.expires_at,
            max_views=s.max_views,
            view_count=s.view_count,
            url=get_shareable_url(s.token),
        )
        for s in shares
    ]


@router.delete("/{share_id}")
def delete_share_link(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    share = db.query(ShareLink).filter(ShareLink.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    if share.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your share link")

    db.delete(share)
    db.commit()
    return {"message": "Share link deleted"}
