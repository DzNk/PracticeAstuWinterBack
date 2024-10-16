from sqlalchemy.ext.asyncio import AsyncSession
from schemas.base import PaginationRequest, PaginationResponse
from sqlalchemy import select, func


class BaseService:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def apply_pagination(stmt, pagination: PaginationRequest):
        return stmt.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)

    async def get_pagination_info(self, stmt) -> PaginationResponse:
        count_stmt = select(
            func.count(),
        ).select_from(stmt.subquery())

        result = await self.session.execute(count_stmt)
        total: int = result.scalar()

        return PaginationResponse(row_count=total)
