from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.ticket import (
    CreateTicketRequest,
    TicketResponse,
    UpdateTicketRequest,
)
from app.services.ticket_service import (
    create_ticket,
    delete_ticket,
    get_ticket,
    get_tickets,
    update_ticket,
)

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post("/", response_model=TicketResponse, status_code=201)
def create(request: CreateTicketRequest):
    return create_ticket(request)


@router.get("/", response_model=list[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    return get_tickets(status, priority)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get(ticket_id: UUID):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update(ticket_id: UUID, request: UpdateTicketRequest):
    ticket = update_ticket(ticket_id, request)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.delete("/{ticket_id}")
def delete(ticket_id: UUID):
    success = delete_ticket(ticket_id)

    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {"message": "Ticket deleted successfully"}