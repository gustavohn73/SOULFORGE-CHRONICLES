# Arquitetura - Soulforge Chronicles

Este documento descreve a arquitetura técnica do jogo.

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENTE (Phaser.js)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Scenes     │  │   Systems    │  │    Network           │  │
│  │ - Boot       │  │ - Combat     │  │  - SocketManager     │  │
│  │ - Menu       │  │ - Movement   │  │  - Prediction        │  │
│  │ - Game       │  │ - MapGen     │  │  - Reconciliation    │  │
│  │ - UI         │  │ - FOV        │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │ Socket.IO (WebSocket)
                               │ - player_move
                               │ - player_attack
                               │ - state_update
┌──────────────────────────────┴───────────────────────────────────┐
│                       SERVIDOR (Python + Flask)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Game Server                            │   │
│  │  - Connection Manager                                     │   │
│  │  - Socket.IO Event Handlers                               │   │
│  │  - Session Management                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Game Loop (20 TPS)                     │   │
│  │  - Process Input Queue                                    │   │
│  │  - Update Game State                                      │   │
│  │  - Broadcast State to Clients                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Models     │  │   Systems    │  │    AI                │  │
│  │ - Player     │  │ - Combat     │  │  - GM Master         │  │
│  │ - NPC        │  │ - Movement   │  │    (Claude/Gemini)   │  │
│  │ - World      │  │ - Marks      │  │  - Local AI          │  │
│  │ - Loop       │  │ - FOV        │  │    (Ollama)          │  │
│  │ - Event      │  │ - Items      │  │  - Prompts           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
         ┌──────┴────────┐          ┌────────┴────────┐
         │   MongoDB      │          │    Ollama       │
         │  - players     │          │  - llama3       │
         │  - worlds      │          │  - NPC dialogue │
         │  - npcs        │          └─────────────────┘
         │  - events      │
         └────────────────┘
```

## Camadas

### 1. Cliente (Frontend)

**Tecnologia**: Phaser.js 3 + ROT.js + Socket.IO Client

#### Estrutura de Diretórios

```
client/src/
├── main.js                  # Entry point
├── config.js                # Configurações do Phaser
├── scenes/                  # Cenas do jogo
│   ├── BootScene.js         # Carregamento de assets
│   ├── MenuScene.js         # Menu principal
│   ├── GameScene.js         # Loop principal do jogo
│   └── UIScene.js           # HUD overlay
├── entities/                # Classes de entidades
│   ├── Player.js
│   ├── Enemy.js
│   └── NPC.js
├── systems/                 # Sistemas do cliente
│   ├── CombatSystem.js      # Lógica de combate client-side
│   ├── MovementSystem.js    # Predição de movimento
│   ├── FOVSystem.js         # Cálculo de field of view
│   └── MapGenerator.js      # Geração procedural (ROT.js)
├── ui/                      # Componentes de UI
│   ├── HUD.js               # HP, marcas, countdown
│   ├── ChatBox.js           # Chat multiplayer
│   ├── MarksDisplay.js      # Visualização das 4 marcas
│   └── Countdown.js         # Timer do loop
├── network/
│   └── SocketManager.js     # Gerenciamento de conexão
└── utils/
    ├── Constants.js         # Constantes globais
    └── Helpers.js           # Funções auxiliares
```

#### Responsabilidades

1. **Renderização**: Desenhar tiles, entidades, UI
2. **Input**: Capturar clique/teclado, enviar para servidor
3. **Predição**: Simular movimento local antes da confirmação do servidor
4. **Reconciliação**: Corrigir posição quando servidor discorda
5. **FOV**: Calcular o que jogador pode ver (sombras)

#### Fluxo de Input

```
Usuário clica tile (5, 10)
    ↓
MovementSystem.requestMove(5, 10)
    ↓
Predição: Move sprite localmente
    ↓
SocketManager.emit('player_move', {x: 5, y: 10})
    ↓
Aguarda confirmação do servidor
    ↓
