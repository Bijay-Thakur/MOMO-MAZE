// 3 Ghost Spirits 3D Models & AI for MOMO MAZE
// Follower, Cutter, Wanderer with Hero Scaling & Elongated Flying Tails
import * as THREE from './three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MazeGenerator, BEAUTY_WAYPOINTS } from './maze_generator.js';

export const GHOST_TYPES = {
  follower: {
    name: 'Follower',
    color: 0xFFF5E6,
    glow: 0xFFE082,
    speed: 2.8,
    eyeType: 'round',
    desc: 'Curious and loyal. Tracks Golumolu directly through the maze.'
  },
  cutter: {
    name: 'Cutter',
    color: 0xFFEDE0,
    glow: 0xFFAB91,
    speed: 3.3,
    eyeType: 'angled',
    desc: 'Clever and quick. Anticipates turns and tries to cut Golumolu off!'
  },
  wanderer: {
    name: 'Wanderer',
    color: 0xF3E5F5,
    glow: 0xCE93D8,
    speed: 2.4,
    eyeType: 'star',
    desc: 'Dreamy and energetic. Swirls through garden corridors.'
  }
};

const gltfLoader = new GLTFLoader();

export class GhostCharacter {
  constructor(typeKey = 'follower', startGridX = 1, startGridY = 1, cellSize = 1.8) {
    this.typeKey = typeKey;
    this.spec = GHOST_TYPES[typeKey] || GHOST_TYPES.follower;
    this.gridX = startGridX;
    this.gridY = startGridY;
    this.cellSize = cellSize;

    this.group = new THREE.Group();
    this.floatCycle = Math.random() * 10;
    this.currentPath = [];
    this.pathTimer = 0;

    // Ghost scale: 1.0 — fits corridor comfortably, doesn't overwhelm the maze
    this.group.scale.set(1.0, 1.0, 1.0);

    this.buildMesh();
    this.loadGLBModel();
  }

