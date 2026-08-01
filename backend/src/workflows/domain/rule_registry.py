"""
Workflow Rule Registry
======================

Этот модуль реализует реестр исполняемых правил Workflow.

Разделение ответственности
--------------------------
В системе существуют два разных понятия "правила":

1. **Rule** (доменная сущность)
   Хранится в базе данных как часть Workflow / Transition.
   Содержит только:
       - type_   (строковый идентификатор)
       - config (JSON-конфигурация)
       - order, kind и т.д.

2. **RuleDefinition** (описание реализации)
   Живёт только в коде приложения.
   Связывает строковый `type_` с:
       - Pydantic-схемой конфигурации
       - функцией-исполнителем (executor)

Зачем это нужно
---------------
Такой подход позволяет:

- Добавлять новые типы правил без изменения доменной модели
  и без миграций базы данных.
- Делать UI полностью динамическим (список доступных правил
  берётся из реестра).
- Держать Workflow Bounded Context независимым от конкретных
  реализаций правил (RequiredField, AssignUser, Webhook и т.д.).

Как пользоваться
----------------
1. Описываете конфигурацию через Pydantic-модель.
2. Регистрируете executor с помощью декоратора ``@rule``.
3. Workflow Engine во время выполнения:
       definition = get_rule(rule.type_)
       config = definition.config_schema.model_validate(rule.config)
       definition.executor(aggregate_type, config)

Регистрация происходит автоматически при импорте модуля,
в котором объявлен ``@rule``.
"""

from typing import get_type_hints

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass

from pydantic import BaseModel

from src.shared.domain.entities import AggregateRoot

from .vo import RuleKind

type RuleExecutor[AggregateT: AggregateRoot, ConfigT: BaseModel] = Callable[
    [AggregateT, ConfigT], Awaitable[None],
]


@dataclass(frozen=True, slots=True)
class RuleDefinition[AggregateT: AggregateRoot, ConfigT: BaseModel]:
    """
    Описание зарегистрированного типа правила.

    RuleDefinition существует только в коде приложения и связывает строковый
    идентификатор правила с его реализацией.

    Workflow хранит в базе данных только:

        type_
        config

    Во время выполнения Workflow Engine находит RuleDefinition через Registry,
    валидирует конфигурацию и вызывает executor.
    """

    type_: str
    kind: RuleKind
    display_name: str
    description: str
    config_schema: type[ConfigT]

    aggregate_type: type[AggregateT]

    executor: RuleExecutor[AggregateT, ConfigT]


# ==============================================
# Регистр объявленных правил модуля
# ==============================================

# Type erasure: конкретные AggregateT и ConfigT известны
# только в момент регистрации. При получении мы работаем
# с наиболее общим допустимым типом.
_rule_registry: dict[str, RuleDefinition[AggregateRoot, BaseModel]] = {}


def register_rule[AggregateT: AggregateRoot, ConfigT: BaseModel](
        definition: RuleDefinition[AggregateT, ConfigT],
) -> None:
    """Зарегистрировать новый тип правила."""

    if definition.type_ in _rule_registry:
        raise ValueError(f"Rule `{definition.type_}` is already registered.")

    _rule_registry[definition.type_] = definition


def get_rule(rule_type: str) -> RuleDefinition[AggregateRoot, BaseModel] | None:
    """Получить описание правила по его типу."""

    return _rule_registry.get(rule_type)


def get_all_rules() -> Mapping[str, RuleDefinition[AggregateRoot, BaseModel]]:
    """Вернуть read-only представление всех зарегистрированных правил."""

    return _rule_registry


def rule[AggregateT: AggregateRoot, ConfigT: BaseModel](
    type_: str,
    *,
    kind: RuleKind,
    display_name: str,
    description: str,
    config_schema: type[ConfigT],
) -> Callable[[RuleExecutor[AggregateT, ConfigT]], RuleExecutor[AggregateT, ConfigT]]:
    """
    Зарегистрировать функцию как Workflow Rule.

    Регистрация выполняется автоматически при импорте модуля.
    """

    def decorator(
            executor: RuleExecutor[AggregateT, ConfigT],
    ) -> RuleExecutor[AggregateT, ConfigT]:

        hints = get_type_hints(executor)
        aggregate_type = hints[0]

        register_rule(
            RuleDefinition(
                type_=type_,
                kind=kind,
                display_name=display_name,
                description=description,
                config_schema=config_schema,
                aggregate_type=aggregate_type,
                executor=executor,
            )
        )

        return executor

    return decorator