Se posição != esperada → Reconcilia (teleporta para posição correta)
```

### 2. Servidor (Backend)

**Tecnologia**: Python 3.11 + Flask + Flask-SocketIO + MongoDB

#### Estrutura de Diretórios

```
server/app/
├── __init__.py
├── game_server.py           # Socket.IO handlers
├── game_loop.py             # Loop principal (20 TPS)
├── models/                  # Data models
│   ├── player.py            # Player entity
│   ├── npc.py               # NPC entity
│   ├── world.py             # World state
│   ├── loop.py              # Loop temporal
│   └── event.py             # Evento dinâmico
├── systems/                 # Game systems
│   ├── combat.py            # Combate (baseado em SPD)
│   ├── movement.py          # Validação de movimento
│   ├── marks.py             # Sistema de marcas
│   ├── fog_of_war.py        # FOV server-side
│   ├── items.py             # Items e inventário
│   ├── events.py            # Eventos dinâmicos
│   ├── crafting.py          # Crafting (baseado em URW)
│   ├── needs.py             # Fome/sede/cansaço
│   ├── skill_tree.py        # Habilidades (baseado em ToME)
│   └── environment.py       # Clima/tempo (baseado em CDDA)
├── ai/                      # IA systems
│   ├── gm_master.py         # GM Master (Claude/Gemini)
│   ├── local_ai.py          # Ollama integration
│   ├── prompts.py           # Prompt templates
│   └── log_aggregator.py    # Agrega ações para análise
├── database/
│   ├── db_manager.py        # MongoDB wrapper
│   └── schemas.py           # Document schemas
└── utils/
    ├── pathfinding.py       # A* (tcod)
    ├── dungeon_gen.py       # Dungeon generation (tcod)
    └── validators.py        # Input validation
```

#### Game Loop (20 Ticks/Segundo)

```python
while True:
    start_time = time.time()

    # 1. Processar input queue
    for event in input_queue:
        process_event(event)

    # 2. Update NPCs
    for npc in active_npcs:
        npc.update(delta_time)

    # 3. Update sistemas
    combat_system.update()
    marks_system.update()
    events_system.update()

    # 4. Atualizar countdown
    world.stability -= 0.05  # ~5 pontos por segundo

    # 5. Broadcast state
    for player in active_players:
        state = get_state_for_player(player)  # Apenas o que ele vê (FOV)
        socketio.emit('state_update', state, room=player.socket_id)

    # 6. Dormir até próximo tick
    elapsed = time.time() - start_time
    sleep(max(0, 0.05 - elapsed))  # 50ms = 20 TPS
```

#### Sistemas

##### Combat System (inspirado em Shattered Pixel Dungeon)

```python
def calculate_damage(attacker, defender, context):
    # Damage roll (arma + nível)
    base_damage = random.randint(
        weapon_min + level_bonus,
        weapon_max + level_bonus * 1.5
    )

    # Modificador de marcas
    if attacker.marks['VIOLENCIA'] > 50:
        base_damage *= 1.0 + (attacker.marks['VIOLENCIA'] - 50) / 200

    # Crítico
    if random.random() < crit_chance:
        base_damage *= 2

    # Surpresa (se defensor não vê atacante)
    if context.get('is_surprise'):
        base_damage *= 1.5

    # Defesa
    defense = random.randint(0, defender.armor + defender.evasion)

    return max(1, base_damage - defense)
```

##### Marks System

```python
class MarksSystem:
    def register_action(self, player, action_type, context):
        if action_type == 'kill':
            player.marks['VIOLENCIA'] += 5
            if context['target_type'] == 'innocent':
                player.marks['VIOLENCIA'] += 10  # Bonus por matar inocente

        elif action_type == 'explore_new_area':
            player.marks['CURIOSIDADE'] += 2

        elif action_type == 'craft':
            player.marks['CONTROLE'] += 1

        # Checar se desbloqueou skill
        self.check_skill_unlock(player)
```

##### Fog of War System (usando TCOD)

```python
import tcod

def calculate_fov(player):
    # Criar mapa de transparência
    fov_map = tcod.map.Map(width=MAP_WIDTH, height=MAP_HEIGHT)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile = world.get_tile(x, y)
            fov_map.transparent[y][x] = tile.transparent

    # Calcular FOV
    radius = player.vision_range + player.marks['CURIOSIDADE'] // 20
    fov_map.compute_fov(player.x, player.y, radius, algorithm=tcod.FOV_SHADOW)

    return fov_map.fov  # Boolean array
