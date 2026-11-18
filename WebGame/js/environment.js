// 3D Environment Builder for MOMO MAZE
// Blender Beauty Maze integration & Rich Procedural Foliage (Grass Tufts, Flowers, Curbs, Trees)
import * as THREE from './three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const gltfLoader = new GLTFLoader();

export class EnvironmentBuilder {
  constructor(scene, cellSize = 2.0) {
    this.scene = scene;
    this.cellSize = cellSize;
    this.momos = [];
    this.movingGates = [];
    this.exitGateMesh = null;
    this.exitArchLight = null;
    this.beautyEnvMesh = null;
    this.blasts = [];

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

  // Pre-generate reusable 3D grass tuft geometry (neat low lawn blades)
  initGrassGeometry() {
    this.grassTuftGeo = new THREE.BufferGeometry();
    const vertices = [];
    const indices = [];

    const bladeAngles = [0, 0.7, 1.4, 2.2, 3.0, 3.8, 4.6, 5.4];
    bladeAngles.forEach((angle, idx) => {
      const height = 0.07 + Math.random() * 0.04; // Neat, short carpet lawn grass!
      const width = 0.032;
      const bend = 0.02 + Math.random() * 0.02;

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

  // Create an authentic, beautiful steamed Momo dumpling mesh
  createMomoMesh(isGolden = false) {
    const group = new THREE.Group();
    const matDough = isGolden ? this.matGoldMomo : this.matMomo;

    // 1. Bamboo steamer leaf / pedestal coaster
    const leafGeo = new THREE.CylinderGeometry(0.38, 0.40, 0.04, 16);
    const leafMat = new THREE.MeshStandardMaterial({
      color: isGolden ? 0x8D6E63 : 0x558B2F, // lush bamboo leaf green
      roughness: 0.85,
      metalness: 0.02
    });
    const leaf = new THREE.Mesh(leafGeo, leafMat);
    leaf.position.y = 0.02;
    leaf.receiveShadow = true;
    group.add(leaf);

    // 2. Plump, juicy steamed dumpling belly
    const bellyGeo = new THREE.SphereGeometry(0.30, 24, 18);
    bellyGeo.scale(1.0, 0.72, 1.0);
    const belly = new THREE.Mesh(bellyGeo, matDough);
    belly.position.y = 0.22;
    belly.castShadow = true;
    belly.receiveShadow = true;
    group.add(belly);

    // 3. Delicate pleated spiral pinch folds (8 radiating petal twists)
    const foldCount = 8;
    for (let i = 0; i < foldCount; i++) {
      const angle = (i / foldCount) * Math.PI * 2;
      const foldGeo = new THREE.SphereGeometry(0.09, 10, 8);
      foldGeo.scale(0.55, 1.35, 0.85);
      const fold = new THREE.Mesh(foldGeo, matDough);

      const rad = 0.12;
      fold.position.set(Math.cos(angle) * rad, 0.36, Math.sin(angle) * rad);
      fold.rotation.y = angle + 0.35; // gentle swirl
      fold.rotation.z = Math.cos(angle) * 0.22;
      fold.rotation.x = Math.sin(angle) * 0.22;
      fold.castShadow = true;
      group.add(fold);
    }

    // 4. Center pleated twist crown / pinch knot
    const twistGeo = new THREE.ConeGeometry(0.08, 0.15, 8);
    const twist = new THREE.Mesh(twistGeo, matDough);
    twist.position.y = 0.44;
    twist.rotation.y = 0.5;
    group.add(twist);

    // 5. Warm golden halo sparkle light
    const light = new THREE.PointLight(isGolden ? 0xFFA000 : 0xFFE082, isGolden ? 2.5 : 1.2, 3.5);
    light.position.y = 0.32;
    group.add(light);

    // Scale momo up so it's juicy and prominent in the corridor
    group.scale.set(1.35, 1.35, 1.35);

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
    this.cellSize = mazeData.cellSize || (size <= 15 ? 1.0 : 1.2);
    const grid = mazeData.grid;
    const offset = (size - 1) / 2;

    this.root = new THREE.Group();
    this.scene.add(this.root);

    // If level has beauty model enabled or is Level 1, load the Blender master scene!
    const isBeautyMaster = mazeData.isBeautyMaster || (mazeData.isGrand31 === false && size <= 15);

    if (isBeautyMaster) {
      this.loadBlenderBeautyScene(mazeData, offset, onReady);
    } else {
      this.buildProceduralMaze(mazeData, offset);
      if (onReady) onReady();
    }
  }

  loadBlenderBeautyScene(mazeData, offset, onReady) {
    this.momos = [];

    // Load the original 12x12 living garden maze exported directly from Blender
    gltfLoader.load(
      'models/beauty_maze.glb',
      (gltf) => {
        const glb = gltf.scene;

        // 1:1 exact metric scaling matching verified wall segments
        glb.scale.set(1.0, 1.0, 1.0);
        glb.position.set(0, 0, 0);

        glb.traverse(child => {
          // Remove any imported glTF lights to avoid tone-mapping blowout
          if (child.isLight) {
            child.visible = false;
            if (child.parent) child.parent.remove(child);
            return;
          }

          // Hide static beauty-render models (Golumolu, spirits, cam target, momo)
          if (child.name) {
            const nl = child.name.toLowerCase();
            if (nl.includes('golu') || nl.includes('spirit_') || nl.includes('momo_collectible') || nl.includes('cam_')) {
              child.visible = false;
              return;
            }
          }

          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;

            const m = child.material;
            if (m) {
              const mn = (m.name || '').toLowerCase();
              if (mn.includes('crown')) {
                m.color.setHex(0x62C426); // sunlit lime crown highlights
                m.roughness = 0.58;
                m.metalness = 0.02;
              } else if (mn.includes('hedge')) {
                m.color.setHex(0x469E20); // lush emerald living hedge
                m.roughness = 0.65;
                m.metalness = 0.02;
              } else if (mn.includes('grass') || mn.includes('blade')) {
                m.color.setHex(0x5EAE2A);
                m.roughness = 0.68;
              } else if (mn.includes('lawn') || mn.includes('ground') || mn.includes('meadow')) {
                m.color.setHex(0x549E26);
                m.roughness = 0.85;
              } else if (mn.includes('curb') || mn.includes('terracotta') || mn.includes('earth')) {
                m.color.setHex(0xBC6E42);
                m.roughness = 0.72;
              } else if (mn.includes('stone') || mn.includes('ancient')) {
                m.color.setHex(0xD4C6AA);
                m.roughness = 0.75;
              } else if (mn.includes('wood') || mn.includes('cedar')) {
                m.color.setHex(0x8D5B36);
                m.roughness = 0.75;
              }
            }
          }
        });

        this.beautyEnvMesh = glb;
        this.root.add(glb);

        // Add broad meadow ground plane at y = -0.40 so there's never a void
        const meadowGeo = new THREE.PlaneGeometry(90, 90);
        const meadowMat = new THREE.MeshStandardMaterial({
          color: 0x4E9426,
          roughness: 0.90,
          metalness: 0.0
        });
        const meadowMesh = new THREE.Mesh(meadowGeo, meadowMat);
        meadowMesh.rotation.x = -Math.PI / 2;
        meadowMesh.position.y = -0.41;
        meadowMesh.receiveShadow = true;
        this.root.add(meadowMesh);

        // Spawn collectible steamed dumplings at verified clear pathway coordinates
        if (mazeData.collectiblesWorld && mazeData.collectiblesWorld.length > 0) {
          mazeData.collectiblesWorld.forEach((c, idx) => {
            const momoMesh = this.createMomoMesh(false);
            momoMesh.position.set(c.x, 0.40, c.z);
            momoMesh.scale.set(1.6, 1.6, 1.6);
            this.root.add(momoMesh);
            this.momos.push({
              id: idx,
              gridX: c.x,
              gridY: c.z,
              worldX: c.x,
              worldZ: c.z,
              mesh: momoMesh,
              collected: false,
              baseY: 0.40,
              rotSpeed: 2.0 + Math.random() * 0.8
            });
          });
        }

        // Setup the Legendary Golden Momo Sanctuary
        const gmX = mazeData.goldenMomoWorld ? mazeData.goldenMomoWorld.x : 0.0;
        const gmZ = mazeData.goldenMomoWorld ? mazeData.goldenMomoWorld.z : -1.0;
        const gmMesh = this.createMomoMesh(true);
        gmMesh.position.set(gmX, 0.55, gmZ);
        gmMesh.scale.set(1.8, 1.8, 1.8);
        this.root.add(gmMesh);

        this.goldenMomo = {
          x: gmX,
          z: gmZ,
          mesh: gmMesh,
          collected: false
        };

        // Try loading the enhanced 3D Golden Momo model exported from Blender
        gltfLoader.load(
          'models/SM_UI_GoldenMomo.glb',
          (gltf) => {
            const gmGlb = gltf.scene;
            gmGlb.position.set(gmX, 0.05, gmZ);
            gmGlb.scale.set(1.4, 1.4, 1.4);
            gmGlb.traverse(c => {
              if (c.isMesh) {
                c.castShadow = true;
                c.receiveShadow = true;
              }
            });
            this.root.remove(gmMesh);
            this.root.add(gmGlb);
            this.goldenMomo.mesh = gmGlb;
          },
          undefined,
          () => {
            // Keep procedural mesh if GLB fails
          }
        );

        // Golden sanctuary point light
        const gLight = new THREE.PointLight(0xFFA000, 3.2, 7.0);
        gLight.position.set(gmX, 1.2, gmZ);
        this.root.add(gLight);

        console.log('Original Blender Beauty Maze loaded with 100% PBR accuracy and zero clipping!');
        if (onReady) onReady();
      },
      undefined,
      (err) => {
        console.warn('Fallback to procedural maze:', err);
        this.buildGroundPlane(mazeData.size);
        this.buildProceduralWalls(mazeData, offset);
        this.buildCollectiblesAndGates(mazeData, offset);
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

  // Celebratory blast animation when Golumolu eats a momo!
  spawnMomoBlast(worldX, worldY, worldZ, isGolden = false) {
    if (!this.root) return;
    const blastGroup = new THREE.Group();
    blastGroup.position.set(worldX, worldY + 0.25, worldZ);
    this.root.add(blastGroup);

    // 1. Expanding golden shockwave ring
    const ringGeo = new THREE.TorusGeometry(0.28, 0.06, 12, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: isGolden ? 0xFFD54F : 0xFFE082,
      transparent: true,
      opacity: 0.95
    });
    const shockwave = new THREE.Mesh(ringGeo, ringMat);
    shockwave.rotation.x = Math.PI / 2;
    blastGroup.add(shockwave);

    // 2. Blast particles (32 sparkling stars, golden crumbs, and rainbow celebration motes)
    const particleColors = isGolden
      ? [0xFFD54F, 0xFFA000, 0xFFF9C4, 0xFFFFFF]
      : [0xFFE082, 0xFFF9C4, 0xFF8A65, 0x81C784, 0x64B5F6, 0xFFFFFF];

    const particles = [];
    const count = 32;
    for (let i = 0; i < count; i++) {
      const pGeo = Math.random() < 0.45
        ? new THREE.SphereGeometry(0.08 + Math.random() * 0.06, 8, 8)
        : new THREE.BoxGeometry(0.10, 0.10, 0.10);

      const color = particleColors[Math.floor(Math.random() * particleColors.length)];
      const pMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 1.0 });
      const pMesh = new THREE.Mesh(pGeo, pMat);

      // Random 3D spherical direction
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const speed = 2.8 + Math.random() * 4.2;

      const vx = Math.sin(phi) * Math.cos(theta) * speed;
      const vy = Math.abs(Math.cos(phi)) * speed * 1.3 + 1.4; // upward celebration fountain bias!
      const vz = Math.sin(phi) * Math.sin(theta) * speed;

      blastGroup.add(pMesh);
      particles.push({
        mesh: pMesh,
        mat: pMat,
        vx, vy, vz,
        rotSpeedX: (Math.random() - 0.5) * 14,
        rotSpeedY: (Math.random() - 0.5) * 14,
        scale: 1.0
      });
    }

    // 2b. Juicy dumpling dough & filling goo splatter drops
    const gooCount = 12;
    for (let j = 0; j < gooCount; j++) {
      const gooGeo = new THREE.SphereGeometry(0.12 + Math.random() * 0.08, 10, 8);
      gooGeo.scale(1.0, 0.45, 1.0); // squashed dough drop
      const gooMat = new THREE.MeshBasicMaterial({
        color: isGolden ? 0xFFCA28 : (Math.random() < 0.6 ? 0xFFF5DD : 0xFFE082),
        transparent: true,
        opacity: 0.95
      });
      const gooMesh = new THREE.Mesh(gooGeo, gooMat);
      const angle = (j / gooCount) * Math.PI * 2 + Math.random() * 0.4;
      const speed = 2.2 + Math.random() * 3.5;
      const vx = Math.cos(angle) * speed;
      const vy = 1.8 + Math.random() * 3.0;
      const vz = Math.sin(angle) * speed;
      blastGroup.add(gooMesh);
      particles.push({
        mesh: gooMesh,
        mat: gooMat,
        vx, vy, vz,
        rotSpeedX: (Math.random() - 0.5) * 8,
        rotSpeedY: (Math.random() - 0.5) * 8,
        scale: 1.0
      });
    }

    // 3. Golden flash point light
    const flashLight = new THREE.PointLight(isGolden ? 0xFFA000 : 0xFFE082, 4.5, 6.0);
    blastGroup.add(flashLight);

    this.blasts.push({
      group: blastGroup,
      shockwave,
      ringMat,
      particles,
      flashLight,
      life: 0.75,
      maxLife: 0.75
    });
  }

  update(delta, activePhase) {
    const time = performance.now() * 0.001;

    // Animate Momo dumplings (gentle bob & swirl)
    this.momos.forEach(m => {
      if (!m.collected && m.mesh) {
        m.mesh.rotation.y += delta * (m.rotSpeed || 2.0);
        const gx = (m.gridX !== undefined) ? m.gridX : (m.worldX || 0);
        const by = m.baseY || 0.40;
        m.mesh.position.y = by + Math.sin(time * 3.5 + gx) * 0.08;
      }
    });

    // Animate Golden Exit Momo
    if (this.goldenExitMomo) {
      this.goldenExitMomo.rotation.y += delta * 2.2;
      this.goldenExitMomo.position.y = 0.35 + Math.sin(time * 4) * 0.12;
    }

    // Animate blast particle explosions
    for (let i = this.blasts.length - 1; i >= 0; i--) {
      const b = this.blasts[i];
      b.life -= delta;
      const progress = 1.0 - (b.life / b.maxLife); // 0.0 -> 1.0

      // Shockwave expands rapidly and fades
      const ringScale = 1.0 + progress * 5.5;
      b.shockwave.scale.set(ringScale, ringScale, ringScale);
      b.ringMat.opacity = Math.max(0, 1.0 - progress * 1.3);

      // Flash light fades
      b.flashLight.intensity = Math.max(0, (1.0 - progress) * 4.5);

      // Move blast particles with gravity and velocity
      b.particles.forEach(p => {
        p.mesh.position.x += p.vx * delta;
        p.mesh.position.y += p.vy * delta;
        p.mesh.position.z += p.vz * delta;
        p.vy -= 10.5 * delta; // gravity pull
        p.mesh.rotation.x += p.rotSpeedX * delta;
        p.mesh.rotation.y += p.rotSpeedY * delta;

        const pScale = Math.max(0.01, (1.0 - progress));
        p.mesh.scale.set(pScale, pScale, pScale);
        p.mat.opacity = Math.max(0, 1.0 - progress);
      });

      if (b.life <= 0) {
        if (this.root) this.root.remove(b.group);
        this.blasts.splice(i, 1);
      }
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
      this.spawnMomoBlast(item.mesh.position.x, item.mesh.position.y, item.mesh.position.z, false);
      return true;
    }
    return false;
  }

  collectMomoAt(worldX, worldZ, radius = 0.95) {
    for (const m of this.momos) {
      if (!m.collected) {
        const dist = Math.hypot(worldX - m.mesh.position.x, worldZ - m.mesh.position.z);
        if (dist < radius) {
          m.collected = true;
          m.mesh.visible = false;
          this.spawnMomoBlast(m.mesh.position.x, m.mesh.position.y, m.mesh.position.z, false);
          return true;
        }
      }
    }
    return false;
  }

  collectGoldenMomoAt(worldX, worldZ, radius = 1.15) {
    if (this.goldenMomo && !this.goldenMomo.collected) {
      const dist = Math.hypot(worldX - this.goldenMomo.x, worldZ - this.goldenMomo.z);
      if (dist < radius) {
        this.goldenMomo.collected = true;
        if (this.goldenMomo.mesh) {
          this.goldenMomo.mesh.visible = false;
        }
        this.spawnMomoBlast(this.goldenMomo.x, 0.4, this.goldenMomo.z, true);
        return true;
      }
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
    this.blasts = [];
    this.beautyEnvMesh = null;
  }
}
