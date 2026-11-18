// 3D Environment Builder for MOMO MAZE
// Blender Beauty Maze integration & Rich Procedural Foliage (Grass Tufts, Flowers, Curbs, Trees)
import * as THREE from './three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const gltfLoader = new GLTFLoader();

export class EnvironmentBuilder {
  constructor(scene, cellSize = 1.8) {
    this.scene = scene;
    this.cellSize = cellSize;
    this.momos = [];
    this.movingGates = [];
    this.exitGateMesh = null;
    this.exitArchLight = null;
    this.beautyEnvMesh = null;

    this.initMaterials();
    this.initGrassGeometry();
  }

  initMaterials() {
    // 1. Living hedge foliage material (rich velvety green)
    this.matHedge = new THREE.MeshStandardMaterial({
      color: 0x488A2C,
      roughness: 0.82,
      metalness: 0.04
    });

    this.matHedgeCrown = new THREE.MeshStandardMaterial({
      color: 0x5CAB34,
      roughness: 0.78,
      metalness: 0.03
    });

    this.matHedgeDark = new THREE.MeshStandardMaterial({
      color: 0x2E631B,
      roughness: 0.88,
      metalness: 0.05
    });

    // 2. Ground path tile (warm sandy stone with mossy earth rim)
    this.matGround = new THREE.MeshStandardMaterial({
      color: 0xD8C7A3,
      roughness: 0.92,
      metalness: 0.02
    });

    this.matLawn = new THREE.MeshStandardMaterial({
      color: 0x6EAD42,
      roughness: 0.88,
      metalness: 0.0
    });

    this.matCurb = new THREE.MeshStandardMaterial({
      color: 0x8E8A78,
      roughness: 0.9,
      metalness: 0.05
    });

    // 3. Grass tuft blade material (vibrant garden green)
    this.matGrassBlade = new THREE.MeshStandardMaterial({
      color: 0x5DA632,
      roughness: 0.75,
      metalness: 0.02,
      side: THREE.DoubleSide
    });

    // 4. Momo dumpling dough (warm cream + gentle golden glow)
    this.matMomo = new THREE.MeshStandardMaterial({
      color: 0xFFF8E7,
      roughness: 0.65,
      metalness: 0.05,
      emissive: 0xFFE082,
      emissiveIntensity: 0.22
    });

    // 5. Golden Grand Momo
    this.matGoldMomo = new THREE.MeshStandardMaterial({
      color: 0xFFCA28,
      roughness: 0.35,
      metalness: 0.45,
      emissive: 0xFFA000,
      emissiveIntensity: 0.45
    });

    // 6. Wood gate & tree trunk
    this.matWood = new THREE.MeshStandardMaterial({
      color: 0x6D4C41,
      roughness: 0.85,
      metalness: 0.05
    });

    this.matTreeLeaf = new THREE.MeshStandardMaterial({
      color: 0x388E3C,
      roughness: 0.8,
      metalness: 0.05
    });

    this.matGateLeaf = new THREE.MeshStandardMaterial({
      color: 0x4CAF50,
      roughness: 0.7,
      metalness: 0.05
    });

    // 7. Flowers
    this.matFlowerPink = new THREE.MeshBasicMaterial({ color: 0xF48FB1 });
    this.matFlowerWhite = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
    this.matFlowerYellow = new THREE.MeshBasicMaterial({ color: 0xFFEB3B });
  }

  // Pre-generate reusable 3D grass tuft geometry (5 fan-out blades)
  initGrassGeometry() {
    this.grassTuftGeo = new THREE.BufferGeometry();
    const vertices = [];
    const indices = [];

    const bladeAngles = [0, 0.7, 1.4, 2.2, 3.0, 3.8, 4.6, 5.4];
    bladeAngles.forEach((angle, idx) => {
      const height = 0.22 + Math.random() * 0.12;
      const width = 0.045;
      const bend = 0.08 + Math.random() * 0.06;

      const cos = Math.cos(angle);
      const sin = Math.sin(angle);

      const baseIdx = idx * 3;
      // Bottom left vertex
      vertices.push(-sin * width, 0, cos * width);
      // Bottom right vertex
      vertices.push(sin * width, 0, -cos * width);
      // Tip vertex (curved outward)
      vertices.push(cos * bend, height, sin * bend);

      indices.push(baseIdx, baseIdx + 1, baseIdx + 2);
    });

    this.grassTuftGeo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    this.grassTuftGeo.setIndex(indices);
    this.grassTuftGeo.computeVertexNormals();
  }

