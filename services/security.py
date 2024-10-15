from collections.abc import Callable
from functools import reduce
from time import time

from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import Response
from jose import JWTError, jwt

import schemas.security as security_schemas
from backend.config import SECRET_KEY, SECURITY_ALGORITHM


class SecurityService:
    @staticmethod
    def generate_jwt(permission_keys: list[str]) -> str:
        permission_values = [getattr(security_schemas.Permission, permission) for permission in permission_keys]
        permissions: int = reduce(SecurityService.reducer, permission_values)
        to_encode = security_schemas.TokenDataSchema(
            permissions=permissions,
            iat=int(time()),
        ).serialize()
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
        return token

    @staticmethod
    async def set_jwt(permission_keys: list[str], response: Response) -> None:
        token = SecurityService.generate_jwt(permission_keys)
        response.set_cookie(key="access_token", value=token, httponly=False, secure=False, samesite="lax")

    @staticmethod
    def reducer(x: int, y: int) -> int:
        return x | y

    @staticmethod
    def verify_jwt(token: str, required_permissions: list[security_schemas.Permission]) -> None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
            user_permissions = security_schemas.TokenDataSchema.deserialize(payload).permissions
            has_required_permissions = True

            for permission in required_permissions:
                if (permission & user_permissions) != permission:
                    has_required_permissions = False
                    break

            if not has_required_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions or invalid token",
                ) from None

        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

    @staticmethod
    def authenticate(required_permissions: list[security_schemas.Permission]) -> Callable:
        def _authenticate(request: Request) -> None:
            token = request.cookies.get("access_token")
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Missing token in cookies",
                )
            SecurityService.verify_jwt(token, required_permissions)

        return _authenticate
