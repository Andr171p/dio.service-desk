"""
Регистрация FastAPI роутеров из всех модулей.
"""

from fastapi import APIRouter

from src.iam.api.v1 import router as iam_router

router = APIRouter()

router.include_router(iam_router)

__all__ = ["router"]
