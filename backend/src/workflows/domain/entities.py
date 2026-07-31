from typing import Annotated, Any, Self

from collections.abc import Mapping
from dataclasses import dataclass, field
from uuid import UUID

from typing_extensions import Doc

from src.shared.domain.entities import AggregateRoot, Entity
from src.shared.domain.exceptions import AlreadyExistsError, NotFoundError

from .exceptions import InvalidWorkflowError
from .types import StatusId, TransitionId
from .vo import RuleKind, StatusCategory, StatusKind


@dataclass(frozen=True, slots=True)
class Rule:
    """Конфигурация одного правила Workflow."""

    type_: str
    kind: RuleKind
    config: Mapping[str, Any]
    order: int = field(default=0)


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

    rules: tuple[Rule, ...] = ()

    @property
    def guards(self) -> tuple[Rule, ...]:
        return tuple(rule for rule in self.rules if rule.kind == RuleKind.GUARD)

    @property
    def actions(self) -> tuple[Rule, ...]:
        return tuple(rule for rule in self.rules if rule.kind == RuleKind.ACTION)


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
