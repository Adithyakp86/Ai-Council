# Testing Guide

This document explains how to run tests for the AI Council backend.

## Prerequisites

1. **Install Poetry** (if not already installed):
   ```bash
   # Linux/macOS
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

## Running Tests

### Run All Tests
```bash
poetry run pytest tests/ -v
```

### Run Specific Test File
```bash
poetry run pytest tests/test_database_schema.py -v
```

### Run Property-Based Tests
```bash
poetry run pytest tests/test_database_schema.py -v
```

### Run with Coverage
```bash
poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term
```

The coverage report will be generated in `htmlcov/index.html`.

## Property-Based Tests

The project uses Hypothesis for property-based testing. These tests generate random test cases to verify properties hold across many inputs.

### Database Schema Tests

**File**: `tests/test_database_schema.py`

**Properties Tested**:
1. **Database Foreign Key Integrity** (Requirements 13.4, 13.5)
   - Deleting a user cascades to delete all their requests and responses
   - Deleting a request cascades to delete its response and subtasks

**Running Property Tests**:
```bash
poetry run pytest tests/test_database_schema.py::test_cascade_delete_user_deletes_requests_and_responses -v
poetry run pytest tests/test_database_schema.py::test_cascade_delete_request_deletes_subtasks -v
poetry run pytest tests/test_database_schema.py::test_cascade_delete_integration -v
```

## Test Configuration

Tests use an in-memory SQLite database for speed and isolation. The configuration is in `tests/conftest.py`.

## Continuous Integration

Tests should be run in CI/CD pipelines before deployment:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    poetry install
    poetry run pytest tests/ -v --cov=app
```

## Troubleshooting

### Poetry not found
Make sure Poetry is installed and in your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Import errors
Make sure you're running tests through Poetry:
```bash
poetry run pytest tests/
```

### Database errors
Tests use in-memory SQLite, so no database setup is required. If you see database errors, check that SQLAlchemy models are properly imported in `conftest.py`.
