import logging

from passlib.context import CryptContext

# Ignores: module 'bcrypt' has no attribute '__about__'
logging.getLogger("passlib").setLevel(logging.ERROR)


class PasswordManager:
    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verifies is user password is correct"""
        return cls._context.verify(secret=plain_password, hash=hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls._context.hash(password)
