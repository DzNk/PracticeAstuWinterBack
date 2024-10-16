import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from backend.session import session_factory
from schemas.security import UserDataRequest, Permission
from services import SecurityService


async def main():
    session: AsyncSession = session_factory()
    service = SecurityService(session)
    await service.create_user(
        user=UserDataRequest(
            username="admin",
            password="valera337",
            permission=Permission.MANAGE_PRODUCTS | Permission.MANAGE_USERS | Permission.SELL_PRODUCTS,
        )
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
