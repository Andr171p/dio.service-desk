from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from src.shared.domain.entities import AggregateRoot
from src.workflows.domain.rule_registry import RuleDefinition, get_all_rules
from src.workflows.domain.vo import RuleKind

router = APIRouter(tags=["Справочник правил переходов | Rule Registry"])


class RuleDefinitionResponse(BaseModel):
    """Определённое правило из глобального registry."""

    aggregate_type: str = Field(description="Агрегат к которому можно применить правило.")

    type_: str = Field(description="Идентификатор правила", examples=["required_field"])
    kind: RuleKind = Field(description="Тип правила")
    display_name: str = Field(description="Название правила для UI")
    description: str = Field(description="Понятное описание правила (мини дока)")
    config_schema: dict[str, Any] = Field(description="JSON схема для конфигурации")


def _map_rule_definition_to_response(
        definition: RuleDefinition[AggregateRoot, BaseModel],
) -> RuleDefinitionResponse:
    return RuleDefinitionResponse(
        aggregate_type=definition.aggregate_type.__name__,
        type_=definition.type_,
        kind=definition.kind,
        display_name=definition.display_name,
        description=definition.description,
        config_schema=definition.config_schema.model_json_schema(),
    )


@router.get(
    path="/rules",
    status_code=status.HTTP_200_OK,
    response_model=list[RuleDefinitionResponse],
    summary="Получить все правила из registry",
)
def get_defined_rules() -> list[RuleDefinitionResponse]:
    return [_map_rule_definition_to_response(rule) for rule in get_all_rules()]
