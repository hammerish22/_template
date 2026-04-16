from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Audit_Base


class User_Type(Audit_Base):
    __tablename__ = "_user_type"

    name: Mapped[str]               = mapped_column(String(100), nullable=False)
    description: Mapped[str]        = mapped_column(String(255), nullable=True)

    users: Mapped[List[User]]       = relationship("User", back_populates="user_type")


class User(Audit_Base):
    __tablename__ = "_user"

    user_type_uid: Mapped[str]      = mapped_column(String(36), ForeignKey("_user_type.uid"), nullable=False)
    username: Mapped[str]           = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str]              = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str]      = mapped_column(String(255), nullable=False)

    user_type: Mapped[User_Type]    = relationship("User_Type", back_populates="users")
