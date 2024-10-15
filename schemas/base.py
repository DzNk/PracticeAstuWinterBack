from typing import Any, Self

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        alias_generator=to_camel,
    )

    @classmethod
    def deserialize(cls: Self, obj: dict[str, Any]) -> Self:
        return cls.model_validate(obj)

    @classmethod
    def deserialize_str(cls, obj: str) -> Self:
        return cls.model_validate_json(obj)

    def serialize(self, by_alias: bool = True) -> dict[str, Any]:
        return self.model_dump(by_alias=by_alias)

    def serialize_str(self, by_alias: bool = True) -> str:
        return self.model_dump_json(by_alias=by_alias)


class OkResponseSchema(ApiModel):
    ok: bool
    message: str = ""
