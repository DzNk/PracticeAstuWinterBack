from fastapi import APIRouter, Response

from backend.dependecies import SessionDependency
from schemas import security as security_schemas
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
