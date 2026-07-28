from uuid import UUID

from src.iam.domain.authz import Subject
from src.iam.domain.exceptions import PermissionDeniedError
from src.iam.domain.repos import UserRepository
from src.shared.domain.repos import get_or_raise_404
from src.shared.utils.time import current_datetime

from ..domain.authz import ProjectAuthZService
from ..domain.entities import Project
from ..domain.repos import ProjectMemberRepository, ProjectRepository
from .stage_report import (
    ProjectStagesReport,
    get_responsible_users,
    map_stage_to_report_row,
)


class ProjectStageExportService:
    """
    Сервис для подготовки отчёта по этапам проекта.
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        member_repo: ProjectMemberRepository,
        user_repo: UserRepository,
        frontend_url: str,
    ) -> None:
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.frontend_url = frontend_url.rstrip("/")
        self.authz_service = ProjectAuthZService(member_repo)

    async def build_report(
        self,
        project_id: UUID,
        current_subject: Subject,
    ) -> ProjectStagesReport:
        """
        Собрать данные отчёта по этапам проекта.
        """

        project = await get_or_raise_404(self.project_repo.read, project_id, Project)

        permission = await self.authz_service.can_export_project(
            subject=current_subject,
            project_id=project_id,
        )
        if not permission.allowed:
            raise PermissionDeniedError(permission.reason)

        stages = sorted(project.stages, key=lambda stage: stage.execution_order)
        responsible_users = await get_responsible_users(stages, self.user_repo)

        return ProjectStagesReport(
            project_id=project.id,
            project_name=project.name,
            project_key=project.key.value,
            project_url=f"{self.frontend_url}/projects/{project.key.value}",
            project_status=project.status.value,
            generated_at=current_datetime(),
            rows=[
                map_stage_to_report_row(
                    number=index,
                    stage=stage,
                    responsible_users=responsible_users,
                )
                for index, stage in enumerate(stages, start=1)
            ],
        )
