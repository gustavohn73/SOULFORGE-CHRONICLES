#!/bin/bash

echo "========================================="
echo "Soulforge Chronicles - Setup Script"
echo "========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# MongoDB
MONGODB_URI=mongodb://mongodb:27017/soulforge

# AI Configuration (optional)
AI_MASTER_PROVIDER=none
AI_MASTER_API_KEY=

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3

# Server
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=True
PORT=5000

# Game Settings
TICK_RATE=20
MAX_PLAYERS_PER_LOOP=10
EOF
    echo "✓ Created .env file"
else
    echo "✓ .env file already exists"
fi

# Create data directory
mkdir -p data/db
echo "✓ Created data directories"

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "To start the game:"
echo "  docker-compose up"
echo ""
echo "Then open your browser at:"
echo "  http://localhost:8080"
echo ""
echo "========================================="
