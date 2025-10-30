/**
 * GameScene - Main game loop and rendering
 */
import io from 'socket.io-client';

export class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene', active: true });
    }

    create() {
        console.log('GameScene started');

        // Game state
        this.player = null;
        this.playerSprite = null;
        this.otherPlayers = new Map();
        this.enemies = new Map();
        this.tiles = new Map();

        // Camera setup
        this.tileSize = 16;
        this.cameras.main.setZoom(2);

        // Input
        this.cursors = this.input.keyboard.createCursorKeys();
        this.wasd = this.input.keyboard.addKeys({
            W: Phaser.Input.Keyboard.KeyCodes.W,
            A: Phaser.Input.Keyboard.KeyCodes.A,
            S: Phaser.Input.Keyboard.KeyCodes.S,
            D: Phaser.Input.Keyboard.KeyCodes.D
        });

        // Mouse click for movement
        this.input.on('pointerdown', this.onMapClick, this);

        // Connect to server
        this.connectToServer();

        // Start UI scene
        this.scene.launch('UIScene');
    }

    connectToServer() {
        const username = this.game.registry.get('username');
        const serverUrl = this.game.registry.get('serverUrl');

        console.log(`Connecting to ${serverUrl} as ${username}...`);

        this.socket = io(serverUrl, {
            auth: { username }
        });

        this.socket.on('connect', () => {
            console.log('Connected to server!');
        });

        this.socket.on('connected', (data) => {
            console.log('Game started:', data);
            this.player = data.player;
            this.createPlayerSprite(data.player);
        });

        this.socket.on('state_update', (data) => {
            this.handleStateUpdate(data);
        });

        this.socket.on('player_joined', (data) => {
            console.log('Player joined:', data.username);
        });

        this.socket.on('player_left', (data) => {
            console.log('Player left:', data.username);
            this.removeOtherPlayer(data.player_id);
        });

        this.socket.on('entity_moved', (data) => {
            this.handleEntityMoved(data);
        });

        this.socket.on('move_confirmed', (data) => {
            // Movement confirmed
        });

        this.socket.on('move_rejected', (data) => {
            console.warn('Move rejected:', data.reason);
            if (this.playerSprite && this.player) {
                this.playerSprite.x = this.player.x * this.tileSize;
                this.playerSprite.y = this.player.y * this.tileSize;
            }
        });

        this.socket.on('attack_result', (data) => {
            console.log('Attack result:', data);
        });

        this.socket.on('mark_changed', (data) => {
            console.log('Mark changed:', data);
            if (this.player) {
                Object.assign(this.player.marks, data);
            }
        });

        this.socket.on('error', (data) => {
            console.error('Server error:', data);
        });
    }

    createPlayerSprite(playerData) {
        // Create simple circle for player
        this.playerSprite = this.add.circle(
            playerData.x * this.tileSize,
            playerData.y * this.tileSize,
            8,
            0x00ff00
        );

        // Add username text
        this.playerText = this.add.text(
            playerData.x * this.tileSize,
            playerData.y * this.tileSize - 12,
            playerData.username,
            { fontSize: '10px', color: '#fff' }
        ).setOrigin(0.5);

        // Camera follow player
        this.cameras.main.startFollow(this.playerSprite);
    }

    handleStateUpdate(data) {
        // Update player data
        if (data.player) {
            this.player = data.player;

            // Update UI
            this.registry.set('player', this.player);

            // Update player sprite position
            if (this.playerSprite) {
                this.playerSprite.x = this.player.x * this.tileSize;
                this.playerSprite.y = this.player.y * this.tileSize;
                this.playerText.x = this.player.x * this.tileSize;
                this.playerText.y = this.player.y * this.tileSize - 12;
            }
        }

        // Render visible tiles
        if (data.visible_tiles) {
            this.renderTiles(data.visible_tiles);
        }

        // Render other entities
        if (data.visible_entities) {
            this.renderEntities(data.visible_entities);
        }
    }

    renderTiles(tiles) {
        // Clear old tiles
        this.tiles.forEach(tile => tile.destroy());
        this.tiles.clear();

        // Render new tiles
        tiles.forEach(tile => {
            const color = tile.type === 'wall' ? 0x666666 : 0x333333;
            const rect = this.add.rectangle(
                tile.x * this.tileSize,
                tile.y * this.tileSize,
                this.tileSize,
                this.tileSize,
                color
            );
            this.tiles.set(`${tile.x},${tile.y}`, rect);
        });
    }

    renderEntities(entities) {
        // Render other players
        if (entities.players) {
            entities.players.forEach(otherPlayer => {
                if (otherPlayer.id !== this.player.id) {
                    let sprite = this.otherPlayers.get(otherPlayer.id);

                    if (!sprite) {
                        sprite = this.add.circle(
                            otherPlayer.x * this.tileSize,
                            otherPlayer.y * this.tileSize,
                            8,
                            0x0088ff
                        );

                        sprite.nameText = this.add.text(
                            otherPlayer.x * this.tileSize,
                            otherPlayer.y * this.tileSize - 12,
                            otherPlayer.username,
                            { fontSize: '10px', color: '#0af' }
                        ).setOrigin(0.5);

                        this.otherPlayers.set(otherPlayer.id, sprite);
                    }

                    sprite.x = otherPlayer.x * this.tileSize;
                    sprite.y = otherPlayer.y * this.tileSize;
                    sprite.nameText.x = otherPlayer.x * this.tileSize;
                    sprite.nameText.y = otherPlayer.y * this.tileSize - 12;
                }
            });
        }

        // Render enemies
        if (entities.enemies) {
            entities.enemies.forEach(enemy => {
                let sprite = this.enemies.get(enemy.id);

                if (!sprite) {
                    sprite = this.add.circle(
                        enemy.x * this.tileSize,
                        enemy.y * this.tileSize,
                        8,
                        0xff0000
                    );
                    this.enemies.set(enemy.id, sprite);
                }

                sprite.x = enemy.x * this.tileSize;
                sprite.y = enemy.y * this.tileSize;
            });
        }
    }

    handleEntityMoved(data) {
        if (data.entity_type === 'player' && data.entity_id !== this.player.id) {
            const sprite = this.otherPlayers.get(data.entity_id);
            if (sprite) {
                sprite.x = data.to.x * this.tileSize;
                sprite.y = data.to.y * this.tileSize;
                sprite.nameText.x = data.to.x * this.tileSize;
                sprite.nameText.y = data.to.y * this.tileSize - 12;
            }
        }
    }

    removeOtherPlayer(playerId) {
        const sprite = this.otherPlayers.get(playerId);
        if (sprite) {
            sprite.destroy();
            if (sprite.nameText) sprite.nameText.destroy();
            this.otherPlayers.delete(playerId);
        }
    }

    onMapClick(pointer) {
        if (!this.player) return;

        const worldX = Math.floor((pointer.x + this.cameras.main.scrollX) / this.tileSize);
        const worldY = Math.floor((pointer.y + this.cameras.main.scrollY) / this.tileSize);

        // Request movement
        this.socket.emit('player_move', { x: worldX, y: worldY, sequence: Date.now() });
    }

    update() {
        if (!this.player || !this.socket) return;

        // WASD movement
        let moveX = 0;
        let moveY = 0;

        if (Phaser.Input.Keyboard.JustDown(this.wasd.W) || Phaser.Input.Keyboard.JustDown(this.cursors.up)) {
            moveY = -1;
        } else if (Phaser.Input.Keyboard.JustDown(this.wasd.S) || Phaser.Input.Keyboard.JustDown(this.cursors.down)) {
            moveY = 1;
        } else if (Phaser.Input.Keyboard.JustDown(this.wasd.A) || Phaser.Input.Keyboard.JustDown(this.cursors.left)) {
            moveX = -1;
        } else if (Phaser.Input.Keyboard.JustDown(this.wasd.D) || Phaser.Input.Keyboard.JustDown(this.cursors.right)) {
            moveX = 1;
        }

        if (moveX !== 0 || moveY !== 0) {
            const targetX = this.player.x + moveX;
            const targetY = this.player.y + moveY;
            this.socket.emit('player_move', { x: targetX, y: targetY, sequence: Date.now() });
        }
    }
}
