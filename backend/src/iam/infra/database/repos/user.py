from sqlalchemy import ColumnElement, func, or_, select

from src.iam.domain.entities import User
from src.iam.domain.vo import Email
from src.iam.infra.database.mappers import UserMapper
from src.iam.infra.database.models import UserOrm
from src.shared.infra.database.postgres import SqlAlchemyRepository


def search_users(query: str) -> ColumnElement[bool]:
    query = query.strip()
    if not query:
        raise ValueError("Search query cannot be empty.")

    ts_query = func.websearch_to_tsquery("russian", query)

    return or_(
        UserOrm.search_vector.bool_op("@@")(ts_query),
        UserOrm.email.ilike(f"{query}%"),
        UserOrm.username.ilike(f"{query}%"),
    )


class SqlUserRepository(SqlAlchemyRepository[User, UserOrm]):
    model = UserOrm
    model_mapper = UserMapper
    search = search_users
    filterable_fields = (
        "id",
        "email",
        "username",
        "full_name",
        "createdAt",
        "updatedAt",
    )

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(self.model).where(
            (self.model.email == email.value) & (self.model.deleted_at.is_(None)),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self.model_mapper.from_model(model) if model else None
