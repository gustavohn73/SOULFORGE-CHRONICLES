# API Reference - Soulforge Chronicles

Documentação completa dos endpoints HTTP e eventos Socket.IO.

## HTTP REST API

Base URL: `http://localhost:5000`

### Health Check

#### `GET /`

Status do servidor.

**Response:**
```json
{
    "status": "Soulforge Chronicles Server Running",
    "version": "0.1.0"
}
```

#### `GET /health`

Health check detalhado.

**Response:**
```json
{
    "status": "ok",
    "players_online": 5,
    "uptime_seconds": 3600,
    "loops_active": 1
}
```

### Authentication

#### `POST /api/auth/register`

Cria nova conta.

**Request:**
```json
{
    "username": "Alice",
    "password": "secure_password"
}
```

**Response:**
```json
{
    "success": true,
    "user_id": "507f1f77bcf86cd799439011",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `400`: Username já existe
- `400`: Username inválido (min 3 caracteres)
- `400`: Senha muito curta (min 6 caracteres)

#### `POST /api/auth/login`

Login.

**Request:**
```json
{
    "username": "Alice",
    "password": "secure_password"
}
```

**Response:**
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "player_data": {
        "username": "Alice",
        "level": 5,
        "marks": {
            "VIOLENCIA": 35,
            "CONTROLE": -10,
            "CURIOSIDADE": 60,
            "MEMORIA": 20
        }
    }
}
```

**Errors:**
- `401`: Credenciais inválidas

### Player Data

#### `GET /api/player/<username>`

Busca dados públicos de um jogador.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "username": "Alice",
    "level": 5,
    "loops_completed": 2,
    "marks": {
        "VIOLENCIA": 35,
        "CONTROLE": -10,
        "CURIOSIDADE": 60,
        "MEMORIA": 20
    },
    "unlocked_skills": ["furia_berserker"],
    "reputation": {
        "Merchants Guild": 80,
        "Dark Cult": -50
    }
}
```

#### `GET /api/player/<username>/history`

Histórico de loops do jogador.

**Response:**
```json
{
    "loops": [
        {
            "loop_number": 1,
            "ended_at": "2025-01-15T10:30:00Z",
            "ending_type": "redentor",
            "duration_minutes": 45,
            "kills": 23,
            "deaths": 1,
            "mark_changes": {
                "VIOLENCIA": +15,
                "CURIOSIDADE": +30
            }
        },
        {
            "loop_number": 2,
            "ended_at": "2025-01-15T12:00:00Z",
            "ending_type": "violento",
            "duration_minutes": 60,
            "kills": 45,
            "deaths": 0,
            "mark_changes": {
                "VIOLENCIA": +20,
                "CONTROLE": -10
            }
        }
    ]
}
```

### World Data

#### `GET /api/world/current`

Estado do world ativo.

**Response:**
```json
{
    "world_id": "507f1f77bcf86cd799439011",
    "current_loop": 3,
    "stability": 75.5,
    "time_remaining_seconds": 1800,
    "players_online": 5,
    "active_events": [
        {
            "type": "meteor_falling",
            "countdown_seconds": 60,
            "position": {"x": 25, "y": 30}
        }
    ]
}
```

### Leaderboard

#### `GET /api/leaderboard?metric=loops_completed&limit=10`

Ranking de jogadores.

**Query Parameters:**
- `metric`: `loops_completed`, `kills`, `VIOLENCIA`, `CURIOSIDADE`, etc
- `limit`: Número de resultados (padrão: 10)

**Response:**
```json
{
    "leaderboard": [
        {"username": "Alice", "loops_completed": 15, "rank": 1},
        {"username": "Bob", "loops_completed": 12, "rank": 2},
        {"username": "Charlie", "loops_completed": 10, "rank": 3}
    ]
}
```

## Socket.IO Events

Namespace: `/` (default)

### Connection

#### `connect`

Cliente conecta ao servidor.

**Emit (Client → Server):**
```javascript
socket.emit('connect', {
    token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
});
```

**Listen (Server → Client):**
```javascript
socket.on('connected', (data) => {
    // data = {
    //     player_id: "507f...",
    //     world_state: {...},
    //     nearby_players: [...]
    // }
});
```

**Errors:**
```javascript
socket.on('connect_error', (error) => {
    // error = {
    //     message: "Invalid token",
    //     code: 401
    // }
});
```

### Movement

#### `player_move`

Jogador quer se mover.

**Emit (Client → Server):**
```javascript
socket.emit('player_move', {
    x: 10,
    y: 15,
    sequence: 123  // Para client prediction
});
```

**Listen (Server → Client):**
```javascript
// Confirmação
socket.on('move_confirmed', (data) => {
    // data = {
    //     x: 10,
    //     y: 15,
    //     sequence: 123,
    //     timestamp: 1234567890
    // }
});

