from typing import Any, NamedTuple

from collections.abc import Mapping

from jinja2 import BaseLoader, StrictUndefined
from jinja2.sandbox import SandboxedEnvironment


class RenderedTemplate(NamedTuple):
    subject: str | None
    body: str


_environment = SandboxedEnvironment(
    loader=BaseLoader(),
    undefined=StrictUndefined,
    autoescape=False,
)


def _render_string(template: str, context: Mapping[str, Any]) -> str:
    return _environment.from_string(template).render(context)


def render_template(
        *, subject: str | None, body: str, context: Mapping[str, Any],
) -> RenderedTemplate:
    """
    Рендерит тему и тело сообщения с использованием безопасного окружения Jinja.
    Выбрасывает jinja2 UndefinedError, если в контексте не хватает обязательных переменных.
    """

    rendered_subject, rendered_body = (
        _render_string(template, context)
        if template is not None else None
        for template in (subject, body)
    )

    return RenderedTemplate(subject=rendered_subject, body=rendered_body)
