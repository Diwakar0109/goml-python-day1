from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

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


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create ticket",
    description="Create a new customer support ticket.",
)
async def create(
    request: CreateTicketRequest,
    repo: TicketRepository = Depends(get_repo),
):
    return await create_ticket(repo, request)


@router.get(
    "/",
    response_model=list[TicketResponse],
    summary="List tickets",
    description="Retrieve support tickets with optional status, priority filtering, and pagination.",
)
async def list_tickets(
    status: Optional[str] = Query(None, description="Filter by status (open, in_progress, resolved, closed)"),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return (1 to 100)"),
    repo: TicketRepository = Depends(get_repo),
):
    return await get_tickets(repo, status=status, priority=priority, skip=skip, limit=limit)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get ticket details",
    description="Fetch a single support ticket by its UUID.",
)
async def get(
    ticket_id: UUID,
    repo: TicketRepository = Depends(get_repo),
):
    ticket = await get_ticket(repo, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return ticket


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update ticket",
    description="Update the attributes of an existing support ticket.",
)
async def update(
    ticket_id: UUID,
    request: UpdateTicketRequest,
    repo: TicketRepository = Depends(get_repo),
):
    ticket = await update_ticket(repo, ticket_id, request)

    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return ticket


@router.delete(
    "/{ticket_id}",
    summary="Delete ticket",
    description="Delete a support ticket by its UUID.",
)
async def delete(
    ticket_id: UUID,
    repo: TicketRepository = Depends(get_repo),
):
    success = await delete_ticket(repo, ticket_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return {"message": "Ticket deleted successfully"}