```

### 3. Comunicação Cliente-Servidor

#### Protocolo Socket.IO

**Cliente → Servidor:**

| Evento | Payload | Descrição |
|--------|---------|-----------|
| `connect` | `{username, token}` | Autenticação inicial |
| `player_move` | `{x, y}` | Requisição de movimento |
| `player_attack` | `{target_id}` | Atacar entidade |
| `player_use_item` | `{item_id, target}` | Usar item |
| `player_craft` | `{recipe_id}` | Iniciar crafting |
| `chat_message` | `{message}` | Enviar mensagem |

**Servidor → Cliente:**

| Evento | Payload | Descrição |
|--------|---------|-----------|
| `state_update` | `{entities, tiles, marks, hp}` | State snapshot |
| `entity_died` | `{entity_id, drops}` | Entidade morreu |
| `mark_changed` | `{mark, old_value, new_value}` | Marca mudou |
| `event_triggered` | `{event_type, data}` | Evento dinâmico |
| `loop_ended` | `{ending_type, narrative}` | Loop terminou |
| `chat_message` | `{username, message}` | Mensagem de chat |

#### State Synchronization

**Estratégia**: Client Prediction + Server Reconciliation

1. **Cliente prevê resultado** imediatamente (responsividade)
2. **Servidor valida** e retorna state autoritativo
3. **Cliente reconcilia** se houver divergência

**Exemplo: Movimento**

```javascript
// Cliente
function requestMove(targetX, targetY) {
    // 1. Predição local
    player.x = targetX;
    player.y = targetY;
    player.pendingMoves.push({x: targetX, y: targetY, sequence: nextSequence++});

    // 2. Enviar para servidor
    socket.emit('player_move', {x: targetX, y: targetY, sequence: nextSequence - 1});
}

// Quando recebe confirmação
socket.on('move_confirmed', (data) => {
    // Remove da fila de pendentes
    player.pendingMoves = player.pendingMoves.filter(m => m.sequence !== data.sequence);

    // Se posição diferente, reconcilia
    if (player.x !== data.x || player.y !== data.y) {
        player.x = data.x;
        player.y = data.y;
    }
});
```

### 4. Banco de Dados (MongoDB)

#### Coleções

**players**
```json
{
    "_id": "ObjectId",
    "username": "Alice",
    "password_hash": "bcrypt_hash",
    "created_at": "ISO_DATE",
    "stats": {
        "level": 5,
        "xp": 1250,
        "hp": 100,
        "max_hp": 100,
        "strength": 10,
        "agility": 8
    },
    "marks": {
        "VIOLENCIA": 35,
        "CONTROLE": -10,
        "CURIOSIDADE": 60,
        "MEMORIA": 20
    },
    "inventory": [
        {"item_id": "iron_sword", "quantity": 1},
        {"item_id": "health_potion", "quantity": 3}
    ],
    "unlocked_skills": ["furia_berserker"],
    "loops_completed": 2
}
```

**worlds**
```json
{
    "_id": "ObjectId",
    "seed": 123456789,
    "current_loop": 3,
    "stability": 75.5,
    "created_at": "ISO_DATE",
    "players_in_world": ["Alice", "Bob"],
    "regions": {
        "0,0": {
            "type": "dungeon",
            "discovered_by": ["Alice"],
            "corruption_level": 10
        }
    }
}
```

**npcs**
```json
{
    "_id": "ObjectId",
    "name": "Merchant Gregor",
    "type": "merchant",
    "personality": {
        "traits": ["greedy", "cowardly"],
        "dialogue_style": "formal"
    },
    "position": {"x": 10, "y": 15},
    "inventory": [...],
    "memory": {
        "Alice": {"reputation": 80, "interactions": 5}
    }
}
```

**events**
```json
{
    "_id": "ObjectId",
    "loop_id": "ObjectId",
    "timestamp": "ISO_DATE",
    "event_type": "meteor_impact",
    "affected_players": ["Alice", "Bob"],
    "outcome": "Alice took 25 damage",
    "mark_changes": {
        "Alice": {"VIOLENCIA": +2}
    }
}
```

### 5. Sistema de IA

#### GM Master (Claude/Gemini)

**Responsabilidades:**
- Analisar ações do loop a cada 5 minutos
- Gerar eventos dinâmicos baseado em marcas
- Decidir final do loop quando stability = 0
- Criar narrativa para NPCs importantes

**Fluxo:**

```python
# A cada 5 minutos ou quando stability < 20
def analyze_loop():
    # 1. Agregar ações
    actions_summary = log_aggregator.get_summary(last_5_minutes)

    # 2. Montar prompt
    prompt = f"""
    Você é o GM de Soulforge Chronicles. Analise as ações dos jogadores:

    {actions_summary}

    Marcas coletivas:
    - VIOLÊNCIA média: {avg_violence}
    - CONTROLE médio: {avg_control}

    Estabilidade: {world.stability}

    Gere um evento dinâmico interessante (JSON format):
    {{
        "event_type": "...",
        "description": "...",
        "mechanical_effects": {{...}}
    }}
    """

    # 3. Chamar API
    if Config.AI_MASTER_PROVIDER == 'claude':
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": prompt}]
        )

    # 4. Parsear resposta e aplicar evento
    event = json.loads(response.content[0].text)
    events_system.trigger_event(event)
