# AI Council Backend

FastAPI backend for the AI Council web application.

## Setup

1. Install Poetry:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry install
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

4. Run database migrations:
```bash
poetry run alembic upgrade head
```

5. Start the development server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core configuration and utilities
│   ├── models/       # SQLAlchemy database models
│   ├── services/     # Business logic and services
│   └── main.py       # FastAPI application entry point
├── alembic/          # Database migrations
├── tests/            # Test files
├── pyproject.toml    # Poetry dependencies
└── .env.example      # Environment variables template
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Testing

Run tests:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=app --cov-report=html
```
