from src.iam.application.dtos import Identity
from src.iam.domain.entities import Permission
from src.iam.domain.exceptions import PermissionDeniedError

from .registry import get_permission_policies


def has_permission(identity: Identity, permission: Permission) -> bool:
    """Проверяет наличие конкретного права у субъекта авторизации."""

    return any(grant.permission == permission.code for grant in identity.grants)


def can(identity: Identity, permission: Permission, resource: object | None = None) -> bool:
    """
    Проверяет доступ субъекта авторизации к ресурсу.

    Если ресурс не передан, проверяется только наличие права.
    При наличии ресурса дополнительно применяются зарегистрированные
    политики авторизации.
    """

    if not has_permission(identity, permission):
        return False

    if resource is None:
        return True

    if not (policies := get_permission_policies(permission)):
        return False

    granted_scopes = {
        grant.scope
        for grant in identity.grants
        if grant.permission == permission.code
    }

    return any(
        scope in granted_scopes and policy(identity, resource)
        for scope, policy in policies
    )


def authorize(identity: Identity, permission: Permission, resource: object | None = None) -> None:
    """Проверяет доступ и выбрасывает исключение при отказе."""

    if can(identity, permission, resource):
        return

    if not has_permission(identity, permission):
        raise PermissionDeniedError(f"Missing required permission: {permission.code}.")

    raise PermissionDeniedError(f"Access denied for permission '{permission.code}'.")
