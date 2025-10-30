"""
World model - Represents the game world state
Inspired by Cataclysm: DDA overmap system
"""
import random
import time
from typing import Dict, List, Optional, Tuple

class World:
    """Game world with regions, stability, and loop state"""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or int(time.time())
        random.seed(self.seed)

        self.id = f"world_{self.seed}"
        self.current_loop = 1
        self.stability = 100.0
        self.created_at = time.time()

        # Map - Tamanho 50x50 para MVP conforme especificação
        self.width = 50
        self.height = 50
        self.tiles = {}  # {(x, y): tile_type}
        self.generate_base_map()

        # Entities
        self.players = {}  # {player_id: Player}
        self.npcs = {}  # {npc_id: NPC}
        self.enemies = {}  # {enemy_id: Enemy}

        # Regions (procedural generation)
        self.regions = {}  # {(region_x, region_y): Region}

        # Events
        self.active_events = []
        self.event_history = []

        # Environment (inspired by CDDA weather)
        self.weather = 'clear'
        self.time_of_day = 12  # 0-23
        self.temperature = 20

    def generate_base_map(self):
        """Generate simple base map with rooms and corridors for MVP"""
        # Inicializar tudo como parede
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[(x, y)] = {
                    'type': 'wall',
                    'walkable': False,
                    'transparent': False
                }

        # Criar sala central grande (20x20)
        for y in range(15, 35):
            for x in range(15, 35):
                self.tiles[(x, y)] = {
                    'type': 'floor',
                    'walkable': True,
                    'transparent': True
                }

        # Criar corredores
        # Corredor horizontal
        for x in range(10, 40):
            self.tiles[(x, 25)] = {
                'type': 'floor',
                'walkable': True,
                'transparent': True
            }

        # Corredor vertical
        for y in range(10, 40):
            self.tiles[(25, y)] = {
                'type': 'floor',
                'walkable': True,
                'transparent': True
            }

        # Criar salas adicionais pequenas (5x5)
        # Sala norte
        for y in range(5, 10):
            for x in range(23, 28):
                self.tiles[(x, y)] = {
                    'type': 'floor',
                    'walkable': True,
                    'transparent': True
                }

        # Sala sul
        for y in range(40, 45):
            for x in range(23, 28):
                self.tiles[(x, y)] = {
                    'type': 'floor',
                    'walkable': True,
                    'transparent': True
                }

        # Sala oeste
        for y in range(23, 28):
            for x in range(5, 10):
                self.tiles[(x, y)] = {
                    'type': 'floor',
                    'walkable': True,
                    'transparent': True
                }

        # Sala leste
        for y in range(23, 28):
            for x in range(40, 45):
                self.tiles[(x, y)] = {
                    'type': 'floor',
                    'walkable': True,
                    'transparent': True
                }

    def get_tile(self, x: int, y: int) -> Optional[Dict]:
        """Get tile at position"""
        return self.tiles.get((x, y))

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if tile is walkable"""
        tile = self.get_tile(x, y)
        if not tile:
            return False

        # Check if any entity blocks
        if self.get_player_at(x, y) or self.get_enemy_at(x, y):
            return False

        return tile.get('walkable', False)

    def is_transparent(self, x: int, y: int) -> bool:
        """Check if tile is transparent (for FOV)"""
        tile = self.get_tile(x, y)
        return tile.get('transparent', False) if tile else False

    def get_player_at(self, x: int, y: int) -> Optional:
        """Get player at position"""
        for player in self.players.values():
            if player.x == x and player.y == y:
                return player
        return None

    def get_enemy_at(self, x: int, y: int) -> Optional:
        """Get enemy at position"""
        for enemy in self.enemies.values():
            if enemy.x == x and enemy.y == y:
                return enemy
        return None

    def add_player(self, player):
        """Add player to world"""
        self.players[player.id] = player
        # Set spawn point if not set
        if player.spawn_x == 0 and player.spawn_y == 0:
            player.set_spawn_point(self.width // 2, self.height // 2)

    def remove_player(self, player_id: str):
        """Remove player from world"""
        if player_id in self.players:
            del self.players[player_id]

    def get_spawn_position(self) -> Tuple[int, int]:
        """Get safe spawn position"""
        # Center of map
        return (self.width // 2, self.height // 2)

    def update_stability(self, delta: float):
        """Update world stability"""
        self.stability = max(0, min(100, self.stability + delta))

    def get_stability_effects(self) -> Dict:
        """Get environmental effects based on stability"""
        effects = {}

        if self.stability > 70:
            self.weather = random.choice(['clear', 'cloudy'])
        elif self.stability > 40:
            self.weather = random.choice(['cloudy', 'rain', 'fog'])
            if self.weather == 'fog':
                effects['visibility'] = -3
        else:
            # Apocalyptic weather
            self.weather = random.choice(['storm', 'ash_rain', 'blood_rain', 'void_fog'])
            if self.weather == 'storm':
                effects['movement_speed'] = 0.7
            elif self.weather == 'void_fog':
                effects['sanity_drain'] = 1

        return effects

    def to_dict(self) -> Dict:
        """Serialize world state"""
        return {
            'id': self.id,
            'seed': self.seed,
            'current_loop': self.current_loop,
            'stability': self.stability,
            'weather': self.weather,
            'player_count': len(self.players),
            'enemy_count': len(self.enemies),
            'active_events': [e.to_dict() for e in self.active_events] if self.active_events else []
        }
