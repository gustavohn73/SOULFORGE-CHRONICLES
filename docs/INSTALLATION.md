# Guia de Instalação - Soulforge Chronicles

Este guia cobre todas as formas de instalar e rodar o jogo.

## Requisitos do Sistema

### Mínimos
- **OS**: Linux, macOS, Windows 10+
- **RAM**: 4GB
- **Espaço em disco**: 2GB
- **Navegador**: Chrome 90+, Firefox 88+, Safari 14+

### Recomendados
- **RAM**: 8GB+ (para rodar IA local)
- **GPU**: Não necessário, mas melhora renderização

## Método 1: Docker (Mais Fácil)

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado

### Passos

```bash
# 1. Clonar repositório
git clone https://github.com/gustavohn73/soulforge-chronicles.git
cd soulforge-chronicles

# 2. (Opcional) Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com seu editor favorito
# Adicionar AI_MASTER_API_KEY se quiser usar Claude/Gemini

# 3. Rodar setup automático
chmod +x scripts/setup.sh
./scripts/setup.sh

# 4. Iniciar todos os serviços
docker-compose up -d

# 5. Aguardar inicialização (30-60 segundos)
docker-compose logs -f server

# Quando ver "Soulforge Chronicles Server Running", está pronto!
```

### Acessar o Jogo

Abra seu navegador em: **http://localhost:8080**

### Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Rebuild após mudanças no código
docker-compose up --build

# Limpar tudo (remove banco de dados!)
docker-compose down -v
```

## Método 2: Instalação Manual

### Pré-requisitos

1. **Python 3.11+**
   ```bash
   python3 --version  # Deve mostrar 3.11 ou superior
   ```

2. **Node.js 18+**
   ```bash
   node --version  # Deve mostrar v18 ou superior
   npm --version
   ```

3. **MongoDB 7+**
   - [Instalar MongoDB Community](https://www.mongodb.com/docs/manual/installation/)

4. **(Opcional) Ollama**
   - [Instalar Ollama](https://ollama.ai/download)

### Passo 1: Clonar Repositório

```bash
git clone https://github.com/gustavohn73/soulforge-chronicles.git
cd soulforge-chronicles
```

### Passo 2: Configurar Servidor Python

```bash
cd server

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No Linux/macOS:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo de configuração
cp .env.example .env

# Editar .env (opcional)
nano .env
```

**Configuração mínima do `.env`:**
```env
MONGODB_URI=mongodb://localhost:27017/soulforge
SECRET_KEY=seu-secret-key-aqui-mude-em-producao
DEBUG=True
PORT=5000

# Opcional: IA externa
AI_MASTER_PROVIDER=claude
AI_MASTER_API_KEY=sua-api-key-aqui

# Opcional: IA local
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Passo 3: Configurar Cliente

```bash
# Voltar para raiz e entrar no client
cd ../client

# Instalar dependências
npm install

# Criar arquivo de configuração
echo "SERVER_URL=http://localhost:5000" > .env.local
```

### Passo 4: Iniciar MongoDB

**Opção A: Serviço do sistema**
```bash
# Linux (systemd)
sudo systemctl start mongod

# macOS (Homebrew)
brew services start mongodb-community
```

**Opção B: Manual**
```bash
# Criar diretório de dados
mkdir -p data/db

# Rodar MongoDB
mongod --dbpath ./data/db
```

Verificar se está rodando:
```bash
mongosh --eval "db.version()"
```

### Passo 5: (Opcional) Iniciar Ollama

```bash
# Iniciar servidor Ollama
ollama serve

# Em outro terminal, baixar modelo
ollama pull llama3
```

### Passo 6: Iniciar Servidor Python

```bash
cd server
source venv/bin/activate  # Ativar venv se não estiver ativo
python main.py
```

Você deve ver:
```
 * Running on http://0.0.0.0:5000
 * Soulforge Chronicles Server Running
```

### Passo 7: Iniciar Cliente

```bash
# Em outro terminal
cd client
npm run dev
```

Você deve ver:
```
Server running at http://localhost:8080
```

