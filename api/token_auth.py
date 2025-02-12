import datetime
import jwt

DEFAULT_EXPIRATION_MINUTES = 30
SECRET_KEY = "SECRET"

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):

    payload = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expiration_minutes = datetime.timedelta(minutes=DEFAULT_EXPIRATION_MINUTES)
        expire = datetime.datetime.now(datetime.UTC) + expiration_minutes

    # must be named `exp` for expiration to work with jwt
    payload["exp"] = expire
    encoded =  jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return encoded
