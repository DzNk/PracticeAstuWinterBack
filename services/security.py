from collections.abc import Callable, Sequence
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
from schemas.base import OkResponseSchema
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

    async def create_user(self, user: security_schemas.UserDataRequest) -> OkResponseSchema:
        stmt = select(models.User).where(models.User.username == user.username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            OkResponseSchema(
                ok=False,
                message="Пользователь с таким именем уже существует",
            )

        pwd_context = CryptContext(schemes=["bcrypt"])
        password_hash = pwd_context.hash(user.password)
        new_user = models.User(username=user.username, password_hash=password_hash, permission=user.permission)
        self.session.add(new_user)
        await self.session.commit()

        return OkResponseSchema(
            ok=True,
            message="",
        )

    @staticmethod
    def apply_keyword_filter(stmt, keyword: str):
        if keyword:
            stmt = stmt.where(models.User.username.ilike(f"%{keyword}%"))
        return stmt

    @staticmethod
    def apply_permission_filter(stmt, permission: int | None):
        if permission:
            stmt = stmt.where(models.User.permission == permission)
        return stmt

    async def list_users(self, user_list_filter: security_schemas.UserListFilter) -> security_schemas.UserList:
        stmt = select(models.User).order_by(models.User.id.desc())
        stmt = self.apply_keyword_filter(stmt, user_list_filter.keyword)
        stmt = self.apply_permission_filter(stmt, user_list_filter.permission)

        pagination_info = await self.get_pagination_info(stmt)
        stmt = self.apply_pagination(stmt, user_list_filter.pagination)

        result = await self.session.execute(stmt)
        rows: Sequence[models.User] = result.scalars().all()
        items = []

        for row in rows:
            items.append(
                security_schemas.UserDataRequest(
                    username=row.username,
                    password="",
                    permission=row.permission,
                )
            )

        return security_schemas.UserList(
            users=items,
            pagination_info=pagination_info,
        )

    async def edit_user(self, user: security_schemas.UserDataRequest) -> OkResponseSchema:
        stmt = select(models.User).where(models.User.username == user.username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            return OkResponseSchema(
                ok=False,
                message="Пользователь не найден",
            )

        db_user.permission = user.permission
        await self.session.commit()

        return OkResponseSchema(
            ok=True,
            message="",
        )
