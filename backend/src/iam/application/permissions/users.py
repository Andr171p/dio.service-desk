from src.iam.domain.vo import PermissionScope

from .registry import register_permission

READ = register_permission(
    resource="users",
    action="read",
    scopes=(PermissionScope.GLOBAL, PermissionScope.ORGANIZATION, PermissionScope.OWN),
    title="Просмотр пользователей",
)

UPDATE = register_permission(
    resource="users",
    action="update",
    scopes=(PermissionScope.GLOBAL, PermissionScope.ORGANIZATION, PermissionScope.OWN),
    title="Изменение пользователей",
)

DEACTIVATE = register_permission(
    resource="users",
    action="deactivate",
    scopes=(PermissionScope.GLOBAL, PermissionScope.ORGANIZATION,),
    title="Деактивация пользователя",
)
