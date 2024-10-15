from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="ID пользователя",
    )
    username: Mapped[str] = mapped_column(
        index=True,
        comment="Имя пользователя",
    )
    permission: Mapped[int] = mapped_column(comment="Права пользователя")
    password_hash: Mapped[str] = mapped_column(
        comment="Хеш пароля",
    )


class Counterparty(BaseModel):
    __tablename__ = "counterparties"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="ID контрагента",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    user: Mapped["User"] = relationship()
