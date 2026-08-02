from typing import Annotated, Any, Self

import json
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from functools import cached_property
from uuid import NAMESPACE_OID, UUID, uuid5

from typing_extensions import Doc

from src.shared.domain.entities import AggregateRoot, Entity
from src.shared.domain.exceptions import AlreadyExistsError, InvariantViolationError, NotFoundError
from src.shared.utils.time import current_datetime

from .exceptions import InvalidWorkflowError
from .types import StatusId, TransitionId
from .vo import RuleKind, StatusCategory, StatusKind


def _generate_rule_id(type_: str, kind: RuleKind, config: Mapping[str, Any]) -> UUID:
    payload = {
        "type_": type_,
        "kind": kind.value,
        "config": config,
    }
    name = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return uuid5(NAMESPACE_OID, name)


@dataclass(frozen=True, slots=True)
class Rule:
    """Конфигурация одного правила Workflow."""

    type_: str
    kind: RuleKind
    config: Mapping[str, Any]
    order: int = field(default=0)

    @cached_property
    def id(self) -> UUID:
        """Детерминированный идентификатор правила.
        Вычисляется на основе: type + kind + config -> одинаковый UUID.
        """

        return _generate_rule_id(self.type_, self.kind, self.config)

    def replace(
            self, *, config: Mapping[str, Any] | None = None, order: int | None = None,
    ) -> "Rule":
        if order is not None and order <= 0:
            raise ValueError("Rule execution order must be > 0")

        return Rule(
            type_=self.type_,
            kind=self.kind,
            config=self.config if config is None else config,
            order=self.order if order is None else order,
        )


@dataclass(kw_only=True)
class Status(Entity):
    """
    Возможный статус Workflow.

    Status является вершиной графа Workflow.
    Переходы между статусами описываются сущностями Transition.
    """

    name: str
    description: str | None = None

    color: Annotated[str, Doc("Hex-код цвета для UI")]
    category: StatusCategory
    kind: StatusKind

    order: int

    @classmethod
    def create(
            cls,
            name: str,
            description: str | None,
            color: str,
            category: StatusCategory,
            kind: StatusKind,
            order: int,
    ) -> "Status":
        if not name.strip():
            raise ValueError("Status name cannot be empty")

        if order < 0:
            raise ValueError("Status order must be >= 0")

        return cls(
            name=name,
            description=description,
            color=color,
            category=category,
            kind=kind,
            order=order,
        )

    def edit(
            self,
            *,
            name: str | None = None,
            description: str | None = None,
            color: str | None = None,
            category: StatusCategory | None = None,
            kind: StatusKind | None = None,
    ) -> None:
        changed = False

        values = {
            "name": name,
            "description": description,
            "color": color,
            "category": category,
            "kind": kind,
        }

        for field_ in fields(self):
            value = values.get(field_.name)

            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    raise ValueError(f"Status {field_.name} cannot be empty.")

            if getattr(self, field_.name) != value:
                setattr(self, field_.name, value)
                changed = True

        if changed:
            self.updated_at = current_datetime()


@dataclass(kw_only=True)
class Transition(Entity):
    """
    Направленное ребро графа Workflow.

    Transition определяет допустимый переход между
    одним или несколькими исходными статусами
    и одним целевым статусом.
    """

    name: str

    sources: set[StatusId]
    destination: StatusId

    rules: list[Rule] = field(default_factory=list)

    @property
    def guards(self) -> tuple[Rule, ...]:
        return tuple(rule for rule in self.rules if rule.kind == RuleKind.GUARD)

    @property
    def actions(self) -> tuple[Rule, ...]:
        return tuple(rule for rule in self.rules if rule.kind == RuleKind.ACTION)

    def _sort_rules(self) -> None:
        """Сортирует правила по их порядку выполнения."""

        self.rules.sort(key=lambda r: r.order)

    def rename(self, new_name: str) -> None:
        cleaned = new_name.strip()

        if not cleaned:
            raise ValueError("New transition name cannot be empty")

        if self.name == cleaned:
            return

        self.name = cleaned
        self.updated_at = current_datetime()

    def change(self, new_sources: set[StatusId], new_destination: StatusId | None = None) -> None:
        """Изменяет переход между статусами, меняет путь из вершин графа Workflow."""

        if not new_sources:
            raise ValueError("Transition must have at least one source status.")

        if new_destination in new_sources:
            raise InvalidWorkflowError(
                "Transition cannot have destination equal to one of its sources."
            )

        if new_sources == self.sources and new_destination == self.destination:
            return

        self.sources = new_sources

        if new_destination:
            self.destination = new_destination

        self.updated_at = current_datetime()

    def _find_rule(self, rule_id: UUID) -> Rule | None:
        return next((rule for rule in self.rules if rule.id == rule_id), None)

    def require_rule(self, rule_id: UUID) -> Rule:
        """Требует обязательного наличия правила."""

        rule = self._find_rule(rule_id)

        if rule is None:
            raise NotFoundError(f"Rule - '{rule_id}' does not exist in transition - '{self.id}'.")

        return rule

    def add_rule(self, rule: Rule) -> None:
        if rule in self.rules:
            raise AlreadyExistsError(
                f"Rule '{rule.type_}' already exists in transition '{self.id}'."
            )

        self.rules.append(rule)
        self._sort_rules()

    def remove_rule(self, rule_id: UUID) -> None:

        rule = self._find_rule(rule_id)

        if rule is None:
            raise NotFoundError(f"Rule '{rule_id}' does not exist in transition '{self.id}'.")

        self.rules.remove(rule)

    def replace_rule(self, rule: Rule) -> None:
        index = self.rules.index(rule)
        self.rules[index] = rule
        self._sort_rules()

    def has_rule(self, rule: Rule) -> bool:
        return rule in self.rules


