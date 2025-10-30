"""
Database Manager - MongoDB integration
"""
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import bcrypt
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MongoDB connections and operations"""

    def __init__(self, uri: str):
        self.uri = uri
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.get_database()
            logger.info(f"Connected to MongoDB: {self.db.name}")
            self._ensure_indexes()
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        """Check if database is connected"""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False

    def _ensure_indexes(self):
        """Create necessary indexes"""
        if not self.db:
            return

        # Players collection
        self.db.players.create_index('username', unique=True)
        self.db.players.create_index('loops_completed')

        # Worlds collection
        self.db.worlds.create_index('seed')
        self.db.worlds.create_index('current_loop')

        logger.info("Database indexes ensured")

    # ========================================================================
    # Player Operations
    # ========================================================================

    def create_player(self, username: str, password: str) -> Optional[Dict]:
        """Create new player account"""
        if not self.db:
            return None

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        player_doc = {
            'username': username,
            'password_hash': password_hash,
            'level': 1,
            'xp': 0,
            'hp': 100,
            'max_hp': 100,
            'stats': {
                'strength': 10,
                'agility': 10,
                'endurance': 10,
                'perception': 10,
                'luck': 10
            },
            'marks': {
                'VIOLENCIA': 0,
                'CONTROLE': 0,
                'CURIOSIDADE': 0,
                'MEMORIA': 0
            },
            'inventory': [],
            'equipped': {},
            'unlocked_skills': [],
            'loops_completed': 0,
            'total_kills': 0,
            'total_deaths': 0
        }

        try:
            result = self.db.players.insert_one(player_doc)
            player_doc['_id'] = str(result.inserted_id)
            return player_doc
        except Exception as e:
            logger.error(f"Failed to create player: {e}")
            return None

    def get_player(self, username: str) -> Optional[Dict]:
        """Get player by username"""
        if not self.db:
            return None

        player = self.db.players.find_one({'username': username})
        if player:
            player['id'] = str(player['_id'])
        return player

    def verify_password(self, username: str, password: str) -> bool:
        """Verify player password"""
        player = self.get_player(username)
        if not player:
            return False

        return bcrypt.checkpw(password.encode('utf-8'), player['password_hash'])

    def save_player(self, player_data: Dict) -> bool:
        """Save/update player data"""
        if not self.db:
            return False

        try:
            self.db.players.update_one(
                {'username': player_data['username']},
                {'$set': player_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save player: {e}")
            return False

    def get_player_count(self) -> int:
        """Get total registered players"""
        if not self.db:
            return 0
        return self.db.players.count_documents({})

    # ========================================================================
    # World Operations
    # ========================================================================

    def save_world(self, world_data: Dict) -> bool:
        """Save world state"""
        if not self.db:
            return False

        try:
            self.db.worlds.update_one(
                {'seed': world_data['seed']},
                {'$set': world_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save world: {e}")
            return False

    def get_world(self, seed: int) -> Optional[Dict]:
        """Get world by seed"""
        if not self.db:
            return None

        return self.db.worlds.find_one({'seed': seed})

    # ========================================================================
    # Loop/Event History
    # ========================================================================

    def save_loop_completion(self, loop_data: Dict) -> bool:
        """Save completed loop data"""
        if not self.db:
            return False

        try:
            self.db.loops.insert_one(loop_data)
            return True
        except Exception as e:
            logger.error(f"Failed to save loop: {e}")
            return False

    def get_completed_loops_count(self) -> int:
        """Get total completed loops"""
        if not self.db:
            return 0
        return self.db.loops.count_documents({})

    def get_player_history(self, username: str, limit: int = 10) -> List[Dict]:
        """Get player's loop history"""
        if not self.db:
            return []

        loops = self.db.loops.find(
            {'players': username}
        ).sort('ended_at', -1).limit(limit)

        return list(loops)

    # ========================================================================
    # Leaderboards
    # ========================================================================

    def get_leaderboard(self, metric: str = 'loops_completed', limit: int = 10) -> List[Dict]:
        """Get leaderboard by metric"""
        if not self.db:
            return []

        valid_metrics = ['loops_completed', 'total_kills', 'level', 'xp']
        if metric not in valid_metrics:
            metric = 'loops_completed'

        players = self.db.players.find(
            {},
            {'username': 1, metric: 1, 'level': 1}
        ).sort(metric, -1).limit(limit)

        return list(players)

    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
