import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "message" in res.json()


def test_api_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_api_create_ticket_success():
    res = client.post(
        "/tickets/",
        json={"title": "Production database latency", "priority": "high"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Production database latency"
    assert data["priority"] == "high"
    assert data["status"] == "open"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "ab", "priority": "high"},
        {"title": "Valid title", "priority": "critical_invalid"}
    ]
)
def test_api_create_ticket_validation_failures(payload):
    res = client.post("/tickets/", json=payload)
    assert res.status_code == 422


def test_api_list_tickets_with_filters_and_pagination():
    res = client.get("/tickets/?status=open&priority=high&skip=0&limit=10")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_api_get_ticket_details(existing_ticket_id):
    res = client.get(f"/tickets/{existing_ticket_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == existing_ticket_id
    assert data["title"] == "Integration test ticket"


def test_api_get_ticket_not_found():
    random_id = uuid4()
    res = client.get(f"/tickets/{random_id}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Ticket not found"


def test_api_update_ticket(existing_ticket_id):
    res = client.put(
        f"/tickets/{existing_ticket_id}",
        json={"title": "Updated Title via API", "status": "in_progress"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Updated Title via API"
    assert data["status"] == "in_progress"


def test_api_e2e_full_lifecycle():
    create_res = client.post(
        "/tickets/",
        json={"title": "E2E Lifecycle Ticket", "priority": "low", "assignee_email": "e2e@example.com"}
    )
    assert create_res.status_code == 201
    ticket_id = create_res.json()["id"]

    get_res = client.get(f"/tickets/{ticket_id}")
    assert get_res.status_code == 200
    assert get_res.json()["assignee_email"] == "e2e@example.com"

    update_res = client.put(
        f"/tickets/{ticket_id}",
        json={"status": "resolved"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["is_resolved"] is True

    list_res = client.get("/tickets/?status=resolved")
    assert list_res.status_code == 200
    ids = [t["id"] for t in list_res.json()]
    assert ticket_id in ids

    del_res = client.delete(f"/tickets/{ticket_id}")
    assert del_res.status_code == 200

    confirm_get = client.get(f"/tickets/{ticket_id}")
    assert confirm_get.status_code == 404