// Rejeição
socket.on('move_rejected', (data) => {
    // data = {
    //     reason: "Tile not walkable",
    //     sequence: 123,
    //     current_position: {x: 9, y: 15}
    // }
});
```

### Combat

#### `player_attack`

Jogador ataca entidade.

**Emit:**
```javascript
socket.emit('player_attack', {
    target_id: "npc_123",
    weapon_slot: 0  // Slot do inventário (0 = mão direita)
});
```

**Listen:**
```javascript
socket.on('attack_result', (data) => {
    // data = {
    //     success: true,
    //     damage: 25,
    //     is_critical: false,
    //     is_surprise: true,
    //     target_hp: 50,
    //     target_died: false,
    //     mark_changes: {VIOLENCIA: +2},
    //     xp_gained: 10
    // }
});
```

#### `player_use_skill`

Usa habilidade especial.

**Emit:**
```javascript
socket.emit('player_use_skill', {
    skill_id: "furia_berserker",
    target_position: {x: 12, y: 18}  // Opcional, para AoE
});
```

**Listen:**
```javascript
socket.on('skill_activated', (data) => {
    // data = {
    //     skill_id: "furia_berserker",
    //     effects: {
    //         damage_bonus: 1.0,
    //         defense_penalty: -0.5,
    //         duration_turns: 5
    //     },
    //     cooldown_remaining: 50
    // }
});

socket.on('skill_failed', (data) => {
    // data = {
    //     reason: "On cooldown",
    //     cooldown_remaining: 23
    // }
});
```

### Items

#### `player_use_item`

Usa item do inventário.

**Emit:**
```javascript
socket.emit('player_use_item', {
    item_id: "health_potion",
    target: "self"  // ou player_id de outro
});
```

**Listen:**
```javascript
socket.on('item_used', (data) => {
    // data = {
    //     item_id: "health_potion",
    //     effects: {hp_restored: 50},
    //     remaining_quantity: 2
    // }
});
```

#### `player_pickup_item`

Pega item do chão.

**Emit:**
```javascript
socket.emit('player_pickup_item', {
    item_id: "ground_item_456",
    position: {x: 10, y: 15}
});
```

#### `player_drop_item`

Solta item no chão.

**Emit:**
```javascript
socket.emit('player_drop_item', {
    item_id: "iron_sword",
    quantity: 1
});
```

### Crafting

#### `player_start_craft`

Inicia crafting.

**Emit:**
```javascript
socket.emit('player_start_craft', {
    recipe_id: "iron_sword"
});
```

**Listen:**
```javascript
socket.on('craft_started', (data) => {
    // data = {
    //     recipe_id: "iron_sword",
    //     time_remaining_seconds: 50,
    //     craft_id: "craft_789"
    // }
});

