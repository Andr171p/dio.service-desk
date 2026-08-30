from src.iam.domain.vo import PermissionScope

from .registry import register_permission

READ = register_permission(
    resource="roles",
    action="read",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Просмотр ролей",
)

CREATE = register_permission(
    resource="roles",
    action="create",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Создание ролей",
)

UPDATE = register_permission(
    resource="roles",
    action="update",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Изменение ролей",
)

DELETE = register_permission(
    resource="roles",
    action="delete",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Удаление ролей",
)
