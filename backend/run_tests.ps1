# Run tests for AI Council Backend (PowerShell)

Write-Host "Running tests..." -ForegroundColor Green

# Run all tests with coverage
poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term

Write-Host ""
Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
