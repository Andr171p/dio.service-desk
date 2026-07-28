from __future__ import annotations

from typing import TYPE_CHECKING

from io import BytesIO

from docxtpl import DocxTemplate, RichText
from jinja2 import Environment, StrictUndefined, select_autoescape

from .common import WORD_TEMPLATE_PATH, build_report_context, ensure_template_exists

if TYPE_CHECKING:
    from ..services.stage_report import ProjectStagesReport


def export_project_stages_to_word(report: ProjectStagesReport) -> bytes:
    """
    Сформировать Word-отчёт по этапам проекта из DOCX-шаблона.
    """

    ensure_template_exists(WORD_TEMPLATE_PATH)
    document = DocxTemplate(WORD_TEMPLATE_PATH)
    context = build_report_context(report)
    context["project_link"] = _build_project_link(document, report.project_url)

    document.render(
        context,
        jinja_env=Environment(
            autoescape=select_autoescape(
                default_for_string=False,
                default=False,
            ),
            undefined=StrictUndefined,
        ),
    )

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _build_project_link(document: DocxTemplate, project_url: str) -> RichText:
    link = RichText()
    link.add(
        project_url,
        color="0563C1",
        underline=True,
        url_id=document.build_url_id(project_url),
    )
    return link
