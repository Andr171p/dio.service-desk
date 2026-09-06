import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logging import configure_logging
from .rabbit import router as rabbit_router
from .redis import redis_client

_BOOTSTRAP_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("alembic", "upgrade", "head"),
    ("cli", "create-super-admin"),
    ("cli", "create-s3-buckets"),
)


async def _run_bootstrap_commands() -> None:
    """Запускает команды необходимые для старта приложения."""

    from src.shared.utils.cli import run_cli_command

    for cmd in _BOOTSTRAP_COMMANDS:
        full_cmd = (sys.executable, "-m", *cmd)
        await run_cli_command(*full_cmd)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(log_level="INFO")

    await redis_client.ping()

    await _run_bootstrap_commands()

    async with rabbit_router.lifespan_context(app):
        yield


__all__ = ["lifespan"]
