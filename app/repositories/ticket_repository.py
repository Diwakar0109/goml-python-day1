from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload) -> Ticket:
        ticket = Ticket(**payload.model_dump())
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        return await self.db.get(Ticket, ticket_id)

    async def get_all(
        self,
        status: str | None = None,
        priority: str | None = None,
    ):
        query = select(Ticket)

        if status:
            query = query.where(Ticket.status == status)

        if priority:
            query = query.where(Ticket.priority == priority)

        result = await self.db.execute(
            query.order_by(Ticket.created_at.desc())
        )

        return list(result.scalars().all())

    async def update(self, ticket, payload) -> Ticket:
        for field, value in payload.model_dump(
            exclude_unset=True
        ).items():
            setattr(ticket, field, value)

        await self.db.flush()
        await self.db.refresh(ticket)

        return ticket

    async def delete(self, ticket) -> None:
        await self.db.delete(ticket)
        await self.db.flush()