  createGrassTuftMesh() {
    return new THREE.Mesh(this.grassTuftGeo, this.matGrassBlade);
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
    const light = new THREE.PointLight(isGolden ? 0xFFA000 : 0xFFE082, isGolden ? 2.2 : 0.85, 2.8);
    light.position.y = 0.25;
    group.add(light);

    return group;
  }

  // Create an organic plush rounded hedge wall unit with crown spheres and grass tufts
  createHedgeUnit(cellSize) {
    const group = new THREE.Group();
    const w = cellSize * 0.96;
    const h = 1.35;
    const d = cellSize * 0.96;

    // Base beveled hedge body
    const hedgeGeo = new THREE.BoxGeometry(w, h * 0.85, d);
    const hedge = new THREE.Mesh(hedgeGeo, this.matHedge);
    hedge.position.y = (h * 0.85) / 2;
    hedge.castShadow = true;
    hedge.receiveShadow = true;
    group.add(hedge);

    // Fluffy rounded crown spheres on top (gives the velvety puffy hedge look!)
    const crownRadii = [w * 0.42, w * 0.36, w * 0.38];
    const offsets = [
      [-w * 0.18, d * 0.12],
      [w * 0.20, -d * 0.15],
      [0, 0]
    ];

    crownRadii.forEach((r, i) => {
      const crownGeo = new THREE.SphereGeometry(r, 12, 10);
      crownGeo.scale(1.0, 0.65, 1.0);
      const crown = new THREE.Mesh(crownGeo, i % 2 === 0 ? this.matHedgeCrown : this.matHedgeDark);
      crown.position.set(offsets[i][0], h * 0.82 + r * 0.3, offsets[i][1]);
      crown.castShadow = true;
      crown.receiveShadow = true;
      group.add(crown);
    });

    // 2 grass tufts sprouting at base of hedge
    const tuft1 = this.createGrassTuftMesh();
    tuft1.position.set(-w * 0.35, 0, d * 0.4);
    tuft1.scale.set(1.2, 1.2, 1.2);
    group.add(tuft1);

    const tuft2 = this.createGrassTuftMesh();
    tuft2.position.set(w * 0.38, 0, -d * 0.38);
    tuft2.scale.set(1.1, 1.1, 1.1);
    group.add(tuft2);

    return group;
  }

  // Build full maze scene
  buildMaze(mazeData, onReady = null) {
    this.clear();
    const size = mazeData.size;
    const grid = mazeData.grid;
    const offset = (size - 1) / 2;

    this.root = new THREE.Group();
    this.scene.add(this.root);

    // If level has beauty model enabled or is Level 1, load the Blender master scene!
    const isBeautyMaster = mazeData.isBeautyMaster || mazeData.isGrand31 === false && size <= 15;

    if (isBeautyMaster) {
      this.loadBlenderBeautyScene(mazeData, offset, onReady);
    } else {
      this.buildProceduralMaze(mazeData, offset);
      if (onReady) onReady();
    }
  }

