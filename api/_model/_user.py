from __future__ import annotations

from typing import List

from sqlalchemy import (
    ForeignKey, 
    String
)

from sqlalchemy.orm import (
    Mapped,
    declared_attr,
    mapped_column,
    relationship
)

from api._database import _Audit_Base

class _User_Type(_Audit_Base):
    __abstract__ = True

    name: Mapped[str]               = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str]        = mapped_column(String(255), nullable=True)

    external_uid: Mapped[str]       = mapped_column(String(255), nullable=
    True, unique=True)

    @declared_attr
    def users(cls) -> Mapped[List["User"]]:
        return relationship("User", back_populates="user_type")


class _User(_Audit_Base):
    __abstract__ = True

    user_type_uid: Mapped[str]      = mapped_column(String(36), ForeignKey("_user_type.uid"), nullable=False)
    first_name: Mapped[str]         = mapped_column(String(100), nullable=False)
    last_name: Mapped[str]          = mapped_column(String(100), nullable=False)
    email: Mapped[str]              = mapped_column(String(255), nullable=False, unique=True)

    external_uid: Mapped[str]       = mapped_column(String(255), nullable=
    True, unique=True)

    @declared_attr
    def user_type(cls) -> Mapped["User_Type"]:
        return relationship("User_Type", back_populates="users")
