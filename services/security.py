from collections.abc import Callable
from functools import reduce
from time import time

from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import Response
from jose import JWTError, jwt
from passlib.context import CryptContext

import models
import schemas.security as security_schemas
from backend.config import SECRET_KEY, SECURITY_ALGORITHM
from services.base import BaseService
from sqlalchemy import select


class SecurityService(BaseService):
    @staticmethod
    def generate_jwt(permission: int) -> str:
        to_encode = security_schemas.TokenDataSchema(
            permission=permission,
            iat=int(time()),
        ).serialize()
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
        return token

    @staticmethod
    async def set_jwt(permission: int, response: Response) -> None:
        token = SecurityService.generate_jwt(permission)
        response.set_cookie(key="access_token", value=token, httponly=False, secure=False, samesite="lax")

    @staticmethod
    def reducer(x: int, y: int) -> int:
        return x | y

    @staticmethod
    def verify_jwt(token: str, required_permissions: list[security_schemas.Permission]) -> None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
            user_permissions = security_schemas.TokenDataSchema.deserialize(payload).permission
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

    async def login_user(self, user: security_schemas.UserLogin, response: Response) -> security_schemas.LoginResponse:
        stmt = select(models.User).where(models.User.username == user.username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if not pwd_context.verify(user.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
            )

        await self.set_jwt(db_user.permission, response)

        return security_schemas.LoginResponse(
            permission=db_user.permission,
            name=db_user.username,
            ok=True,
        )

    async def create_user(self, user: security_schemas.UserCreateRequest) -> security_schemas.LoginResponse:
        stmt = select(models.User).where(models.User.username == user.username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        pwd_context = CryptContext(schemes=["bcrypt"])
        password_hash = pwd_context.hash(user.password)
        new_user = models.User(username=user.username, password_hash=password_hash, permission=user.permission)
        self.session.add(new_user)
        await self.session.commit()

        return security_schemas.LoginResponse(
            permission=new_user.permission,
            name=new_user.username,
        )

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
