import pytest
from sqlmodel import Session, create_engine

import api.database
from api.models import UserCreate
from api.password import PasswordManager


# Hack to make monkeypatching with a session scope
@pytest.fixture(scope="session")
def monkeysession():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="session")
def patch_env_vars(monkeysession):
    monkeysession.setenv("SECRET_KEY", "secret")
    monkeysession.setenv("ALGORITHM", "HS256")
    monkeysession.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")


@pytest.fixture(scope="session", autouse=True)
def patch_engine(monkeysession):
    monkeysession.setattr(api.database, "engine", create_engine("duckdb:///:memory:"))
    assert str(api.database.engine.url) == "duckdb:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def test_create_user(patch_engine, patch_env_vars):
    api.database.init_db(api.database.engine)

    user = UserCreate(
        username="user",
        password=PasswordManager.get_password_hash("pass"),
        full_name="User Name",
        email="use@mail.com",
    )

    try:
        with Session(api.database.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
    except Exception:
        assert False
    assert True
    assert str(api.database.engine.url) == "duckdb:///:memory:"

    yield user
