"""
Game Server - Handles Socket.IO connections and game logic coordination
"""
import logging
import time
from flask import request
from flask_socketio import emit, disconnect, join_room, leave_room
from typing import Dict, Optional
from app.models.player import Player
from app.models.world import World
from app.systems.combat import CombatSystem
from app.systems.marks import MarksSystem
from app.systems.fog_of_war import FogOfWarSystem

logger = logging.getLogger(__name__)

class GameServer:
    """Main game server managing connections and game state"""

    def __init__(self, socketio, db, config):
        self.socketio = socketio
        self.db = db
        self.config = config

        # Game state
        self.world = World()
        self.connected_players = {}  # {socket_id: player_id}
        self.player_sockets = {}  # {player_id: socket_id}

        # Systems
        self.combat_system = CombatSystem(config)
        self.marks_system = MarksSystem(config)
        self.fov_system = FogOfWarSystem(config)

        # Server stats
        self.start_time = time.time()

        logger.info("Game server initialized")

    def start(self):
        """Start game server"""
        logger.info("Game server started")
        # Game loop is handled by Flask-SocketIO's threading

    def get_uptime(self) -> int:
        """Get server uptime in seconds"""
        return int(time.time() - self.start_time)

    def get_player_count(self) -> int:
        """Get number of connected players"""
        return len(self.connected_players)

    def get_active_loop_count(self) -> int:
        """Get number of active loops"""
        return 1  # Single loop for MVP

    def get_world_state(self) -> Dict:
        """Get current world state"""
        if self.world:
            return self.world.to_dict()
        return {}

    # ========================================================================
    # Socket.IO Event Handlers
    # ========================================================================

    def handle_connect(self, auth):
        """Handle client connection"""
        socket_id = request.sid
        logger.info(f"Client connecting: {socket_id}")

        # For MVP, we'll use simple username auth
        # In production, use JWT tokens
        username = auth.get('username') if auth else None

        if not username:
            logger.warning(f"Connection rejected: no username")
            emit('error', {'message': 'Username required'})
            disconnect()
            return

        # Load or create player
        player_data = self.db.get_player(username) if self.db else None

        if player_data:
            player = Player.from_dict(player_data)
        else:
            # Guest player (not persisted)
            player = Player(username)
            spawn_x, spawn_y = self.world.get_spawn_position()
            player.set_spawn_point(spawn_x, spawn_y)

        player.socket_id = socket_id

        # Add to world
        self.world.add_player(player)

        # Track connection
        self.connected_players[socket_id] = player.id
        self.player_sockets[player.id] = socket_id

        # Join world room
        join_room('world')

        # Send initial state
        emit('connected', {
            'player': player.to_dict(include_private=True),
            'world': self.world.to_dict(),
            'spawn_position': (player.x, player.y)
        })

        # Broadcast to others
        self.socketio.emit('player_joined', {
            'username': player.username,
            'player_id': player.id
        }, room='world', skip_sid=socket_id)

        logger.info(f"Player {username} connected at ({player.x}, {player.y})")

        # Send initial FOV state
        self._send_state_update(player)

    def handle_disconnect(self):
        """Handle client disconnection"""
        socket_id = request.sid
        player_id = self.connected_players.get(socket_id)

        if player_id:
            player = self.world.players.get(player_id)

            # Save player state
            if player and self.db:
                self.db.save_player(player.to_dict(include_private=True))

            # Remove from world
            self.world.remove_player(player_id)

            # Clean up tracking
            del self.connected_players[socket_id]
            if player_id in self.player_sockets:
                del self.player_sockets[player_id]

            # Notify others
            self.socketio.emit('player_left', {
                'player_id': player_id,
                'username': player.username if player else 'Unknown'
            }, room='world')

            logger.info(f"Player {player_id} disconnected")

    def handle_player_move(self, data):
        """Handle player movement request"""
        socket_id = request.sid
        player = self._get_player_from_socket(socket_id)

        if not player:
            return

        # Rate limiting
        if not player.can_perform_action(self.config.MAX_ACTIONS_PER_SECOND_PER_PLAYER):
            emit('move_rejected', {'reason': 'Rate limit exceeded'})
            return

        target_x = data.get('x')
        target_y = data.get('y')
        sequence = data.get('sequence', 0)

        # Validate movement
        valid, reason = self._validate_movement(player, target_x, target_y)

        if not valid:
            emit('move_rejected', {
                'reason': reason,
                'sequence': sequence,
                'current_position': {'x': player.x, 'y': player.y}
            })
            return

        # Apply movement
        old_x, old_y = player.x, player.y
        player.set_position(target_x, target_y)

        # Confirm to client
        emit('move_confirmed', {
            'x': target_x,
            'y': target_y,
            'sequence': sequence
        })

        # Broadcast to others (who can see this player)
        self.socketio.emit('entity_moved', {
            'entity_id': player.id,
            'entity_type': 'player',
            'from': {'x': old_x, 'y': old_y},
            'to': {'x': target_x, 'y': target_y}
        }, room='world', skip_sid=socket_id)

        # Send updated state (with new FOV)
        self._send_state_update(player)

        logger.debug(f"Player {player.username} moved to ({target_x}, {target_y})")

    def handle_player_attack(self, data):
        """Handle player attack request"""
        socket_id = request.sid
        player = self._get_player_from_socket(socket_id)

        if not player:
            return

        target_id = data.get('target_id')

        # Find target
        target = self.world.enemies.get(target_id) or self.world.players.get(target_id)

        if not target:
            emit('error', {'message': 'Target not found'})
            return

        # Check if target is in range
        distance = abs(target.x - player.x) + abs(target.y - player.y)
        if distance > 1:  # Adjacent only for melee
            emit('error', {'message': 'Target too far'})
            return

        # Calculate FOV for surprise check
        fov_set = self.fov_system.calculate_fov(self.world, target)

        # Process attack
        result = self.combat_system.process_attack(player, target, fov_set)

        # Send result to attacker
        emit('attack_result', result)

        # Update marks
        if result['target_died']:
            mark_changes = self.marks_system.register_action(
                player,
                'kill',
                {'target_type': target.entity_type}
            )

            if mark_changes:
                emit('mark_changed', mark_changes)

                # Check for skill unlocks
                for mark_name, change_data in mark_changes.items():
                    if change_data.get('skill_unlocked'):
                        emit('skill_unlocked', {
                            'skill_id': change_data['skill_unlocked'],
                            'mark': mark_name
                        })

            # Award XP
            if result.get('xp_reward', 0) > 0:
                level_up = player.gain_xp(result['xp_reward'])
                if level_up:
                    emit('level_up', level_up)

        # Broadcast attack animation
        self.socketio.emit('attack_animation', {
            'attacker_id': player.id,
            'target_id': target_id,
            'damage': result['damage'],
            'hit_type': result['hit_type']
        }, room='world')

        # Update state
        self._send_state_update(player)

        logger.info(f"Player {player.username} attacked {target_id} for {result['damage']} damage")

    def handle_player_use_item(self, data):
        """Handle item usage"""
        socket_id = request.sid
        player = self._get_player_from_socket(socket_id)

        if not player:
            return

        item_id = data.get('item_id')

        # Simple health potion implementation
        if item_id == 'health_potion':
            if player.has_item(item_id):
                healed = player.heal(50)
                player.remove_item(item_id, 1)

                emit('item_used', {
                    'item_id': item_id,
                    'effects': {'hp_restored': healed},
                    'remaining_quantity': sum(
                        item['quantity'] for item in player.inventory
                        if item['item_id'] == item_id
                    )
                })

                self._send_state_update(player)
            else:
                emit('error', {'message': 'Item not in inventory'})

    def handle_player_use_skill(self, data):
        """Handle skill usage"""
        socket_id = request.sid
        player = self._get_player_from_socket(socket_id)

        if not player:
            return

        skill_id = data.get('skill_id')

        can_use, reason = player.can_use_skill(skill_id)

        if not can_use:
            emit('skill_failed', {'reason': reason})
            return

        # Simple skill implementation (expand in future)
        skill_data = self._get_skill_data(skill_id)

        if not skill_data:
            emit('error', {'message': 'Unknown skill'})
            return

        # Use skill
        player.use_skill(skill_id, skill_data['cooldown'])

        emit('skill_activated', {
            'skill_id': skill_id,
            'effects': skill_data.get('effects', {}),
            'cooldown_remaining': skill_data['cooldown']
        })

        # Broadcast effect
        self.socketio.emit('skill_used', {
            'player_id': player.id,
            'skill_id': skill_id,
            'position': {'x': player.x, 'y': player.y}
        }, room='world')

    def handle_player_interact(self, data):
        """Handle player interaction"""
        # Placeholder for NPC dialogue, object interaction
        emit('interaction_started', {
            'type': 'dialogue',
            'message': 'NPC interaction not yet implemented'
        })

    def handle_chat_message(self, data):
        """Handle chat message"""
        socket_id = request.sid
        player = self._get_player_from_socket(socket_id)

        if not player:
            return

        message = data.get('message', '')

        if len(message) > 200:
            emit('error', {'message': 'Message too long'})
            return

        # Broadcast to all
        self.socketio.emit('chat_message', {
            'username': player.username,
            'message': message,
            'timestamp': time.time()
        }, room='world')

    def handle_player_start_craft(self, data):
        """Handle crafting start"""
        # Placeholder
        emit('error', {'message': 'Crafting not yet implemented'})

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_player_from_socket(self, socket_id: str) -> Optional[Player]:
        """Get player object from socket ID"""
        player_id = self.connected_players.get(socket_id)
        if player_id:
            return self.world.players.get(player_id)
        return None

    def _validate_movement(self, player, target_x: int, target_y: int) -> tuple:
        """Validate movement request"""
        # Bounds check
        if not (0 <= target_x < self.world.width and 0 <= target_y < self.world.height):
            return False, "Out of bounds"

        # Distance check (can only move 1 tile)
        distance = abs(target_x - player.x) + abs(target_y - player.y)
        if distance != 1:
            return False, "Invalid distance (must be adjacent)"

        # Walkable check
        if not self.world.is_walkable(target_x, target_y):
            return False, "Tile not walkable"

        return True, "OK"

    def _send_state_update(self, player):
        """Send state update to player (only what they can see)"""
        # Calculate FOV
        fov_set = self.fov_system.calculate_fov(self.world, player)

        # Get visible entities
        visible_entities = self.fov_system.get_visible_entities(self.world, player, fov_set)

        # Get visible tiles
        visible_tiles = self.fov_system.get_visible_tiles(self.world, fov_set)

        # Send state
        socket_id = self.player_sockets.get(player.id)
        if socket_id:
            self.socketio.emit('state_update', {
                'player': player.to_dict(include_private=True),
                'visible_entities': visible_entities,
                'visible_tiles': visible_tiles,
                'world': self.world.to_dict(),
                'timestamp': time.time()
            }, room=socket_id)

    def _get_skill_data(self, skill_id: str) -> Optional[Dict]:
        """Get skill data (placeholder)"""
        skills = {
            'furia_berserker': {
                'name': 'Berserker Fury',
                'cooldown': 50,
                'effects': {'damage_bonus': 1.0, 'defense_penalty': -0.5, 'duration': 5}
            },
            'tempo_congelado': {
                'name': 'Frozen Time',
                'cooldown': 100,
                'effects': {'freeze_radius': 5, 'duration': 2}
            }
        }
        return skills.get(skill_id)
