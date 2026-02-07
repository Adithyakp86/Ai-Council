# Setup script for AI Council Backend (PowerShell)

Write-Host "Setting up AI Council Backend..." -ForegroundColor Green

# Check if Poetry is installed
$poetryInstalled = Get-Command poetry -ErrorAction SilentlyContinue
if (-not $poetryInstalled) {
    Write-Host "Poetry not found. Please install Poetry first:" -ForegroundColor Yellow
    Write-Host "Visit: https://python-poetry.org/docs/#installation" -ForegroundColor Yellow
    Write-Host "Or run: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" -ForegroundColor Cyan
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
poetry install

# Copy environment file
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Green
    Copy-Item .env.example .env
    Write-Host "Please update .env with your configuration" -ForegroundColor Yellow
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env with your database and API credentials"
Write-Host "2. Run database migrations: poetry run alembic upgrade head"
Write-Host "3. Start the server: poetry run uvicorn app.main:app --reload"
