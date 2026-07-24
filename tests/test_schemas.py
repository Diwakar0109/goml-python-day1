import pytest
from app.schemas.ticket import (
    CreateTicketRequest,
    UpdateTicketRequest,
    TicketResponse,
    SummarizeRequest,
)


@pytest.mark.parametrize(
    "title,priority",
    [
        ("Fix database index issue", "high"),
        ("Documentation update", "low"),
        ("API latency spikes", "medium"),
    ]
)
def test_create_ticket_validation_valid(title, priority):
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


def test_summarize_request_validation():
    req = SummarizeRequest(ticket_description="Valid long description for testing.")
    assert req.ticket_description == "Valid long description for testing."

    with pytest.raises(ValueError):
        SummarizeRequest(ticket_description="short")