```

#### Local AI (Ollama)

**Responsabilidades:**
- Gerar diálogos de NPCs em tempo real
- Respostas rápidas (não pode ter latência de API externa)

```python
def generate_npc_dialogue(npc, player_message):
    prompt = f"""
    NPC: {npc.name}
    Personalidade: {npc.personality}
    Player disse: "{player_message}"

    Responda em 1-2 frases como o NPC:
    """

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()['response']
```

### 6. Segurança

#### Validações Server-Side

**Todas** as ações são validadas no servidor:

```python
def validate_move(player, target_x, target_y):
    # 1. Dentro do mapa?
    if not (0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT):
        return False, "Out of bounds"

    # 2. Distância válida? (máximo 1 tile por movimento)
    distance = abs(target_x - player.x) + abs(target_y - player.y)
    if distance > 1:
        return False, "Too far"

    # 3. Tile andável?
    tile = world.get_tile(target_x, target_y)
    if not tile.walkable:
        return False, "Tile not walkable"

    # 4. Ocupado por outro player?
    if world.get_player_at(target_x, target_y):
        return False, "Tile occupied"

    return True, "OK"
```

#### Anti-Cheat

- **Rate Limiting**: Máximo 10 ações por segundo por player
- **Sequence Numbers**: Detectar replay attacks
- **Hash de Assets**: Cliente não pode modificar sprites para "ver através de paredes"

### 7. Performance

#### Otimizações

**Server-Side:**
- Estado do mundo em memória (não lê MongoDB a cada tick)
- Broadcast apenas para players próximos (spatial hashing)
- FOV cacheado (só recalcula quando player move)

**Client-Side:**
- Object pooling para sprites (reusa ao invés de criar/destruir)
- Culling: só renderiza tiles visíveis na camera
- Delta compression: só envia o que mudou

#### Escalabilidade

**Current MVP**: 10 players por world
**Future**: Sharding (múltiplos worlds em paralelo)

### 8. DevOps

#### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd server && pytest
      - run: cd client && npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: docker-compose build
      - run: docker-compose up -d
```

#### Monitoramento

- **Logs**: Winston (cliente), Python logging (servidor)
- **Métricas**: Players online, loops completados, crashes
- **Alertas**: Se servidor cai, enviar notificação

## Diagramas de Sequência

### Player Attack

```
Player      Client          Server         Database
  │           │               │               │
  │──click──>│               │               │
  │           │──attack────>│               │
  │           │  {target_id} │               │
  │           │               │──validate──>│
  │           │               │<─player_data─┤
  │           │               │──calc_damage│
  │           │<─damage_dealt─┤             │
  │<─animate──┤               │──update_hp─>│
  │           │<─state_update─┤<────ok──────┤
  │<─update───┤               │               │
```

### Loop End

```
GameLoop    IA_Master     Database      Clients
  │             │            │             │
  │──stability=0│            │             │
  ├─aggregate───>│           │             │
  │   actions    │           │             │
  │             ├──query────>│             │
  │             │<─all_marks─┤             │
  │<─generate_end┤           │             │
  │   narrative  │           │             │
  ├──save_loop──────────────>│             │
  ├──broadcast_ending───────────────────>│
  │                                        │
  │<─────────────player_feedback──────────┤
  ├──reset_world│            │             │
  ├──new_loop──────────────>│             │
  └──notify_clients─────────────────────>│
```

## Tecnologias e Bibliotecas

### Frontend
- **Phaser 3.60+**: Game engine
- **ROT.js 2.2+**: Roguelike toolkit
- **Socket.IO Client 4.5+**: WebSocket
- **Webpack 5**: Bundler

### Backend
- **Python 3.11**: Linguagem
- **Flask 3.0**: Web framework
- **Flask-SocketIO 5.3**: WebSocket
- **PyMongo 4.6**: MongoDB driver
- **TCOD 16.0**: Roguelike algorithms
- **Anthropic SDK**: Claude API
- **Google GenAI SDK**: Gemini API

### DevOps
- **Docker + Docker Compose**: Containerização
- **MongoDB 7**: Database
- **Ollama**: Local LLM hosting
- **pytest**: Testes Python
- **Jest**: Testes JavaScript

## Próximos Passos de Arquitetura

### v0.2.0
- [ ] WebRTC para voice chat
- [ ] Redis para session store (escalabilidade)
- [ ] Load balancer (múltiplos servidores)

### v0.3.0
- [ ] Kubernetes deployment
- [ ] Sharding de worlds
- [ ] CDN para assets

### v1.0.0
- [ ] Microserviços (IA separada do game server)
- [ ] GraphQL para queries complexas
- [ ] Machine learning para balanceamento automático
