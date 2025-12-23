from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    full_name: str | None = None
    password: str


class UserOut(BaseModel):
    username: str
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class RefreshRequest(BaseModel):
    refresh_token: str

