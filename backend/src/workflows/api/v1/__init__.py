from fastapi import APIRouter

from . import builder, crud, rules

router = APIRouter(prefix="/workflows", tags=["Workflow | Рабочие процессы"])

router.include_router(crud.router)
router.include_router(builder.router)
router.include_router(rules.router)

__all__ = ["router"]