// Quando completa
socket.on('craft_completed', (data) => {
    // data = {
    //     craft_id: "craft_789",
    //     result: {item_id: "iron_sword", quantity: 1},
    //     mark_changes: {CONTROLE: +1}
    // }
});
```

### Interaction

#### `player_interact`

Interage com NPC/objeto.

**Emit:**
```javascript
socket.emit('player_interact', {
    target_id: "npc_merchant_01"
});
```

**Listen:**
```javascript
socket.on('interaction_started', (data) => {
    // data = {
    //     type: "dialogue",
    //     npc: {
    //         name: "Gregor the Merchant",
    //         portrait: "merchant_01.png",
    //         dialogue: "Welcome, traveler! What brings you here?"
    //     },
    //     options: [
    //         {id: 1, text: "I want to trade"},
    //         {id: 2, text: "Tell me about this place"},
    //         {id: 3, text: "Goodbye"}
    //     ]
    // }
});
```

#### `player_dialogue_choice`

Escolhe opção de diálogo.

**Emit:**
```javascript
socket.emit('player_dialogue_choice', {
    npc_id: "npc_merchant_01",
    choice_id: 1
});
```

### Chat

#### `chat_message`

Envia mensagem no chat.

**Emit:**
```javascript
socket.emit('chat_message', {
    message: "Hello everyone!",
    channel: "global"  // global, party, whisper
});
```

**Listen:**
```javascript
socket.on('chat_message', (data) => {
    // data = {
    //     username: "Alice",
    //     message: "Hello everyone!",
    //     channel: "global",
    //     timestamp: 1234567890
    // }
});
```

### State Updates

#### `state_update`

Servidor envia snapshot do estado visível ao jogador.

**Listen (Server → Client):**
```javascript
socket.on('state_update', (data) => {
    // data = {
    //     timestamp: 1234567890,
    //     player: {
    //         x: 10,
    //         y: 15,
    //         hp: 80,
    //         max_hp: 100,
    //         marks: {
    //             VIOLENCIA: 35,
    //             CONTROLE: -10,
    //             CURIOSIDADE: 60,
    //             MEMORIA: 20
    //         }
    //     },
    //     visible_entities: [
    //         {
    //             id: "player_bob",
    //             type: "player",
    //             x: 12,
    //             y: 14,
    //             username: "Bob",
    //             hp: 100
    //         },
    //         {
    //             id: "enemy_001",
    //             type: "enemy",
    //             x: 15,
    //             y: 18,
    //             enemy_type: "goblin",
    //             hp: 30
    //         }
    //     ],
    //     visible_tiles: [
    //         {x: 9, y: 14, type: "floor"},
    //         {x: 10, y: 14, type: "floor"},
    //         {x: 11, y: 14, type: "wall"}
    //     ],
    //     world: {
    //         stability: 75.5,
    //         time_remaining: 1800
    //     }
    // }
});
```

**Frequency**: ~20 updates/segundo (20 TPS)

### Events

#### `event_triggered`

Evento dinâmico aconteceu.

**Listen:**
```javascript
socket.on('event_triggered', (data) => {
    // data = {
    //     event_type: "meteor_falling",
    //     description: "A meteor is falling from the sky!",
    //     countdown_seconds: 60,
    //     affected_area: {
    //         center: {x: 25, y: 30},
    //         radius: 5
    //     },
    //     effects: {
    //         damage: 50,
    //         creates: "crater_with_ore"
    //     }
    // }
});
```

#### `loop_ending`

Loop temporal está terminando.

**Listen:**
```javascript
socket.on('loop_ending', (data) => {
    // data = {
    //     countdown_seconds: 10,
    //     message: "The world is collapsing... the GM is deciding your fate..."
    // }
});
```

#### `loop_ended`

Loop terminou, mostrando narrativa gerada.

**Listen:**
```javascript
socket.on('loop_ended', (data) => {
    // data = {
    //     ending_type: "redentor",
    //     narrative: "As the world collapsed, you and your companions...",
    //     collective_marks: {
    //         VIOLENCIA: 45,
    //         CONTROLE: 20,
    //         CURIOSIDADE: 70,
    //         MEMORIA: 30
    //     },
    //     rewards: {
    //         xp_bonus: 500,
    //         unique_item: "Fragment of Memory"
    //     },
    //     next_loop_starts_in: 60
    // }
});
```

#### `mark_changed`

Uma marca do jogador mudou significativamente.

**Listen:**
```javascript
socket.on('mark_changed', (data) => {
    // data = {
    //     mark: "VIOLENCIA",
    //     old_value: 45,
    //     new_value: 55,
    //     reason: "Killed innocent NPC",
    //     unlocked_skill: null  // ou "furia_berserker" se desbloqueou
    // }
});
```

#### `skill_unlocked`

Nova habilidade desbloqueada.

**Listen:**
```javascript
socket.on('skill_unlocked', (data) => {
    // data = {
    //     skill_id: "furia_berserker",
    //     skill_name: "Berserker Fury",
    //     description: "+100% damage, -50% defense for 5 turns",
    //     cooldown: 50,
    //     requirement: {mark: "VIOLENCIA", value: 80}
    // }
});
```

### Error Handling

Todos os eventos podem retornar erro:

```javascript
socket.on('error', (data) => {
    // data = {
    //     code: 400,
    //     message: "Invalid action",
    //     details: "Target is too far away"
    // }
});
```

## Rate Limits

| Ação | Limite |
|------|--------|
| Movimento | 10/segundo |
| Ataque | 5/segundo |
| Uso de item | 3/segundo |
| Chat | 2/segundo |
| Interação | 1/segundo |

## Data Types

### Player Object
```typescript
{
    id: string,
    username: string,
    x: number,
    y: number,
    hp: number,
    max_hp: number,
    level: number,
    xp: number,
    marks: {
        VIOLENCIA: number,    // -100 a 100
        CONTROLE: number,     // -100 a 100
        CURIOSIDADE: number,  // -100 a 100
        MEMORIA: number       // -100 a 100
    },
    stats: {
        strength: number,
        agility: number,
        endurance: number,
        perception: number,
        luck: number
    },
    inventory: Array<{item_id: string, quantity: number}>,
    equipped: {
        weapon: object | null,
        armor: object | null,
        accessory: object | null
    }
}
```

### Entity Object
```typescript
{
    id: string,
    type: "player" | "npc" | "enemy",
    x: number,
    y: number,
    hp: number,
    max_hp: number,
    sprite: string,
    // Se type === "player"
    username?: string,
    // Se type === "npc"
    npc_type?: "merchant" | "quest_giver" | "companion",
    // Se type === "enemy"
    enemy_type?: "goblin" | "skeleton" | "boss"
}
```

### Tile Object
```typescript
{
    x: number,
    y: number,
    type: "floor" | "wall" | "water" | "door" | "stairs",
    walkable: boolean,
    transparent: boolean,  // Para FOV
    sprite_index: number
}
```

## Testing

### Postman Collection

Importar: `docs/postman_collection.json`

### WebSocket Test Client

```html
<!DOCTYPE html>
<html>
<head>
    <title>Socket.IO Test</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
</head>
<body>
    <script>
        const socket = io('http://localhost:5000', {
            auth: {token: 'YOUR_TOKEN_HERE'}
        });

        socket.on('connect', () => {
            console.log('Connected!');
            socket.emit('player_move', {x: 5, y: 5, sequence: 1});
        });

        socket.on('state_update', (data) => {
            console.log('State:', data);
        });
    </script>
</body>
</html>
```

## Changelog

### v0.1.0 (Current)
- Initial API release
- Basic movement, combat, items
- Mark system
- Loop temporal

### v0.2.0 (Planned)
- Voice chat endpoints
- Party system
- Trading between players

### v1.0.0 (Future)
- GraphQL endpoint
- REST API v2 (breaking changes)
- Webhooks for external integrations
