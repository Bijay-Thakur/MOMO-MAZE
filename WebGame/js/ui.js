// UI Controller & Screen Management for MOMO MAZE
import { CAMPAIGN_LEVELS } from './game_data.js';
import { SKINS } from './character.js';
import { GHOST_TYPES } from './ghosts.js';
import { audio } from './audio.js';

export class UIManager {
  constructor(game) {
    this.game = game;
    this.currentScreen = 'menu';
    this.isPaused = false;
    this.isMapOpen = false;

    this.cacheDOMElements();
    this.bindEvents();
    this.renderLevelSelect();
    this.renderCloset();
    this.renderSpiritBook();
  }

  cacheDOMElements() {
    // Screens
    this.screenMenu = document.getElementById('screen-menu');
    this.screenLevels = document.getElementById('screen-levels');
    this.screenCloset = document.getElementById('screen-closet');
    this.screenSpirits = document.getElementById('screen-spirits');
    this.screenSettings = document.getElementById('screen-settings');
    this.screenHUD = document.getElementById('screen-hud');
    this.screenPause = document.getElementById('screen-pause');
    this.screenVictory = document.getElementById('screen-victory');
    this.screenDefeat = document.getElementById('screen-defeat');
    this.mapOverlay = document.getElementById('map-overlay');

    // HUD Elements
    this.hudLives = document.getElementById('hud-lives');
    this.hudMomos = document.getElementById('hud-momos');
    this.hudTimer = document.getElementById('hud-timer');
    this.hudGatePhase = document.getElementById('hud-gate-phase');
    this.hudGateTimer = document.getElementById('hud-gate-timer');
    this.minimapCanvas = document.getElementById('minimap-canvas');
    this.minimapCtx = this.minimapCanvas.getContext('2d');
    this.fullmapCanvas = document.getElementById('fullmap-canvas');
    this.fullmapCtx = this.fullmapCanvas.getContext('2d');

    // Victory/Defeat Details
    this.vicLevelName = document.getElementById('vic-level-name');
    this.vicTime = document.getElementById('vic-time');
    this.vicMomos = document.getElementById('vic-momos');
    this.vicStars = document.getElementById('vic-stars');

    // Virtual Joystick
    this.joystickBase = document.getElementById('virtual-joystick');
    this.joystickStick = document.getElementById('joystick-stick');
  }

