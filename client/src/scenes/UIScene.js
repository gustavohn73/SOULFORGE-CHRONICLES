/**
 * UIScene - HUD overlay with HP, marks, etc
 */
export class UIScene extends Phaser.Scene {
    constructor() {
        super({ key: 'UIScene', active: false });
    }

    create() {
        console.log('UIScene started');

        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        // Background panel
        this.add.rectangle(10, 10, 300, 200, 0x000000, 0.7).setOrigin(0);

        // Title
        this.add.text(20, 20, 'SOULFORGE CHRONICLES', {
            fontSize: '16px',
            fontWeight: 'bold',
            color: '#f44'
        });

        // HP bar
        this.hpText = this.add.text(20, 50, 'HP: 100/100', {
            fontSize: '14px',
            color: '#0f0'
        });

        // Marks
        this.add.text(20, 80, 'SOUL MARKS', {
            fontSize: '12px',
            color: '#fff',
            fontWeight: 'bold'
        });

        this.violenciaText = this.add.text(20, 100, 'VIOLENCIA: 0', {
            fontSize: '11px',
            color: '#f44'
        });

        this.controleText = this.add.text(20, 120, 'CONTROLE: 0', {
            fontSize: '11px',
            color: '#44f'
        });

        this.curiosidadeText = this.add.text(20, 140, 'CURIOSIDADE: 0', {
            fontSize: '11px',
            color: '#ff4'
        });

        this.memoriaText = this.add.text(20, 160, 'MEMORIA: 0', {
            fontSize: '11px',
            color: '#f4f'
        });

        // Level
        this.levelText = this.add.text(20, 185, 'Level: 1', {
            fontSize: '11px',
            color: '#fff'
        });

        // Update loop
        this.events.on('update', this.update, this);
    }

    update() {
        const player = this.registry.get('player');

        if (player) {
            this.hpText.setText(`HP: ${player.hp}/${player.max_hp}`);
            this.hpText.setColor(player.hp < player.max_hp * 0.3 ? '#f00' : '#0f0');

            this.violenciaText.setText(`VIOLENCIA: ${player.marks.VIOLENCIA}`);
            this.controleText.setText(`CONTROLE: ${player.marks.CONTROLE}`);
            this.curiosidadeText.setText(`CURIOSIDADE: ${player.marks.CURIOSIDADE}`);
            this.memoriaText.setText(`MEMORIA: ${player.marks.MEMORIA}`);

            this.levelText.setText(`Level: ${player.level}`);
        }
    }
}
