from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert "message" in data
    assert "version" in data


def test_create_ticket():
    response = client.post(
        "/tickets/",
        json={
            "title": "Login Issue",
            "priority": "high"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Login Issue"
    assert data["priority"] == "high"
    assert data["status"] == "open"



def test_get_all_tickets():
    response = client.get("/tickets/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_ticket():
    create = client.post(
        "/tickets/",
        json={
            "title": "Sample Ticket",
            "priority": "medium"
        }
    )

    ticket_id = create.json()["id"]

    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_update_ticket():

    create = client.post(
        "/tickets/",
        json={
            "title": "Old Title",
            "priority": "low"
        }
    )

    ticket_id = create.json()["id"]

    response = client.put(
        f"/tickets/{ticket_id}",
        json={
            "status": "resolved"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "resolved"
    assert data["is_resolved"] is True


def test_delete_ticket():

    create = client.post(
        "/tickets/",
        json={
            "title": "Delete Me",
            "priority": "low"
        }
    )

    ticket_id = create.json()["id"]

    response = client.delete(f"/tickets/{ticket_id}")

    assert response.status_code == 200


def test_filter_priority():

    client.post(
        "/tickets/",
        json={
            "title": "High Ticket",
            "priority": "high"
        }
    )

    response = client.get("/tickets/?priority=high")

    assert response.status_code == 200

    for ticket in response.json():
        assert ticket["priority"] == "high"


def test_filter_status():

    create = client.post(
        "/tickets/",
        json={
            "title": "Status Ticket",
            "priority": "medium"
        }
    )

    ticket_id = create.json()["id"]

    client.put(
        f"/tickets/{ticket_id}",
        json={
            "status": "resolved"
        }
    )

    response = client.get("/tickets/?status=resolved")

    assert response.status_code == 200

    for ticket in response.json():
        assert ticket["status"] == "resolved"


def test_validation_short_title():

    response = client.post(
        "/tickets/",
        json={
            "title": "ab",
            "priority": "high"
        }
    )

    assert response.status_code == 422


def test_validation_invalid_priority():

    response = client.post(
        "/tickets/",
        json={
            "title": "Login",
            "priority": "urgent"
        }
    )

    assert response.status_code == 422


def test_validation_blank_title():

    response = client.post(
        "/tickets/",
        json={
            "title": "   ",
            "priority": "low"
        }
    )

    assert response.status_code == 422


def test_ticket_not_found():

    response = client.get(
        "/tickets/11111111-1111-1111-1111-111111111111"
    )

    assert response.status_code == 404