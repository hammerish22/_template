import uuid
from datetime import datetime as dt
from datetime import UTC

from sqlalchemy import (
    ForeignKey, 
    Boolean, DateTime, Integer, String
)

from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column
)


DEFAULT_USER_ID = "admin"


class Base(DeclarativeBase):
    pass


class _Audit_Base(Base):
    __abstract__ = True

    uid: Mapped[str]                    = mapped_column(String(36), primary_key=True, default=uuid.uuid7(), nullable=False)
    state: Mapped[int]                  = mapped_column(Integer, default=1, nullable=False)
    is_deleted: Mapped[bool]            = mapped_column(Boolean, default=False, nullable=False)

    created_datetime: Mapped[dt]        = mapped_column(DateTime, default=dt.now(UTC), nullable=False)
    created_user_id: Mapped[str]        = mapped_column(String(36), default=DEFAULT_USER_ID, nullable=False)
    modified_datetime: Mapped[dt]       = mapped_column(DateTime, onupdate=dt.now(UTC), nullable=False)
    modified_user_id: Mapped[str]       = mapped_column(String(36), default=DEFAULT_USER_ID, nullable=False)
