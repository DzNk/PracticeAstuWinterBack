import base64
import os
from collections.abc import Sequence
from time import strftime

from sqlalchemy import select, func, Integer, or_
from sqlalchemy.orm import joinedload
from weasyprint import HTML

import models
import schemas.base as base_schemas
import schemas.products as products_schemas
from backend.config import TEMPLATES
from schemas.base import OkResponseSchema, FileResponse
from services import SecurityService
from services.base import BaseService
from fastapi import Request


class ProductsService(BaseService):

    @staticmethod
    def apply_keyword_filter(stmt, keyword: str):
        if keyword:
            stmt = stmt.where(
                or_(
                    models.Product.name.ilike(f"%{keyword}%"),
                    models.Product.article.ilike(f"%{keyword}%"),
                )
            )
        return stmt

    async def get_products_list(
        self, products_list_filter: products_schemas.ProductListFilter
    ) -> products_schemas.ProductList:
        stmt = select(models.Product).order_by(models.Product.id.desc())
        stmt = self.apply_keyword_filter(stmt, products_list_filter.keyword)

        pagination_info = await self.get_pagination_info(stmt)
        stmt = self.apply_pagination(stmt, products_list_filter.pagination)

        result = await self.session.execute(stmt)
        rows: Sequence[models.Product] = result.scalars().all()
        products: list[products_schemas.ProductItem] = []
        for row in rows:
            products.append(
                products_schemas.ProductItem(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    price=row.price,
                    article=row.article,
                    quantity=row.quantity,
                )
            )

        return products_schemas.ProductList(
            products=products,
            pagination_info=pagination_info,
        )

    async def create_product(self, product: products_schemas.ProductEditRequest) -> OkResponseSchema:
        stmt = select(models.Product).where(models.Product.article == product.article)
        result = await self.session.execute(stmt)
        existing_product = result.scalars().first()

        if existing_product:
            return OkResponseSchema(ok=False, message="Товар с таким артикулом уже существует")

        new_product = models.Product(
            name=product.name,
            article=product.article,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
        )
        self.session.add(new_product)
        await self.session.commit()

        return OkResponseSchema(
            ok=True,
        )

    async def edit_product(self, product: products_schemas.ProductEditRequest) -> OkResponseSchema:
        stmt = select(models.Product).where(models.Product.article == product.article)
        result = await self.session.execute(stmt)
        existing_product = result.scalars().first()

        if not existing_product:
            return OkResponseSchema(ok=False, message="Товар с таким артикулом не найден")

        existing_product.name = product.name
        existing_product.description = product.description
        existing_product.price = product.price
        existing_product.quantity = product.quantity
        await self.session.commit()

        return OkResponseSchema(
            ok=True,
        )

    async def create_sales_request(self, sales_request: products_schemas.SalesRequest) -> OkResponseSchema:
        stmt = select(models.Product).where(models.Product.article == sales_request.article)
        result = await self.session.execute(stmt)
        product: models.Product | None = result.scalars().first()

        if not product:
            return OkResponseSchema(ok=False, message="Товар не найден")

        if product.quantity < sales_request.quantity:
            return OkResponseSchema(ok=False, message="Недостаточно товара на складе")

        product.quantity -= sales_request.quantity
        self.session.add(
            models.SalesRequests(
                user_id=sales_request.user_id,
                product_id=product.id,
                price=sales_request.price,
                quantity=sales_request.quantity,
                income=sales_request.income,
            )
        )
        await self.session.commit()

        return OkResponseSchema(
            ok=True,
        )

    @staticmethod
    def apply_keyword_sales_filter(stmt, keyword):
        if keyword:
            stmt = stmt.where(
                models.User.username.ilike(f"%{keyword}%"),
            )
        return stmt

    @staticmethod
    def apply_user_id_filter(stmt, request: Request):
        user_id = SecurityService.get_user_id(request)
        is_admin = SecurityService.is_admin(request)
        if not is_admin:
            stmt = stmt.where(models.ProductOrder.user_id == user_id)
        return stmt

    async def list_product_orders(
        self, orders_request: products_schemas.ProductOrdersRequest, request: Request
    ) -> products_schemas.ProductOrderResponse:
        stmt = (
            select(
                models.ProductOrder.id.label("id"),
                models.ProductOrder.realization_date.label("date"),
                models.User.username.label("username"),
                func.sum(models.SalesRequests.price * models.SalesRequests.quantity).label("total_price"),
                func.sum(models.SalesRequests.income * models.SalesRequests.quantity).label("total_income"),
                models.ProductOrder.finished.label("finished"),
            )
            .join(models.User, models.ProductOrder.user_id == models.User.id)
            .join(models.SalesRequests, models.ProductOrder.id == models.SalesRequests.product_order_id)
            .group_by(
                models.ProductOrder.id,
                models.ProductOrder.realization_date,
                models.User.username,
                models.ProductOrder.finished,
            )
            .order_by(models.ProductOrder.id.desc())
        )
        stmt = self.apply_keyword_sales_filter(stmt, orders_request.keyword)
        stmt = self.apply_user_id_filter(stmt, request)
        pagination_info = await self.get_pagination_info(stmt)
        stmt = self.apply_pagination(stmt, orders_request.pagination)

        result = await self.session.execute(stmt)
        products: list[products_schemas.ProductOrderItem] = []
        for row in result.all():
            products.append(
                products_schemas.ProductOrderItem(
                    id=row.id,
                    date=row.date,
                    username=row.username,
                    price=row.total_price,
                    finished=row.finished,
                    income=row.total_income,
                )
            )

        return products_schemas.ProductOrderResponse(
            items=products,
            pagination_info=pagination_info,
        )

    async def finish_order(self, order_id: int) -> OkResponseSchema:
        stmt = select(models.ProductOrder).where(models.ProductOrder.id == order_id)
        result = await self.session.execute(stmt)
        order = result.scalars().first()
        if not order:
            return OkResponseSchema(ok=False, message="Заказ не найден")
        order.finished = True
        await self.session.commit()
        return OkResponseSchema(ok=True)

    async def get_order_pdf(self, order_id: int) -> base_schemas.FileResponse:
        stmt = (
            select(models.ProductOrder)
            .where(models.ProductOrder.id == order_id)
            .options(joinedload(models.ProductOrder.requests).joinedload(models.SalesRequests.product))
        )
        result = await self.session.execute(stmt)
        order: models.ProductOrder = result.scalars().first()

        products = []
        final_product_price = 0
        final_income = 0
        for request in order.requests:
            product: models.Product = request.product
            products.append(
                {
                    "name": product.name,
                    "article": product.article,
                    "quantity": request.quantity,
                    "price": f"{request.price:.2f}" if request.price % 1 != 0 else f"{request.price:.0f}",
                    "income": f"{request.income:.2f}" if request.income % 1 != 0 else f"{request.income:.0f}",
                }
            )

            final_product_price += request.price * request.quantity
            final_income += request.income * request.quantity

        final_html = TEMPLATES.get_template("product_order.html").render(
            date_from=order.realization_date.strftime("%d.%m.%Y"),
            products=products,
            final_product_price=(
                f"{final_product_price:.2f}" if final_product_price % 1 != 0 else f"{final_product_price:.0f}"
            ),
            final_income=f"{final_income:.2f}" if final_income % 1 != 0 else f"{final_income:.0f}",
            finished=order.finished,
        )

        pdf = HTML(string=final_html).write_pdf()
        encoded_pdf = base64.b64encode(pdf).decode("ascii")
        random_filename = f"order_{order.id}_{os.urandom(8).hex()}.pdf"

        return base_schemas.FileResponse(
            file=encoded_pdf,
            file_type="application/pdf",
            file_name=random_filename,
        )
