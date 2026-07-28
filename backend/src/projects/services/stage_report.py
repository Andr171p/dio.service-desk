from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.iam.domain.entities import User
from src.iam.domain.repos import UserRepository

from ..domain.entities import ProjectStage


@dataclass(frozen=True)
class ProjectStageReportRow:
    """
    Строка отчёта по одному этапу проекта.
    """

    number: int
    name: str
    status: str
    planned_start: str
    planned_end: str
    started_at: str
    completed_at: str
    responsible: str
    is_overdue: str
    planned_duration_days: str
    description: str
    completion_criteria: str


@dataclass(frozen=True)
class ProjectStagesReport:
    """
    Данные отчёта по этапам проекта в формате, независимом от типа файла.
    """

    project_id: UUID
    project_name: str
    project_key: str
    project_url: str
    project_status: str
    generated_at: datetime
    rows: list[ProjectStageReportRow]


async def get_responsible_users(
    stages: list[ProjectStage],
    user_repo: UserRepository,
) -> dict[UUID, User]:
    responsible_ids = {
        stage.responsible_id for stage in stages if stage.responsible_id is not None
    }

    users: dict[UUID, User] = {}
    for user_id in responsible_ids:
        user = await user_repo.read(user_id)
        if user is not None:
            users[user_id] = user

    return users


def map_stage_to_report_row(
    number: int,
    stage: ProjectStage,
    responsible_users: dict[UUID, User],
) -> ProjectStageReportRow:
    return ProjectStageReportRow(
        number=number,
        name=stage.name,
        status=stage.status.value,
        planned_start=format_date(stage.planned_start),
        planned_end=format_date(stage.planned_end),
        started_at=format_datetime(stage.started_at),
        completed_at=format_datetime(stage.completed_at),
        responsible=format_responsible(stage.responsible_id, responsible_users),
        is_overdue="Да" if stage.is_overdue else "Нет",
        planned_duration_days=format_int(stage.planned_duration_days),
        description=stage.description or "-",
        completion_criteria=format_list(stage.completion_criteria),
    )


def format_responsible(
    responsible_id: UUID | None,
    responsible_users: dict[UUID, User],
) -> str:
    if responsible_id is None:
        return "-"

    user = responsible_users.get(responsible_id)
    if user is None:
        return str(responsible_id)

    if user.full_name is not None:
        return user.full_name.value

    if user.username is not None:
        return user.username.value

    return user.email.value


def format_date(value: date | None) -> str:
    if value is None:
        return "-"

    return value.strftime("%d.%m.%Y")


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "-"

    return value.strftime("%d.%m.%Y %H:%M")


def format_int(value: int | None) -> str:
    if value is None:
        return "-"

    return str(value)


def format_list(value: list[str]) -> str:
    if not value:
        return "-"

    return "\n".join(value)
