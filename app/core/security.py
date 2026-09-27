"""
Password hashing and session token utilities.
"""

import hashlib
import secrets
from datetime import timedelta

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

# ✅ Явно указываем bcrypt
password_hash = PasswordHash((BcryptHasher(),))
SESSION_TOKEN_BYTES = 32  # 256 bits of entropy
SESSION_TTL = timedelta(days=7)
SESSION_COOKIE_NAME = "session_id"
SESSION_MAX_AGE = 7 * 24 * 3600


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def is_verified_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def generate_session_token() -> str:
    """
    Generate a cryptographically secure session token.

    Returns a URL-safe string with ~256 bits of entropy.
    """
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """
    Hash a session token with SHA-256 for storage.

    SHA-256 (not bcrypt) is used because session tokens are
    high-entropy random strings, not passwords. Bcrypt would
    slow down every request without adding security.
    """
    return hashlib.sha256(token.encode()).hexdigest()
