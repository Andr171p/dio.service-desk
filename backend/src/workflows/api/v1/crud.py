from uuid import UUID

from fastapi import APIRouter, status

from src.iam.dependencies import CurrentSubjectDep
from src.shared.application.dtos import Page
from src.shared.dependencies import PaginationDep
from src.workflows.application.dtos import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from src.workflows.dependencies import WorkflowCrudDep, WorkflowRepoDep

router = APIRouter(tags=["CRUD"])


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=WorkflowResponse,
    summary="Создать рабочий процесс",
)
async def create_workflow(
        dto: WorkflowCreate, current_subject: CurrentSubjectDep, crud: WorkflowCrudDep,
) -> WorkflowResponse:
    return await crud.create(dto, current_subject)


@router.patch(
    path="/{workflow_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Обновить рабочий процесс",
)
async def update_workflow(
        workflow_id: UUID,
        dto: WorkflowUpdate,
        workflow_repo: WorkflowRepoDep,
        crud: WorkflowCrudDep,
) -> WorkflowResponse:
    return await crud.update(workflow_id, dto, workflow_repo)


@router.delete(
    path="/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить рабочий процесс",
)
async def delete_workflow(
        workflow_id: UUID, workflow_repo: WorkflowRepoDep, crud: WorkflowCrudDep,
) -> None:
    return await crud.delete(workflow_id, workflow_repo)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=Page[WorkflowResponse],
    summary="Получить список рабочих процессов",
)
async def get_workflows(
        pagination: PaginationDep, crud: WorkflowCrudDep,
) -> Page[WorkflowResponse]:
    return await crud.paginate(pagination)


@router.get(
    path="/{workflow_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Получить рабочий процесс",
)
async def get_workflow(workflow_id: UUID, crud: WorkflowCrudDep) -> WorkflowResponse:
    return await crud.read(workflow_id)
