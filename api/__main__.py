import datetime
import os
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from api.auth import authenticate_user, create_access_token, get_current_active_user
from api.database import engine, init_db
from api.models import Token, UserBase, UserCreate, UserRequest
from api.password import PasswordManager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    """Creates duckdb database if it does not exist"""
    init_db(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/users/create", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def add_user(user_data: UserRequest):
    with Session(engine) as session:
        statement = select(UserCreate.uid).where(user_data.username == UserCreate.username)
        is_user = session.exec(statement).first()
        if is_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

        hashed_password = PasswordManager().get_password_hash(user_data.password)

        user = UserCreate(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            password=hashed_password,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

    return UserBase(username=user.username, email=user.email, full_name=user.email)


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(
        minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
    )
    access_token = create_access_token(
        data={"sub": user.username}, expire_deltas=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserBase)
async def read_users_me(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
) -> UserBase:
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
) -> list[dict]:
    return [{"item_id": "Foo", "owner": current_user.username}]


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
