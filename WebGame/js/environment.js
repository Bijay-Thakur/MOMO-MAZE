// 3D Environment Builder for MOMO MAZE
// Lush hedges, stone/grass paths, steamed Momo dumplings, timed leaf gates, exit archway
import * as THREE from './three.module.js';

export class EnvironmentBuilder {
  constructor(scene, cellSize = 1.8) {
    this.scene = scene;
    this.cellSize = cellSize;
    this.momos = [];
    this.movingGates = [];
    this.exitGateMesh = null;
    this.exitArchLight = null;

    this.initMaterials();
  }

  initMaterials() {
    // 1. Lush hedge material
    this.matHedge = new THREE.MeshStandardMaterial({
      color: 0x559635,
      roughness: 0.88,
      metalness: 0.05
    });

    this.matHedgeDark = new THREE.MeshStandardMaterial({
      color: 0x3E7824,
      roughness: 0.9,
      metalness: 0.05
    });

    // 2. Ground path tile (stone & grassy soil blend)
    this.matGround = new THREE.MeshStandardMaterial({
      color: 0xCBB892,
      roughness: 0.95,
      metalness: 0.0
    });

    this.matLawn = new THREE.MeshStandardMaterial({
      color: 0x76B34A,
      roughness: 0.9,
      metalness: 0.0
    });

    // 3. Momo dumpling dough (warm cream + gentle golden glow)
    this.matMomo = new THREE.MeshStandardMaterial({
      color: 0xFFF6E0,
      roughness: 0.75,
      metalness: 0.05,
      emissive: 0xFFE082,
      emissiveIntensity: 0.18
    });

    // 4. Golden Grand Momo
    this.matGoldMomo = new THREE.MeshStandardMaterial({
      color: 0xFFD54F,
      roughness: 0.35,
      metalness: 0.4,
      emissive: 0xFFA000,
      emissiveIntensity: 0.4
    });

    // 5. Wood gate trellis
    this.matWoodGate = new THREE.MeshStandardMaterial({
      color: 0x8D6E63,
      roughness: 0.8,
      metalness: 0.1
    });

    this.matGateLeaf = new THREE.MeshStandardMaterial({
      color: 0x4CAF50,
      roughness: 0.7,
      metalness: 0.05
    });

    // 6. Flowers
    this.matFlowerPink = new THREE.MeshBasicMaterial({ color: 0xF48FB1 });
    this.matFlowerWhite = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
    this.matFlowerYellow = new THREE.MeshBasicMaterial({ color: 0xFFEB3B });
  }

  // Create a stylized steamed Momo dumpling mesh
  createMomoMesh(isGolden = false) {
    const group = new THREE.Group();
    const mat = isGolden ? this.matGoldMomo : this.matMomo;

    // Dumpling bottom round base
    const baseGeo = new THREE.SphereGeometry(0.24, 16, 12);
    baseGeo.scale(1.0, 0.75, 1.0);
    const base = new THREE.Mesh(baseGeo, mat);
    base.position.y = 0.16;
    base.castShadow = true;
    group.add(base);

    // Top pleated pinch folds
    const pinchGeo = new THREE.ConeGeometry(0.12, 0.16, 8);
    const pinch = new THREE.Mesh(pinchGeo, mat);
    pinch.position.y = 0.32;
    pinch.rotation.y = 0.4;
    group.add(pinch);

    // Golden sparkle point light
    const light = new THREE.PointLight(isGolden ? 0xFFA000 : 0xFFE082, isGolden ? 2.0 : 0.8, 2.5);
    light.position.y = 0.25;
    group.add(light);

    return group;
  }

  // Create a stylized rounded hedge wall unit
  createHedgeUnit(isCorner = false) {
    const group = new THREE.Group();
    const w = this.cellSize * 0.96;
    const h = 1.6;
    const d = this.cellSize * 0.96;

    // Base rounded box
    const hedgeGeo = new THREE.BoxGeometry(w, h, d);
    const hedge = new THREE.Mesh(hedgeGeo, this.matHedge);
    hedge.position.y = h / 2;
    hedge.castShadow = true;
    hedge.receiveShadow = true;
    group.add(hedge);

    // Rounded crown bush on top
    const crownGeo = new THREE.SphereGeometry(w * 0.48, 12, 10);
    crownGeo.scale(1.0, 0.45, 1.0);
    const crown = new THREE.Mesh(crownGeo, this.matHedgeDark);
    crown.position.y = h + 0.12;
    crown.castShadow = true;
    group.add(crown);

    return group;
  }

