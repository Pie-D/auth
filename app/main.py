from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models
from app.database import Base, engine, get_db
from app.schemas import RefreshRequest, Token, TokenPayload, UserCreate, UserOut
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_password,
)

app = FastAPI(title="FastAPI Auth Demo", version="0.1.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Tạo bảng nếu chưa có (demo)
Base.metadata.create_all(bind=engine)


def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    payload = decode_access_token(token)
    token_data = TokenPayload(sub=payload.get("sub"))
    user_id = token_data.sub
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    user = crud.create_user(db, user_in)
    return UserOut(username=user.username, full_name=user.full_name)


@app.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    device_id = form_data.client_id or "default"
    session = crud.get_session_by_user_device(db, user.id, device_id)
    if session:
        refresh_token = session.refresh_token
        crud.touch_session(db, session)
    else:
        refresh_token = create_refresh_token(user.id)
        crud.create_session(db, user.id, device_id, refresh_token)
    access_token = create_access_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@app.post("/refresh", response_model=Token)
def refresh_tokens(request: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(request.refresh_token)
    token_data = TokenPayload(sub=payload.get("sub"))
    user_id = token_data.sub
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session = crud.get_session_by_refresh_token(db, request.refresh_token)
    if not session or session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    crud.touch_session(db, session)
    new_access_token = create_access_token(user.id)
    return Token(access_token=new_access_token, refresh_token=session.refresh_token)


@app.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(request.refresh_token)
    token_data = TokenPayload(sub=payload.get("sub"))
    user_id = token_data.sub
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session = crud.get_session_by_refresh_token(db, request.refresh_token)
    if not session or session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    crud.delete_session(db, session)
    return None


@app.get("/me", response_model=UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return UserOut(username=current_user.username, full_name=current_user.full_name)

