from src.iam.domain.vo import PermissionScope

from .registry import register_permission

READ = register_permission(
    resource="service_accounts",
    action="read",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Просмотр сервисных аккаунтов",
)

CREATE = register_permission(
    resource="service_accounts",
    action="create",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Создание сервисных аккаунтов",
)

UPDATE = register_permission(
    resource="service_accounts",
    action="update",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Изменение сервисных аккаунтов",
)

DELETE = register_permission(
    resource="service_accounts",
    action="revoke",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Деактивация сервисного аккаунта",
)

ROTATE_SECRET = register_permission(
    resource="service_accounts",
    action="rotate_secret",
    scopes=(PermissionScope.ORGANIZATION,),
    title="Ротация секрета сервисного аккаунта",
)
