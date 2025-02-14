import datetime
import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from api.database import engine
from api.models import TokenData, UserBase, UserCreate
from api.password import PasswordManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(username: str) -> UserCreate | None:
    """Retrieve the user if exists"""
    with Session(engine) as session:
        statement = select(UserCreate).where(UserCreate.username == username)
        user = session.exec(statement).first()
    if user:
        return user
    return None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserBase | HTTPException:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            jwt=token, key=os.environ["SECRET_KEY"], algorithms=[os.environ["ALGORITHM"]]
        )
        username: str = payload.get("sub")  # Means subject
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user: UserBase = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    self, current_user: Annotated[UserBase, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def authenticate_user(username: str, password: str) -> UserBase | bool:
    user = get_user(username=username)
    if not user:
        return False
    if not PasswordManager().verify_password(
        plain_password=password, hashed_password=user.password
    ):
        return False
    return user


def create_access_token(data: dict, expire_deltas: datetime.timedelta | None = None) -> str:
    """Creates access token based on sub(subject) and exp(expiration)"""
    to_encode = data.copy()
    if expire_deltas:
        expire = datetime.datetime.now(tz=datetime.UTC) + expire_deltas
    else:
        expire = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(minutes=15)
    # The field must be called exp for this to work
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode, key=os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"]
    )
    return encoded_jwt
