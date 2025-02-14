import datetime
import importlib.resources as pkg_resources
import os
from contextlib import asynccontextmanager
from typing import Annotated

import jwt
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, create_engine, select

from api.database import init_db
from api.models import Token, TokenData, UserBase, UserCreate, UserRequest
from api.password import PasswordManager

load_dotenv()

with pkg_resources.path("api", "../data/duck.db") as db_path:
    DATABASE_URL = f"duckdb:///{db_path}"
engine = create_engine(DATABASE_URL, echo=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    """Creates duckdb database if it does not exist"""
    init_db(engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_user(username: str) -> UserCreate | None:
    """Retrieve the user if exists"""
    with Session(engine) as session:
        statement = select(UserCreate).where(UserCreate.username == username)
        user = session.exec(statement).first()
    if user:
        return user
    return None


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


async def get_current_active_user(current_user: Annotated[UserBase, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


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
