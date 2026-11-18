// 3 Ghost Spirits 3D Models & AI for MOMO MAZE
// Follower, Cutter, Wanderer matching Asset Spec
import * as THREE from './three.module.js';
import { MazeGenerator } from './maze_generator.js';

export const GHOST_TYPES = {
  follower: {
    name: 'Follower',
    color: 0xFFF5E6,
    glow: 0xFFE082,
    speed: 2.1,
    eyeType: 'round',
    desc: 'Curious and loyal. Tracks Golumolu directly through the maze.'
  },
  cutter: {
    name: 'Cutter',
    color: 0xFFEDE0,
    glow: 0xFFAB91,
    speed: 2.4,
    eyeType: 'angled',
    desc: 'Clever and quick. Anticipates turns and tries to cut Golumolu off!'
  },
  wanderer: {
    name: 'Wanderer',
    color: 0xF3E5F5,
    glow: 0xCE93D8,
    speed: 1.8,
    eyeType: 'star',
    desc: 'Dreamy and energetic. Swirls through garden corridors.'
  }
};

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

    this.buildMesh();
  }

  buildMesh() {
    this.modelRoot = new THREE.Group();
    this.group.add(this.modelRoot);

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
    const headGeo = new THREE.SphereGeometry(0.36, 20, 16);
    this.headMesh = new THREE.Mesh(headGeo, matGhost);
    this.headMesh.position.y = 0.55;
    this.modelRoot.add(this.headMesh);

    // 2. Tapered Wispy Tail (multiple soft spheres or cone)
    this.tailSegments = [];
    const tailSizes = [0.26, 0.18, 0.11, 0.06];
    tailSizes.forEach((radius, i) => {
      const segGeo = new THREE.SphereGeometry(radius, 12, 10);
      const seg = new THREE.Mesh(segGeo, matGhost);
      seg.position.set(0, 0.38 - i * 0.12, -i * 0.08);
      this.modelRoot.add(seg);
      this.tailSegments.push(seg);
    });

    // 3. Eyes based on personality
    if (this.spec.eyeType === 'round') {
      // Follower: Round, cute dots with highlight
      const eyeGeo = new THREE.SphereGeometry(0.045, 12, 10);
      const leftEye = new THREE.Mesh(eyeGeo, matEyes);
      leftEye.position.set(-0.11, 0.58, 0.32);
      this.modelRoot.add(leftEye);

      const rightEye = new THREE.Mesh(eyeGeo, matEyes);
      rightEye.position.set(0.11, 0.58, 0.32);
      this.modelRoot.add(rightEye);

      const glintGeo = new THREE.SphereGeometry(0.015, 8, 8);
      const glintL = new THREE.Mesh(glintGeo, matEyeWhite);
      glintL.position.set(-0.095, 0.60, 0.35);
      this.modelRoot.add(glintL);

      const glintR = new THREE.Mesh(glintGeo, matEyeWhite);
      glintR.position.set(0.125, 0.60, 0.35);
      this.modelRoot.add(glintR);
    } else if (this.spec.eyeType === 'angled') {
      // Cutter: Angled mischievous eyes
      const eyeGeo = new THREE.CylinderGeometry(0.02, 0.05, 0.11, 10);
      const leftEye = new THREE.Mesh(eyeGeo, matEyes);
      leftEye.position.set(-0.12, 0.58, 0.32);
      leftEye.rotation.z = 0.45;
      this.modelRoot.add(leftEye);

      const rightEye = new THREE.Mesh(eyeGeo, matEyes);
      rightEye.position.set(0.12, 0.58, 0.32);
      rightEye.rotation.z = -0.45;
      this.modelRoot.add(rightEye);
    } else {
      // Wanderer: Wide starry / dreamy eyes
      const eyeGeo = new THREE.SphereGeometry(0.052, 14, 10);
      const leftEye = new THREE.Mesh(eyeGeo, matEyes);
      leftEye.position.set(-0.12, 0.58, 0.32);
      this.modelRoot.add(leftEye);

      const rightEye = new THREE.Mesh(eyeGeo, matEyes);
      rightEye.position.set(0.12, 0.58, 0.32);
      this.modelRoot.add(rightEye);

      // Star twinkles
      const starGeo = new THREE.SphereGeometry(0.02, 8, 8);
      const starMat = new THREE.MeshBasicMaterial({ color: 0xFFF9C4 });
      const starL = new THREE.Mesh(starGeo, starMat);
      starL.position.set(-0.10, 0.60, 0.355);
      this.modelRoot.add(starL);

      const starR = new THREE.Mesh(starGeo, starMat);
      starR.position.set(0.14, 0.60, 0.355);
      this.modelRoot.add(starR);
    }

    // Rosy cheeks for Follower & Wanderer
    if (this.typeKey !== 'cutter') {
      const blushMat = new THREE.MeshBasicMaterial({ color: 0xFFB0AA });
      const blushGeo = new THREE.CircleGeometry(0.05, 12);

      const bL = new THREE.Mesh(blushGeo, blushMat);
      bL.position.set(-0.18, 0.49, 0.30);
      bL.rotation.y = -0.3;
      this.modelRoot.add(bL);

      const bR = new THREE.Mesh(blushGeo, blushMat);
      bR.position.set(0.18, 0.49, 0.30);
      bR.rotation.y = 0.3;
      this.modelRoot.add(bR);
    }

    // Point light for ethereal glowing aura
    this.light = new THREE.PointLight(this.spec.glow, 1.2, 3.8);
    this.light.position.set(0, 0.6, 0);
    this.group.add(this.light);
  }

  update(delta, player, grid, gridSize, activePhase) {
    this.floatCycle += delta * 3.5;
    const hover = Math.sin(this.floatCycle) * 0.12;
    this.modelRoot.position.y = hover;

    // Tail waving effect
    this.tailSegments.forEach((seg, i) => {
      seg.position.x = Math.sin(this.floatCycle - i * 0.8) * (0.04 * (i + 1));
      seg.position.z = -i * 0.08 + Math.cos(this.floatCycle - i * 0.8) * 0.03;
    });

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

      if (dist < 0.1) {
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
