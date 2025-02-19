from api.password import PasswordManager


def test_get_password_hash_and_verify():
    password = "password"
    hashed_password = PasswordManager.get_password_hash(password)

    assert isinstance(hashed_password, bytes)
    assert hashed_password != password.encode()
    assert PasswordManager.verify_password(password, hashed_password)
    assert not PasswordManager.verify_password("password!", hashed_password)
