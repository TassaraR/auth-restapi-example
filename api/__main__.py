import datetime
from typing import Annotated

import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from api.models import Token, TokenData, User, UserInDB

# openssl rand -hex 32
SECRET_KEY = "aaff11c39f767ce0c4408b49f805dc81c5f4e25428460eb3b4d442c2c4349a26"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        # password: "secret"
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", 
        "disabled": False
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(secret=plain_password, hash=hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# TODO: db should not be a dict
def get_user(db: dict, username: str) -> UserInDB | None:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
# TODO: fake_db should not be a dict
def authenticate_user(fake_db: dict, username: str, password: str) -> UserInDB | bool:
    user = get_user(db=fake_db, username=username)
    if not user:
        return False
    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expire_deltas: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expire_deltas:
        expire = datetime.datetime.now(tz=datetime.UTC) + expire_deltas
    else:
        expire = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(minutes=15)
    # The field must be called exp for this to work
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB | HTTPException:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # Means subject
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(db=fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(fake_db=fake_users_db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expire_deltas=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> list[dict]:
    return [
        {"item_id": "Foo", "owner": current_user.username}
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
