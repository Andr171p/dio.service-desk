from typing import Annotated

from enum import StrEnum
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from src.iam.dependencies import CurrentSubjectDep

from ..dependencies import ProjectServiceDep, ProjectStageExportServiceDep
from ..exporters import (
    export_project_stages_to_excel,
    export_project_stages_to_pdf,
    export_project_stages_to_word,
)
from ..schemas import (
    NewProjectStagesOrder,
    ProjectResponse,
    ProjectStageCreate,
    ProjectStagePlan,
    ProjectStageResponse,
    ProjectStageUpdate,
)

router = APIRouter(prefix="/projects", tags=["Этапы проекта"])


class ProjectStageExportFormat(StrEnum):
    EXCEL = "excel"
    PDF = "pdf"
    WORD = "word"


def create_export_response(
    content: bytes,
    filename: str,
    media_type: str,
) -> StreamingResponse:
    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post(
    path="/{project_id}/stages",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectResponse,
    summary="Создать этап проекта",
)
async def create_project_stage(
    project_id: UUID,
    data: ProjectStageCreate,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectResponse:
    return await service.add_stage(project_id, data, current_subject)


@router.get(
    path="/{project_id}/stages/export",
    status_code=status.HTTP_200_OK,
    summary="Экспортировать этапы проекта",
)
async def export_project_stages(
    project_id: UUID,
    export_format: Annotated[ProjectStageExportFormat, Query(alias="format")],
    current_subject: CurrentSubjectDep,
    service: ProjectStageExportServiceDep,
) -> StreamingResponse:
    report = await service.build_report(
        project_id=project_id,
        current_subject=current_subject,
    )

    export_settings = {
        ProjectStageExportFormat.EXCEL: (
            export_project_stages_to_excel,
            "xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        ProjectStageExportFormat.PDF: (
            export_project_stages_to_pdf,
            "pdf",
            "application/pdf",
        ),
        ProjectStageExportFormat.WORD: (
            export_project_stages_to_word,
            "docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    }
    exporter, extension, media_type = export_settings[export_format]

    return create_export_response(
        content=exporter(report),
        filename=f"project-stages-{report.project_key}.{extension}",
        media_type=media_type,
    )


@router.patch(
    path="/{project_id}/stages/{stage_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectStageResponse,
    summary="Обновить этап проекта",
)
async def update_project_stage(
    project_id: UUID,
    stage_id: UUID,
    current_subject: CurrentSubjectDep,
    data: ProjectStageUpdate,
    service: ProjectServiceDep,
) -> ProjectStageResponse:
    return await service.edit_stage(
        project_id=project_id,
        stage_id=stage_id,
        data=data,
        current_subject=current_subject,
    )


@router.patch(
    path="/{project_id}/stages/order",
    status_code=status.HTTP_200_OK,
    response_model=ProjectResponse,
    summary="Изменить порядок проведения этапов",
)
async def reorder_project_stages(
    project_id: UUID,
    new_order: NewProjectStagesOrder,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectResponse:
    return await service.reorder_stages(
        project_id=project_id,
        new_order=new_order,
        current_subject=current_subject,
    )


@router.delete(
    path="/{project_id}/stages/{stage_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectResponse,
    summary="Удалить этап из проекта",
)
async def delete_project_stage(
    project_id: UUID,
    stage_id: UUID,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectResponse:
    return await service.remove_stage(
        project_id=project_id,
        stage_id=stage_id,
        current_subject=current_subject,
    )


@router.post(
    path="/{project_id}/stages/{stage_id}/start",
    status_code=status.HTTP_200_OK,
    response_model=ProjectResponse,
    summary="Начать этап проекта",
)
async def start_project_stage(
    project_id: UUID,
    stage_id: UUID,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectResponse:
    return await service.start_stage(
        project_id=project_id,
        stage_id=stage_id,
        current_subject=current_subject,
    )


@router.post(
    path="/{project_id}/stages/{stage_id}/complete",
    status_code=status.HTTP_200_OK,
    response_model=ProjectResponse,
    summary="Завершить этап проекта",
)
async def complete_project_stage(
    project_id: UUID,
    stage_id: UUID,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectResponse:
    return await service.complete_stage(
        project_id=project_id,
        stage_id=stage_id,
        current_subject=current_subject,
    )


@router.post(
    path="/{project_id}/stages/{stage_id}/skip",
    status_code=status.HTTP_200_OK,
    response_model=ProjectResponse,
    summary="Пропустить этап проекта",
)
async def skip_project_stage(
    project_id: UUID,
    stage_id: UUID,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectResponse:
    return await service.skip_stage(
        project_id=project_id,
        stage_id=stage_id,
        current_subject=current_subject,
    )


@router.patch(
    path="/{project_id}/stages/{stage_id}/schedule",
    status_code=status.HTTP_200_OK,
    response_model=ProjectStageResponse,
    summary="Запланировать проведение этапа",
)
async def schedule_project_stage(
    project_id: UUID,
    stage_id: UUID,
    data: ProjectStagePlan,
    current_subject: CurrentSubjectDep,
    service: ProjectServiceDep,
) -> ProjectStageResponse:
    return await service.schedule_stage(
        project_id=project_id,
        stage_id=stage_id,
        data=data,
        current_subject=current_subject,
    )
