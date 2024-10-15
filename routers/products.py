from fastapi import APIRouter, Depends

from backend.dependecies import SessionDependency
from schemas.security import Permission
from services import SecurityService, ProductsService
from schemas.products import ProductListFilter, ProductList

products_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@products_router.post(
    "/list",
    operation_id="get_products_list",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.SELL_PRODUCTS,
                ]
            )
        )
    ],
    response_model=ProductList,
)
async def get_products_list(
    products_list_filter: ProductListFilter,
    session: SessionDependency,
) -> ProductList:

    service = ProductsService(session)
    return await service.get_products_list(products_list_filter)
