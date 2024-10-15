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
