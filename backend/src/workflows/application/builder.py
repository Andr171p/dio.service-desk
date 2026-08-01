from uuid import UUID

from src.shared.application.repos import get_or_raise_404
from src.shared.application.transaction import Transaction
from src.workflows.domain.entities import Rule, Status, Transition, Workflow
from src.workflows.domain.types import StatusId, TransitionId

from .dtos import (
    RuleCreate,
    RuleUpdate,
    StatusCreate,
    StatusUpdate,
    TransitionCreate,
    TransitionUpdate,
    WorkflowResponse,
)
from .repos import WorkflowRepository
from .response_mappers import map_workflow_to_response


class WorkflowBuilder:
    def __init__(
            self, workflow_repo: WorkflowRepository, transaction: Transaction[Workflow],
    ) -> None:
        self._workflow_repo = workflow_repo
        self._transaction = transaction

    async def _load(self, workflow_id: UUID) -> Workflow:
        """Загружает рабочий процесс, если не найден - NotFoundError."""

        return await get_or_raise_404(self._workflow_repo.read, workflow_id, Workflow)

    async def _persist(self, workflow: Workflow) -> WorkflowResponse:
        """Сохраняет все применённые изменения и возвращает ResponseDTO."""

        await self._workflow_repo.update(workflow)
        await self._transaction(workflow)

        return map_workflow_to_response(workflow)

    async def add_status(self, workflow_id: UUID, dto: StatusCreate) -> WorkflowResponse:
        """Добавить новый статус."""

        workflow = await self._load(workflow_id)

        status = Status.create(
            name=dto.name,
            description=dto.description,
            color=dto.color,
            category=dto.category,
            kind=dto.kind,
            order=dto.order,
        )
        workflow.add_status(status)

        return await self._persist(workflow)

    async def update_status(
        self,
        workflow_id: UUID,
        status_id: UUID,
        dto: StatusUpdate,
    ) -> WorkflowResponse:
        """Редактирует статус внутри рабочего процесса."""

        workflow = await self._load(workflow_id)

        status = workflow.require_status(StatusId(status_id))
        status.edit(
            name=dto.name,
            description=dto.description,
            color=dto.color,
            category=dto.category,
            kind=dto.kind,
        )

        return await self._persist(workflow)

    async def remove_status(self, workflow_id: UUID, status_id: UUID) -> WorkflowResponse:
        """Удалить статус из рабочего процесса (удаляет фактически)."""

        workflow = await self._load(workflow_id)

        workflow.remove_status(StatusId(status_id))

        return await self._persist(workflow)

    async def change_initial_status(self, workflow_id: UUID, status_id: UUID) -> WorkflowResponse:
        """Изменить исходный статус рабочего процесса."""

        workflow = await self._load(workflow_id)

        workflow.change_initial_status(StatusId(status_id))

        return await self._persist(workflow)

    async def add_transition(self, workflow_id: UUID, dto: TransitionCreate) -> WorkflowResponse:
        """Добавить переход между статусами."""

        workflow = await self._load(workflow_id)

        transition = Transition(
            name=dto.name,
            sources=dto.sources,
            destination=dto.destination,
            rules=[
                Rule(
                    type_=rule.type,
                    kind=rule.kind,
                    config=rule.config,
                    order=rule.order,
                )
                for rule in dto.rules
            ],
        )
        workflow.add_transition(transition)

        return await self._persist(workflow)

    async def update_transition(
        self,
        workflow_id: UUID,
        transition_id: UUID,
        dto: TransitionUpdate,
    ) -> WorkflowResponse:
        """Обновление перехода между статусами Workflow."""

        workflow = await self._load(workflow_id)

        transition = workflow.require_transition(TransitionId(transition_id))

        if dto.name:
            transition.rename(dto.name)

        transition.change(new_sources=dto.sources, new_destination=dto.destination)

        return await self._persist(workflow)

    async def remove_transition(self, workflow_id: UUID, transition_id: UUID) -> WorkflowResponse:
        """Удалить переход между статусами."""

        workflow = await self._load(workflow_id)

        workflow.remove_transition(TransitionId(transition_id))

        return await self._persist(workflow)

    async def add_rule(
        self,
        workflow_id: UUID,
        transition_id: UUID,
        dto: RuleCreate,
    ) -> WorkflowResponse:
        """Добавить новое правило для перехода."""

        workflow = await self._load(workflow_id)

        transition = workflow.require_transition(TransitionId(transition_id))
        transition.add_rule(
            Rule(
                type_=dto.type,
                kind=dto.kind,
                config=dto.config,
                order=dto.order,
            ),
        )

        return await self._persist(workflow)

    async def update_rule(
        self,
        workflow_id: UUID,
        transition_id: UUID,
        rule_id: UUID,
        dto: RuleUpdate,
    ) -> WorkflowResponse:
        """Обновить правило внутри перехода."""

        workflow = await self._load(workflow_id)

        transition = workflow.require_transition(TransitionId(transition_id))
        rule = transition.require_rule(rule_id)
        transition.replace_rule(
            rule.replace(config=dto.config, order=dto.order),
        )

        return await self._persist(workflow)

    async def remove_rule(
        self,
        workflow_id: UUID,
        transition_id: UUID,
        rule_id: UUID,
    ) -> WorkflowResponse:
        """Удалить правило из перехода."""

        workflow = await self._load(workflow_id)

        transition = workflow.require_transition(TransitionId(transition_id))
        transition.remove_rule(rule_id)

        return await self._persist(workflow)
