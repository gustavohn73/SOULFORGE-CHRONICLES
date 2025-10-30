/**
 * Soulforge Chronicles - Main Entry Point
 */
import Phaser from 'phaser';
import { GameScene } from './scenes/GameScene.js';
import { UIScene } from './scenes/UIScene.js';

// Login handling
const loginScreen = document.getElementById('login-screen');
const usernameInput = document.getElementById('username-input');
const startButton = document.getElementById('start-button');

let gameStarted = false;

startButton.addEventListener('click', () => {
    const username = usernameInput.value.trim();

    if (username.length >= 3) {
        loginScreen.style.display = 'none';

        if (!gameStarted) {
            startGame(username);
            gameStarted = true;
        }
    } else {
        alert('Username must be at least 3 characters');
    }
});

usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        startButton.click();
    }
});

function startGame(username) {
    const config = {
        type: Phaser.AUTO,
        width: 1280,
        height: 720,
        parent: 'game-container',
        backgroundColor: '#000000',
        scene: [GameScene, UIScene],
        physics: {
            default: 'arcade',
            arcade: {
                gravity: { y: 0 },
                debug: false
            }
        },
        scale: {
            mode: Phaser.Scale.FIT,
            autoCenter: Phaser.Scale.CENTER_BOTH
        }
    };

    const game = new Phaser.Game(config);

    // Pass username to game
    game.registry.set('username', username);
    game.registry.set('serverUrl', 'http://localhost:5000');
}
