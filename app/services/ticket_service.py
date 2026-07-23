from uuid import UUID

from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import (
    CreateTicketRequest,
    UpdateTicketRequest,
)


async def create_ticket(
    repo: TicketRepository,
    ticket: CreateTicketRequest,
):
    return await repo.create(ticket)


async def get_tickets(
    repo: TicketRepository,
    status: str | None = None,
    priority: str | None = None,
):
    return await repo.get_all(status, priority)


async def get_ticket(
    repo: TicketRepository,
    ticket_id: UUID,
):
    return await repo.get_by_id(ticket_id)


async def update_ticket(
    repo: TicketRepository,
    ticket_id: UUID,
    update: UpdateTicketRequest,
):
    ticket = await repo.get_by_id(ticket_id)

    if ticket is None:
        return None

    return await repo.update(ticket, update)


async def delete_ticket(
    repo: TicketRepository,
    ticket_id: UUID,
):
    ticket = await repo.get_by_id(ticket_id)

    if ticket is None:
        return False

    await repo.delete(ticket)
    return True