### Passo 8: Acessar o Jogo

Abra seu navegador em: **http://localhost:8080**

## Método 3: Desenvolvimento (Hot Reload)

Para desenvolvimento com hot reload automático:

### Terminal 1: MongoDB
```bash
mongod --dbpath ./data/db
```

### Terminal 2: Ollama (Opcional)
```bash
ollama serve
```

### Terminal 3: Servidor Python com Reload
```bash
cd server
source venv/bin/activate
export FLASK_ENV=development
python main.py
# Servidor recarrega automaticamente ao mudar .py files
```

### Terminal 4: Cliente com Webpack Dev Server
```bash
cd client
npm run dev
# Cliente recarrega automaticamente ao mudar .js files
```

## Configuração de IA

### Usar Claude (Recomendado para qualidade)

1. Obter API Key em: https://console.anthropic.com/
2. Adicionar ao `.env`:
   ```env
   AI_MASTER_PROVIDER=claude
   AI_MASTER_API_KEY=sk-ant-api03-xxx
   ```

### Usar Gemini (Alternativa gratuita)

1. Obter API Key em: https://makersuite.google.com/app/apikey
2. Adicionar ao `.env`:
   ```env
   AI_MASTER_PROVIDER=gemini
   AI_MASTER_API_KEY=AIzaSyxxx
   ```

### Usar Ollama (Local, sem internet)

1. Instalar Ollama: https://ollama.ai/download
2. Baixar modelo:
   ```bash
   ollama pull llama3
   ```
3. Configurar `.env`:
   ```env
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

**Nota**: Ollama é usado apenas para diálogos de NPCs. GM Master requer Claude ou Gemini.

## Seed do Banco de Dados

Para popular o banco com dados iniciais:

```bash
cd server
python scripts/seed_database.py
```

Isso cria:
- Itens base (espadas, poções, etc)
- Bestiário (tipos de inimigos)
- Facções
- Templates de NPCs

## Troubleshooting

### Erro: "Connection refused" ao conectar MongoDB

**Solução**: Verificar se MongoDB está rodando
```bash
sudo systemctl status mongod
# ou
ps aux | grep mongod
```

### Erro: "Module not found" no Python

**Solução**: Reinstalar dependências
```bash
cd server
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Erro: "EADDRINUSE" no cliente

**Solução**: Porta 8080 em uso. Mudar porta:
```bash
# client/package.json, mudar script:
"dev": "webpack serve --port 8081"
```

### Cliente não conecta ao servidor

**Solução**: Verificar CORS e URL
1. Abrir DevTools (F12)
2. Ver console para erros
3. Verificar se `SERVER_URL` em `.env.local` está correto

### Performance ruim

**Soluções**:
1. Desabilitar IA local (usar só IA externa)
2. Reduzir `TICK_RATE` em `server/config.py`
3. Usar Docker ao invés de manual

### Ollama não responde

**Solução**: Verificar memória RAM
```bash
# Ollama precisa de ~4GB RAM
free -h
```

Se RAM insuficiente, usar modelo menor:
```bash
ollama pull llama3:8b-instruct-q4_0  # Versão quantizada
```

## Testes

### Testar Servidor

```bash
cd server
pytest
```

### Testar Cliente

```bash
cd client
npm test
```

### Teste de Integração (2 Players)

1. Abrir http://localhost:8080 em aba 1
2. Criar conta "Alice"
3. Abrir http://localhost:8080 em aba 2 (janela anônima)
4. Criar conta "Bob"
5. Ambos devem se ver movendo em tempo real

## Próximos Passos

Após instalação bem-sucedida:

1. Ler [GAME_DESIGN.md](GAME_DESIGN.md) para entender mecânicas
2. Ler [ARCHITECTURE.md](ARCHITECTURE.md) para entender código
3. Ver [API_REFERENCE.md](API_REFERENCE.md) para endpoints

## Suporte

- **Issues**: https://github.com/gustavohn73/soulforge-chronicles/issues
- **Discord**: [Em breve]
