from datetime import datetime, timedelta
import hashlib
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_MAX_PASSWORD_BYTES = 72


def _normalize_for_bcrypt(password: str) -> str:
    if len(password.encode("utf-8")) <= BCRYPT_MAX_PASSWORD_BYTES:
        return password
    # Preserve support for arbitrarily long user passwords while keeping bcrypt backend.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Backward compatibility for existing hashes produced from raw password.
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except ValueError:
        pass

    normalized = _normalize_for_bcrypt(plain_password)
    try:
        return pwd_context.verify(normalized, hashed_password)
    except ValueError:
        # Final fallback: verify against digest directly if backend still rejects.
        fallback = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        try:
            return pwd_context.verify(fallback, hashed_password)
        except ValueError:
            return False


def get_password_hash(password: str) -> str:
    normalized = _normalize_for_bcrypt(password)
    try:
        return pwd_context.hash(normalized)
    except ValueError:
        # Fallback avoids runtime failures from backend-specific bcrypt edge cases.
        fallback = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return pwd_context.hash(fallback)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
