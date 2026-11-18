// Main Game Engine for MOMO MAZE Browser Edition
import * as THREE from './three.module.js';
import { MazeGenerator } from './maze_generator.js';
import { GolumoluCharacter } from './character.js';
import { GhostCharacter } from './ghosts.js';
import { EnvironmentBuilder } from './environment.js';
import { UIManager } from './ui.js';
import { audio } from './audio.js';

export class MomoGame {
  constructor() {
    this.container = document.getElementById('game-container');
    this.cellSize = 1.8;
    this.currentSkin = 'cream';
    this.currentLevelId = 1;
    this.isGrand31 = false;

    // Game state
    this.lives = 3;
    this.collectedMomos = 0;
    this.targetMomos = 6;
    this.elapsedTime = 0;
    this.invulnerableTimer = 0;

    // Moving Gates Phase (A vs B)
    this.activePhase = 'A';
    this.phaseTimer = 8.0;

    // Camera settings
    this.cameraMode = 'iso'; // 'iso' | 'top'
    this.camDistance = 12;
    this.camHeight = 14;

    // Input state
    this.keys = {};
    this.input = {
      moveX: 0,
      moveZ: 0,
      joystickX: 0,
      joystickY: 0
    };

    this.ghosts = [];

    this.initThree();
    this.initLighting();
    this.env = new EnvironmentBuilder(this.scene, this.cellSize);
    this.ui = new UIManager(this);

    this.bindInput();
    this.setupMenuDiorama();

    this.lastTime = performance.now();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initThree() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xF5EBD8); // Cozy warm sky
    this.scene.fog = new THREE.FogExp2(0xF5EBD8, 0.015);