  bindEvents() {
    // Menu navigation
    document.getElementById('btn-play-campaign').onclick = () => {
      audio.playClick();
      this.showScreen('levels');
    };

    document.getElementById('btn-play-grand-31').onclick = () => {
      audio.playClick();
      this.game.startGrand31Maze();
    };

    document.getElementById('btn-open-closet').onclick = () => {
      audio.playClick();
      this.showScreen('closet');
    };

    document.getElementById('btn-open-spirits').onclick = () => {
      audio.playClick();
      this.showScreen('spirits');
    };

    document.getElementById('btn-open-settings').onclick = () => {
      audio.playClick();
      this.showScreen('settings');
    };

    // Back to Menu buttons
    document.querySelectorAll('.btn-back-to-menu').forEach(b => {
      b.onclick = () => {
        audio.playClick();
        this.showScreen('menu');
      };
    });

    // In-game buttons
    document.getElementById('btn-hud-pause').onclick = () => {
      audio.playClick();
      this.togglePause();
    };

    document.getElementById('btn-hud-map').onclick = () => {
      audio.playClick();
      this.toggleMapOverlay();
    };

    document.getElementById('btn-close-map').onclick = () => {
      audio.playClick();
      this.toggleMapOverlay(false);
    };

    document.getElementById('btn-hud-camera').onclick = () => {
      audio.playClick();
      this.game.toggleCameraMode();
    };

    // Pause menu buttons
    document.getElementById('btn-pause-resume').onclick = () => {
      audio.playClick();
      this.togglePause(false);
    };

    document.getElementById('btn-pause-restart').onclick = () => {
      audio.playClick();
      this.togglePause(false);
      this.game.restartLevel();
    };

    document.getElementById('btn-pause-menu').onclick = () => {
      audio.playClick();
      this.togglePause(false);
      this.game.quitToMenu();
    };

    // Victory buttons
    document.getElementById('btn-vic-next').onclick = () => {
      audio.playClick();
      this.game.nextLevel();
    };

    document.getElementById('btn-vic-replay').onclick = () => {
      audio.playClick();
      this.game.restartLevel();
    };

    document.getElementById('btn-vic-menu').onclick = () => {
      audio.playClick();
      this.game.quitToMenu();
    };

    // Defeat buttons
    document.getElementById('btn-def-retry').onclick = () => {
      audio.playClick();
      this.game.restartLevel();
    };

    document.getElementById('btn-def-menu').onclick = () => {
      audio.playClick();
      this.game.quitToMenu();
    };

    // Sound toggle
    const chkMute = document.getElementById('chk-mute');
    if (chkMute) {
      chkMute.onchange = (e) => {
        audio.setMuted(e.target.checked);
      };
    }

    // Camera mode setting select
    const selCam = document.getElementById('sel-camera-mode');
    if (selCam) {
      selCam.onchange = (e) => {
        this.game.setCameraMode(e.target.value);
      };
    }

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {
        if (this.currentScreen === 'game') {
          this.togglePause();
        }
      } else if (e.key === 'm' || e.key === 'M') {
        if (this.currentScreen === 'game') {
          this.toggleMapOverlay();
        }
      } else if (e.key === 'c' || e.key === 'C') {
        if (this.currentScreen === 'game') {
          this.game.toggleCameraMode();
        }
      }
    });

    this.setupVirtualJoystick();
  }

  setupVirtualJoystick() {
    let active = false;
    let startX = 0, startY = 0;

    const handleStart = (clientX, clientY) => {
      active = true;
      const rect = this.joystickBase.getBoundingClientRect();
      startX = rect.left + rect.width / 2;
      startY = rect.top + rect.height / 2;
      handleMove(clientX, clientY);
    };

    const handleMove = (clientX, clientY) => {
      if (!active) return;
      let dx = clientX - startX;
      let dy = clientY - startY;
      const dist = Math.hypot(dx, dy);
      const maxDist = 45;

      if (dist > maxDist) {
        dx = (dx / dist) * maxDist;
        dy = (dy / dist) * maxDist;
      }

      this.joystickStick.style.transform = `translate(${dx}px, ${dy}px)`;
      // Normalized input (-1 to 1)
      this.game.input.joystickX = dx / maxDist;
      this.game.input.joystickY = dy / maxDist;
    };

    const handleEnd = () => {
      active = false;
      this.joystickStick.style.transform = 'translate(0px, 0px)';
      this.game.input.joystickX = 0;
      this.game.input.joystickY = 0;
    };

    this.joystickBase.addEventListener('mousedown', (e) => handleStart(e.clientX, e.clientY));
    window.addEventListener('mousemove', (e) => handleMove(e.clientX, e.clientY));
    window.addEventListener('mouseup', handleEnd);

    this.joystickBase.addEventListener('touchstart', (e) => {
      if (e.touches[0]) handleStart(e.touches[0].clientX, e.touches[0].clientY);
    });
    window.addEventListener('touchmove', (e) => {
      if (e.touches[0]) handleMove(e.touches[0].clientX, e.touches[0].clientY);
    });
    window.addEventListener('touchend', handleEnd);
  }

  showScreen(name) {
    this.currentScreen = name;
    const screens = [
      this.screenMenu,
      this.screenLevels,
      this.screenCloset,
      this.screenSpirits,
      this.screenSettings,
      this.screenHUD,
      this.screenPause,
      this.screenVictory,
      this.screenDefeat
    ];

    screens.forEach(s => {
      if (s) s.classList.remove('active');
    });

    if (name === 'menu') this.screenMenu.classList.add('active');
    else if (name === 'levels') this.screenLevels.classList.add('active');
    else if (name === 'closet') this.screenCloset.classList.add('active');
    else if (name === 'spirits') this.screenSpirits.classList.add('active');
    else if (name === 'settings') this.screenSettings.classList.add('active');
    else if (name === 'game') this.screenHUD.classList.add('active');
  }

  togglePause(forceState = null) {
    this.isPaused = forceState !== null ? forceState : !this.isPaused;
    if (this.isPaused) {
      this.screenPause.classList.add('active');
    } else {
      this.screenPause.classList.remove('active');
    }
  }

  toggleMapOverlay(forceState = null) {
    this.isMapOpen = forceState !== null ? forceState : !this.isMapOpen;
    if (this.isMapOpen) {
      this.mapOverlay.classList.add('active');
      this.drawFullMap();
    } else {
      this.mapOverlay.classList.remove('active');
    }
  }

  updateHUD(state) {
    // Lives
    let heartsHtml = '';
    for (let i = 0; i < 3; i++) {
      heartsHtml += i < state.lives ? '❤️ ' : '🖤 ';
    }
    this.hudLives.innerHTML = heartsHtml;

    // Momos
    this.hudMomos.innerText = `🥟 ${state.collectedMomos} / ${state.targetMomos}`;

    // Timer
    const mins = Math.floor(state.elapsedTime / 60);
    const secs = Math.floor(state.elapsedTime % 60);
    this.hudTimer.innerText = `⏱️ ${mins}:${secs < 10 ? '0' : ''}${secs}`;

    // Gates
    if (state.hasMovingGates) {
      this.hudGatePhase.innerText = `Phase ${state.activePhase}`;
      this.hudGateTimer.innerText = `${Math.ceil(state.phaseTimer)}s`;
    } else {
      this.hudGatePhase.innerText = 'Gates Open';
      this.hudGateTimer.innerText = '';
    }

    this.drawMinimap(state);
    if (this.isMapOpen) {
      this.drawFullMap(state);
    }
  }

  drawMinimap(state) {
    const ctx = this.minimapCtx;
    const canvas = this.minimapCanvas;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const size = state.mazeData.size;
    const cellSize = w / size;

    // Draw walls
    ctx.fillStyle = '#4E8C2A';
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (state.mazeData.grid[y][x] === 1) {
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }

    // Draw Momos
    ctx.fillStyle = '#FFE082';
    state.mazeData.collectibles.forEach(c => {
      if (!c.collected) {
        ctx.beginPath();
        ctx.arc((c.x + 0.5) * cellSize, (c.y + 0.5) * cellSize, cellSize * 0.45, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Draw Exit
    if (state.mazeData.exitGate) {
      ctx.fillStyle = '#FFB300';
      ctx.fillRect(
        state.mazeData.exitGate.x * cellSize,
        state.mazeData.exitGate.y * cellSize,
        cellSize,
        cellSize
      );
    }

    // Draw Ghosts
    state.ghosts.forEach(g => {
      ctx.fillStyle = g.typeKey === 'cutter' ? '#FF7043' : (g.typeKey === 'wanderer' ? '#AB47BC' : '#FFF9C4');
      ctx.beginPath();
      ctx.arc((g.gridX + 0.5) * cellSize, (g.gridY + 0.5) * cellSize, cellSize * 0.6, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw Player
    ctx.fillStyle = '#FF7043';
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc((state.player.gridX + 0.5) * cellSize, (state.player.gridY + 0.5) * cellSize, cellSize * 0.75, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  drawFullMap(state = this.game.getState()) {
    if (!state || !state.mazeData) return;
    const ctx = this.fullmapCtx;
    const canvas = this.fullmapCanvas;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const size = state.mazeData.size;
    const cellSize = w / size;

    // Draw walls
    ctx.fillStyle = '#3E7824';
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (state.mazeData.grid[y][x] === 1) {
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }

    // Draw moving gates
    if (state.mazeData.movingGates) {
      state.mazeData.movingGates.forEach(g => {
        ctx.fillStyle = g.phase === state.activePhase ? '#D32F2F' : '#388E3C';
        ctx.fillRect(g.x * cellSize, g.y * cellSize, cellSize, cellSize);
      });
    }

    // Draw Momos
    ctx.fillStyle = '#FFD54F';
    state.mazeData.collectibles.forEach(c => {
      if (!c.collected) {
        ctx.beginPath();
        ctx.arc((c.x + 0.5) * cellSize, (c.y + 0.5) * cellSize, cellSize * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Draw Exit
    if (state.mazeData.exitGate) {
      ctx.fillStyle = '#FFA000';
      ctx.fillRect(
        state.mazeData.exitGate.x * cellSize,
        state.mazeData.exitGate.y * cellSize,
        cellSize,
        cellSize
      );
    }

    // Draw Player Beacon
    ctx.fillStyle = '#E64A19';
    ctx.beginPath();
    ctx.arc((state.player.gridX + 0.5) * cellSize, (state.player.gridY + 0.5) * cellSize, cellSize * 0.85, 0, Math.PI * 2);
    ctx.fill();
  }

  showVictory(stats) {
    audio.playWin();
    this.screenVictory.classList.add('active');
    this.vicLevelName.innerText = stats.levelName;
    this.vicTime.innerText = `Time: ${Math.floor(stats.time)}s`;
    this.vicMomos.innerText = `Momos: ${stats.collected}/${stats.total}`;

    // Stars rating
    let starsHtml = '⭐ ⭐ ⭐';
    if (stats.time > 90) starsHtml = '⭐ ⭐';
    if (stats.time > 150) starsHtml = '⭐';
    this.vicStars.innerHTML = starsHtml;
  }

  showDefeat() {
    audio.playDefeat();
    this.screenDefeat.classList.add('active');
  }

  renderLevelSelect() {
    const container = document.getElementById('levels-grid');
    if (!container) return;
    container.innerHTML = '';

    // Group by chapter
    let currentChapter = 0;
    CAMPAIGN_LEVELS.forEach(lvl => {
      if (lvl.chapter !== currentChapter) {
        currentChapter = lvl.chapter;
        const chapHeader = document.createElement('div');
        chapHeader.className = 'chapter-header';
        chapHeader.innerHTML = `<h3>Chapter ${lvl.chapter}: ${lvl.chapter_name}</h3>`;
        container.appendChild(chapHeader);
      }

      const card = document.createElement('div');
      card.className = 'level-card';
      card.innerHTML = `
        <div class="level-num">Level ${lvl.level_id}</div>
        <div class="level-title">${lvl.name}</div>
        <div class="level-info">🥟 ${lvl.target_momos} Momos | ${lvl.grid_size}x${lvl.grid_size} | 👻 ${lvl.starting_spirits}</div>
      `;
      card.onclick = () => {
        audio.playClick();
        this.game.startLevel(lvl.level_id);
      };
      container.appendChild(card);
    });
  }

  renderCloset() {
    const list = document.getElementById('closet-skins-list');
    if (!list) return;
    list.innerHTML = '';

    Object.keys(SKINS).forEach(key => {
      const s = SKINS[key];
      const btn = document.createElement('div');
      btn.className = `skin-pill ${key === this.game.currentSkin ? 'selected' : ''}`;
      btn.innerHTML = `
        <span class="skin-circle" style="background-color: #${s.body.toString(16).padStart(6, '0')}"></span>
        <span>${s.name}</span>
      `;
      btn.onclick = () => {
        audio.playClick();
        document.querySelectorAll('.skin-pill').forEach(p => p.classList.remove('selected'));
        btn.classList.add('selected');
        this.game.setSkin(key);
      };
      list.appendChild(btn);
    });
  }

  renderSpiritBook() {
    const container = document.getElementById('spirits-list');
    if (!container) return;
    container.innerHTML = '';

    Object.keys(GHOST_TYPES).forEach(key => {
      const g = GHOST_TYPES[key];
      const card = document.createElement('div');
      card.className = 'spirit-card';
      card.innerHTML = `
        <div class="spirit-header">
          <span class="spirit-icon" style="background-color: #${g.glow.toString(16).padStart(6, '0')}">👻</span>
          <h4>${g.name}</h4>
        </div>
        <p class="spirit-desc">${g.desc}</p>
        <div class="spirit-stat">Speed: <strong>${g.speed}x</strong> | Eye Style: <strong>${g.eyeType}</strong></div>
      `;
      container.appendChild(card);
    });
  }
}
