from src.shared.infra.repos import ModelMapper
from src.workflows.domain.entities import Status, Transition, Workflow

from .models import StatusOrm, TransitionOrm, WorkflowOrm


class _StatusMapper(ModelMapper[Status, StatusOrm]):
    @staticmethod
    def to_entity(model: StatusOrm) -> Status:
        return Status(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            name=model.name,
            description=model.description,
            color=model.color,
            category=model.category,
            kind=model.kind,
            order=model.order,
        )

    @staticmethod
    def from_entity(entity: Status) -> StatusOrm:
        return StatusOrm(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            name=entity.name,
            description=entity.description,
            color=entity.color,
            category=entity.category,
            kind=entity.kind,
            order=entity.order,
        )


class _TransitionMapper(ModelMapper[Transition, TransitionOrm]):
    @staticmethod
    def to_entity(model: TransitionOrm) -> Transition:
        return Transition(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            name=model.name,
            sources=set(model.sources),
            destination=model.destination,
            rules=tuple(model.rules)
        )

    @staticmethod
    def from_entity(entity: Transition) -> TransitionOrm:
        return TransitionOrm(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            name=entity.name,
            sources=list(entity.sources),
            destination=entity.destination,
            rules=list(entity.rules),
        )


class WorkflowMapper(ModelMapper[Workflow, WorkflowOrm]):
    @staticmethod
    def to_entity(model: WorkflowOrm) -> Workflow:
        statuses = {status.id: _StatusMapper.to_entity(status) for status in model.statuses}
        transitions = {
            transition.id: _TransitionMapper.to_entity(transition)
            for transition in model.transitions
        }

        return Workflow(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            name=model.name,
            description=model.description,
            is_default=model.is_default,
            is_active=model.is_active,
            version=model.version,
            author_id=model.author_id,
            initial_status_id=model.initial_status_id,
            statuses=statuses,
            transitions=transitions,
        )

    @staticmethod
    def from_entity(workflow: Workflow) -> WorkflowOrm:
        statuses = [_StatusMapper.from_entity(status) for status in workflow.statuses.values()]
        transitions = [
            _TransitionMapper.from_entity(transition)
            for transition in workflow.transitions.values()
        ]

        return WorkflowOrm(
            id=workflow.id,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            deleted_at=workflow.deleted_at,
            name=workflow.name,
            description=workflow.description,
            is_default=workflow.is_default,
            is_active=workflow.is_active,
            version=workflow.version,
            author_id=workflow.author_id,
            initial_status_id=workflow.initial_status_id,
            statuses=statuses,
            transitions=transitions,
        )


__all__ = ["WorkflowMapper"]
