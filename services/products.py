from collections.abc import Sequence

from sqlalchemy import select, func, Integer, or_

import models
import schemas.base as base_schemas
import schemas.products as products_schemas
from schemas.base import OkResponseSchema
from services.base import BaseService


class ProductsService(BaseService):
    @staticmethod
    def apply_pagination(stmt, pagination: products_schemas.PaginationRequest):
        return stmt.offset(pagination.page - 1).limit(pagination.per_page)

    async def get_pagination_info(self, stmt, per_page: int) -> base_schemas.PaginationResponse:
        count_stmt = select(
            func.cast(func.ceil(func.count() / per_page), Integer),
            func.count(),
        ).select_from(stmt.subquery())

        result = await self.session.execute(count_stmt)
        pages, total = result.first()

        return base_schemas.PaginationResponse(
            pages=pages,
            total=total,
        )

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

        pagination_info = await self.get_pagination_info(stmt, products_list_filter.pagination.per_page)
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