  loadBlenderBeautyScene(mazeData, offset, onReady) {
    // 1. Build ground and cobblestone path tiles
    this.buildGroundPlane(mazeData.size);
    this.buildPathTiles(mazeData, offset);
    this.buildCollectiblesAndGates(mazeData, offset);

    // 2. Load beauty_maze_env.glb (1,171 objects from Blender)
    gltfLoader.load(
      'models/beauty_maze_env.glb',
      (gltf) => {
        const glb = gltf.scene;

        // Auto-scale to match current maze grid dimension
        const box = new THREE.Box3().setFromObject(glb);
        const sizeVec = box.getSize(new THREE.Vector3());
        const targetWidth = mazeData.size * this.cellSize;
        const scaleFactor = targetWidth / (sizeVec.x || 12.0);

        glb.scale.set(scaleFactor, scaleFactor, scaleFactor);
        glb.position.set(0, 0, 0);

        glb.traverse(child => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;

            const nameLow = (child.name + ' ' + (child.material?.name || '')).toLowerCase();
            if (nameLow.includes('hedge')) {
              child.material = this.matHedge;
            } else if (nameLow.includes('grass') || nameLow.includes('meadow') || nameLow.includes('tuft') || nameLow.includes('blade')) {
              child.material = this.matGrassBlade;
            } else if (nameLow.includes('curb') || nameLow.includes('rim')) {
              child.material = this.matCurb;
            } else if (nameLow.includes('tree') || nameLow.includes('canopy')) {
              child.material = this.matTreeLeaf;
            } else if (nameLow.includes('wood') || (nameLow.includes('cylinder') && (nameLow.includes('004') || nameLow.includes('005') || nameLow.includes('006') || nameLow.includes('007')))) {
              child.material = this.matWood;
            } else if (nameLow.includes('flower') || nameLow.includes('petal')) {
              child.material = nameLow.includes('pink') ? this.matFlowerPink : this.matFlowerWhite;
            }
          }
        });

        this.beautyEnvMesh = glb;
        this.root.add(glb);
        console.log('Blender Beauty Maze Environment loaded successfully into scene with lush vibrant foliage!');
        if (onReady) onReady();
      },
      undefined,
      (err) => {
        console.warn('Fallback to rich procedural maze:', err);
        this.buildProceduralWalls(mazeData, offset);
        if (onReady) onReady();
      }
    );
  }

  buildPathTiles(mazeData, offset) {
    const size = mazeData.size;
    const grid = mazeData.grid;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const cell = grid[y][x];
        if (cell === 0 || cell === 2 || cell === 3) {
          const worldX = (x - offset) * this.cellSize;
          const worldZ = (y - offset) * this.cellSize;
          const tileGeo = new THREE.BoxGeometry(this.cellSize * 0.98, 0.08, this.cellSize * 0.98);
          const tile = new THREE.Mesh(tileGeo, this.matGround);
          tile.position.set(worldX, 0.04, worldZ);
          tile.receiveShadow = true;
          this.root.add(tile);
        }
      }
    }
  }

  buildProceduralMaze(mazeData, offset) {
    this.buildGroundPlane(mazeData.size);
    this.buildProceduralWalls(mazeData, offset);
    this.buildCollectiblesAndGates(mazeData, offset);
    this.buildPerimeterCurbsAndTrees(mazeData.size, offset);
  }

  buildGroundPlane(size) {
    // 1. Vast scenic meadow plane underneath
    const vastSize = Math.max(80, size * this.cellSize * 2.8);
    const vastGroundGeo = new THREE.PlaneGeometry(vastSize, vastSize);
    const vastGround = new THREE.Mesh(vastGroundGeo, this.matLawn);
    vastGround.rotation.x = -Math.PI / 2;
    vastGround.position.y = -0.05;
    vastGround.receiveShadow = true;
    this.root.add(vastGround);
  }

  buildProceduralWalls(mazeData, offset) {
    const size = mazeData.size;
    const grid = mazeData.grid;

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

          // Path grass tufts & flowers
          if ((x * 7 + y * 13) % 11 === 0) {
            const tuft = this.createGrassTuftMesh();
            tuft.position.set(worldX + 0.35, 0.08, worldZ + 0.35);
            tuft.scale.set(0.9, 0.9, 0.9);
            this.root.add(tuft);
          }

          if ((x * 13 + y * 17) % 19 === 0) {
            this.addFlowerCluster(worldX - 0.3, worldZ + 0.35);
          }
        }

        // Wall: Hedge
        if (cell === 1) {
          const hedge = this.createHedgeUnit(this.cellSize);
          hedge.position.set(worldX, 0, worldZ);
          this.root.add(hedge);

          // Flower clusters on border hedges
          if ((x === 0 || x === size - 1 || y === 0 || y === size - 1) && (x + y) % 5 === 0) {
            this.addFlowerCluster(worldX, worldZ, 1.45);
          }
        }
      }
    }
  }

  buildPerimeterCurbsAndTrees(size, offset) {
    const totalSpan = size * this.cellSize;
    const halfSpan = totalSpan / 2;

    // Raised cobblestone curbs along outer perimeter
    const curbW = totalSpan + 0.6;
    const curbH = 0.25;
    const curbD = 0.35;

    const northCurb = new THREE.Mesh(new THREE.BoxGeometry(curbW, curbH, curbD), this.matCurb);
    northCurb.position.set(0, curbH / 2, -halfSpan - 0.2);
    northCurb.receiveShadow = true;
    northCurb.castShadow = true;
    this.root.add(northCurb);

    const southCurb = new THREE.Mesh(new THREE.BoxGeometry(curbW, curbH, curbD), this.matCurb);
    southCurb.position.set(0, curbH / 2, halfSpan + 0.2);
    southCurb.receiveShadow = true;
    southCurb.castShadow = true;
    this.root.add(southCurb);

    const westCurb = new THREE.Mesh(new THREE.BoxGeometry(curbD, curbH, curbW), this.matCurb);
    westCurb.position.set(-halfSpan - 0.2, curbH / 2, 0);
    westCurb.receiveShadow = true;
    westCurb.castShadow = true;
    this.root.add(westCurb);

    const eastCurb = new THREE.Mesh(new THREE.BoxGeometry(curbD, curbH, curbW), this.matCurb);
    eastCurb.position.set(halfSpan + 0.2, curbH / 2, 0);
    eastCurb.receiveShadow = true;
    eastCurb.castShadow = true;
    this.root.add(eastCurb);

    // Scenic Garden Trees at the four outer corners
    const treePositions = [
      [-halfSpan - 4, -halfSpan - 4],
      [halfSpan + 4, -halfSpan - 4],
      [-halfSpan - 4, halfSpan + 4],
      [halfSpan + 4, halfSpan + 4],
      [0, -halfSpan - 6],
      [0, halfSpan + 6]
    ];

    treePositions.forEach(([tx, tz]) => {
      this.addGardenTree(tx, tz);
    });
  }

  addGardenTree(x, z) {
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    // Trunk
    const trunkGeo = new THREE.CylinderGeometry(0.35, 0.45, 3.2, 8);
    const trunk = new THREE.Mesh(trunkGeo, this.matWood);
    trunk.position.y = 1.6;
    trunk.castShadow = true;
    group.add(trunk);

    // Foliage puffy canopy
    const canopyGeo1 = new THREE.SphereGeometry(1.6, 12, 10);
    canopyGeo1.scale(1.0, 0.8, 1.0);
    const canopy1 = new THREE.Mesh(canopyGeo1, this.matTreeLeaf);
    canopy1.position.y = 3.6;
    canopy1.castShadow = true;
    group.add(canopy1);

    const canopyGeo2 = new THREE.SphereGeometry(1.2, 10, 8);
    const canopy2 = new THREE.Mesh(canopyGeo2, this.matHedgeCrown);
    canopy2.position.set(0.4, 4.3, -0.3);
    canopy2.castShadow = true;
    group.add(canopy2);

    this.root.add(group);
  }

  buildCollectiblesAndGates(mazeData, offset) {
    // Moving Gates (Phase A & B)
    if (mazeData.movingGates && mazeData.movingGates.length > 0) {
      mazeData.movingGates.forEach(g => {
        const wx = (g.x - offset) * this.cellSize;
        const wz = (g.y - offset) * this.cellSize;

        const gateGroup = new THREE.Group();
        gateGroup.position.set(wx, 0, wz);

        // Trellis posts
        const postGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.5, 8);
        const postL = new THREE.Mesh(postGeo, this.matWood);
        postL.position.set(-this.cellSize * 0.42, 0.75, 0);
        postL.castShadow = true;
        gateGroup.add(postL);

        const postR = new THREE.Mesh(postGeo, this.matWood);
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

    // Momo Collectibles
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

    // Grand Exit Leaf Arch
    if (mazeData.exitGate) {
      const exitX = (mazeData.exitGate.x - offset) * this.cellSize;
      const exitZ = (mazeData.exitGate.y - offset) * this.cellSize;

      const archGroup = new THREE.Group();
      archGroup.position.set(exitX, 0, exitZ);

      // Curved Arch Torus
      const archGeo = new THREE.TorusGeometry(0.85, 0.14, 12, 24, Math.PI);
      const arch = new THREE.Mesh(archGeo, this.matWood);
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
      const isBlocking = g.phase === activePhase;
      const targetY = isBlocking ? 0.65 : -1.0;
      g.barrier.position.y += (targetY - g.barrier.position.y) * Math.min(1.0, delta * 6.0);

      const pulse = 0.8 + Math.sin(time * 6) * 0.2;
      g.lantern.scale.set(pulse, pulse, pulse);
    });
  }

  collectMomo(gridX, gridY) {
    const item = this.momos.find(m => !m.collected && m.gridX === gridX && m.gridY === gridY);
    if (item) {
      item.collected = true;
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
    this.beautyEnvMesh = null;
  }
}
