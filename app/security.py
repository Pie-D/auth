from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from app.config import settings

# pwdlib 0.3.0 chỉ cung cấp hasher recommended (bao gồm bcrypt/argon2 tuỳ build)
pwd_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_hasher.verify(password, hashed)


def _create_token(
    data: Dict[str, Any], secret_key: str, expires_delta: timedelta
) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update({"iat": now, "exp": now + expires_delta})
    return jwt.encode(to_encode, secret_key, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, extra: Dict[str, Any] | None = None) -> str:
    payload = {"sub": subject}
    if extra:
        payload.update(extra)
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(payload, settings.SECRET_KEY, expires)


def create_refresh_token(subject: str, extra: Dict[str, Any] | None = None) -> str:
    payload = {"sub": subject}
    if extra:
        payload.update(extra)
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(payload, settings.REFRESH_SECRET_KEY, expires)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def decode_refresh_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

