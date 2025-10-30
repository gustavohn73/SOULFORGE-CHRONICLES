/**
 * Player Entity - Visual representation with effects
 */
export default class Player {
    constructor(scene, data) {
        this.scene = scene;
        this.id = data.id || data.player_id;
        this.username = data.username;
        this.x = data.x;
        this.y = data.y;
        this.isMe = false;

        console.log(`👤 Creating player: ${this.username} at (${this.x}, ${this.y}), isMe: ${this.isMe}`);

        // Configurações visuais
        const color = this.isMe ? 0x00ff00 : 0x0088ff;
        const size = this.isMe ? 30 : 26;

        // ⭐ CONTAINER para agrupar todos os elementos
        this.container = scene.add.container(
            this.x * 32 + 16,
            this.y * 32 + 16
        );
        this.container.setDepth(10); // Acima dos tiles

        // ⭐ SHADOW (sombra embaixo)
        this.shadow = scene.add.ellipse(0, 8, 32, 16, 0x000000, 0.4);
        this.container.add(this.shadow);

        // ⭐ GLOW EFFECT (se for player principal)
        if (this.isMe) {
            this.glow = scene.add.circle(0, 0, 20, 0x00ff00, 0.3);
            this.container.add(this.glow);

            // Pulsação do glow
            scene.tweens.add({
                targets: this.glow,
                scale: { from: 1, to: 1.4 },
                alpha: { from: 0.3, to: 0.5 },
                duration: 1000,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }

        // ⭐ SPRITE PRINCIPAL (quadrado/círculo)
        this.sprite = scene.add.circle(0, 0, size / 2, color);
        this.sprite.setStrokeStyle(3, 0xffffff); // borda branca grossa
        this.container.add(this.sprite);

        // ⭐ NOME com background
        const nameWidth = this.username.length * 8 + 8;
        this.nameBackground = scene.add.rectangle(
            0, -28,
            nameWidth, 18,
            0x000000, 0.8
        );
        this.nameBackground.setStrokeStyle(1, this.isMe ? 0x00ff00 : 0x0088ff);
        this.container.add(this.nameBackground);

        this.nameText = scene.add.text(0, -28, this.username, {
            fontSize: '13px',
            fill: this.isMe ? '#00ff00' : '#ffffff',
            stroke: '#000000',
            strokeThickness: 3,
            fontFamily: 'Arial',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        this.container.add(this.nameText);

        // ⭐ HP BAR (se for meu player)
        if (this.isMe) {
            this.hpBarBg = scene.add.rectangle(0, 24, 32, 5, 0x660000);
            this.hpBar = scene.add.rectangle(-16, 24, 32, 5, 0x00ff00).setOrigin(0, 0.5);
            this.container.add(this.hpBarBg);
            this.container.add(this.hpBar);
        }

        console.log(`✅ Player container created at pixel position (${this.container.x}, ${this.container.y})`);
    }

    moveTo(x, y, smooth = true) {
        this.x = x;
        this.y = y;

        const targetX = x * 32 + 16;
        const targetY = y * 32 + 16;

        console.log(`🚶 Moving player to grid (${x}, ${y}) = pixel (${targetX}, ${targetY})`);

        if (smooth) {
            this.scene.tweens.add({
                targets: this.container,
                x: targetX,
                y: targetY,
                duration: 150,
                ease: 'Power2'
            });

            // Efeito de movimento
            if (this.isMe) {
                this.createMovementEffect();
            }
        } else {
            this.container.setPosition(targetX, targetY);
        }
    }

    createMovementEffect() {
        // Pequeno squash & stretch
        this.scene.tweens.add({
            targets: this.sprite,
            scaleX: 1.1,
            scaleY: 0.9,
            duration: 75,
            yoyo: true,
            ease: 'Sine.easeInOut'
        });
    }

    updateHP(current, max) {
        if (this.hpBar) {
            const width = (current / max) * 32;
            this.hpBar.width = width;

            // Mudar cor baseado em HP
            if (current / max > 0.5) {
                this.hpBar.setFillStyle(0x00ff00); // Verde
            } else if (current / max > 0.25) {
                this.hpBar.setFillStyle(0xffaa00); // Amarelo
            } else {
                this.hpBar.setFillStyle(0xff0000); // Vermelho
            }
        }
    }

    destroy() {
        console.log(`🗑️  Destroying player: ${this.username}`);
        if (this.container) {
            this.container.destroy();
        }
    }
}
