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
    this.cellSize = 2.0;
    this.currentSkin = 'cream';
    this.currentLevelId = 1;
    this.isGrand31 = false;

    // Game state
    this.lives = 3;
    this.collectedMomos = 0;
    this.targetMomos = 12;
    this.elapsedTime = 0;
    this.invulnerableTimer = 0;
    this.ghostDivideStage = 1; // 1 ghost at start -> 2 at 30s -> 3 at 60s

    // Moving Gates Phase (A vs B)
    this.activePhase = 'A';
    this.phaseTimer = 8.0;

    // Camera settings (hero 3/4 isometric perspective matching Reference 08-A)
    this.cameraMode = 'iso'; // 'iso' | 'top'
    this.camDistance = 9.5;
    this.camHeight = 11.5;

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
    this.scene.background = new THREE.Color(0x8ED6F8); // Bright sunny garden sky
    this.scene.fog = new THREE.FogExp2(0x8ED6F8, 0.006); // Soft atmospheric distance haze

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
    this.renderer.toneMappingExposure = 1.05;

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
    const handleKeyDown = (e) => {
      this.keys[e.code] = true;
      this.keys[e.key] = true;
      if (e.key) this.keys[e.key.toLowerCase()] = true;
      audio.init();
      audio.startBGM();
    };

    const handleKeyUp = (e) => {
      this.keys[e.code] = false;
      this.keys[e.key] = false;
      if (e.key) this.keys[e.key.toLowerCase()] = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    document.addEventListener('keyup', handleKeyUp);

    // Canvas click & drag to move Golumolu
    let isPointerDown = false;
    const handlePointer = (clientX, clientY) => {
      if (this.ui.currentScreen !== 'game' || !this.player) return;
      const rect = this.renderer.domElement.getBoundingClientRect();
      const clickX = clientX - (rect.left + rect.width / 2);
      const clickY = clientY - (rect.top + rect.height / 2);
      const dist = Math.hypot(clickX, clickY);
      if (dist > 25) {
        this.input.joystickX = Math.max(-1, Math.min(1, clickX / 70));
        this.input.joystickY = Math.max(-1, Math.min(1, clickY / 70));
      }
    };

    this.container.addEventListener('pointerdown', (e) => {
      isPointerDown = true;
      audio.init();
      audio.startBGM();
      handlePointer(e.clientX, e.clientY);
    });

    window.addEventListener('pointermove', (e) => {
      if (isPointerDown) {
        handlePointer(e.clientX, e.clientY);
      }
    });

    window.addEventListener('pointerup', () => {
      isPointerDown = false;
      this.input.joystickX = 0;
      this.input.joystickY = 0;
    });

    // Mouse wheel camera zoom (smoothly scales distance and height)
    window.addEventListener('wheel', (e) => {
      if (this.ui.currentScreen === 'game') {
        this.camDistance = Math.max(7, Math.min(28, this.camDistance + e.deltaY * 0.015));
        this.camHeight = this.camDistance * 1.2;
      }
    }, { passive: true });
  }

  setupMenuDiorama() {
    // Build a miniature cozy garden preview for the menu using the Blender beauty maze
    this.mazeData = MazeGenerator.generateCampaignLevel(MazeGenerator.getLevelConfig(1));
    this.mazeData.isBeautyMaster = true;
    this.cellSize = 1.0;
    this.env.cellSize = 1.0;
    this.env.buildMaze(this.mazeData);

    this.player = new GolumoluCharacter(this.currentSkin);
    this.player.worldX = -4.6;
    this.player.worldZ = 4.8;
    this.player.group.position.set(this.player.worldX, 0, this.player.worldZ);
    this.scene.add(this.player.group);

    this.ghosts = [
      new GhostCharacter('follower', 2, 3, 1.0)
    ];
    this.ghosts.forEach(g => {
      g.group.position.set(2.2, 0, -2.5);
      this.scene.add(g.group);
    });

    this.camera.position.set(0, 11, 14);
    this.camera.lookAt(0, 0.5, 0);
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
    this.collectedGoldenMomo = false;
    this.exitGateOpen = false;
    this.cellSize = this.mazeData.cellSize || (this.mazeData.size <= 15 ? 2.0 : 1.2);
    this.env.cellSize = this.cellSize;
    this.targetMomos = this.mazeData.isBeautyMaster 
      ? ((this.mazeData.collectiblesWorld ? this.mazeData.collectiblesWorld.length : 10) + 1)
      : (this.mazeData.collectibles ? this.mazeData.collectibles.length : targetMomos);
    this.elapsedTime = 0;
    this.invulnerableTimer = 0;
    this.ghostDivideStage = 1; // Initially only 1 ghost active!
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

    // Spawn player at start position inside corridor
    const offset = (this.mazeData.size - 1) / 2;
    this.player = new GolumoluCharacter(this.currentSkin);
    if (this.mazeData.isBeautyMaster && this.mazeData.playerStartWorld) {
      this.player.worldX = this.mazeData.playerStartWorld.x;
      this.player.worldZ = this.mazeData.playerStartWorld.z;
    } else {
      this.player.gridX = this.mazeData.playerStart.x;
      this.player.gridY = this.mazeData.playerStart.y;
      this.player.worldX = (this.player.gridX - offset) * this.cellSize;
      this.player.worldZ = (this.player.gridY - offset) * this.cellSize;
    }
    this.player.group.position.set(this.player.worldX, 0, this.player.worldZ);
    this.scene.add(this.player.group);

    // Initial Ghost: Spawn strictly 1 Ghost (Follower) at start
    const initialGhost = new GhostCharacter('follower', 2, 3, this.cellSize);
    if (this.mazeData.isBeautyMaster && this.mazeData.ghostsWorld) {
      initialGhost.group.position.set(this.mazeData.ghostsWorld[0].x, 0, this.mazeData.ghostsWorld[0].z);
    } else {
      const initialGX = (this.mazeData.ghosts && this.mazeData.ghosts[0]) ? this.mazeData.ghosts[0].x : 2;
      const initialGY = (this.mazeData.ghosts && this.mazeData.ghosts[0]) ? this.mazeData.ghosts[0].y : 3;
      initialGhost.group.position.set((initialGX - offset) * this.cellSize, 0, (initialGY - offset) * this.cellSize);
    }
    this.scene.add(initialGhost.group);
    this.ghosts.push(initialGhost);

    // Snap camera directly over Golumolu at level start so follow begins centered
    this.camera.position.set(
      this.player.worldX,
      this.player.group.position.y + this.camHeight,
      this.player.worldZ + this.camDistance
    );
    this.camera.lookAt(this.player.worldX, 0.7, this.player.worldZ);

    this.ui.showScreen('game');
    this.ui.updateHUD(this.getState());
  }

  // Timed Ghost Division: spawns new spirit with magical poof and sound
  spawnDividedGhost(type, defaultX, defaultY) {
    const offset = (this.mazeData.size - 1) / 2;
    let wx, wz;

    if (this.mazeData.isBeautyMaster) {
      if (type === 'cutter') {
        wx = -2.0; wz = -2.5;
      } else {
        wx = 0.0; wz = -2.0;
      }
    } else {
      let spawnGX = defaultX;
      let spawnGY = defaultY;
      if (this.ghosts.length > 0) {
        const parent = this.ghosts[0];
        const pGX = Math.round(parent.gridX);
        const pGY = Math.round(parent.gridY);
        const candidates = [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [-1, -1]];
        for (const [ox, oy] of candidates) {
          const nx = pGX + ox;
          const ny = pGY + oy;
          if (this.mazeData.grid[ny]?.[nx] === 0) {
            spawnGX = nx;
            spawnGY = ny;
            break;
          }
        }
      }
      wx = (spawnGX - offset) * this.cellSize;
      wz = (spawnGY - offset) * this.cellSize;
    }

    const ghost = new GhostCharacter(type, 2, 3, this.cellSize);
    ghost.group.position.set(wx, 0, wz);
    this.scene.add(ghost.group);
    this.ghosts.push(ghost);

    // Magical division burst
    this.env.spawnMomoBlast(wx, 0.6, wz, true);
    audio.playGateToggle();

    if (this.ui) {
      const spiritName = type.charAt(0).toUpperCase() + type.slice(1);
      this.ui.showToast(`👻 Spirit Divided! ${spiritName} joined (${this.ghosts.length} Ghosts active!)`);
    }
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

  startCustom(config) {
    this.isGrand31 = false;
    // Map size to nearest campaign level or use grand maze
    if (config.size >= 31) {
      this.isGrand31 = true;
      this.mazeData = MazeGenerator.getMaster31x31Maze();
    } else {
      // Find a campaign level with matching grid size, or generate one
      const matchingLevel = MazeGenerator.getLevelConfig(1);
      this.mazeData = MazeGenerator.generateCampaignLevel(matchingLevel);
      if (config.size !== 12) {
        // Generate fresh maze at the requested size
        const fakeConfig = {
          level_id: 99, name: 'Custom', grid_size: config.size,
          target_momos: Math.floor(config.size * 0.8),
          has_moving_gates: config.gates,
          starting_spirits: config.ghosts
        };
        this.mazeData = MazeGenerator.generateCampaignLevel(fakeConfig);
      }
    }
    // Apply custom ghost speed modifier
    this._customSpeedMod = config.speed || 1.0;
    this._customInitialGhosts = Math.max(1, Math.min(4, config.ghosts || 1));
    this.initPlaySession('Custom Play', this.mazeData.collectibles?.length || 8, config.gates);
    // Spawn extra initial ghosts if requested
    const types = ['follower','cutter','wanderer','wanderer'];
    for (let i = 1; i < this._customInitialGhosts; i++) {
      this.spawnDividedGhost(types[i] || 'wanderer', i * 3, i * 2);
    }
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
      exitGateOpen: this.exitGateOpen,
      collectedGoldenMomo: this.collectedGoldenMomo,
      mazeData: this.mazeData,
      player: this.player,
      ghosts: this.ghosts
    };
  }

  triggerDash() {
    if (this.dashCooldownTimer > 0) return;
    this.dashTimer = 1.0;
    this.dashCooldownTimer = 2.5;
    audio.playPowerup();
    if (this.player && this.env) {
      this.env.spawnMomoBlast(this.player.worldX, 0.4, this.player.worldZ, false);
    }
  }

  handlePlayerInput(delta) {
    let dx = 0;
    let dz = 0;

    const isUp = this.keys['KeyW'] || this.keys['w'] || this.keys['W'] || this.keys['ArrowUp'];
    const isDown = this.keys['KeyS'] || this.keys['s'] || this.keys['S'] || this.keys['ArrowDown'];
    const isLeft = this.keys['KeyA'] || this.keys['a'] || this.keys['A'] || this.keys['ArrowLeft'];
    const isRight = this.keys['KeyD'] || this.keys['d'] || this.keys['D'] || this.keys['ArrowRight'];

    if (isUp) dz -= 1;
    if (isDown) dz += 1;
    if (isLeft) dx -= 1;
    if (isRight) dx += 1;

    // Dash input (Space key)
    if (this.keys['Space'] || this.keys[' ']) {
      this.triggerDash();
    }

    if (this.dashCooldownTimer > 0) this.dashCooldownTimer -= delta;
    let speed = 5.2;
    if (this.dashTimer > 0) {
      this.dashTimer -= delta;
      speed = 8.5; // Dash boost!
    }

    // Add virtual joystick or canvas pointer drag input
    if (Math.hypot(this.input.joystickX, this.input.joystickY) > 0.12) {
      dx += this.input.joystickX;
      dz += this.input.joystickY;
    }

    const len = Math.hypot(dx, dz);

    if (len > 0.05) {
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
      this.player.modelRoot.rotation.y += diff * Math.min(1.0, delta * 14);

      const offset = (this.mazeData.size - 1) / 2;
      const r = 0.32; // Player collision radius

      // Desired new world position
      const nextX = this.player.worldX + dx * speed * delta;
      const nextZ = this.player.worldZ + dz * speed * delta;

      const isWallBlocked = (wx, wz) => {
        if (this.mazeData.isBeautyMaster && this.mazeData.wallSegments) {
          // Bounding box border
          if (Math.abs(wx) > 5.35 || Math.abs(wz) > 5.35) {
            // Check if exiting through open North Leaf Gate
            if (this.exitGateOpen && wz < -5.3 && Math.abs(wx) < 1.25) {
              return false; // Free passage through open leaf gate!
            }
            return true;
          }

          // Check if North Leaf Gate is closed
          if (!this.exitGateOpen && wz < -5.3 && Math.abs(wx) < 1.25) {
            return true;
          }

          // Test against all 21 verified hedge wall segments
          for (const w of this.mazeData.wallSegments) {
            const hx = w.sx / 2.0;
            const hz = w.sz / 2.0;
            const cx = Math.max(w.x - hx, Math.min(wx, w.x + hx));
            const cz = Math.max(w.z - hz, Math.min(wz, w.z + hz));
            if ((wx - cx) ** 2 + (wz - cz) ** 2 < r * r) {
              return true;
            }
          }
          return false;
        }

        // Procedural grid fallback
        const isCellPassable = (cx, cy) => {
          if (cx < 0 || cx >= this.mazeData.size || cy < 0 || cy >= this.mazeData.size) return false;
          const cell = this.mazeData.grid[cy][cx];
          if (cell === 1) return false;
          if (cell === 2 && this.activePhase === 'A') return false;
          if (cell === 3 && this.activePhase === 'B') return false;
          return true;
        };

        const corners = [
          [wx - r, wz - r],
          [wx + r, wz - r],
          [wx - r, wz + r],
          [wx + r, wz + r]
        ];
        return !corners.every(([cx, cz]) => {
          const gx = Math.round(cx / this.cellSize + offset);
          const gy = Math.round(cz / this.cellSize + offset);
          return isCellPassable(gx, gy);
        });
      };

      // Slide along walls (test X and Z independently)
      if (!isWallBlocked(nextX, this.player.worldZ)) {
        this.player.worldX = nextX;
      }
      if (!isWallBlocked(this.player.worldX, nextZ)) {
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
    const pPos = this.player.group.position;

    // 1. Regular steamed momo dumplings
    if (this.env.collectMomoAt(pPos.x, pPos.z, 1.05)) {
      this.collectedMomos++;
      this.player.triggerEat();
      audio.playCollectMomo();
      if (this.ui) this.ui.updateHUD(this.getState());
    }

    // 2. The Legendary Golden Momo Sanctuary
    if (!this.collectedGoldenMomo && this.env.collectGoldenMomoAt(pPos.x, pPos.z, 1.25)) {
      this.collectedGoldenMomo = true;
      this.collectedMomos++;
      this.exitGateOpen = true;
      this.player.triggerEat();
      audio.playCollectGolden();
      if (this.ui) {
        this.ui.updateHUD(this.getState());
        this.ui.showToast('👑 GOLDEN MOMO CONSUMED! North Leaf Gate is Open!');
      }
    }
  }

  checkExitGate() {
    if (!this.exitGateOpen && this.collectedMomos < this.targetMomos && !this.collectedGoldenMomo) return;
    const pPos = this.player.group.position;
    const exitWX = (this.mazeData.isBeautyMaster && this.mazeData.exitGateWorld) ? this.mazeData.exitGateWorld.x : 0.0;
    const exitWZ = (this.mazeData.isBeautyMaster && this.mazeData.exitGateWorld) ? this.mazeData.exitGateWorld.z : -5.75;
    const dist = Math.hypot(pPos.x - exitWX, pPos.z - exitWZ);

    if (dist < 2.0) {
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
      if (dist < 0.95) {
        // Hit by ghost!
        this.lives--;
        this.invulnerableTimer = 2.0;
        audio.playHit();

        if (this.ui) {
          this.ui.showToast('💥 Spirit Tagged Golumolu! 1 Life Lost 💔');
          this.ui.setInvulnFlash(true);
          setTimeout(() => this.ui.setInvulnFlash(false), 400);
        }

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
        // Active, responsive follow: camera tracks Golumolu directly while framing surrounding maze corridors
        const targetCamX = pPos.x;
        const targetCamY = pPos.y + this.camHeight;
        const targetCamZ = pPos.z + this.camDistance;

        const lerpFactor = Math.min(1.0, delta * 7.0);
        this.camera.position.x += (targetCamX - this.camera.position.x) * lerpFactor;
        this.camera.position.y += (targetCamY - this.camera.position.y) * lerpFactor;
        this.camera.position.z += (targetCamZ - this.camera.position.z) * lerpFactor;
        this.camera.lookAt(pPos.x, pPos.y + 0.7, pPos.z);
      } else {
        // Top-down tactical overview
        const targetCamX = pPos.x;
        const targetCamY = pPos.y + this.camHeight * 1.5;
        const targetCamZ = pPos.z + 0.01;

        const lerpFactor = Math.min(1.0, delta * 8.0);
        this.camera.position.x += (targetCamX - this.camera.position.x) * lerpFactor;
        this.camera.position.y += (targetCamY - this.camera.position.y) * lerpFactor;
        this.camera.position.z += (targetCamZ - this.camera.position.z) * lerpFactor;
        this.camera.lookAt(pPos.x, pPos.y, pPos.z);
      }
    } else {
      // Menu rotating diorama camera
      const time = performance.now() * 0.0003;
      this.camera.position.x = Math.sin(time) * 18;
      this.camera.position.z = Math.cos(time) * 18;
      this.camera.position.y = 12 + Math.sin(time * 2) * 1.5;
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

        // Timed Ghost Division (User Specification):
        // Start: 1 Follower ghost
        // 30s  → splits: adds Cutter (2 ghosts total)
        // 60s  → splits: adds Wanderer (3 ghosts total)
        // Max 4 ghosts
        if (this.elapsedTime >= 30.0 && this.ghostDivideStage === 1) {
          this.ghostDivideStage = 2;
          this.spawnDividedGhost('cutter', 9, 3);
        }
        if (this.elapsedTime >= 60.0 && this.ghostDivideStage === 2) {
          this.ghostDivideStage = 3;
          this.spawnDividedGhost('wanderer', 2, 9);
        }

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
          g.update(delta, this.player, this.mazeData.grid, this.mazeData.size, this.activePhase, this.mazeData);
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
