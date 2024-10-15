from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session
