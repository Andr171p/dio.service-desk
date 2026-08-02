from uuid import UUID

from pydantic import BaseModel, Field

from src.crm.domain.vo import OrganizationKind


class OrganizationRef(BaseModel):
    """Ссылка на организацию."""

    id: UUID = Field(description="Уникальный идентификатор организации")
    name: str = Field(description="Наименование организации", examples=["Microsoft"])
    kind: OrganizationKind = Field(description="Вид организации в системе")
