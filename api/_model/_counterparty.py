from __future__ import annotations

from typing import List

from sqlalchemy import (
    ForeignKey,
    String
)
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.orm import (
    Mapped,
    declared_attr,
    mapped_column,
    relationship
)

from api._database import _Audit_Base


class _Counterparty_Type(_Audit_Base):
    __abstract__ = True

    name: Mapped[str]               = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str]        = mapped_column(String(255), nullable=True)

    external_uid: Mapped[str]       = mapped_column(String(255), nullable=
    True, unique=True)

    @declared_attr
    def counterparties(cls) -> Mapped[List["Counterparty"]]:
        return relationship("Counterparty", back_populates="counterparty_type")


class _Counterparty(_Audit_Base):
    __abstract__ = True

    counterparty_type_uid: Mapped[str] = mapped_column(String(36), ForeignKey("_counterparty_type.uid"), nullable=False)
    name: Mapped[str]               = mapped_column(String(255), nullable=False)
    
    registration_number: Mapped[str]  = mapped_column(String(255), nullable=True, unique=True)
    registration_country: Mapped[str] = mapped_column(String(2), nullable=True)

    address: Mapped[list[str]]      = mapped_column(ARRAY(String(255)), nullable=True)
    email: Mapped[str]              = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str]       = mapped_column(String(50), nullable=True)

    external_uid: Mapped[str]       = mapped_column(String(255), nullable=
    True, unique=True)

    @declared_attr
    def parent_counterparty_uid(cls) -> Mapped[str]:
        return mapped_column(String(36), ForeignKey(f"{cls.__tablename__}.uid"), nullable=True)
    
    @declared_attr
    def counterparty_type(cls) -> Mapped["Counterparty_Type"]:
        return relationship("Counterparty_Type", back_populates="counterparties")
