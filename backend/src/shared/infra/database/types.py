from typing import Annotated

from datetime import datetime
from uuid import UUID

from sqlalchemy import TEXT, DateTime
from sqlalchemy.orm import mapped_column

str_unique = Annotated[str, mapped_column(unique=True)]
str_null = Annotated[str | None, mapped_column(nullable=True)]
uuid_null = Annotated[UUID | None, mapped_column(nullable=True)]
text_null = Annotated[str | None, mapped_column(TEXT, nullable=True)]
datetime_tz = Annotated[datetime, mapped_column(DateTime(timezone=True))]
datetime_null = Annotated[datetime | None, mapped_column(DateTime(timezone=True), nullable=True)]
