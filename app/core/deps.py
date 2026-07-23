from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.ticket_repository import TicketRepository


async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


def get_repo(
    db: AsyncSession = Depends(get_db),
) -> TicketRepository:
    return TicketRepository(db)