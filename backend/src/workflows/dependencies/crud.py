from typing import Annotated

from uuid import UUID

from fastapi import Depends

from src.iam.domain.authz import Subject
from src.shared.application.crud import Crud
from src.workflows.application.crud import create_workflow, delete_workflow, update_workflow
from src.workflows.application.dtos import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from src.workflows.application.repos import WorkflowRepository
from src.workflows.application.response_mappers import map_workflow_to_response
from src.workflows.domain.entities import Workflow

from .base import WorkflowRepoDep, WorkflowTransactionDep

type WorkflowCrud = Crud[
    Workflow,
    WorkflowResponse,
    [WorkflowCreate, Subject],
    [UUID, WorkflowUpdate, WorkflowRepository],
    [UUID, WorkflowRepository],
]


def get_workflow_crud(
        workflow_repo: WorkflowRepoDep, transaction: WorkflowTransactionDep,
) -> WorkflowCrud:
    return Crud[
        Workflow,
        WorkflowResponse,
        [WorkflowCreate, Subject],
        [UUID, WorkflowUpdate, WorkflowRepository],
        [UUID, WorkflowRepository],
    ](
        workflow_repo,
        transaction,
        map_workflow_to_response,
        create_handler=create_workflow,
        update_handler=update_workflow,
        delete_handler=delete_workflow,
    )


WorkflowCrudDep = Annotated[WorkflowCrud, Depends(get_workflow_crud)]
