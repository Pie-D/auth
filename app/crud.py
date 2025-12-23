from sqlalchemy.orm import Session

from app import models
from app.schemas import UserCreate
from app.security import hash_password


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> models.User:
    db_user = models.User(
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_session_by_user_id(db: Session, user_id: str) -> models.Session | None:
    return db.query(models.Session).filter(models.Session.user_id == user_id).first()


def get_session_by_refresh_token(
    db: Session, refresh_token: str
) -> models.Session | None:
    return (
        db.query(models.Session)
        .filter(models.Session.refresh_token == refresh_token)
        .first()
    )


def get_session_by_user_device(
    db: Session, user_id: str, device_id: str
) -> models.Session | None:
    return (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id, models.Session.device_id == device_id)
        .first()
    )


def create_session(
    db: Session, user_id: str, device_id: str, refresh_token: str
) -> models.Session:
    session = models.Session(
        user_id=user_id, device_id=device_id, refresh_token=refresh_token
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def touch_session(db: Session, session: models.Session) -> models.Session:
    # chỉ cập nhật last_used_at
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session: models.Session) -> None:
    db.delete(session)
    db.commit()

