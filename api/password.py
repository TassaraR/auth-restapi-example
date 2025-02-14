import logging

from passlib.context import CryptContext

# Ignores: module 'bcrypt' has no attribute '__about__'
logging.getLogger("passlib").setLevel(logging.ERROR)


class PasswordManager:
    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies is user password is correct"""
        return self._context.verify(secret=plain_password, hash=hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self._context.hash(password)
