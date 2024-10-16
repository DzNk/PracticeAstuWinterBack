from enum import IntEnum, unique

from .base import ApiModel, PaginationResponse, PaginationRequest


@unique
class Permission(IntEnum):
    MANAGE_USERS = 1 << 0
    MANAGE_PRODUCTS = 1 << 1
    SELL_PRODUCTS = 1 << 2


class TokenDataSchema(ApiModel):
    permission: int
    iat: int


class UserLogin(ApiModel):
    username: str
    password: str


class UserDataRequest(ApiModel):
    username: str
    password: str
    permission: int


class LoginResponse(ApiModel):
    permission: int
    name: str
    ok: bool = False


class UserListFilter(ApiModel):
    keyword: str = ""
    permission: int | None = None
    pagination: PaginationRequest


class UserList(ApiModel):
    users: list[UserDataRequest]
    pagination_info: PaginationResponse
