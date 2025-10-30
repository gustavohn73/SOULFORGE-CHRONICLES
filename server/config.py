"""
Configuration module for Soulforge Chronicles server
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Main configuration class"""

    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/soulforge')

    # AI Configuration
    AI_MASTER_PROVIDER = os.getenv('AI_MASTER_PROVIDER', 'claude')  # 'claude' or 'gemini'
    AI_MASTER_API_KEY = os.getenv('AI_MASTER_API_KEY', '')
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

    # Server
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')

    # Game Settings
    TICK_RATE = int(os.getenv('TICK_RATE', 20))  # 20 ticks per second
    TICK_INTERVAL = 1.0 / TICK_RATE  # 0.05 seconds
    MAX_PLAYERS_PER_LOOP = int(os.getenv('MAX_PLAYERS_PER_LOOP', 10))
    LOOP_MIN_DURATION = int(os.getenv('LOOP_MIN_DURATION', 900))  # 15 minutes
    LOOP_MAX_DURATION = int(os.getenv('LOOP_MAX_DURATION', 3600))  # 60 minutes

    # Map Settings
    MAP_WIDTH = 50
    MAP_HEIGHT = 50
    DEFAULT_FOV_RADIUS = 8

    # Combat Settings
    BASE_CRIT_CHANCE = 0.05  # 5%
    SURPRISE_DAMAGE_MULTIPLIER = 1.5
    CRITICAL_DAMAGE_MULTIPLIER = 2.0

    # Mark Settings
    MARK_MIN = -100
    MARK_MAX = 100
    SKILL_UNLOCK_THRESHOLD = 80

    # Performance
    MAX_ACTIONS_PER_SECOND_PER_PLAYER = 10
    STATE_BROADCAST_RATE = TICK_RATE  # Broadcast every tick

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/soulforge.log')

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if cls.AI_MASTER_PROVIDER not in ['claude', 'gemini', 'none']:
            raise ValueError(f"Invalid AI_MASTER_PROVIDER: {cls.AI_MASTER_PROVIDER}")

        if cls.AI_MASTER_PROVIDER != 'none' and not cls.AI_MASTER_API_KEY:
            print("WARNING: AI_MASTER_API_KEY not set. AI features will be limited.")

        if cls.TICK_RATE < 10 or cls.TICK_RATE > 60:
            raise ValueError(f"TICK_RATE must be between 10 and 60, got {cls.TICK_RATE}")

        return True
