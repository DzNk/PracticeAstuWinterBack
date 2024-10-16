from fastapi import APIRouter, Response, Depends

from backend.dependecies import SessionDependency
from schemas import security as security_schemas
from schemas.base import OkResponseSchema
from schemas.security import Permission, UserList
from services import SecurityService

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user_router.post(
    "/login",
    response_model=security_schemas.LoginResponse,
    operation_id="login_user",
)
async def login_user(
    user: security_schemas.UserLogin,
    session: SessionDependency,
    response: Response,
) -> security_schemas.LoginResponse:
    service = SecurityService(session)
    return await service.login_user(user, response)


@user_router.post(
    "/create",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.MANAGE_USERS,
                ]
            )
        )
    ],
    response_model=OkResponseSchema,
    operation_id="create_user",
)
async def create_user(
    user: security_schemas.UserDataRequest,
    session: SessionDependency,
) -> OkResponseSchema:
    service = SecurityService(session)
    return await service.create_user(user)


@user_router.post(
    "/list",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.MANAGE_USERS,
                ]
            )
        )
    ],
    response_model=security_schemas.UserList,
    operation_id="list_users",
)
async def create_user(
    user_list_filter: security_schemas.UserListFilter,
    session: SessionDependency,
) -> UserList:
    service = SecurityService(session)
    return await service.list_users(user_list_filter)


@user_router.post(
    "/edit",
    dependencies=[
        Depends(
            SecurityService.authenticate(
                [
                    Permission.MANAGE_USERS,
                ]
            )
        )
    ],
    response_model=OkResponseSchema,
    operation_id="edit_user",
)
async def edit_user(
    user_data: security_schemas.UserDataRequest,
    session: SessionDependency,
) -> OkResponseSchema:
    service = SecurityService(session)
    return await service.edit_user(user_data)
