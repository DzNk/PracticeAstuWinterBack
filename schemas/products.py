from datetime import datetime
from schemas.base import ApiModel, PaginationResponse, PaginationRequest


class ProductItem(ApiModel):
    id: int
    name: str
    description: str
    price: float
    article: str
    quantity: int


class ProductList(ApiModel):
    products: list[ProductItem]
    pagination_info: PaginationResponse


class ProductListFilter(ApiModel):
    keyword: str = ""
    pagination: PaginationRequest


class ProductEditRequest(ApiModel):
    name: str
    description: str
    price: float
    article: str
    quantity: int


class SalesRequest(ApiModel):
    article: str
    quantity: int
    price: float
    user_id: int
    income: float


class ProductOrdersRequest(ApiModel):
    keyword: str = ""
    pagination: PaginationRequest


class ProductOrderItem(ApiModel):
    id: int
    date: datetime
    username: str
    income: float
    price: float
    finished: bool


class ProductOrderResponse(ApiModel):
    items: list[ProductOrderItem]
    pagination_info: PaginationResponse


class FinishProductRequest(ApiModel):
    id: int


class DownloadProductOrderRequest(ApiModel):
    id: int


class SalesRequestFilter(ApiModel):
    keyword: str = ""
    pagination: PaginationRequest


class SalesItem(ApiModel):
    id: int
    product_name: str
    price: float
    quantity: int
    income: float


class SalesUserResponse(ApiModel):
    items: list[SalesItem]


class CreateProductOrderRequest(ApiModel):
    ids: list[int]
