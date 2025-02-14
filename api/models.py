import uuid

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(SQLModel):
    username: str = Field(..., unique=True, index=True)
    email: str = Field(...)
    full_name: str = Field(...)


class UserRequest(UserBase):
    password: str = Field(..., description="Hashed password")


class UserCreate(UserRequest, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(..., default_factory=uuid.uuid4, primary_key=True)
    disabled: bool = Field(default=False)
