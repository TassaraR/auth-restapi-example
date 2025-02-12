import uvicorn
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import timedelta
from api.token_auth import create_access_token, SECRET_KEY

app = FastAPI()

oauth2scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserLogin(BaseModel):
    username: str
    password: str


def get_current_user(token: str = Depends(oauth2scheme)):
    #oauth2scheme extracts token from authorization header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return username


@app.post("/login")
def login(user_login: UserLogin):
    """Content-Type: application/json"""
    
    print(user_login.username, user_login.password)
    if user_login.username != "john" or user_login.password != "pwd":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data = {"sub": user_login.username}, # sub = subject
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def read_current_user(current_user: str = Depends(get_current_user)):
    """Authorization bearer token"""
    return {"user": current_user}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
