from enum import IntEnum, unique

from .base import ApiModel


@unique
class Permission(IntEnum):
    MANAGE_DOCUMENTATION = 1 << 0


class TokenDataSchema(ApiModel):
    permissions: int
    iat: int


class TelegramData(ApiModel):
    id: int
    first_name: str
    auth_date: int
    hash: str
    last_name: str | None = None
    photo_url: str | None = None
    username: str | None = None
