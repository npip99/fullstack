from __future__ import annotations

import datetime as dt
from uuid import UUID

from sqlalchemy import (
    JSON,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry,
)

# pyright: reportUnannotatedClassAttribute=false
# pyright: reportUninitializedInstanceVariable=false

# CAREFUL! `int` has to be before `float`, so that ints render as int objects when serializing/deserializing.
type Json = None | bool | str | int | float | list[Json] | dict[str, Json]
type JsonDocument = dict[str, Json]


reg = registry(
    type_annotation_map={
        JsonDocument: JSON,
    }
)


# AsyncAttrs:
#   - https://sqlalche.me/e/20/xd2s
#   - https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
@reg.as_declarative_base()
class Base(AsyncAttrs, DeclarativeBase):
    pass


@reg.mapped_as_dataclass(kw_only=True)
class DBAccount:
    __tablename__ = "account"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
        default=None,
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
        default=None,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        default=None,
    )

    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    email: Mapped[str | None] = mapped_column(index=True)
    phone: Mapped[str | None] = mapped_column(index=True)
