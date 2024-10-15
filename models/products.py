from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="ID товара",
    )

    name: Mapped[str] = mapped_column(
        comment="Название товара",
        index=True,
    )

    article: Mapped[str] = mapped_column(
        comment="Артикул товара",
        index=True,
    )

    description: Mapped[str] = mapped_column(
        comment="Описание товара",
    )

    price: Mapped[float] = mapped_column(
        comment="Цена товара",
    )

    quantity: Mapped[int] = mapped_column(
        comment="Количество товара",
    )