    this.camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      250
    );
    this.camera.position.set(0, 18, 16);

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;

    this.container.appendChild(this.renderer.domElement);

    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  initLighting() {
    // Ambient fill
    const hemiLight = new THREE.HemisphereLight(0xFFF0D6, 0x8DAE65, 0.9);
    this.scene.add(hemiLight);

    // Peach sunlight
    this.sunLight = new THREE.DirectionalLight(0xFFE3B8, 1.8);
    this.sunLight.position.set(25, 45, 20);
    this.sunLight.castShadow = true;
    this.sunLight.shadow.mapSize.width = 2048;
    this.sunLight.shadow.mapSize.height = 2048;
    this.sunLight.shadow.camera.near = 0.5;
    this.sunLight.shadow.camera.far = 120;
    this.sunLight.shadow.camera.left = -30;
    this.sunLight.shadow.camera.right = 30;
    this.sunLight.shadow.camera.top = 30;
    this.sunLight.shadow.camera.bottom = -30;
    this.sunLight.shadow.bias = -0.0005;
    this.scene.add(this.sunLight);
  }

  bindInput() {
    window.addEventListener('keydown', (e) => {
      this.keys[e.code] = true;
      audio.init();
      audio.startBGM();
    });

    window.addEventListener('keyup', (e) => {
      this.keys[e.code] = false;
    });

    // Mouse wheel camera zoom
    window.addEventListener('wheel', (e) => {
      if (this.ui.currentScreen === 'game') {
        this.camDistance = Math.max(8, Math.min(26, this.camDistance + e.deltaY * 0.015));
      }
    }, { passive: true });
  }

  setupMenuDiorama() {
    // Build a miniature cozy garden preview for the menu using the Blender beauty maze
    this.mazeData = MazeGenerator.generateCampaignLevel(MazeGenerator.getLevelConfig(1));
    this.mazeData.isBeautyMaster = true;
    this.env.buildMaze(this.mazeData);

    this.player = new GolumoluCharacter(this.currentSkin);
    this.player.group.position.set(0, 0, 0);
    this.scene.add(this.player.group);

    this.ghosts = [
      new GhostCharacter('follower', 2, 2, this.cellSize),
      new GhostCharacter('cutter', -2, 2, this.cellSize)
    ];
    this.ghosts.forEach(g => {
      g.group.position.set(g.gridX * this.cellSize, 0, g.gridY * this.cellSize);
      this.scene.add(g.group);
    });

    this.camera.position.set(0, 8, 10);
    this.camera.lookAt(0, 1, 0);
  }

  startLevel(levelId) {
    this.currentLevelId = levelId;
    this.isGrand31 = false;
    const config = MazeGenerator.getLevelConfig(levelId);
    this.mazeData = MazeGenerator.generateCampaignLevel(config);
    if (levelId === 1) {
      this.mazeData.isBeautyMaster = true;
    }
    this.initPlaySession(config.name, config.target_momos, !!config.has_moving_gates);
  }

  startGrand31Maze() {
    this.isGrand31 = true;
    this.mazeData = MazeGenerator.getMaster31x31Maze();
    this.initPlaySession('Master 31x31 Grand Maze', 21, true);
  }

  initPlaySession(levelName, targetMomos, hasMovingGates) {
    this.currentLevelName = levelName;
    this.lives = 3;
    this.collectedMomos = 0;
    this.targetMomos = targetMomos;
    this.elapsedTime = 0;
    this.invulnerableTimer = 0;
    this.activePhase = 'A';
    this.phaseTimer = 8.0;
    this.hasMovingGates = hasMovingGates;

    // Clear previous entities
    this.ghosts.forEach(g => this.scene.remove(g.group));
    this.ghosts = [];

    if (this.player) {
      this.scene.remove(this.player.group);
    }

    // Build environment
    this.env.buildMaze(this.mazeData);

    // Spawn player at start position
    const offset = (this.mazeData.size - 1) / 2;
    this.player = new GolumoluCharacter(this.currentSkin);
    this.player.gridX = this.mazeData.playerStart.x;
    this.player.gridY = this.mazeData.playerStart.y;
    this.player.worldX = (this.player.gridX - offset) * this.cellSize;
    this.player.worldZ = (this.player.gridY - offset) * this.cellSize;
    this.player.group.position.set(this.player.worldX, 0, this.player.worldZ);
    this.scene.add(this.player.group);

    // Spawn Ghost Spirits
    const ghostConfigs = this.isGrand31
      ? [{ type: 'follower', x: 11, y: 15 }, { type: 'cutter', x: 19, y: 15 }, { type: 'wanderer', x: 15, y: 25 }]
      : [{ type: 'follower', x: this.mazeData.size - 3, y: this.mazeData.size - 3 }];

    if (!this.isGrand31 && this.currentLevelId >= 3) {
      ghostConfigs.push({ type: 'cutter', x: this.mazeData.size - 3, y: 2 });
    }
    if (!this.isGrand31 && this.currentLevelId >= 6) {
      ghostConfigs.push({ type: 'wanderer', x: 2, y: this.mazeData.size - 3 });
    }

    ghostConfigs.forEach(cfg => {
      const ghost = new GhostCharacter(cfg.type, cfg.x, cfg.y, this.cellSize);
      ghost.group.position.set((cfg.x - offset) * this.cellSize, 0, (cfg.y - offset) * this.cellSize);
      this.scene.add(ghost.group);
      this.ghosts.push(ghost);
    });

    this.ui.showScreen('game');
    this.ui.updateHUD(this.getState());
  }

  restartLevel() {
    if (this.isGrand31) {
      this.startGrand31Maze();
    } else {
      this.startLevel(this.currentLevelId);
    }
  }

  nextLevel() {
    this.startLevel(this.currentLevelId + 1);
  }

  quitToMenu() {
    this.ui.showScreen('menu');
    this.setupMenuDiorama();
  }

  setSkin(skinKey) {
    this.currentSkin = skinKey;
    if (this.player) {
      this.player.setSkin(skinKey);
    }
  }

  setCameraMode(mode) {
    this.cameraMode = mode;
  }

  toggleCameraMode() {
    this.cameraMode = this.cameraMode === 'iso' ? 'top' : 'iso';
  }

  getState() {
    return {
      lives: this.lives,
      collectedMomos: this.collectedMomos,
      targetMomos: this.targetMomos,
      elapsedTime: this.elapsedTime,
      activePhase: this.activePhase,
      phaseTimer: this.phaseTimer,
      hasMovingGates: this.hasMovingGates,
      mazeData: this.mazeData,
      player: this.player,
      ghosts: this.ghosts
    };
  }

  handlePlayerInput(delta) {
    let dx = 0;
    let dz = 0;

    if (this.keys['KeyW'] || this.keys['ArrowUp']) dz -= 1;
    if (this.keys['KeyS'] || this.keys['ArrowDown']) dz += 1;
    if (this.keys['KeyA'] || this.keys['ArrowLeft']) dx -= 1;
    if (this.keys['KeyD'] || this.keys['ArrowRight']) dx += 1;

    // Add virtual joystick input
    if (Math.hypot(this.input.joystickX, this.input.joystickY) > 0.1) {
      dx += this.input.joystickX;
      dz += this.input.joystickY;
    }

    const len = Math.hypot(dx, dz);
    const speed = 4.2;

    if (len > 0.1) {
      dx = dx / len;
      dz = dz / len;

      this.player.isMoving = true;
      this.player.dirX = dx;
      this.player.dirY = dz;

      // Rotate player facing direction smoothly
      const targetAngle = Math.atan2(dx, dz);
      let curAngle = this.player.modelRoot.rotation.y;
      let diff = targetAngle - curAngle;
      while (diff < -Math.PI) diff += Math.PI * 2;
      while (diff > Math.PI) diff -= Math.PI * 2;
      this.player.modelRoot.rotation.y += diff * Math.min(1.0, delta * 12);

      // Desired new world position
      const nextX = this.player.worldX + dx * speed * delta;
      const nextZ = this.player.worldZ + dz * speed * delta;

      // Collision detection against walls & moving gates
      const offset = (this.mazeData.size - 1) / 2;
      const radius = 0.38;

      const canMoveTo = (wx, wz) => {
        const gx = Math.round(wx / this.cellSize + offset);
        const gy = Math.round(wz / this.cellSize + offset);
        if (gx < 0 || gx >= this.mazeData.size || gy < 0 || gy >= this.mazeData.size) return false;

        const cell = this.mazeData.grid[gy][gx];
        if (cell === 1) return false; // Wall

        // Moving Gates
        if (cell === 2 && this.activePhase === 'A') return false; // Gate A closed in Phase A
        if (cell === 3 && this.activePhase === 'B') return false; // Gate B closed in Phase B

        return true;
      };

      // Slide along walls (test X and Z independently)
      if (canMoveTo(nextX, this.player.worldZ)) {
        this.player.worldX = nextX;
      }
      if (canMoveTo(this.player.worldX, nextZ)) {
        this.player.worldZ = nextZ;
      }

      this.player.group.position.x = this.player.worldX;
      this.player.group.position.z = this.player.worldZ;

      // Update player grid coordinates
      this.player.gridX = this.player.worldX / this.cellSize + offset;
      this.player.gridY = this.player.worldZ / this.cellSize + offset;

      // Cute footstep sound
      if (Math.random() < delta * 4) {
        audio.playStep();
      }
    } else {
      this.player.isMoving = false;
    }
  }

  checkMomoCollection() {
    const pX = Math.round(this.player.gridX);
    const pY = Math.round(this.player.gridY);

    if (this.env.collectMomo(pX, pY)) {
      this.collectedMomos++;
      this.player.triggerEat();
      audio.playCollectMomo();

      // Check if all collected
      if (this.collectedMomos >= this.targetMomos) {
        audio.playCollectGolden();
      }
    }
  }

  checkExitGate() {
    if (this.collectedMomos < this.targetMomos) return;
    const pX = Math.round(this.player.gridX);
    const pY = Math.round(this.player.gridY);

    if (pX === this.mazeData.exitGate.x && pY === this.mazeData.exitGate.y) {
      // Victory!
      this.ui.showVictory({
        levelName: this.currentLevelName,
        time: this.elapsedTime,
        collected: this.collectedMomos,
        total: this.targetMomos
      });
    }
  }

  checkGhostCollisions(delta) {
    if (this.invulnerableTimer > 0) {
      this.invulnerableTimer -= delta;
      this.player.modelRoot.visible = Math.floor(this.invulnerableTimer * 12) % 2 === 0;
      return;
    } else {
      this.player.modelRoot.visible = true;
    }

    const pPos = this.player.group.position;
    for (const g of this.ghosts) {
      const dist = Math.hypot(pPos.x - g.group.position.x, pPos.z - g.group.position.z);
      if (dist < 0.65) {
        // Hit by ghost!
        this.lives--;
        this.invulnerableTimer = 2.0;
        audio.playHit();

        if (this.lives <= 0) {
          this.ui.showDefeat();
        }
        break;
      }
    }
  }

  updateCamera(delta) {
    if (this.ui.currentScreen === 'game' && this.player) {
      const pPos = this.player.group.position;

      if (this.cameraMode === 'iso') {
        const targetCamX = pPos.x;
        const targetCamY = pPos.y + this.camHeight;
        const targetCamZ = pPos.z + this.camDistance;

        this.camera.position.x += (targetCamX - this.camera.position.x) * Math.min(1.0, delta * 6);
        this.camera.position.y += (targetCamY - this.camera.position.y) * Math.min(1.0, delta * 6);
        this.camera.position.z += (targetCamZ - this.camera.position.z) * Math.min(1.0, delta * 6);
        this.camera.lookAt(pPos.x, pPos.y + 0.6, pPos.z);
      } else {
        // Top-down camera
        const targetCamX = pPos.x;
        const targetCamY = pPos.y + this.camHeight * 1.5;
        const targetCamZ = pPos.z + 0.01;

        this.camera.position.x += (targetCamX - this.camera.position.x) * Math.min(1.0, delta * 6);
        this.camera.position.y += (targetCamY - this.camera.position.y) * Math.min(1.0, delta * 6);
        this.camera.position.z += (targetCamZ - this.camera.position.z) * Math.min(1.0, delta * 6);
        this.camera.lookAt(pPos.x, pPos.y, pPos.z);
      }
    } else {
      // Menu rotating diorama camera
      const time = performance.now() * 0.0003;
      this.camera.position.x = Math.sin(time) * 14;
      this.camera.position.z = Math.cos(time) * 14;
      this.camera.position.y = 9 + Math.sin(time * 2) * 1.5;
      this.camera.lookAt(0, 1, 0);
    }
  }

  animate() {
    requestAnimationFrame(this.animate);

    const now = performance.now();
    const delta = Math.min(0.1, (now - this.lastTime) * 0.001);
    this.lastTime = now;

    if (!this.ui.isPaused) {
      if (this.ui.currentScreen === 'game') {
        this.elapsedTime += delta;

        // Gate phase timer
        if (this.hasMovingGates) {
          this.phaseTimer -= delta;
          if (this.phaseTimer <= 0) {
            this.phaseTimer = 8.0;
            this.activePhase = this.activePhase === 'A' ? 'B' : 'A';
            audio.playGateToggle();
          }
        }

        this.handlePlayerInput(delta);
        this.checkMomoCollection();
        this.checkExitGate();
        this.checkGhostCollisions(delta);

        // Update ghosts AI
        this.ghosts.forEach(g => {
          g.update(delta, this.player, this.mazeData.grid, this.mazeData.size, this.activePhase);
        });

        this.ui.updateHUD(this.getState());
      }

      if (this.player) {
        this.player.update(delta);
      }

      this.env.update(delta, this.activePhase);
    }

    this.updateCamera(delta);
    this.renderer.render(this.scene, this.camera);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.game = new MomoGame();
});
