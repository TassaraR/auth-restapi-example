import datetime
import os

import jwt

from api.models import UserCreate


def test_get_user(test_create_user: UserCreate):
    import api.auth

    user = api.auth.get_user("user")
    assert user is not None
    assert user == test_create_user


def test_get_user_not_found(test_create_user: UserCreate):
    import api.auth

    user = api.auth.get_user("other")
    assert user is None


def test_authenticate_user(test_create_user: UserCreate):
    import api.auth

    auth_user = api.auth.authenticate_user(username="user", password="pass")

    assert auth_user
    assert auth_user == test_create_user

    auth_user = api.auth.authenticate_user(username="user", password="other")
    assert auth_user is False


def test_create_access_token():
    import api.auth

    data = {"sub": "user"}
    expire = datetime.timedelta(int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")

    token = api.auth.create_access_token(data=data, expire_deltas=expire)

    decoded = jwt.decode(token, key=secret_key, algorithms=algorithm)

    assert decoded.get("sub") == "user"
    assert "exp" in decoded
