import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ticket import CreateTicketRequest, UpdateTicketRequest, TicketResponse
from app.services import ticket_service

client = TestClient(app)


@pytest.mark.parametrize(
    "title,priority",
    [
        ("Fix database index issue", "high"),
        ("Documentation update", "low"),
        ("API latency spikes", "medium"),
    ]
)
def test_create_ticket_validation(title, priority):
    req = CreateTicketRequest(title=title, priority=priority)
    assert req.title == title
    assert req.priority == priority


@pytest.mark.parametrize(
    "title,priority",
    [
        ("   ", "low"),
        ("ab", "medium"),
        ("", "high"),
    ]
)
def test_create_ticket_failures(title, priority):
    with pytest.raises(ValueError):
        CreateTicketRequest(title=title, priority=priority)


@pytest.mark.parametrize(
    "title,priority,status",
    [
        ("   ", None, None),
        (None, "urgent", None),
        (None, None, "unknown"),
    ]
)
def test_update_ticket_failures(title, priority, status):
    with pytest.raises(ValueError):
        UpdateTicketRequest(title=title, priority=priority, status=status)


@pytest.mark.parametrize(
    "status,expected_resolved",
    [
        ("resolved", True),
        ("open", False),
        ("in_progress", False),
        ("closed", False),
    ]
)
def test_ticket_response_is_resolved(status, expected_resolved):
    resp = TicketResponse(
        title="Valid ticket",
        priority="low",
        status=status
    )
    assert resp.is_resolved == expected_resolved


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


def test_api_create_ticket():
    res = client.post(
        "/tickets/",
        json={"title": "Production crash", "priority": "high"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Production crash"
    assert data["priority"] == "high"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "ab", "priority": "high"},
        {"title": "   ", "priority": "low"},
        {"title": "Valid title", "priority": "bad"}
    ]
)
def test_api_create_ticket_failures(payload):
    res = client.post("/tickets/", json=payload)
    assert res.status_code == 422


def test_api_get_ticket_details(existing_ticket_id):
    res = client.get(f"/tickets/{existing_ticket_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == existing_ticket_id
    assert data["title"] == "Integration test ticket"


def test_api_delete_flow(existing_ticket_id):
    del_res = client.delete(f"/tickets/{existing_ticket_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/tickets/{existing_ticket_id}")
    assert get_res.status_code == 404


def test_api_summarize_ticket():
    from app.api.ai import get_bedrock_service
    from app.services.bedrock_services import FakeBedrockService
    
    app.dependency_overrides[get_bedrock_service] = lambda: FakeBedrockService()
    try:
        res = client.post(
            "/ai/summarize",
            json={"ticket_description": "My computer is not turning on and I need help urgently."}
        )
        assert res.status_code == 200
        data = res.json()
        assert "summary" in data
        assert "suggested_response" in data
        assert data["summary"].startswith("Support issue:")
    finally:
        app.dependency_overrides.clear()