  loadGLBModel() {
    const modelPath = `models/ghost_${this.typeKey}.glb`;
    gltfLoader.load(
      modelPath,
      (gltf) => {
        const glbScene = gltf.scene;
        // Ghost GLB scale: 1.0 — matches maze corridors
        glbScene.scale.set(1.0, 1.0, 1.0);
        glbScene.position.set(0, 0, 0);

        glbScene.traverse(child => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
            if (child.material) {
              child.material.transparent = true;
              child.material.opacity = 0.92;
            }
          }
        });

        // Hide procedural mesh and show GLB
        if (this.proceduralRoot) {
          this.proceduralRoot.visible = false;
        }
        this.glbMesh = glbScene;
        this.modelRoot.add(glbScene);
      },
      undefined,
      (err) => {
        // Fallback to procedural mesh silently
        console.log(`Using procedural model for ghost ${this.typeKey}`);
      }
    );
  }

  buildMesh() {
    this.modelRoot = new THREE.Group();
    this.group.add(this.modelRoot);

    this.proceduralRoot = new THREE.Group();
    this.modelRoot.add(this.proceduralRoot);

    // Main spirit translucent material
    const matGhost = new THREE.MeshStandardMaterial({
      color: this.spec.color,
      roughness: 0.35,
      metalness: 0.05,
      transparent: true,
      opacity: 0.88,
      emissive: this.spec.glow,
      emissiveIntensity: 0.28
    });

    const matEyes = new THREE.MeshBasicMaterial({
      color: 0x3D2B1F
    });

    const matEyeWhite = new THREE.MeshBasicMaterial({
      color: 0xFFFFFF
    });

    // 1. Round fluffy head
    const headGeo = new THREE.SphereGeometry(0.35, 24, 20);
    this.headMesh = new THREE.Mesh(headGeo, matGhost);
    this.headMesh.position.y = 0.45;
    this.headMesh.castShadow = true;
    this.proceduralRoot.add(this.headMesh);

    // 2. Wavy Flowing Ribbon Wisp Tail (S-curve undulation curving upwards & back!)
    const curvePoints = [
      new THREE.Vector3(0, 0.44, 0.05),
      new THREE.Vector3(0.14, 0.48, -0.25),  // wave crest right
      new THREE.Vector3(-0.12, 0.44, -0.55), // wave trough left
      new THREE.Vector3(0.15, 0.58, -0.85),  // wave crest right
      new THREE.Vector3(0, 0.72, -1.15)      // rounded puff tip up
    ];
    const curve = new THREE.CatmullRomCurve3(curvePoints);
    const tailGeo = new THREE.TubeGeometry(curve, 28, 0.18, 14, false);
    this.mainTail = new THREE.Mesh(tailGeo, matGhost);
    this.mainTail.castShadow = true;
    this.proceduralRoot.add(this.mainTail);

    // Rounded cloud puff at tail end
    const puffGeo = new THREE.SphereGeometry(0.18, 14, 10);
    const puff = new THREE.Mesh(puffGeo, matGhost);
    puff.position.set(0, 0.72, -1.15);
    this.proceduralRoot.add(puff);

    this.tailSegments = [];

    // 3. Side floating wisps/wings
    const finGeo = new THREE.SphereGeometry(0.12, 12, 10);
    finGeo.scale(1.8, 0.45, 1.2);
    this.finL = new THREE.Mesh(finGeo, matGhost);
    this.finL.position.set(-0.30, 0.42, -0.05);
    this.finL.rotation.z = -0.3;
    this.proceduralRoot.add(this.finL);

    this.finR = new THREE.Mesh(finGeo, matGhost);
    this.finR.position.set(0.30, 0.42, -0.05);
    this.finR.rotation.z = 0.3;
    this.proceduralRoot.add(this.finR);

    // 4. Eyes based on personality
    if (this.spec.eyeType === 'round') {
      // Follower: Round, cute dots with highlight
      const eyeGeo = new THREE.SphereGeometry(0.045, 12, 10);
      const leftEye = new THREE.Mesh(eyeGeo, matEyes);
      leftEye.position.set(-0.11, 0.58, 0.32);
      this.proceduralRoot.add(leftEye);

      const rightEye = new THREE.Mesh(eyeGeo, matEyes);
      rightEye.position.set(0.11, 0.58, 0.32);
      this.proceduralRoot.add(rightEye);

      const glintGeo = new THREE.SphereGeometry(0.015, 8, 8);
      const glintL = new THREE.Mesh(glintGeo, matEyeWhite);
      glintL.position.set(-0.095, 0.60, 0.35);
      this.proceduralRoot.add(glintL);

      const glintR = new THREE.Mesh(glintGeo, matEyeWhite);
      glintR.position.set(0.125, 0.60, 0.35);
      this.proceduralRoot.add(glintR);
    } else if (this.spec.eyeType === 'angled') {
      // Cutter: Angled mischievous eyes
      const eyeGeo = new THREE.CylinderGeometry(0.02, 0.05, 0.11, 10);
      const leftEye = new THREE.Mesh(eyeGeo, matEyes);
      leftEye.position.set(-0.12, 0.58, 0.32);
      leftEye.rotation.z = 0.45;
      this.proceduralRoot.add(leftEye);

      const rightEye = new THREE.Mesh(eyeGeo, matEyes);
      rightEye.position.set(0.12, 0.58, 0.32);
      rightEye.rotation.z = -0.45;
      this.proceduralRoot.add(rightEye);
    } else {
      // Wanderer: Wide starry / dreamy eyes
      const eyeGeo = new THREE.SphereGeometry(0.052, 14, 10);
      const leftEye = new THREE.Mesh(eyeGeo, matEyes);
      leftEye.position.set(-0.12, 0.58, 0.32);
      this.proceduralRoot.add(leftEye);

      const rightEye = new THREE.Mesh(eyeGeo, matEyes);
      rightEye.position.set(0.12, 0.58, 0.32);
      this.proceduralRoot.add(rightEye);

      // Star twinkles
      const starGeo = new THREE.SphereGeometry(0.02, 8, 8);
      const starMat = new THREE.MeshBasicMaterial({ color: 0xFFF9C4 });
      const starL = new THREE.Mesh(starGeo, starMat);
      starL.position.set(-0.10, 0.60, 0.355);
      this.proceduralRoot.add(starL);

      const starR = new THREE.Mesh(starGeo, starMat);
      starR.position.set(0.14, 0.60, 0.355);
      this.proceduralRoot.add(starR);
    }

    // Rosy cheeks for Follower & Wanderer
    if (this.typeKey !== 'cutter') {
      const blushMat = new THREE.MeshBasicMaterial({ color: 0xFFB0AA });
      const blushGeo = new THREE.CircleGeometry(0.05, 12);

      const bL = new THREE.Mesh(blushGeo, blushMat);
      bL.position.set(-0.18, 0.49, 0.30);
      bL.rotation.y = -0.3;
      this.proceduralRoot.add(bL);

      const bR = new THREE.Mesh(blushGeo, blushMat);
      bR.position.set(0.18, 0.49, 0.30);
      bR.rotation.y = 0.3;
      this.proceduralRoot.add(bR);
    }

    // Point light for ethereal glowing aura
    this.light = new THREE.PointLight(this.spec.glow, 1.4, 4.2);
    this.light.position.set(0, 0.6, 0);
    this.group.add(this.light);
  }

  update(delta, player, grid, gridSize, activePhase, mazeData = null) {
    this.floatCycle += delta * 3.8;
    const hover = Math.sin(this.floatCycle) * 0.16;
    // Hover mid-air at eye level above garden pathways
    this.modelRoot.position.y = 0.95 + hover;

    // Swimming wave animation for elongated tail
    this.tailSegments.forEach((seg, i) => {
      // Propagating horizontal wave
      seg.position.x = Math.sin(this.floatCycle - i * 0.6) * (0.05 * (i + 1));
      // Subtle vertical ripple
      seg.position.y = 0.44 - i * 0.04 + Math.cos(this.floatCycle - i * 0.5) * (0.025 * (i + 1));
      seg.position.z = -i * 0.16 + Math.sin(this.floatCycle * 0.5 - i * 0.4) * 0.02;
    });

    if (this.finL && this.finR) {
      this.finL.rotation.z = -0.3 + Math.sin(this.floatCycle * 1.5) * 0.2;
      this.finR.rotation.z = 0.3 - Math.sin(this.floatCycle * 1.5) * 0.2;
    }

    // Subtle pitch/roll of GLB mesh if loaded
    if (this.glbMesh) {
      this.glbMesh.rotation.z = Math.sin(this.floatCycle) * 0.08;
      this.glbMesh.rotation.x = Math.cos(this.floatCycle * 0.8) * 0.06;
    }

    // If in Beauty Master Maze: use verified open corridor waypoints!
    if (mazeData && mazeData.isBeautyMaster) {
      if (!this.targetWaypoint || Math.hypot(this.group.position.x - this.targetWaypoint.x, this.group.position.z - this.targetWaypoint.z) < 0.45) {
        const wps = BEAUTY_WAYPOINTS;
        if (this.typeKey === 'follower') {
          // Pursue closest waypoint to Golumolu
          let best = wps[0];
          let bestDist = 999;
          for (const wp of wps) {
            const d = Math.hypot(player.group.position.x - wp.x, player.group.position.z - wp.z);
            if (d < bestDist && wp !== this.targetWaypoint) {
              bestDist = d;
              best = wp;
            }
          }
          this.targetWaypoint = best;
        } else {
          // Patrol open waypoints
          const choices = wps.filter(w => w !== this.targetWaypoint);
          this.targetWaypoint = choices[Math.floor(Math.random() * choices.length)];
        }
      }

      const dx = this.targetWaypoint.x - this.group.position.x;
      const dz = this.targetWaypoint.z - this.group.position.z;
      const dist = Math.hypot(dx, dz);
      if (dist > 0.05) {
        const moveDist = Math.min(dist, this.spec.speed * delta);
        this.group.position.x += (dx / dist) * moveDist;
        this.group.position.z += (dz / dist) * moveDist;

        const targetAngle = Math.atan2(dx, dz);
        let curAngle = this.modelRoot.rotation.y;
        let diff = targetAngle - curAngle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        this.modelRoot.rotation.y += diff * Math.min(1.0, delta * 9);
      }
      return;
    }

    // AI Path recalculation (every 0.4s)
    this.pathTimer -= delta;
    if (this.pathTimer <= 0) {
      this.pathTimer = 0.35 + Math.random() * 0.15;
      this.calculatePath(player, grid, gridSize, activePhase);
    }

    // Move along path
    if (this.currentPath.length > 0) {
      const nextCell = this.currentPath[0];
      const targetWorldX = (nextCell.x - (gridSize - 1) / 2) * this.cellSize;
      const targetWorldZ = (nextCell.y - (gridSize - 1) / 2) * this.cellSize;

      const dx = targetWorldX - this.group.position.x;
      const dz = targetWorldZ - this.group.position.z;
      const dist = Math.hypot(dx, dz);

      if (dist < 0.22) {
        // Arrived at waypoint
        this.gridX = nextCell.x;
        this.gridY = nextCell.y;
        this.currentPath.shift();
      } else {
        const moveDist = Math.min(dist, this.spec.speed * delta);
        this.group.position.x += (dx / dist) * moveDist;
        this.group.position.z += (dz / dist) * moveDist;

        // Smoothly rotate facing direction
        const targetAngle = Math.atan2(dx, dz);
        let curAngle = this.modelRoot.rotation.y;
        let diff = targetAngle - curAngle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        this.modelRoot.rotation.y += diff * Math.min(1.0, delta * 9);
      }
    }
  }

  calculatePath(player, grid, gridSize, activePhase) {
    const myCell = { x: Math.round(this.gridX), y: Math.round(this.gridY) };
    let targetCell = { x: Math.round(player.gridX), y: Math.round(player.gridY) };

    if (this.typeKey === 'cutter') {
      // Cutter predicts player movement vector (2 cells ahead)
      const pDirX = player.dirX || 0;
      const pDirY = player.dirY || 0;
      const predX = Math.max(1, Math.min(gridSize - 2, targetCell.x + pDirX * 2));
      const predY = Math.max(1, Math.min(gridSize - 2, targetCell.y + pDirY * 2));
      if (grid[predY]?.[predX] === 0) {
        targetCell = { x: predX, y: predY };
      }
    } else if (this.typeKey === 'wanderer') {
      // Wanderer randomly wanders between nearby open paths if not close
      const distToPlayer = Math.hypot(myCell.x - targetCell.x, myCell.y - targetCell.y);
      if (distToPlayer > 8 || Math.random() < 0.3) {
        const randomOffsets = [[-3, 0], [3, 0], [0, -3], [0, 3], [-2, 2], [2, -2]];
        for (const [ox, oy] of randomOffsets) {
          const rx = Math.max(1, Math.min(gridSize - 2, myCell.x + ox));
          const ry = Math.max(1, Math.min(gridSize - 2, myCell.y + oy));
          if (grid[ry]?.[rx] === 0) {
            targetCell = { x: rx, y: ry };
            break;
          }
        }
      }
    }

    const path = MazeGenerator.findPath(grid, gridSize, myCell, targetCell, activePhase);
    if (path.length > 1) {
      this.currentPath = path.slice(1); // Drop current position
    }
  }
}
