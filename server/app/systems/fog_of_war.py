"""
Fog of War System - Using TCOD for shadowcasting FOV
Inspired by Shattered Pixel Dungeon's field of view
"""
import tcod
from typing import Set, Tuple, Optional

class FogOfWarSystem:
    """Handles field of view calculations using shadowcasting"""

    def __init__(self, config):
        self.config = config
        self.default_radius = config.DEFAULT_FOV_RADIUS

    def calculate_fov(self, world, player) -> Set[Tuple[int, int]]:
        """
        Calculate field of view for player
        Returns set of visible (x, y) coordinates
        """
        # Check if we can use cached FOV
        if not player.fov_dirty and player.fov_cache:
            return player.fov_cache

        # Create transparency map
        transparency_map = self._create_transparency_map(world)

        # Calculate radius (modified by stats and marks)
        radius = self._calculate_vision_radius(player)

        # Use TCOD to calculate FOV
        visible_tiles = set()

        # TCOD expects boolean array for transparency
        tcod_transparent = [[False for _ in range(world.height)] for _ in range(world.width)]

        for x in range(world.width):
            for y in range(world.height):
                if transparency_map.get((x, y), False):
                    tcod_transparent[x][y] = True

        # Compute FOV using shadowcasting
        fov = tcod.map.compute_fov(
            transparency=tcod_transparent,
            pov=(player.x, player.y),
            radius=radius,
            light_walls=True,
            algorithm=tcod.FOV_SHADOW
        )

        # Convert to set of coordinates
        for x in range(world.width):
            for y in range(world.height):
                if fov[x][y]:
                    visible_tiles.add((x, y))

        # Cache result
        player.fov_cache = visible_tiles
        player.fov_dirty = False

        return visible_tiles

    def _create_transparency_map(self, world) -> dict:
        """Create transparency map from world tiles"""
        transparency = {}

        for (x, y), tile in world.tiles.items():
            transparency[(x, y)] = tile.get('transparent', False)

        return transparency

    def _calculate_vision_radius(self, player) -> int:
        """Calculate vision radius based on player stats and marks"""
        base_radius = self.default_radius

        # Perception bonus
        perception_bonus = (player.stats.get('perception', 10) - 10) // 3
        radius = base_radius + perception_bonus

        # CURIOSIDADE mark bonus
        curiosidade = player.marks.get('CURIOSIDADE', 0)
        if curiosidade > 50:
            radius += (curiosidade - 50) // 20

        # Vision range from player (calculated in Player._recalculate_derived_stats)
        radius = player.vision_range

        return max(3, min(20, radius))  # Clamp between 3 and 20

    def get_visible_entities(self, world, player, fov_set: Set[Tuple[int, int]]) -> dict:
        """
        Get all entities visible to player
        Returns dict with players, npcs, enemies
        """
        visible = {
            'players': [],
            'npcs': [],
            'enemies': []
        }

        # Check other players
        for other_player in world.players.values():
            if other_player.id != player.id:
                if (other_player.x, other_player.y) in fov_set:
                    visible['players'].append(other_player.to_dict(include_private=False))

        # Check NPCs
        for npc in world.npcs.values():
            if (npc.x, npc.y) in fov_set:
                visible['npcs'].append(npc.to_dict())

        # Check enemies
        for enemy in world.enemies.values():
            if (enemy.x, enemy.y) in fov_set:
                visible['enemies'].append(enemy.to_dict())

        return visible

    def get_visible_tiles(self, world, fov_set: Set[Tuple[int, int]]) -> list:
        """Get tile data for visible tiles"""
        visible_tiles = []

        for (x, y) in fov_set:
            tile = world.get_tile(x, y)
            if tile:
                visible_tiles.append({
                    'x': x,
                    'y': y,
                    'type': tile['type'],
                    'walkable': tile['walkable']
                })

        return visible_tiles
