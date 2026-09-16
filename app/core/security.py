from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

# ✅ Явно указываем bcrypt
password_hash = PasswordHash((BcryptHasher(),))


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def is_verified_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)
