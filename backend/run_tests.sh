#!/bin/bash
# Run tests for AI Council Backend

echo "Running tests..."

# Run all tests with coverage
poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term

echo ""
echo "Coverage report generated in htmlcov/index.html"
