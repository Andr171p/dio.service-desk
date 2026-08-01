from typing import Any

import json
from collections.abc import Mapping

from src.shared.infra.repos import ModelMapper
from src.workflows.domain.entities import Rule, Status, Transition, Workflow
from src.workflows.domain.vo import RuleKind

from .models import StatusOrm, TransitionOrm, WorkflowOrm


def _map_rule_to_dict(rule: Rule) -> Mapping[str, Any]:
    return {
        "type_": rule.type_,
        "kind": rule.kind.value,
        "config": rule.config,
        "order": rule.order,
    }


def _build_rule_from_dict(raw: Mapping[str, Any]) -> Rule:
    kind_str = raw.get("kind")
    if kind_str is None:
        raise ValueError(f"Kind required for rule building, raw JSON: {json.dumps(raw)}")

    order = raw.get("order")
    if order is None:
        raise ValueError("Missing rule order")

    return Rule(
        type_=raw.get("type_", ""),
        kind=RuleKind(kind_str),
        config=raw.get("config", {}),
        order=int(order),
    )


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
            rules=[_build_rule_from_dict(rule) for rule in model.rules],
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
            rules=[_map_rule_to_dict(rule) for rule in entity.rules],
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
