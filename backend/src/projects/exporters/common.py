from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup, escape

from src.core.settings import TEMPLATES_DIR

if TYPE_CHECKING:
    from ..services.stage_report import ProjectStagesReport

PROJECT_STAGES_TEMPLATES_DIR = TEMPLATES_DIR / "projects" / "stages"
EXCEL_TEMPLATE_PATH = PROJECT_STAGES_TEMPLATES_DIR / "report.xlsx"
PDF_TEMPLATE_NAME = "report.html"
WORD_TEMPLATE_PATH = PROJECT_STAGES_TEMPLATES_DIR / "report.docx"


def build_report_context(report: ProjectStagesReport) -> dict[str, Any]:
    """
    Подготовить общий контекст для шаблонов отчёта.
    """

    return {
        "project_id": str(report.project_id),
        "project_name": report.project_name,
        "project_key": report.project_key,
        "project_url": report.project_url,
        "project_status": report.project_status,
        "generated_at": report.generated_at.strftime("%d.%m.%Y %H:%M"),
        "rows": [asdict(row) for row in report.rows],
    }


def create_html_template_environment() -> Environment:
    """
    Создать Jinja-окружение для HTML-шаблона PDF.
    """

    environment = Environment(
        loader=FileSystemLoader(PROJECT_STAGES_TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["nl2br"] = _nl2br
    return environment


def render_template_string(template: str, context: dict[str, Any]) -> str:
    """
    Подставить параметры в строку шаблона без HTML-экранирования.
    """

    environment = Environment(
        autoescape=select_autoescape(
            default_for_string=False,
            default=False,
        ),
        undefined=StrictUndefined,
    )
    return environment.from_string(template).render(**context)


def ensure_template_exists(path: Path) -> None:
    """
    Проверить наличие файлового шаблона до начала генерации.
    """

    if not path.is_file():
        raise FileNotFoundError(f"Project stages report template not found: {path}")


def _nl2br(value: object) -> Markup:
    lines = escape(str(value)).splitlines() or [Markup("")]
    return Markup("<br/>").join(lines)
