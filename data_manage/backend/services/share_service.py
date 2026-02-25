import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from config import settings
from models.share_link import ShareLink
from services.auth_service import get_password_hash, verify_password



def generate_share_token() -> str:
    return secrets.token_urlsafe(32)


def create_share_link(
    db: Session,
    file_path: str,
    creator_id: int,
    permission: str = "view",
    expires_days: int = settings.SHARE_LINK_EXPIRE_DAYS,
    password: Optional[str] = None,
    max_views: Optional[int] = None,
) -> ShareLink:
    password_hash = None
    if password:
        password_hash = get_password_hash(password)
    share_link = ShareLink(
        token=generate_share_token(),
        file_path=file_path,
        creator_id=creator_id,
        permission=permission,
        expires_at=datetime.utcnow() + timedelta(days=expires_days),
        password_hash=password_hash,
        max_views=max_views,
    )
    db.add(share_link)
    db.commit()
    db.refresh(share_link)
    return share_link


def validate_share_link(db: Session, token: str, password: Optional[str] = None) -> Optional[ShareLink]:
    share_link = (
        db.query(ShareLink)
        .filter(
            ShareLink.token == token,
            ShareLink.is_active.is_(True),
            ShareLink.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not share_link:
        return None

    if share_link.password_hash:
        if not password or not verify_password(password, share_link.password_hash):
            return None

    if share_link.max_views and share_link.view_count >= share_link.max_views:
        share_link.is_active = False
        db.commit()
        return None

    share_link.view_count += 1
    db.commit()
    db.refresh(share_link)
    return share_link


def get_shareable_url(token: str, frontend_url: str | None = None) -> str:
    base = (frontend_url or settings.FRONTEND_URL).rstrip("/")
    return f"{base}/share/{token}"
