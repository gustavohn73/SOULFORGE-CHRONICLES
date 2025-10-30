/**
 * FOV System - Field of View with gradient visibility
 */
export default class FOVSystem {
    constructor(scene, radius = 10) {
        this.scene = scene;
        this.radius = radius;
        this.visibleTiles = new Map(); // key -> distance
    }

    calculate(playerX, playerY) {
        this.visibleTiles.clear();

        // ⭐ RAYCASTING em 360 graus
        for (let angle = 0; angle < 360; angle += 2) {
            const rad = angle * Math.PI / 180;

            for (let distance = 0; distance <= this.radius; distance += 0.5) {
                const x = Math.round(playerX + Math.cos(rad) * distance);
                const y = Math.round(playerY + Math.sin(rad) * distance);

                const key = `${x},${y}`;

                // Armazenar menor distância
                if (!this.visibleTiles.has(key) || this.visibleTiles.get(key) > distance) {
                    this.visibleTiles.set(key, distance);
                }

                // TODO: Parar em paredes (implementar depois quando houver tiles.isWalkable)
            }
        }

        return this.visibleTiles;
    }

    applyToTiles(tiles, playerX, playerY) {
        const visible = this.calculate(playerX, playerY);

        tiles.forEach((tile, index) => {
            const x = index % 50;
            const y = Math.floor(index / 50);
            const key = `${x},${y}`;

            if (visible.has(key)) {
                const distance = visible.get(key);

                // ⭐ GRADIENT de visibilidade baseado em distância
                const maxAlpha = 1.0;
                const minAlpha = 0.5;
                const alpha = maxAlpha - (distance / this.radius) * (maxAlpha - minAlpha);

                tile.setAlpha(Math.max(0.5, alpha));
                tile.clearTint(); // Sem tint (cores normais)
            } else {
                // ⭐ FOG OF WAR
                tile.setAlpha(0.2);
                tile.setTint(0x333333); // Tint escuro
            }
        });
    }

    // ⭐ VISUALIZAR raio de visão (debug)
    drawFOVCircle(graphics, playerX, playerY) {
        graphics.clear();
        graphics.lineStyle(2, 0x00ff00, 0.3);
        graphics.strokeCircle(
            playerX * 32 + 16,
            playerY * 32 + 16,
            this.radius * 32
        );
    }
}
