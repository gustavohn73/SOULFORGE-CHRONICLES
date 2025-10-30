/**
 * GameScene - Main game loop and rendering
 */
import io from 'socket.io-client';
import Player from '../entities/Player.js';

export class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene', active: true });
    }

    create() {
        console.log('GameScene started');

        // Game state
        this.player = null;
        this.playerEntity = null; // Player instance with visual effects
        this.myPlayerId = null;
        this.otherPlayers = new Map();
        this.enemies = new Map();
        this.tiles = [];

        // Camera setup
        this.tileSize = 32; // Aumentar tile size para visualização melhor
        this.cameras.main.setZoom(1.5);

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

        // Connection indicator
        this.createConnectionIndicator();

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
            console.log('🔌 Connected to server!');
            this.updateConnectionStatus('connecting', 'Connecting...');
        });

        this.socket.on('connected', (data) => {
            console.log('✅ Game started:', data);
            this.player = data.player;
            this.myPlayerId = data.player.id;

            // Update connection status
            this.updateConnectionStatus('connected', 'Connected');

            // Renderizar mundo PRIMEIRO
            if (data.world) {
                console.log('🗺️  Rendering initial world...');
                this.renderInitialWorld(data.world);
            }

            // Criar sprite do player DEPOIS do mundo
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
            console.warn('❌ Move rejected:', data.reason);
            // Rollback para posição correta do servidor
            if (this.playerEntity && data.current_position) {
                this.player.x = data.current_position.x;
                this.player.y = data.current_position.y;

                // Snap back usando Player.moveTo sem smooth
                this.playerEntity.moveTo(data.current_position.x, data.current_position.y, false);
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
            console.error('❌ Server error:', data);
            this.updateConnectionStatus('error', 'Error');
        });

        this.socket.on('disconnect', () => {
            console.warn('⚠️  Disconnected from server');
            this.updateConnectionStatus('disconnected', 'Disconnected');
        });

        this.socket.on('reconnecting', () => {
            console.log('🔄 Reconnecting...');
            this.updateConnectionStatus('connecting', 'Reconnecting...');
        });
    }

    createConnectionIndicator() {
        // Criar indicador de conexão no canto superior esquerdo
        const x = 60;
        const y = 30;

        this.connectionIndicator = this.add.circle(x, y, 8, 0xffaa00);
        this.connectionIndicator.setScrollFactor(0); // Fixo na tela
        this.connectionIndicator.setDepth(1000);

        this.connectionText = this.add.text(x + 20, y, 'Connecting...', {
            fontSize: '14px',
            color: '#ffffff',
            fontFamily: 'Arial'
        });
        this.connectionText.setScrollFactor(0);
        this.connectionText.setDepth(1000);
        this.connectionText.setOrigin(0, 0.5);
    }

    updateConnectionStatus(status, text) {
        if (!this.connectionIndicator || !this.connectionText) return;

        const colors = {
            'connecting': 0xffaa00,  // Orange
            'connected': 0x00ff00,   // Green
            'disconnected': 0xff0000, // Red
            'error': 0xff0000         // Red
        };

        this.connectionIndicator.setFillStyle(colors[status] || 0xffaa00);
        this.connectionText.setText(text);

        // Pulse animation for connecting
        if (status === 'connecting') {
            this.tweens.add({
                targets: this.connectionIndicator,
                alpha: 0.3,
                duration: 500,
                yoyo: true,
                repeat: -1
            });
        } else {
            this.tweens.killTweensOf(this.connectionIndicator);
            this.connectionIndicator.setAlpha(1);
        }
    }

    renderInitialWorld(worldData) {
        // Renderizar todos os tiles do mundo (não apenas os visíveis)
        // Isso é temporário para MVP - depois usaremos FOV
        console.log('🗺️  World data:', worldData);

        // ⭐ GRID LINES (renderizar PRIMEIRO, atrás de tudo)
        const gridGraphics = this.add.graphics();
        gridGraphics.lineStyle(1, 0x333333, 0.3);
        gridGraphics.setDepth(-1); // Atrás de tudo

        for (let x = 0; x <= 50; x++) {
            gridGraphics.moveTo(x * this.tileSize, 0);
            gridGraphics.lineTo(x * this.tileSize, 50 * this.tileSize);
        }
        for (let y = 0; y <= 50; y++) {
            gridGraphics.moveTo(0, y * this.tileSize);
            gridGraphics.lineTo(50 * this.tileSize, y * this.tileSize);
        }
        gridGraphics.strokePath();
        console.log('✅ Grid lines rendered');

        // Criar uma camada base com todos os tiles
        for (let y = 0; y < 50; y++) {
            for (let x = 0; x < 50; x++) {
                // Criar tile de parede por padrão (será sobrescrito se for floor)
                const color = 0x222222;
                const rect = this.add.rectangle(
                    x * this.tileSize + this.tileSize / 2,
                    y * this.tileSize + this.tileSize / 2,
                    this.tileSize,
                    this.tileSize,
                    color
                );
                rect.setStrokeStyle(1, 0x111111);
                rect.setDepth(0); // Acima do grid, abaixo dos players
                this.tiles.push(rect);
            }
        }

        // ⭐ SPAWN INDICATOR (marcador temporário onde players nascem)
        const spawnMarker = this.add.circle(25 * this.tileSize + 16, 25 * this.tileSize + 16, 24, 0xffff00, 0.6);
        spawnMarker.setDepth(5);
        this.tweens.add({
            targets: spawnMarker,
            alpha: 0,
            scale: 2,
            duration: 2000,
            ease: 'Power2',
            onComplete: () => spawnMarker.destroy()
        });

        console.log(`✅ Rendered ${this.tiles.length} tiles with grid`);
    }

    createPlayerSprite(playerData) {
        console.log('👤 Creating player entity at:', playerData.x, playerData.y);

        // ⭐ CRIAR PLAYER usando classe Player
        this.playerEntity = new Player(this, {
            ...playerData,
            id: this.myPlayerId
        });
        this.playerEntity.isMe = true;

        // ⭐ FLASH verde para indicar spawn
        this.cameras.main.flash(500, 0, 255, 0, true);

        // ⭐ FOCAR camera NO PLAYER
        console.log(`🎥 Focusing camera on player at (${playerData.x}, ${playerData.y})`);
        this.cameras.main.startFollow(this.playerEntity.container, true, 0.1, 0.1);

        // ⭐ ZOOM inicial
        this.cameras.main.setZoom(1.5);

        console.log('✅ Player entity created with visual effects');
    }

    handleStateUpdate(data) {
        // Update player data
        if (data.player) {
            this.player = data.player;

            // Update UI
            this.registry.set('player', this.player);

            // Update player entity position
            if (this.playerEntity) {
                // Usar moveTo sem animação para correções do servidor
                if (this.playerEntity.x !== this.player.x || this.playerEntity.y !== this.player.y) {
                    this.playerEntity.moveTo(this.player.x, this.player.y, false);
                }

                // Atualizar HP bar se existir
                if (this.player.hp !== undefined) {
                    this.playerEntity.updateHP(this.player.hp, this.player.max_hp);
                }
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
        // Atualizar tiles existentes com cores corretas baseado em visibilidade
        const visibleSet = new Set(tiles.map(t => `${t.x},${t.y}`));

        tiles.forEach(tileData => {
            const index = tileData.y * 50 + tileData.x;
            const rect = this.tiles[index];

            if (rect) {
                // Atualizar cor baseado no tipo
                const color = tileData.type === 'wall' ? 0x555555 : 0x444444;
                rect.setFillStyle(color);
                rect.setAlpha(1); // Totalmente visível

                // Borda mais clara para tiles visíveis
                rect.setStrokeStyle(1, 0x777777);
            }
        });

        // Escurecer tiles não visíveis (fog of war simples)
        this.tiles.forEach((rect, index) => {
            const x = index % 50;
            const y = Math.floor(index / 50);
            const key = `${x},${y}`;

            if (!visibleSet.has(key)) {
                rect.setAlpha(0.3); // Fog of war
                rect.setStrokeStyle(1, 0x111111);
            }
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
                            otherPlayer.x * this.tileSize + this.tileSize / 2,
                            otherPlayer.y * this.tileSize + this.tileSize / 2,
                            12,
                            0x0088ff
                        );

                        sprite.nameText = this.add.text(
                            otherPlayer.x * this.tileSize + this.tileSize / 2,
                            otherPlayer.y * this.tileSize - 16,
                            otherPlayer.username,
                            { fontSize: '14px', color: '#0af', fontFamily: 'Arial', fontStyle: 'bold' }
                        ).setOrigin(0.5);

                        this.otherPlayers.set(otherPlayer.id, sprite);
                    }

                    sprite.x = otherPlayer.x * this.tileSize + this.tileSize / 2;
                    sprite.y = otherPlayer.y * this.tileSize + this.tileSize / 2;
                    sprite.nameText.x = otherPlayer.x * this.tileSize + this.tileSize / 2;
                    sprite.nameText.y = otherPlayer.y * this.tileSize - 16;
                }
            });
        }

        // Render enemies
        if (entities.enemies) {
            entities.enemies.forEach(enemy => {
                let sprite = this.enemies.get(enemy.id);

                if (!sprite) {
                    sprite = this.add.circle(
                        enemy.x * this.tileSize + this.tileSize / 2,
                        enemy.y * this.tileSize + this.tileSize / 2,
                        12,
                        0xff0000
                    );
                    this.enemies.set(enemy.id, sprite);
                }

                sprite.x = enemy.x * this.tileSize + this.tileSize / 2;
                sprite.y = enemy.y * this.tileSize + this.tileSize / 2;
            });
        }
    }

    handleEntityMoved(data) {
        if (data.entity_type === 'player' && data.entity_id !== this.player.id) {
            const sprite = this.otherPlayers.get(data.entity_id);
            if (sprite) {
                // Smooth movement com tween
                this.tweens.add({
                    targets: sprite,
                    x: data.to.x * this.tileSize + this.tileSize / 2,
                    y: data.to.y * this.tileSize + this.tileSize / 2,
                    duration: 150,
                    ease: 'Linear'
                });

                this.tweens.add({
                    targets: sprite.nameText,
                    x: data.to.x * this.tileSize + this.tileSize / 2,
                    y: data.to.y * this.tileSize - 16,
                    duration: 150,
                    ease: 'Linear'
                });
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

            // Client-side prediction: move immediately
            this.player.x = targetX;
            this.player.y = targetY;

            // ⭐ Usar Player.moveTo para movimento suave
            if (this.playerEntity) {
                this.playerEntity.moveTo(targetX, targetY, true);
            }

            // Send to server
            this.socket.emit('player_move', { x: targetX, y: targetY, sequence: Date.now() });
        }
    }
}
