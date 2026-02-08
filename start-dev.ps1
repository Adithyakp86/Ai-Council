#!/usr/bin/env pwsh
# Development Server Startup Script

Write-Host "🚀 Starting AI Council Development Servers..." -ForegroundColor Cyan
Write-Host ""

# Check if backend dependencies are installed
Write-Host "📦 Checking backend dependencies..." -ForegroundColor Yellow
Push-Location backend
if (-not (Test-Path "poetry.lock")) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    poetry install
}
Pop-Location

# Check if frontend dependencies are installed  
Write-Host "📦 Checking frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}
Pop-Location

Write-Host ""
Write-Host "✅ Dependencies ready!" -ForegroundColor Green
Write-Host ""

# Start backend server
Write-Host "🔧 Starting Backend Server (FastAPI)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Start frontend server
Write-Host "⚛️  Starting Frontend Server (Next.js)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "✅ Servers starting..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "📍 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop the servers" -ForegroundColor Yellow
