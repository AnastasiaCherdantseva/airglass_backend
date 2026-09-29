"""
Фикстуры сессий.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    SESSION_TTL,
    generate_session_token,
    hash_session_token,
)
from app.models.system import Session, User


def _build_session(user_id: UUID) -> tuple[Session, str, str]:
    """Helper: session + open token + hash."""
    token = generate_session_token()
    token_hash = hash_session_token(token)
    now = datetime.now(UTC)
    session = Session(
        id=uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=now + SESSION_TTL,
        last_used_at=now,
        created_at=now,
        user_agent="Test Agent",
        ip_address="127.0.0.1",
    )
    return session, token, token_hash


@pytest_asyncio.fixture
async def session(
    db_session: AsyncSession,
    user: User,
) -> dict[str, Session | str]:
    """Ready-to-use session for active user in the database."""
    token = generate_session_token()
    token_hash = hash_session_token(token)
    now = datetime.now(UTC)

    session = Session(
        id=uuid4(),
        user_id=user.id,
        token_hash=token_hash,
        expires_at=now + SESSION_TTL,
        last_used_at=now,
    )
    db_session.add(session)
    await db_session.flush()
    return {"data": session, "token": token, "token_hash": token_hash}


@pytest_asyncio.fixture
async def sessions(
    db_session: AsyncSession,
    user: User,
) -> dict[str, list[Session | str]]:
    """Ready-to-use sessions (3) for active user in the database."""
    tokens = []
    tokens_hashes = []
    data = []
    for _ in range(3):
        now = datetime.now(UTC)
        token = generate_session_token()
        token_hash = hash_session_token(token)
        session = Session(
            id=uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + SESSION_TTL,
            last_used_at=now,
        )
        data.append(session)
        tokens.append(token)
        tokens_hashes.append(token_hash)
        db_session.add(session)
    await db_session.flush()
    return {"data": data, "tokens": tokens, "tokens_hashes": tokens_hashes}


@pytest_asyncio.fixture
async def session_in_memory(user_in_memory: User) -> dict:
    session, token, token_hash = _build_session(user_in_memory.id)
    return {"data": session, "token": token, "token_hash": token_hash}


@pytest_asyncio.fixture
async def inactive_user_session_in_memory(
    inactive_user_in_memory: User,
) -> dict:
    session, token, token_hash = _build_session(inactive_user_in_memory.id)
    return {"data": session, "token": token, "token_hash": token_hash}


@pytest_asyncio.fixture
async def sessions_for_two_users(
    db_session: AsyncSession,
    users: list[User],
) -> dict:
    """По 3 сессии для первых двух юзеров."""
    result = {}
    for user in users[:2]:
        tokens = []
        tokens_hashes = []
        data = []
        ids = []
        for _ in range(3):
            now = datetime.now(UTC)
            token = generate_session_token()
            token_hash = hash_session_token(token)
            session = Session(
                id=uuid4(),
                user_id=user.id,
                token_hash=token_hash,
                expires_at=now + SESSION_TTL,
                last_used_at=now,
            )
            data.append(session)
            tokens.append(token)
            tokens_hashes.append(token_hash)
            ids.append(session.id)
            db_session.add(session)
        await db_session.flush()
        result[user.id] = {
            "data": data,
            "tokens": tokens,
            "tokens_hashes": tokens_hashes,
            "ids": ids,
        }
    return result
