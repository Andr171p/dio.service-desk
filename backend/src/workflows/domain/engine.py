"""
Workflow Engine
===============

Модуль отвечает за выполнение переходов Workflow.

Основная ответственность
------------------------
Workflow Engine оркестрирует выполнение одного перехода агрегата:

1. Находит Transition по текущему и целевому статусу.
2. Выполняет все guards (условия и валидаторы) в порядке ``order``.
3. Изменяет статус агрегата через переданную функцию ``change_status``.
4. Выполняет все actions в порядке ``order``.

Разделение ответственности
--------------------------
- **Workflow / Transition / Rule** — доменные сущности.
  Хранят только декларативное описание (type + config).
- **Rule Registry** — связывает строковый ``type`` правила
  с конкретной реализацией (executor + config schema).
- **Workflow Engine** (этот модуль) — знает *когда* и *в каком порядке*
  выполнять правила, но не знает *как* они реализованы.

Такое разделение позволяет добавлять новые типы правил
без изменения движка и доменной модели.

Порядок выполнения правил
-------------------------
Правила внутри Transition выполняются строго по полю ``order``.
Сначала все guards, затем смена статуса, затем все actions.

Ошибки
------
- Если Transition не найден — ``NotFoundError``.
- Если rule.type не зарегистрирован или kind не совпадает —
  ``WorkflowConfigurationError``.
- Ошибки внутри executor'а правила пробрасываются как есть
  (обычно доменные исключения).
"""

from collections.abc import Callable

from src.shared.domain.entities import AggregateRoot
from src.shared.domain.exceptions import NotFoundError

from .entities import Rule, Workflow
from .exceptions import WorkflowConfigurationError
from .rule_registry import get_rule
from .types import StatusId
from .vo import RuleKind

type StatusChanger[AggregateT: AggregateRoot] = Callable[[AggregateT, StatusId], None]


def _sorted_rules(rules: tuple[Rule, ...]) -> list[Rule]:
    """Сортирует правила по их порядку выполнения."""

    return sorted(rules, key=lambda rule: rule.order)


async def _execute_rule[AggregateT: AggregateRoot](
    aggregate: AggregateT, rule: Rule, *, expected_kind: RuleKind,
) -> None:
    """
    Выполняет одно правило Workflow.
    Находит зарегистрированный executor, валидирует конфигурацию и вызывает обработчик.
    """

    definition = get_rule(rule.type_)

    if definition.kind != expected_kind:
        raise WorkflowConfigurationError(
            f"Rule '{rule.type_}' "
            f"is registered as '{definition.kind}', "
            f"expected '{expected_kind}'."
        )

    config = definition.config_schema.model_validate(rule.config)

    await definition.executor(aggregate, config)


async def execute_transition[AggregateT: AggregateRoot](
    aggregate: AggregateT,
    workflow: Workflow,
    current_status: StatusId,
    destination_status: StatusId,
    change_status: StatusChanger[AggregateT],
) -> None:
    """
    Выполняет переход Workflow.

    Порядок выполнения:
     1. Поиск Transition
     2. Выполнение guards
     3. Изменение статуса агрегата
     4. Выполнение actions
    """

    transition = workflow.find_transition(current_status, destination_status)

    if transition is None:
        raise NotFoundError(
            f"Transition {current_status} -> {destination_status} does not exist "
            f"in workflow - {workflow.id}."
        )

    for guard in _sorted_rules(transition.guards):
        await _execute_rule(aggregate, guard, expected_kind=RuleKind.GUARD)

    change_status(aggregate, destination_status)

    for action in _sorted_rules(transition.actions):
        await _execute_rule(aggregate, action, expected_kind=RuleKind.ACTION)


__all__ = ["execute_transition"]
