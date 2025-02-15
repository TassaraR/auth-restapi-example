import bcrypt


class PasswordManager:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: bytes) -> bool:
        """Verifies is user password is correct"""
        return bcrypt.checkpw(plain_password.encode(), hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> bytes:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password
