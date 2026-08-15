from src.iam.application.dtos import PermissionResponse
from src.iam.domain.entities import Permission
from src.iam.domain.vo import PermissionScope

perm = Permission(
    resource="task",
    action="create",
    title="Создать задачу",
    description="Что то там ...",
    scopes=frozenset({PermissionScope.ORGANIZATION, PermissionScope.PROJECT}),
)

print(perm)

print(PermissionResponse.model_validate(perm))
