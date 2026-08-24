from fastapi import APIRouter

from . import auth, invitations, permissions, roles, users

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(invitations.router)
router.include_router(permissions.router)
router.include_router(roles.router)
router.include_router(users.router)
