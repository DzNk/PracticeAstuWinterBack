from collections.abc import Sequence

from sqlalchemy import select, func, Integer, or_

import models
from services.base import BaseService
import schemas.products as products_schemas
import schemas.base as base_schemas


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