  // Build full maze scene
  buildMaze(mazeData) {
    this.clear();
    const size = mazeData.size;
    const grid = mazeData.grid;
    const offset = (size - 1) / 2;

    this.root = new THREE.Group();
    this.scene.add(this.root);

    // 1. Vast scenic garden ground plane underneath
    const vastGroundGeo = new THREE.PlaneGeometry(size * this.cellSize * 3, size * this.cellSize * 3);
    const vastGround = new THREE.Mesh(vastGroundGeo, this.matLawn);
    vastGround.rotation.x = -Math.PI / 2;
    vastGround.position.y = -0.05;
    vastGround.receiveShadow = true;
    this.root.add(vastGround);

    // 2. Build grid cells
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const worldX = (x - offset) * this.cellSize;
        const worldZ = (y - offset) * this.cellSize;
        const cell = grid[y][x];

        // Path tile for walkable areas
        if (cell === 0 || cell === 2 || cell === 3) {
          const tileGeo = new THREE.BoxGeometry(this.cellSize * 0.98, 0.08, this.cellSize * 0.98);
          const tile = new THREE.Mesh(tileGeo, this.matGround);
          tile.position.set(worldX, 0.04, worldZ);
          tile.receiveShadow = true;
          this.root.add(tile);

          // Random flower cluster along corners
          if ((x * 13 + y * 17) % 19 === 0) {
            this.addFlowerCluster(worldX + 0.35, worldZ + 0.35);
          }
        }

        // Wall: Hedge
        if (cell === 1) {
          const hedge = this.createHedgeUnit();
          hedge.position.set(worldX, 0, worldZ);
          this.root.add(hedge);

          // Walltop flower on border hedges
          if ((x === 0 || x === size - 1 || y === 0 || y === size - 1) && (x + y) % 4 === 0) {
            this.addFlowerCluster(worldX, worldZ, 1.8);
          }
        }
      }
    }

    // 3. Build Moving Gates (Phase A & B)
    if (mazeData.movingGates && mazeData.movingGates.length > 0) {
      mazeData.movingGates.forEach(g => {
        const wx = (g.x - offset) * this.cellSize;
        const wz = (g.y - offset) * this.cellSize;

        const gateGroup = new THREE.Group();
        gateGroup.position.set(wx, 0, wz);

        // Trellis posts
        const postGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.5, 8);
        const postL = new THREE.Mesh(postGeo, this.matWoodGate);
        postL.position.set(-this.cellSize * 0.42, 0.75, 0);
        postL.castShadow = true;
        gateGroup.add(postL);

        const postR = new THREE.Mesh(postGeo, this.matWoodGate);
        postR.position.set(this.cellSize * 0.42, 0.75, 0);
        postR.castShadow = true;
        gateGroup.add(postR);

        // Movable lattice barrier
        const barGeo = new THREE.BoxGeometry(this.cellSize * 0.78, 1.2, 0.15);
        const barrier = new THREE.Mesh(barGeo, this.matGateLeaf);
        barrier.position.set(0, 0.65, 0);
        barrier.castShadow = true;
        gateGroup.add(barrier);

        // Indicator lantern on gate
        const lanternGeo = new THREE.SphereGeometry(0.12, 10, 8);
        const lanternMat = new THREE.MeshBasicMaterial({
          color: g.phase === 'A' ? 0xFF8A65 : 0x81C784
        });
        const lantern = new THREE.Mesh(lanternGeo, lanternMat);
        lantern.position.set(0, 1.35, 0);
        gateGroup.add(lantern);

        this.root.add(gateGroup);
        this.movingGates.push({
          x: g.x,
          y: g.y,
          phase: g.phase,
          group: gateGroup,
          barrier: barrier,
          lantern: lantern
        });
      });
    }

    // 4. Build Momo Collectibles
    this.momos = [];
    if (mazeData.collectibles) {
      mazeData.collectibles.forEach(c => {
        const wx = (c.x - offset) * this.cellSize;
        const wz = (c.y - offset) * this.cellSize;

        const momo = this.createMomoMesh(false);
        momo.position.set(wx, 0.15, wz);
        this.root.add(momo);

        this.momos.push({
          gridX: c.x,
          gridY: c.y,
          mesh: momo,
          collected: false,
          baseY: 0.22,
          rotSpeed: 1.8 + Math.random() * 0.8
        });
      });
    }

    // 5. Build Grand Exit Leaf Arch
    if (mazeData.exitGate) {
      const exitX = (mazeData.exitGate.x - offset) * this.cellSize;
      const exitZ = (mazeData.exitGate.y - offset) * this.cellSize;

      const archGroup = new THREE.Group();
      archGroup.position.set(exitX, 0, exitZ);

      // Curved Arch Torus / Tube
      const archGeo = new THREE.TorusGeometry(0.85, 0.14, 12, 24, Math.PI);
      const arch = new THREE.Mesh(archGeo, this.matWoodGate);
      arch.position.y = 0.85;
      archGroup.add(arch);

      // Leaf clusters atop arch
      const leafGeo = new THREE.SphereGeometry(0.2, 10, 8);
      leafGeo.scale(1.2, 0.6, 0.8);
      const leafTop = new THREE.Mesh(leafGeo, this.matGateLeaf);
      leafTop.position.set(0, 1.75, 0);
      archGroup.add(leafTop);

      // Golden Grand Momo waiting at exit
      this.goldenExitMomo = this.createMomoMesh(true);
      this.goldenExitMomo.position.set(0, 0.35, 0);
      this.goldenExitMomo.scale.set(1.4, 1.4, 1.4);
      archGroup.add(this.goldenExitMomo);

      this.exitArchLight = new THREE.PointLight(0xFFD54F, 2.5, 6.0);
      this.exitArchLight.position.set(0, 1.5, 0);
      archGroup.add(this.exitArchLight);

      this.root.add(archGroup);
      this.exitGateMesh = archGroup;
    }
  }

  addFlowerCluster(x, z, y = 0.08) {
    const fGroup = new THREE.Group();
    fGroup.position.set(x, y, z);

    const petalMat = Math.random() < 0.5 ? this.matFlowerPink : this.matFlowerWhite;
    for (let i = 0; i < 5; i++) {
      const pGeo = new THREE.CircleGeometry(0.045, 8);
      const p = new THREE.Mesh(pGeo, petalMat);
      p.rotation.x = -Math.PI / 2;
      const angle = (i / 5) * Math.PI * 2;
      p.position.set(Math.cos(angle) * 0.05, 0, Math.sin(angle) * 0.05);
      fGroup.add(p);
    }
    const centerGeo = new THREE.SphereGeometry(0.025, 8, 8);
    const center = new THREE.Mesh(centerGeo, this.matFlowerYellow);
    center.position.y = 0.02;
    fGroup.add(center);

    this.root.add(fGroup);
  }

  update(delta, activePhase) {
    const time = performance.now() * 0.001;

    // Animate Momo dumplings
    this.momos.forEach(m => {
      if (!m.collected) {
        m.mesh.rotation.y += delta * m.rotSpeed;
        m.mesh.position.y = m.baseY + Math.sin(time * 3 + m.gridX) * 0.08;
      }
    });

    // Animate Golden Exit Momo
    if (this.goldenExitMomo) {
      this.goldenExitMomo.rotation.y += delta * 2.2;
      this.goldenExitMomo.position.y = 0.35 + Math.sin(time * 4) * 0.12;
    }

    // Animate Moving Gates (Phase A vs B)
    this.movingGates.forEach(g => {
      // If phase matches activePhase, gate is RAISED (blocking)
      // Otherwise it is LOWERED into the ground (open)
      const isBlocking = g.phase === activePhase;
      const targetY = isBlocking ? 0.65 : -1.0;
      g.barrier.position.y += (targetY - g.barrier.position.y) * Math.min(1.0, delta * 6.0);

      // Lantern glow pulses
      const pulse = 0.8 + Math.sin(time * 6) * 0.2;
      g.lantern.scale.set(pulse, pulse, pulse);
    });
  }

  collectMomo(gridX, gridY) {
    const item = this.momos.find(m => !m.collected && m.gridX === gridX && m.gridY === gridY);
    if (item) {
      item.collected = true;
      // Animate popping scale down and remove
      item.mesh.visible = false;
      return true;
    }
    return false;
  }

  clear() {
    if (this.root) {
      this.scene.remove(this.root);
      this.root = null;
    }
    this.momos = [];
    this.movingGates = [];
  }
}
