from fastapi import APIRouter, Depends, Request

from backend.dependecies import SessionDependency
from schemas.base import OkResponseSchema, FileResponse
from schemas.products import (
    ProductListFilter,
    ProductList,
    ProductEditRequest,
    SalesRequest,
    ProductOrdersRequest,
    ProductOrderResponse,
    FinishProductRequest,
    DownloadProductOrderRequest,
    SalesUserResponse,
    CreateProductOrderRequest,
)
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


@products_router.post(
    "/create-sales-request",
    operation_id="create_sales_request",
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
async def create_sales_request(
    sales_request: SalesRequest,
    session: SessionDependency,
) -> OkResponseSchema:
    service = ProductsService(session)
    return await service.create_sales_request(sales_request)


@products_router.post(
    "/list-product-orders",
    operation_id="list_product_orders",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.SELL_PRODUCTS,
                ]
            )
        )
    ],
    response_model=ProductOrderResponse,
)
async def list_product_orders(
    session: SessionDependency,
    orders_request: ProductOrdersRequest,
    request: Request,
) -> ProductOrderResponse:
    service = ProductsService(session)
    return await service.list_product_orders(orders_request, request)


@products_router.post(
    "/finish-order",
    operation_id="finish_order",
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
async def list_product_orders(
    session: SessionDependency,
    finish_order_request: FinishProductRequest,
) -> OkResponseSchema:
    service = ProductsService(session)
    return await service.finish_order(finish_order_request.id)


@products_router.post(
    "/get-order-pdf",
    operation_id="get-order-pdf",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.SELL_PRODUCTS,
                ]
            )
        )
    ],
    response_model=FileResponse,
)
async def get_order_pdf(session: SessionDependency, request: DownloadProductOrderRequest) -> FileResponse:
    service = ProductsService(session)
    return await service.get_order_pdf(request.id)


@products_router.post(
    "/sales-list",
    operation_id="get_sales_list",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.SELL_PRODUCTS,
                ]
            )
        )
    ],
    response_model=SalesUserResponse,
)
async def get_order_pdf(session: SessionDependency, request: Request) -> SalesUserResponse:
    service = ProductsService(session)
    return await service.get_sales_requests(request)


@products_router.post(
    "/create-order",
    operation_id="create_order",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.SELL_PRODUCTS,
                ]
            )
        )
    ],
    response_model=OkResponseSchema,
)
async def create_order(
    session: SessionDependency, create_request: CreateProductOrderRequest, request: Request
) -> OkResponseSchema:
    service = ProductsService(session)
    return await service.create_product_order(create_request, request)
