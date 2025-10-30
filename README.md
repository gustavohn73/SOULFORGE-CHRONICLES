# Soulforge Chronicles

**Roguelike multiplayer com narrativa emergente gerada por IA**

Um jogo onde suas escolhas moldam sua alma. Cada ação violenta, cada decisão moral, cada momento de curiosidade deixa uma marca permanente que afeta suas habilidades e destino. Quando a estabilidade do mundo chega a zero, uma IA decide como o loop temporal termina.

## Características

- **Multiplayer Assíncrono**: 2-10 jogadores no mesmo mundo persistente
- **Sistema de Marcas**: 4 marcas que evoluem baseado em suas ações
  - VIOLÊNCIA: Combate e destruição
  - CONTROLE: Ordem vs Caos
  - CURIOSIDADE: Exploração e descobertas
  - MEMÓRIA: Retenção de loops anteriores
- **Fog of War**: Cada jogador vê apenas sua área
- **IA como Mestre**: GM analisa ações e gera eventos narrativos
- **Loop Temporal**: Mundo reseta, mas marcas persistem
- **Geração Procedural**: Dungeons, NPCs e eventos únicos

## Instalação Rápida

### Usando Docker (Recomendado)

```bash
# Clonar repositório
git clone https://github.com/gustavohn73/soulforge-chronicles.git
cd soulforge-chronicles

# Setup automático
chmod +x scripts/setup.sh
./scripts/setup.sh

# Rodar com Docker
docker-compose up
```

Acesse: **http://localhost:8080**

### Instalação Manual

Veja [INSTALLATION.md](docs/INSTALLATION.md) para instruções detalhadas.

## Tecnologias

### Frontend
- **Phaser.js 3**: Engine de jogo 2D
- **ROT.js**: Toolkit roguelike (geração procedural, pathfinding)
- **Socket.IO Client**: Comunicação real-time

### Backend
- **Python 3.11+**: Servidor principal
- **Flask + Flask-SocketIO**: API e websockets
- **MongoDB**: Banco de dados persistente
- **TCOD**: Algoritmos roguelike (FOV, pathfinding)

### IA
- **Claude/Gemini**: GM Master (análise de loops, eventos)
- **Ollama + Llama3**: NPCs locais (diálogos, comportamentos)

## Arquitetura

```
Cliente (Phaser.js)          Servidor (Python)              IA
     │                             │                         │
     ├── Renderiza tiles           ├── Game Loop (20 TPS)    ├── GM Master
     ├── Input do jogador          ├── Sistemas:             │   └── Análise de ações
     ├── Predição local            │   ├── Combat            │   └── Geração de eventos
     └── Socket.IO ─────────────→  │   ├── Movement          │
                                   │   ├── Marks             └── Ollama (Local)
                                   │   ├── FOV                   └── Diálogo NPCs
                                   │   └── Events
                                   ├── MongoDB
                                   └── State Sync
```

## Como Jogar

1. **Crie uma Conta**: Nome de usuário único
2. **Entre no Loop**: Mundo compartilhado com outros jogadores
3. **Explore**: Use WASD ou clique para mover
4. **Combate**: Clique em inimigos para atacar
5. **Observe suas Marcas**: Cada ação afeta sua alma
6. **Sobreviva ao Countdown**: Quando chegar a zero, o GM decide seu destino

### Controles

- **WASD / Setas**: Movimento
- **Mouse Click**: Atacar / Interagir
- **E**: Usar item
- **I**: Inventário
- **C**: Crafting
- **Tab**: Chat

## Sistema de Marcas

Suas ações mudam quem você é:

| Marca | Aumenta com | Efeitos Positivos | Efeitos Negativos |
|-------|-------------|-------------------|-------------------|
| **VIOLÊNCIA** | Matar, destruir | +Dano, +Crit | Mercadores fogem, NPCs hostis |
| **CONTROLE** | Planejar, organizar | +Defesa, Dano consistente | Menos loot, NPCs desconfiam |
| **CURIOSIDADE** | Explorar, abrir baús | +Visão, Encontra segredos | Armadilhas, NPCs te testam |
| **MEMÓRIA** | Loops completados | Lembra mapas, Skills especiais | Sanidade diminui |

Marcas extremas (>80 ou <-80) desbloqueiam **habilidades únicas**.

## Desenvolvimento

### Estrutura do Projeto

```
soulforge-chronicles/
├── client/          # Frontend Phaser.js
├── server/          # Backend Python
├── docs/            # Documentação
├── ai-configs/      # Prompts para IAs
└── scripts/         # Utilitários
```

### Rodar em Desenvolvimento

```bash
# Terminal 1: Servidor
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Terminal 2: Cliente
cd client
npm install
npm run dev

# Terminal 3: MongoDB
mongod --dbpath ./data/db

# Terminal 4: Ollama (opcional)
ollama serve
ollama pull llama3
```

### Testes

```bash
# Testes do servidor
cd server
pytest

# Testes do cliente
cd client
npm test
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Roadmap

### v0.1.0 - MVP (Atual)
- [x] Movimento multiplayer
- [x] Combate básico
- [x] Sistema de marcas
- [x] Fog of War
- [x] Geração procedural

### v0.2.0 - IA Narrativa
- [ ] GM Master funcional
- [ ] NPCs com diálogos gerados
- [ ] Eventos dinâmicos
- [ ] Finais múltiplos por loop

### v0.3.0 - Conteúdo
- [ ] 10+ tipos de inimigos
- [ ] Sistema de crafting completo
- [ ] Skills desbloqueáveis
- [ ] Boss fights

### v1.0.0 - Lançamento
- [ ] Balanceamento completo
- [ ] Tutorial interativo
- [ ] Achievements
- [ ] Leaderboards

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Créditos

Inspirado em mecânicas de:
- Shattered Pixel Dungeon (combate, FOV)
- Cataclysm: DDA (overworld)
- Tales of Maj'Eyal (skill trees)
- AI Dungeon (narrativa gerada)
- Cultist Simulator (timers)

## Contato

- **Issues**: https://github.com/gustavohn73/soulforge-chronicles/issues
- **Discord**: [Em breve]

---

**"Cada escolha forja sua alma. Cada loop revela seu destino."**
