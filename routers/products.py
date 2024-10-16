from fastapi import APIRouter, Depends

from backend.dependecies import SessionDependency
from schemas.base import OkResponseSchema
from schemas.products import ProductListFilter, ProductList, ProductEditRequest
from schemas.security import Permission
from services import SecurityService, ProductsService

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


@products_router.post(
    "/create",
    operation_id="create_product",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.MANAGE_PRODUCTS,
                ]
            )
        )
    ],
    response_model=OkResponseSchema,
)
async def create_product(
    product_create_request: ProductEditRequest,
    session: SessionDependency,
) -> OkResponseSchema:
    service = ProductsService(session)
    return await service.create_product(product_create_request)


@products_router.post(
    "/edit",
    operation_id="edit_product",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.MANAGE_PRODUCTS,
                ]
            )
        )
    ],
    response_model=OkResponseSchema,
)
async def edit_product(
    product_edit_request: ProductEditRequest,
    session: SessionDependency,
) -> OkResponseSchema:
    service = ProductsService(session)
    return await service.edit_product(product_edit_request)
