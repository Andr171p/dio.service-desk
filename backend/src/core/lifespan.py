import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logging import configure_logging

_BOOTSTRAP_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("alembic", "upgrade", "head"),
    ("cli", "create-super-admin"),
    ("cli", "create-s3-buckets"),
)


async def _run_bootstrap_commands() -> None:
    """"""

    from src.shared.utils.cli import run_cli_command

    for cmd in _BOOTSTRAP_COMMANDS:
        full_cmd = (sys.executable, "-m", *cmd)
        await run_cli_command(*full_cmd)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging(log_level="INFO")

    await _run_bootstrap_commands()

    yield


__all__ = ["lifespan"]
