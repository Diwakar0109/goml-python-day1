import random
from locust import HttpUser, between, task


class TicketApiUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts running."""
        self.created_ticket_ids = []

    @task(4)
    def check_health(self) -> None:
        self.client.get("/health", name="GET /health")

    @task(4)
    def check_ready(self) -> None:
        self.client.get("/ready", name="GET /ready")

    @task(2)
    def check_root(self) -> None:
        self.client.get("/", name="GET /")

    @task(5)
    def list_tickets(self) -> None:
        self.client.get("/tickets/", name="GET /tickets/")

    @task(3)
    def create_ticket(self) -> None:
        payload = {
            "title": f"Load test ticket {random.randint(1000, 9999)}",
            "priority": random.choice(["low", "medium", "high"]),
            "assignee_email": f"user{random.randint(1, 100)}@example.com"
        }
        with self.client.post("/tickets/", name="POST /tickets/", json=payload) as response:
            if response.status_code == 201:
                try:
                    ticket_id = response.json().get("id")
                    if ticket_id:
                        self.created_ticket_ids.append(ticket_id)
                except Exception:
                    pass

    @task(3)
    def get_ticket_details(self) -> None:
        if self.created_ticket_ids:
            ticket_id = random.choice(self.created_ticket_ids)
            self.client.get(f"/tickets/{ticket_id}", name="GET /tickets/{ticket_id}")

    @task(2)
    def update_ticket(self) -> None:
        if self.created_ticket_ids:
            ticket_id = random.choice(self.created_ticket_ids)
            payload = {
                "title": f"Updated ticket title {random.randint(1000, 9999)}",
                "priority": random.choice(["low", "medium", "high"]),
                "status": random.choice(["open", "in_progress", "resolved", "closed"])
            }
            self.client.put(f"/tickets/{ticket_id}", name="PUT /tickets/{ticket_id}", json=payload)

    @task(2)
    def summarize_ticket(self) -> None:
        payload = {
            "ticket_description": (
                "The database is crashing periodically under high load. "
                "We need to investigate connection pooling and index optimization. "
                "It is affecting multiple users in production."
            )
        }
        self.client.post("/ai/summarize", name="POST /ai/summarize", json=payload)

    @task(1)
    def delete_ticket(self) -> None:
        if self.created_ticket_ids:
            ticket_id = self.created_ticket_ids.pop(random.randrange(len(self.created_ticket_ids)))
            self.client.delete(f"/tickets/{ticket_id}", name="DELETE /tickets/{ticket_id}")
