from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class SalesRequests(BaseModel):
    __tablename__ = "sales_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="ID запроса на реализацию товара",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        comment="ID пользователя",
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        comment="ID товара",
    )

    product: Mapped[Product] = relationship()

    price: Mapped[float] = mapped_column(
        comment="Цена продажи",
    )

    income: Mapped[float] = mapped_column(
        comment="Доход за продажу",
        server_default="0",
    )

    quantity: Mapped[int] = mapped_column(
        comment="Количество товара",
    )

    product_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_orders.id"),
        comment="ID реализации на товар",
    )


class ProductOrder(BaseModel):
    __tablename__ = "product_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="ID реализации на товар",
    )

    finished: Mapped[bool] = mapped_column(
        index=True,
        comment="Завершен ли ордер",
    )

    requests: Mapped[list[SalesRequests]] = relationship()
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        comment="ID пользователя",
    )

    realization_date: Mapped[datetime] = mapped_column(comment="Дата реализации", default=datetime.now())
