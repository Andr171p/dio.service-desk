from typing import Any

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import jwt
from passlib.context import CryptContext

from src.core.settings import settings
from src.iam.domain.exceptions import UnauthorizedError
from src.iam.domain.vo import Email
from src.shared.utils.time import current_datetime

MEMORY_COST = 100
TIME_COST = 2
PARALLELISM = 2
SALT_SIZE = 16
ROUNDS = 14

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    argon2__memory_cost=MEMORY_COST,
    argon2__time_cost=TIME_COST,
    argon2__parallelism=PARALLELISM,
    argon2__salt_size=SALT_SIZE,
    bcrypt__rounds=ROUNDS,
    deprecated="auto"
)

MAX_WORKERS = max(1, (os.cpu_count() or 2) // 2)

# В `lifespan` вызвать `crypto_executor.shutdown(wait=True)`
crypto_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="crypto_worker")


async def hash_password_async(password: str) -> str:
    """Асинхронное хэширует пароль в отдельном потоке."""

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(crypto_executor, hash_password, password)


async def verify_password_async(plain_password: str, password_hash: str) -> bool:
    """Асинхронно сверяет хеш пароля в отдельном потоке."""

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        crypto_executor, verify_password, plain_password, password_hash
    )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_authentication_token(user_id: UUID) -> str:
    """Выпускает очень короткоживущий токен для аутентификации."""

    now = current_datetime()
    expires_at = now + timedelta(minutes=settings.jwt.authentication_token_expires_in_minutes)

    payload = {
        "sub": str(user_id),
        "typ": "authentication",
        "jti": str(uuid4()),
        "exp": expires_at.timestamp(),
        "iat": now.timestamp(),
    }

    return jwt.encode(payload=payload, key=settings.secret_key, algorithm=settings.jwt.algorithm)


def create_access_token(
        user_id: UUID,
        email: Email,
        membership_id: UUID,
        organization_id: UUID,
        roles: set[str],
        permissions: set[str],
) -> str:

    now = current_datetime()
    expires_at = now + timedelta(minutes=settings.jwt.access_token_expires_in_minutes)

    payload = {
        # Базовые поля
        "sub": str(user_id),
        "exp": expires_at.timestamp(),
        "iat": now.timestamp(),
        "typ": "access",
        "jti": str(uuid4()),

        # Кастомные поля
        "mid": str(membership_id),
        "org_id": str(organization_id),
        "email": str(email),
        "roles": list(roles),
        "perms": list(permissions),
    }

    return jwt.encode(payload=payload, key=settings.secret_key, algorithm=settings.jwt.algorithm)


def create_refresh_token(user_id: UUID, membership_id: UUID) -> str:
    """Выпускает долгоживущий токен для получения новой пары access + refresh."""

    now = current_datetime()
    expires_at = now + timedelta(days=settings.jwt.refresh_token_expires_in_days)

    payload = {
        # Базовые поля
        "sub": str(user_id),
        "exp": expires_at.timestamp(),
        "iat": now.timestamp(),
        "typ": "refresh",
        "jti": str(uuid4()),

        # Кастомные поля
        "mid": str(membership_id),
    }

    return jwt.encode(payload=payload, key=settings.secret_key, algorithm=settings.jwt.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Декодирует JWT и проверяет его подпись и срок действия."""

    try:
        return jwt.decode(
            token,
            key=settings.secret_key,
            algorithms=[settings.jwt.algorithm],
            options={"verify_aud": False}
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token signature expired!") from None
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid token!") from None
