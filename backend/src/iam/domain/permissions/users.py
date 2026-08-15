from src.iam.domain.entities import Permission
from src.iam.domain.vo import PermissionScope

from .registry import register_permission

READ = register_permission(
    Permission(
        resource="users",
        action="read",
        scopes=frozenset({PermissionScope.ORGANIZATION}),
        description="Просмотр пользователей организации",
    ),
)

UPDATE = register_permission(
    Permission(
        resource="users",
        action="update",
        scope=PermissionScope.ORGANIZATION,
        description="Изменение пользователей организации",
    ),
)

DEACTIVATE = register_permission(
    Permission(
        resource="users",
        action="deactivate",
        scope=PermissionScope.ORGANIZATION,
        description="Деактивация пользователей организации",
    ),
)