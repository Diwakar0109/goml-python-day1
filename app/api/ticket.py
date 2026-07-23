from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_repo
from app.repositories.ticket_repository import TicketRepository
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
async def create(
    request: CreateTicketRequest,
    repo: TicketRepository = Depends(get_repo),
):
    return await create_ticket(repo, request)


@router.get("/", response_model=list[TicketResponse])
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    repo: TicketRepository = Depends(get_repo),
):
    return await get_tickets(repo, status, priority)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get(
    ticket_id: UUID,
    repo: TicketRepository = Depends(get_repo),
):
    ticket = await get_ticket(repo, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update(
    ticket_id: UUID,
    request: UpdateTicketRequest,
    repo: TicketRepository = Depends(get_repo),
):
    ticket = await update_ticket(repo, ticket_id, request)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.delete("/{ticket_id}")
async def delete(
    ticket_id: UUID,
    repo: TicketRepository = Depends(get_repo),
):
    success = await delete_ticket(repo, ticket_id)

    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {"message": "Ticket deleted successfully"}

