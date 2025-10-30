"""
Main entry point for Soulforge Chronicles server
"""
import logging
import os
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from app.game_server import GameServer
from app.database.db_manager import DatabaseManager

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=Config.DEBUG,
    engineio_logger=Config.DEBUG
)

# Initialize database
try:
    db = DatabaseManager(Config.MONGODB_URI)
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    db = None

# Initialize game server
game_server = GameServer(socketio, db, Config)
logger.info("Game server initialized")

# ============================================================================
# HTTP Routes
# ============================================================================

@app.route('/')
def index():
    """Server status endpoint"""
    return jsonify({
        'status': 'Soulforge Chronicles Server Running',
        'version': '0.1.0',
        'debug': Config.DEBUG
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'players_online': game_server.get_player_count(),
        'loops_active': game_server.get_active_loop_count(),
        'uptime_seconds': game_server.get_uptime(),
        'database_connected': db is not None and db.is_connected()
    })

@app.route('/api/world/current')
def world_current():
    """Get current world state"""
    world_state = game_server.get_world_state()
    if world_state:
        return jsonify(world_state)
    return jsonify({'error': 'No active world'}), 404

@app.route('/api/stats')
def stats():
    """Server statistics"""
    return jsonify({
        'total_players_registered': db.get_player_count() if db else 0,
        'players_online': game_server.get_player_count(),
        'total_loops_completed': db.get_completed_loops_count() if db else 0,
        'server_version': '0.1.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# Socket.IO Event Handlers (delegated to GameServer)
# ============================================================================

@socketio.on('connect')
def handle_connect(auth):
    """Handle client connection"""
    game_server.handle_connect(auth)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    game_server.handle_disconnect()

@socketio.on('player_move')
def handle_player_move(data):
    """Handle player movement request"""
    game_server.handle_player_move(data)

@socketio.on('player_attack')
def handle_player_attack(data):
    """Handle player attack request"""
    game_server.handle_player_attack(data)

@socketio.on('player_use_item')
def handle_player_use_item(data):
    """Handle player item usage"""
    game_server.handle_player_use_item(data)

@socketio.on('player_use_skill')
def handle_player_use_skill(data):
    """Handle player skill usage"""
    game_server.handle_player_use_skill(data)

@socketio.on('player_interact')
def handle_player_interact(data):
    """Handle player interaction with entities"""
    game_server.handle_player_interact(data)

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat message"""
    game_server.handle_chat_message(data)

@socketio.on('player_start_craft')
def handle_player_start_craft(data):
    """Handle crafting start"""
    game_server.handle_player_start_craft(data)

# ============================================================================
# Startup
# ============================================================================

def on_server_start():
    """Called when server starts"""
    logger.info("=" * 60)
    logger.info("Soulforge Chronicles Server Starting...")
    logger.info(f"Host: {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug Mode: {Config.DEBUG}")
    logger.info(f"Tick Rate: {Config.TICK_RATE} TPS")
    logger.info(f"AI Provider: {Config.AI_MASTER_PROVIDER}")
    logger.info("=" * 60)

    # Start game loop
    game_server.start()

if __name__ == '__main__':
    on_server_start()

    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False,  # Disable reloader to avoid double initialization
        log_output=Config.DEBUG,
        allow_unsafe_werkzeug=True  # For development only
    )
