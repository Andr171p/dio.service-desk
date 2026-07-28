from __future__ import annotations

from typing import TYPE_CHECKING

from io import BytesIO

from xhtml2pdf import pisa

from .common import (
    PDF_TEMPLATE_NAME,
    PROJECT_STAGES_TEMPLATES_DIR,
    build_report_context,
    create_html_template_environment,
)

if TYPE_CHECKING:
    from ..services.stage_report import ProjectStagesReport


def resolve_pdf_resource(uri: str, _: str | None = None) -> str:
    """
    Преобразовать относительный путь ресурса PDF-шаблона в абсолютный.
    """

    templates_path = PROJECT_STAGES_TEMPLATES_DIR.resolve()
    resource_path = (templates_path / uri).resolve()

    if not resource_path.is_relative_to(templates_path):
        raise ValueError(f"PDF resource is outside templates directory: {uri}")

    if not resource_path.is_file():
        raise FileNotFoundError(f"PDF resource not found: {resource_path}")

    return str(resource_path)


def export_project_stages_to_pdf(report: ProjectStagesReport) -> bytes:
    """
    Сформировать PDF-отчёт по этапам проекта из HTML-шаблона.
    """

    environment = create_html_template_environment()
    template = environment.get_template(PDF_TEMPLATE_NAME)
    html = template.render(**build_report_context(report))

    output = BytesIO()
    result = pisa.CreatePDF(
        src=html,
        dest=output,
        encoding="utf-8",
        link_callback=resolve_pdf_resource,
    )
    if result.err:
        raise RuntimeError("Failed to render project stages PDF report")

    return output.getvalue()
