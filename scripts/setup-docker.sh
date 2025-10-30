#!/bin/bash

echo "🎮 Soulforge Chronicles - Docker Setup"
echo "======================================"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale: https://docker.com"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado"
    exit 1
fi

echo "✅ Docker detectado"

# Criar arquivos .env se não existirem
if [ ! -f server/.env ]; then
    echo "📝 Criando server/.env..."
    cat > server/.env <<EOF
# MongoDB
MONGODB_URI=mongodb://mongodb:27017/soulforge

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3

# AI Configuration
AI_MASTER_PROVIDER=none
AI_MASTER_API_KEY=

# Server
SECRET_KEY=dev-secret-key-change-me
DEBUG=True
PORT=5000
HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/soulforge.log
EOF
fi

if [ ! -f .env ]; then
    echo "📝 Criando .env raiz..."
    cat > .env <<EOF
AI_MASTER_API_KEY=
SECRET_KEY=dev-secret-key-change-me
EOF
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Build e iniciar containers
echo "🏗️  Building containers..."
docker-compose build || docker compose build

echo "🚀 Starting services..."
docker-compose up -d || docker compose up -d

# Aguardar MongoDB ficar pronto
echo "⏳ Aguardando MongoDB..."
sleep 10

# Verificar status dos serviços
echo ""
echo "📊 Status dos serviços:"
docker-compose ps || docker compose ps

# Download modelo Ollama (opcional, comentado por enquanto pois demora muito)
# echo "📥 Baixando modelo Ollama (pode demorar)..."
# docker exec soulforge-ollama ollama pull llama3 2>/dev/null || echo "⚠️  Ollama pull falhou (continuando...)"

echo ""
echo "✅ Setup completo!"
echo "🌐 Cliente: http://localhost:8080"
echo "🔌 Server: http://localhost:5000"
echo "🔌 Health: http://localhost:5000/health"
echo "📊 MongoDB: localhost:27017"
echo ""
echo "Comandos úteis:"
echo "  - Ver logs server: docker-compose logs -f server"
echo "  - Ver logs client: docker-compose logs -f client"
echo "  - Ver todos logs: docker-compose logs -f"
echo "  - Parar: docker-compose down"
echo "  - Rebuild: docker-compose up --build -d"
echo "  - Restart: docker-compose restart"
