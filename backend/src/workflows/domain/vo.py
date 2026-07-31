from enum import StrEnum


class RuleKind(StrEnum):
    """Разновидность правила перехода."""

    GUARD = "guard"
    ACTION = "action"


class StatusCategory(StrEnum):
    """
    Категория для статуса Workflow.
    В основном делятся на 3 категории:
     - готово к выполнению;
     - в работе;
     - завершен.
    """

    TODO = "todo"
    ACTIVE = "active"
    DONE = "done"


class StatusKind(StrEnum):
    """Рои статуса внутри Workflow."""

    NORMAL = "normal"
    TERMINAL = "terminal"
