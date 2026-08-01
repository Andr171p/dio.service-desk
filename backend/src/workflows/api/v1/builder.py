from uuid import UUID

from fastapi import APIRouter, status

from src.workflows.application.dtos import (
    RuleCreate,
    RuleUpdate,
    StatusCreate,
    StatusUpdate,
    TransitionCreate,
    TransitionUpdate,
    WorkflowResponse,
)
from src.workflows.dependencies import WorkflowBuilderDep

router = APIRouter(tags=["Настройка Workflow"])


# ========================================================================================
# Статусы - /statuses
# ========================================================================================


@router.post(
    path="/{workflow_id}/statuses",
    status_code=status.HTTP_201_CREATED,
    response_model=WorkflowResponse,
    summary="Добавить статус в Workflow",
)
async def create_status(
        workflow_id: UUID, dto: StatusCreate, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.add_status(workflow_id=workflow_id, dto=dto)


@router.patch(
    path="/{workflow_id}/statuses/{status_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Обновить статус",
)
async def update_status(
        workflow_id: UUID, status_id: UUID, dto: StatusUpdate, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.update_status(workflow_id=workflow_id, status_id=status_id, dto=dto)


@router.delete(
    path="/{workflow_id}/statuses/{status_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Удалить статус из Workflow",
)
async def delete_status(
        workflow_id: UUID, status_id: UUID, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.remove_status(workflow_id=workflow_id, status_id=status_id)


# ========================================================================================
# Переходы - /transitions
# ========================================================================================


@router.post(
    path="/{workflow_id}/transitions",
    status_code=status.HTTP_201_CREATED,
    response_model=WorkflowResponse,
    summary="Добавить переход в Workflow",
)
async def create_transition(
        workflow_id: UUID, dto: TransitionCreate, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.add_transition(workflow_id=workflow_id, dto=dto)


@router.patch(
    path="/{workflow_id}/transitions/{transition_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Обновить переход",
)
async def update_transition(
        workflow_id: UUID, transition_id: UUID, dto: TransitionUpdate, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.update_transition(
        workflow_id=workflow_id, transition_id=transition_id, dto=dto,
    )


@router.delete(
    path="/{workflow_id}/transitions/{transition_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Удалить переход из Workflow",
)
async def delete_transition(
        workflow_id: UUID, transition_id: UUID, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.remove_transition(workflow_id=workflow_id, transition_id=transition_id)


# ========================================================================================
# Правила переходов - /transitions/rules
# ========================================================================================


@router.post(
    path="/{workflow_id}/transitions/{transition_id}/rules",
    status_code=status.HTTP_201_CREATED,
    response_model=WorkflowResponse,
    summary="Добавить правило для перехода",
)
async def create_rule(
        workflow_id: UUID, transition_id: UUID, dto: RuleCreate, builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.add_rule(workflow_id=workflow_id, transition_id=transition_id, dto=dto)


@router.patch(
    path="/{workflow_id}/transitions/{transition_id}/rules/{rule_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Обновить конфигурацию правила",
)
async def update_rule(
        workflow_id: UUID,
        transition_id: UUID,
        rule_id: UUID,
        dto: RuleUpdate,
        builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.update_rule(
        workflow_id=workflow_id,
        transition_id=transition_id,
        rule_id=rule_id,
        dto=dto,
    )


@router.delete(
    path="/{workflow_id}/transitions/{transition_id}/rules/{rule_id}",
    status_code=status.HTTP_200_OK,
    response_model=WorkflowResponse,
    summary="Удалить правило из перехода",
)
async def delete_rule(
        workflow_id: UUID,
        transition_id: UUID,
        rule_id: UUID,
        builder: WorkflowBuilderDep,
) -> WorkflowResponse:
    return await builder.remove_rule(
        workflow_id=workflow_id, transition_id=transition_id, rule_id=rule_id,
    )