@dataclass(kw_only=True)
class Workflow(AggregateRoot):
    """
    Workflow представляет ориентированный граф жизненного цикла агрегата.

    **Вершины графа** - Status.

    **Ребра графа** - Transition.

    Каждый Transition содержит набор Rule, которые должны успешно выполниться
    для разрешения перехода.
    """

    name: str
    description: str | None = None

    is_default: bool
    is_active: bool
    version: int
    author_id: UUID | None = None

    initial_status_id: StatusId | None = None
    statuses: dict[StatusId, Status] = field(default_factory=dict)
    transitions: dict[TransitionId, Transition] = field(default_factory=dict)

    def _validate(self) -> None:
        """Проверка внутренних инвариантов."""

        if not self.statuses:
            raise InvalidWorkflowError("Workflow must contain at least one status.")

        if self.initial_status_id not in self.statuses:
            raise InvalidWorkflowError(
                f"Initial status '{self.initial_status_id}' does not exist."
            )

        for transition in self.transitions.values():
            if not transition.sources:
                raise InvalidWorkflowError(
                    f"Transition '{transition.id}' must contain at least one source status."
                )

            if transition.destination not in self.statuses:
                raise InvalidWorkflowError(
                    f"Transition '{transition.id}' references unknown destination status."
                )

            for source in transition.sources:
                if source not in self.statuses:
                    raise InvalidWorkflowError(
                        f"Transition '{transition.id}' "
                        f"references unknown source status '{source}'."
                    )

                if source == transition.destination:
                    raise InvalidWorkflowError(
                        f"Transition '{transition.id}' cannot transition into itself."
                    )

    @classmethod
    def create(
            cls,
            name: str,
            version: int,
            description: str | None = None,
            author_id: UUID | None = None,
            is_default: bool = False,
    ) -> Self:

        if not name.strip():
            raise ValueError("Workflow name cannot be empty")

        if version < 0:
            raise ValueError("Workflow version must be > 0")

        return cls(
            name=name.strip(),
            description=description,
            version=version,
            author_id=author_id,
            is_default=is_default,
            is_active=True,
            initial_status_id=None,
        )

    def edit(self, name: str | None = None, description: str | None = None) -> None:

        changed = False

        kwargs = {"name": name, "description": description}
        for field_name, value in kwargs.items():
            if value is not None:
                cleaned = value.strip()
                if not cleaned:
                    raise ValueError(f"Workflow {field_name} cannot be empty")

                if getattr(self, field_name) != cleaned:
                    setattr(self, field_name, cleaned)
                    changed = True

        if changed:
            self.updated_at = current_datetime()

    def archive(self) -> None:

        if self.is_default:
            raise InvariantViolationError("Cannot archive default workflow")

        if self.is_deleted:
            return

        self.is_active = False
        self.deleted_at = current_datetime()

    def add_status(self, status: Status) -> None:

        if status.id in self.statuses:
            raise AlreadyExistsError(
                f"Status - {status.id} already exists in workflow - {self.id}."
            )

        self.statuses[status.id] = status

    def remove_status(self, status_id: StatusId) -> None:

        if status_id not in self.statuses:
            raise NotFoundError(f"Status '{status_id}' does not exist in workflow '{self.id}'.")

        if status_id == self.initial_status_id:
            raise InvalidWorkflowError("")

        if any(
            status_id in transition.sources or transition.destination == status_id
            for transition in self.transitions.values()
        ):
            raise InvalidWorkflowError("")

        del self.statuses[status_id]

    def change_initial_status(self, status_id: StatusId) -> None:
        if status_id not in self.statuses:
            raise NotFoundError(f"Status - {status_id} does not exist in workflow - {self.id}.")

        self.initial_status_id = status_id

    def require_status(self, status_id: StatusId) -> Status:
        """Требует наличие статуса, иначе выбрасывает NotFoundError."""

        status = self.statuses.get(status_id)
        if not status:
            raise NotFoundError(
                f"Status - {status_id} does not exists in workflow - {self.id}."
            )

        return status

    def add_transition(self, transition: Transition) -> None:
        if transition.id in self.transitions:
            raise AlreadyExistsError(
                f"Transition with ID {transition.id} already exist in workflow."
            )

        if transition.destination not in self.statuses:
            raise NotFoundError(
                f"Destination status '{transition.destination}' "
                f"does not exist in workflow '{self.id}'."
            )

        unknown = transition.sources - self.statuses.keys()
        if unknown:
            raise NotFoundError(f"Unknown source statuses: {sorted(map(str, unknown))}.")

        self.transitions[transition.id] = transition

    def remove_transition(self, transition_id: TransitionId) -> None:
        if transition_id not in self.transitions:
            raise NotFoundError(
                f"Transition - {transition_id} does not exists in workflow - {self.id}."
            )

        del self.transitions[transition_id]

    def get_outgoing_transitions(self, status_id: StatusId) -> tuple[Transition, ...]:
        return tuple(
            transition
            for transition in self.transitions.values()
            if status_id in transition.sources
        )

    def find_transition(self, source: StatusId, destination: StatusId) -> Transition | None:
        for transition in self.get_outgoing_transitions(source):
            if transition.destination == destination:
                return transition

        return None

    def can_transition(self, source: StatusId, destination: StatusId) -> bool:
        """Можно ли выполнить переход из одного статуса в другой."""

        return self.find_transition(source, destination) is not None

    def require_transition(self, transition_id: TransitionId) -> Transition:
        """Требует наличие перехода, иначе выбрасывает NotFoundError."""

        transition = self.transitions.get(transition_id)
        if not transition:
            raise NotFoundError(
                f"Transition - {transition_id} does not exists in workflow - {self.id}."
            )

        return transition
