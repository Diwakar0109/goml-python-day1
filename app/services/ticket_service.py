from uuid import UUID

from app.schemas.ticket import (
    CreateTicketRequest,
    TicketResponse,
    UpdateTicketRequest,
)

# In-memory storage
tickets: list[TicketResponse] = []


def create_ticket(ticket: CreateTicketRequest) -> TicketResponse:
    new_ticket = TicketResponse(
        title=ticket.title,
        priority=ticket.priority,
    )

    tickets.append(new_ticket)
    return new_ticket


def get_tickets(
    status: str | None = None,
    priority: str | None = None,
) -> list[TicketResponse]:

    results = tickets

    if status:
        results = [t for t in results if t.status == status]

    if priority:
        results = [t for t in results if t.priority == priority]

    return results


def get_ticket(ticket_id: UUID) -> TicketResponse | None:
    for ticket in tickets:
        if ticket.id == ticket_id:
            return ticket
    return None


def update_ticket(
    ticket_id: UUID,
    update: UpdateTicketRequest,
) -> TicketResponse | None:

    ticket = get_ticket(ticket_id)

    if ticket is None:
        return None

    data = update.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(ticket, key, value)

    return ticket


def delete_ticket(ticket_id: UUID) -> bool:

    ticket = get_ticket(ticket_id)

    if ticket is None:
        return False

    tickets.remove(ticket)
    return True