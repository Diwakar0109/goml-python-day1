# AI Service Desk — Ticket Management API

An intelligent customer-support ticket management system built with **FastAPI**, **PostgreSQL**, and **Amazon Bedrock AI**. It provides a full CRUD REST API for support tickets alongside an AI-powered summarization endpoint that leverages AWS Bedrock foundation models to generate ticket summaries and suggested agent responses.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
  - [Project Structure](#project-structure)
  - [Layered Architecture](#layered-architecture)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Database](#database)
  - [Schema](#schema)
  - [Migrations](#migrations)
  - [Visualization](#visualization)
- [API Reference](#api-reference)
  - [General Endpoints](#general-endpoints)
  - [Ticket Endpoints](#ticket-endpoints)
  - [AI Endpoints](#ai-endpoints)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Test Structure](#test-structure)
  - [Code Coverage](#code-coverage)
- [Performance Profiling](#performance-profiling)
  - [cProfile](#cprofile)
  - [Locust Load Testing](#locust-load-testing)
- [Prompt Templates](#prompt-templates)
- [Docker Services](#docker-services)
- [API Documentation](#api-documentation)

---

## Features

- **Full CRUD Operations** — Create, read, update, and delete support tickets with UUID-based identification.
- **AI-Powered Summarization** — Integrates with Amazon Bedrock Converse API for ticket summarization and suggested responses.
- **Demo Mode** — Offline `FakeBedrockService` for classroom or local demonstrations without AWS credentials.
- **Pagination & Filtering** — Query tickets by status, priority with `skip`/`limit` pagination (max 100 per page).
- **Database Migrations** — Automated schema versioning via Alembic with auto-migration on container startup.
- **Structured Logging** — Application-wide structured logging with request duration tracking via middleware.
- **Global Exception Handling** — Catches `SQLAlchemyError` and unhandled exceptions, returning clean JSON error responses.
- **Health & Readiness Probes** — Dedicated `/health` and `/ready` endpoints for container orchestration.
- **YAML Prompt Templates** — Externalized, versioned AI prompt templates loaded from YAML configuration.
- **Docker-Compose Stack** — Multi-container deployment with PostgreSQL, API server, and Adminer database UI.
- **Comprehensive Test Suite** — 30 tests (20 unit + 10 integration/E2E) with 79% code coverage.
- **Performance Profiling** — cProfile CPU profiling and Locust HTTP load testing.

---

## Technology Stack

| Layer            | Technology                                   |
| ---------------- | -------------------------------------------- |
| **Framework**    | FastAPI 0.139+                               |
| **Language**     | Python 3.13                                  |
| **Database**     | PostgreSQL 17 (Alpine)                       |
| **ORM**          | SQLAlchemy 2.0 (async) + asyncpg             |
| **Migrations**   | Alembic 1.18+                                |
| **AI Service**   | Amazon Bedrock (boto3 Converse API)          |
| **Validation**   | Pydantic v2 + pydantic-settings              |
| **Config**       | YAML (prompt templates), `.env` (secrets)    |
| **Testing**      | pytest + pytest-cov + httpx                  |
| **Load Testing** | Locust 2.46+                                 |
| **Profiling**    | cProfile + pstats + SnakeViz                 |
| **Packaging**    | uv (dependency management)                   |
| **Container**    | Docker + Docker Compose                      |
| **DB Viewer**    | Adminer (web-based)                          |

---

## Architecture

### Project Structure

```
t1/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application, middleware, exception handlers
│   ├── api/
│   │   ├── ticket.py                # Ticket CRUD route handlers
│   │   └── ai.py                    # AI summarization route handler
│   ├── core/
│   │   ├── config.py                # Pydantic settings (loads .env)
│   │   └── deps.py                  # Dependency injection (DB session, repository)
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   └── session.py               # Async engine and session factory
│   ├── models/
│   │   └── ticket.py                # SQLAlchemy Ticket ORM model
│   ├── repositories/
│   │   └── ticket_repository.py     # Data access layer (CRUD queries)
│   ├── schemas/
│   │   └── ticket.py                # Pydantic request/response schemas
│   └── services/
│       ├── ticket_service.py        # Business logic layer
│       ├── bedrock_services.py      # AWS Bedrock AI integration
│       ├── prompt_templates.py      # YAML prompt template loader
│       └── prompt_templates.yaml    # Versioned AI prompt definitions
├── alembic/
│   ├── env.py                       # Alembic migration environment config
│   ├── script.py.mako               # Migration script template
│   └── versions/                    # Auto-generated migration scripts
├── tests/
│   ├── conftest.py                  # Shared fixtures (DB cleanup, mock repo)
│   ├── test_schemas.py              # 14 Pydantic schema unit tests
│   ├── test_services.py             # 6 service layer unit tests
│   ├── test_routes.py               # 10 integration & E2E route tests
│   ├── profile_cprofile.py          # cProfile performance profiling script
│   ├── locustfile.py                # Locust HTTP load test definitions
│   └── profiles/                    # Binary .prof output files
├── alembic.ini                      # Alembic configuration
├── docker-compose.yml               # Multi-service Docker Compose stack
├── Dockerfile                       # Multi-stage production container build
├── entrypoint.sh                    # Container entrypoint (DB wait + migrations)
├── pyproject.toml                   # Project metadata and dependencies
├── uv.lock                          # Locked dependency versions
├── .env                             # Environment variables (not committed)
├── .env.example                     # Template for environment variables
├── .gitignore                       # Git exclusion rules
└── .dockerignore                    # Docker build exclusion rules
```

### Layered Architecture

```
┌───────────────────────────────────────────────┐
│                   Client                      │
└──────────────────────┬────────────────────────┘
                       │  HTTP
┌──────────────────────▼────────────────────────┐
│              FastAPI Application              │
│  ┌─────────────────────────────────────────┐  │
│  │  Middleware (CORS, Request Logging)      │  │
│  ├─────────────────────────────────────────┤  │
│  │  Exception Handlers (SQLAlchemy, Global) │  │
│  ├─────────────────────────────────────────┤  │
│  │  API Routes (ticket.py, ai.py)          │  │
│  └─────────────────┬───────────────────────┘  │
│                    │                          │
│  ┌─────────────────▼───────────────────────┐  │
│  │  Service Layer                          │  │
│  │  (ticket_service, bedrock_services)     │  │
│  └─────────────────┬───────────────────────┘  │
│                    │                          │
│  ┌─────────────────▼───────────────────────┐  │
│  │  Repository Layer                       │  │
│  │  (ticket_repository.py)                 │  │
│  └─────────────────┬───────────────────────┘  │
│                    │                          │
│  ┌─────────────────▼───────────────────────┐  │
│  │  Database Layer (SQLAlchemy Async ORM)   │  │
│  │  PostgreSQL 17                          │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │  External: AWS Bedrock (AI)             │  │
│  └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

The application follows a strict **Repository Pattern** with clean separation of concerns:

1. **API Layer** (`app/api/`) — Route definitions, request validation, HTTP status codes.
2. **Service Layer** (`app/services/`) — Business logic, orchestration between repositories and external services.
3. **Repository Layer** (`app/repositories/`) — Database query abstraction using SQLAlchemy ORM.
4. **Schema Layer** (`app/schemas/`) — Pydantic models for request/response validation and serialization.
5. **Model Layer** (`app/models/`) — SQLAlchemy ORM table definitions.
6. **Core Layer** (`app/core/`) — Configuration, dependency injection.

---

## Prerequisites

- **Python** 3.13+
- **uv** (Python package manager) — [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker** and **Docker Compose**
- **PostgreSQL 17** (provided via Docker, or install locally)
- **AWS credentials** (optional — enable `AWS_DEMO_MODE=true` for offline use)

---

## Getting Started

### Local Development

```bash
# Clone the repository
git clone https://github.com/Diwakar0109/goml-python-day1.git
cd goml-python-day1

# Create environment file from template
cp .env.example .env
# Edit .env with your database credentials and AWS keys

# Install dependencies
uv sync

# Start PostgreSQL (via Docker or locally)
docker compose up db -d

# Run database migrations
uv run alembic upgrade head

# Start the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Docker Deployment

```bash
# Build and start all services (API + PostgreSQL + Adminer)
docker compose up --build -d

# Verify all containers are running
docker ps

# View application logs
docker logs -f t1_web
```

The entrypoint script automatically:
1. Polls the database until it accepts connections (up to 30 retries).
2. Runs `alembic upgrade head` to apply pending migrations.
3. Starts Uvicorn on port 8000.

---

## Environment Variables

Create a `.env` file based on `.env.example`:

| Variable               | Description                            | Default                                               |
| ---------------------- | -------------------------------------- | ----------------------------------------------------- |
| `APP_NAME`             | Application display name               | `t1`                                                  |
| `API_VERSION`          | API version string                     | `v1`                                                  |
| `DEBUG`                | Enable debug mode                      | `True`                                                |
| `POSTGRES_USER`        | PostgreSQL username                    | `postgres`                                            |
| `POSTGRES_PASSWORD`    | PostgreSQL password                    | `123`                                                 |
| `POSTGRES_DB`          | PostgreSQL database name               | `ai_service_desk`                                     |
| `DATABASE_URL`         | Async database connection string       | `postgresql+asyncpg://postgres:123@db:5432/ai_service_desk` |
| `SECRET_KEY`           | Application secret key                 | `my-secret-key`                                       |
| `AWS_ACCESS_KEY_ID`    | AWS access key for Bedrock             | —                                                     |
| `AWS_SECRET_ACCESS_KEY`| AWS secret key for Bedrock             | —                                                     |
| `AWS_REGION`           | AWS region for Bedrock                 | `us-east-1`                                           |
| `AWS_DEMO_MODE`        | Use fake AI service (no AWS needed)    | `false`                                               |
| `BEDROCK_MODEL_ID`     | Bedrock foundation model identifier    | —                                                     |

> **Note:** When running inside Docker, the database host is `db` (Docker service name). When running locally, the application auto-detects and falls back to `localhost`.

---

## Database

### Schema

The `tickets` table stores all support ticket data:

| Column           | Type                     | Constraints                                       |
| ---------------- | ------------------------ | ------------------------------------------------- |
| `id`             | `UUID`                   | Primary key, auto-generated (`uuid4`)             |
| `title`          | `VARCHAR(200)`           | Not null, 3–200 characters                        |
| `priority`       | `ENUM(low, medium, high)`| Default: `medium`                                 |
| `status`         | `ENUM(open, in_progress, resolved, closed)` | Default: `open`                  |
| `created_at`     | `TIMESTAMP WITH TZ`      | Server default: `now()`                           |
| `assignee_email` | `VARCHAR(255)`           | Nullable                                          |

### Migrations

Database schema migrations are managed with **Alembic**:

```bash
# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "description of change"

# Apply all pending migrations
uv run alembic upgrade head

# Rollback the last migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Visualization

The Docker Compose stack includes **Adminer**, a web-based database management tool:

1. Open `http://localhost:8080` in your browser.
2. Login with:
   - **System:** PostgreSQL
   - **Server:** `db`
   - **Username:** Value of `POSTGRES_USER`
   - **Password:** Value of `POSTGRES_PASSWORD`
   - **Database:** Value of `POSTGRES_DB`

---

## API Reference

### General Endpoints

#### `GET /` — Root Welcome

Returns the application name and API version.

```json
{
  "message": "Welcome to t1",
  "version": "v1"
}
```

#### `GET /health` — Health Check

Verifies API and database connectivity. Returns `503` if the database is unreachable.

```json
{
  "status": "healthy",
  "service": "t1",
  "version": "v1"
}
```

#### `GET /ready` — Readiness Probe

Confirms the database is ready to accept traffic.

```json
{
  "status": "ready"
}
```

---

### Ticket Endpoints

All ticket endpoints are prefixed with `/tickets`.

#### `POST /tickets/` — Create Ticket

**Request Body:**

```json
{
  "title": "Database connection timeout",
  "priority": "high",
  "assignee_email": "admin@example.com"
}
```

**Response** (`201 Created`):

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Database connection timeout",
  "priority": "high",
  "status": "open",
  "created_at": "2026-07-24T11:30:00Z",
  "assignee_email": "admin@example.com",
  "is_resolved": false
}
```

#### `GET /tickets/` — List Tickets

| Query Parameter | Type   | Description                                     | Default |
| --------------- | ------ | ----------------------------------------------- | ------- |
| `status`        | string | Filter by status (`open`, `in_progress`, `resolved`, `closed`) | —       |
| `priority`      | string | Filter by priority (`low`, `medium`, `high`)    | —       |
| `skip`          | int    | Number of records to skip                       | `0`     |
| `limit`         | int    | Maximum records to return (1–100)               | `50`    |

**Example:**

```
GET /tickets/?status=open&priority=high&skip=0&limit=10
```

#### `GET /tickets/{ticket_id}` — Get Ticket

Returns a single ticket by UUID. Returns `404` if not found.

#### `PUT /tickets/{ticket_id}` — Update Ticket

**Request Body** (all fields optional):

```json
{
  "title": "Updated title",
  "priority": "medium",
  "status": "in_progress",
  "assignee_email": "dev@example.com"
}
```

#### `DELETE /tickets/{ticket_id}` — Delete Ticket

Returns `200` on success with confirmation message. Returns `404` if not found.

```json
{
  "message": "Ticket deleted successfully"
}
```

---

### AI Endpoints

#### `POST /ai/summarize` — Summarize Ticket

Generates an AI-powered summary and suggested response using Amazon Bedrock.

**Request Body:**

```json
{
  "ticket_description": "The database is crashing periodically under high load. We need to investigate connection pooling and index optimization."
}
```

**Response:**

```json
{
  "summary": "Database stability issue under high load requiring connection pool and index investigation.",
  "suggested_response": "We acknowledge the database instability under high load conditions. Our team is investigating connection pooling configuration and index optimization."
}
```

> **Demo Mode:** When `AWS_DEMO_MODE=true`, a deterministic `FakeBedrockService` returns template responses without making AWS API calls.

---

## Testing

### Running Tests

```bash
# Run all 30 tests with coverage
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_schemas.py

# Run specific test by name
uv run pytest -k "test_create_ticket"
```

### Test Structure

The test suite is organized into three categories:

| File                | Category                | Count | Description                                          |
| ------------------- | ----------------------- | ----- | ---------------------------------------------------- |
| `test_schemas.py`   | Unit Tests              | 14    | Pydantic schema validation (field constraints, enums, computed fields) |
| `test_services.py`  | Unit Tests              | 6     | Service layer logic with mocked repositories         |
| `test_routes.py`    | Integration & E2E Tests | 10    | Full HTTP request lifecycle against live database     |

**Total: 30 tests** (20 unit + 10 integration/E2E)

**Test Fixtures** (`conftest.py`):

- `clear_tickets` — Truncates the tickets table before each test (autouse).
- `mock_repo` — Provides an `AsyncMock` repository for isolated unit testing.
- `existing_ticket_id` — Creates a ticket and returns its UUID for integration tests.

### Code Coverage

Coverage is automatically collected when running `pytest` (configured in `pyproject.toml`):

```ini
[tool.pytest.ini_options]
addopts = "--cov=app --cov-report=term-missing --cov-report=html"
```

- **Terminal report** — Displays coverage percentage and missed lines after each run.
- **HTML report** — Generated at `htmlcov/index.html` for interactive browsing.
- **Current coverage:** **79%**

---

## Performance Profiling

### cProfile

CPU profiling is performed using Python's built-in `cProfile` module:

```bash
# Run the profiling script
uv run python tests/profile_cprofile.py
```

This profiles four endpoint flows:
1. `GET /` — Root endpoint (50 iterations)
2. `GET /health` — Health check (50 iterations)
3. `GET /ready` — Readiness check (50 iterations)
4. Full CRUD flow — Create → Get → Delete → List (20 iterations)

Binary `.prof` files are saved to `tests/profiles/` and can be visualized with **SnakeViz**:

```bash
uv run snakeviz tests/profiles/tickets_crud_flow.prof
```

### Locust Load Testing

HTTP load testing is defined in `tests/locustfile.py` with weighted task distribution:

| Task                  | Weight | Description                                 |
| --------------------- | ------ | ------------------------------------------- |
| `list_tickets`        | 5      | List all tickets                            |
| `check_health`        | 4      | Health check probe                          |
| `check_ready`         | 4      | Readiness probe                             |
| `create_ticket`       | 3      | Create ticket with random data              |
| `get_ticket_details`  | 3      | Get individual ticket details               |
| `update_ticket`       | 2      | Update ticket attributes                    |
| `summarize_ticket`    | 2      | AI summarization endpoint                   |
| `check_root`          | 2      | Root endpoint                               |
| `delete_ticket`       | 1      | Delete a ticket                             |

```bash
# Start Locust web UI (http://localhost:8089)
uv run locust -f tests/locustfile.py --host=http://localhost:8000

# Run headless with 50 users and spawn rate of 10/s for 60 seconds
uv run locust -f tests/locustfile.py --host=http://localhost:8000 \
  --users 50 --spawn-rate 10 --run-time 60s --headless
```

---

## Prompt Templates

AI prompts are externalized into `app/services/prompt_templates.yaml` for easy versioning and modification without code changes:

```yaml
ticket_summary_v1:
  name: "ticket_summary"
  version: "1.0.0"
  template: >-
    Return only valid JSON with keys summary and suggested_response.
    Summarize the following support ticket and suggest a concise,
    professional response. Ticket: {ticket_description}
```

Templates are loaded at module import via `load_prompt_template()` and rendered at runtime with Python's `str.format()`:

```python
from app.services.prompt_templates import TICKET_SUMMARY_V1

rendered = TICKET_SUMMARY_V1.render(ticket_description="User cannot login...")
```

---

## Docker Services

The `docker-compose.yml` defines three services:

| Service   | Image                | Container   | Port  | Description                              |
| --------- | -------------------- | ----------- | ----- | ---------------------------------------- |
| `db`      | `postgres:17-alpine` | `t1_db`     | 5432  | PostgreSQL database with health checks   |
| `web`     | `t1-web` (built)     | `t1_web`    | 8000  | FastAPI application server               |
| `db-ui`   | `adminer:latest`     | `t1_db_ui`  | 8080  | Web-based database management interface  |

**Docker Commands:**

```bash
# Start full stack
docker compose up --build -d

# Stop all services
docker compose down

# Full cleanup (remove images, volumes, and containers)
docker compose down --rmi all --volumes

# View logs
docker logs -f t1_web

# Check container status
docker ps
```

**Dockerfile Highlights:**

- Uses `python:3.13-slim` base image.
- Copies `uv` binary from `ghcr.io/astral-sh/uv:latest` for fast dependency installation.
- Runs as non-root `appuser` for security.
- Dependency layer caching — `pyproject.toml` and `uv.lock` copied before application code.
- Production-only dependencies installed with `--no-dev`.

---

## API Documentation

FastAPI auto-generates interactive API documentation:

| Documentation    | URL                              |
| ---------------- | -------------------------------- |
| **Swagger UI**   | `http://localhost:8000/docs`     |
| **ReDoc**        | `http://localhost:8000/redoc`    |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` |

---

## License

This project is developed as part of the GOML Python training program.
