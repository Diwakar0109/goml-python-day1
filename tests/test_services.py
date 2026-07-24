import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.schemas.ticket import CreateTicketRequest, UpdateTicketRequest
from app.services import ticket_service


@pytest.mark.anyio
async def test_service_create_ticket(mock_repo):
    req = CreateTicketRequest(title="New Ticket", priority="high")
    mock_repo.create.return_value = "created_ticket_obj"
    res = await ticket_service.create_ticket(mock_repo, req)
    assert res == "created_ticket_obj"
    mock_repo.create.assert_called_once_with(req)


@pytest.mark.anyio
async def test_service_get_ticket_by_id(mock_repo):
    ticket_id = uuid4()
    mock_repo.get_by_id.return_value = "ticket_obj"
    res = await ticket_service.get_ticket(mock_repo, ticket_id)
    assert res == "ticket_obj"
    mock_repo.get_by_id.assert_called_once_with(ticket_id)


@pytest.mark.anyio
async def test_service_get_tickets_pagination(mock_repo):
    mock_repo.get_all.return_value = []
    res = await ticket_service.get_tickets(mock_repo, status="open", priority="high", skip=10, limit=20)
    assert res == []
    mock_repo.get_all.assert_called_once_with(status="open", priority="high", skip=10, limit=20)


@pytest.mark.anyio
async def test_service_update_ticket_success(mock_repo):
    ticket_id = uuid4()
    mock_repo.get_by_id.return_value = "existing_ticket"
    mock_repo.update.return_value = "updated_ticket"
    req = UpdateTicketRequest(title="Updated Title")
    
    res = await ticket_service.update_ticket(mock_repo, ticket_id, req)
    assert res == "updated_ticket"
    mock_repo.update.assert_called_once_with("existing_ticket", req)


@pytest.mark.anyio
async def test_service_update_nonexistent_ticket(mock_repo):
    mock_repo.get_by_id.return_value = None
    req = UpdateTicketRequest(status="closed")
    res = await ticket_service.update_ticket(mock_repo, uuid4(), req)
    assert res is None


@pytest.mark.anyio
async def test_service_delete_nonexistent_ticket(mock_repo):
    mock_repo.get_by_id.return_value = None
    res = await ticket_service.delete_ticket(mock_repo, uuid4())
    assert res is False
