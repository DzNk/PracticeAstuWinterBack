from sqlalchemy.orm import Mapped, mapped_column

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
    password_hash: Mapped[str] = mapped_column(
        comment="Хеш пароля",
    )

    is_admin: Mapped[bool] = mapped_column(
        default=False,
        comment="Администратор",
    )

