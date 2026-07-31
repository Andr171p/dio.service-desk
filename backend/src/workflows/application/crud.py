from src.iam.domain.authz import Subject
from src.shared.application.crud import Crud
from src.workflows.domain.entities import Workflow

from .dtos import WorkflowCreate


async def create_workflow(dto: WorkflowCreate, current_subject: Subject) -> Workflow:  # noqa: RUF029
    return Workflow.create(
        name=dto.name,
        description=dto.description,
        version=dto.version,
        author_id=current_subject.id,
    )


async def update_handler(dto: ...) -> Workflow:
    ...
