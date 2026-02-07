#!/bin/bash
# Setup script for AI Council Backend

echo "Setting up AI Council Backend..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your database and API credentials"
echo "2. Run database migrations: poetry run alembic upgrade head"
echo "3. Start the server: poetry run uvicorn app.main:app --reload"
