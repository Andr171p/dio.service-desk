from uuid import UUID

from src.iam.domain.authz import Subject
from src.shared.application.repos import get_or_raise_404
from src.workflows.domain.entities import Workflow

from .dtos import WorkflowCreate, WorkflowUpdate
from .repos import WorkflowRepository


async def create_workflow(dto: WorkflowCreate, current_subject: Subject) -> Workflow:  # noqa: RUF029
    return Workflow.create(
        name=dto.name,
        description=dto.description,
        version=dto.version,
        author_id=current_subject.id,
    )


async def update_workflow(
        workflow_id: UUID,
        dto: WorkflowUpdate,
        workflow_repo: WorkflowRepository,
) -> Workflow:

    workflow = await get_or_raise_404(workflow_repo.read, workflow_id, Workflow)
    workflow.edit(name=dto.name, description=dto.description)

    return workflow


async def delete_workflow(workflow_id: UUID, workflow_repo: WorkflowRepository) -> Workflow:

    workflow = await get_or_raise_404(workflow_repo.read, workflow_id, Workflow)
    workflow.archive()

    return workflow
