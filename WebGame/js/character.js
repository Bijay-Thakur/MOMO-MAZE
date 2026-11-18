// Golumolu 3D Character Model & Animation Rig for Three.js
// Enhanced with Dinosaur Back Spikes, Distinct Warm Honey/Apricot Color & Hero Scaling
import * as THREE from './three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const gltfLoader = new GLTFLoader();

export const SKINS = {
  honey_dino: {
    name: 'Honey Dino (Original)',
    body: 0xFF9E44,     // Rich warm golden apricot / honey dino
    belly: 0xFFF3E0,    // Soft cream belly
    spikes: 0xFF7043,   // Terracotta peach dinosaur spikes
    accent: 0xFFB74D,   // Peach paws & feet
    blush: 0xFF4081,    // Vibrant rosy cheeks
    eyes: 0x3E2723,     // Dark glossy brown eyes
    mouth: 0xE53935
  },
  golden_momo: {
    name: 'Golden Momo',
    body: 0xFFD54F,
    belly: 0xFFF9C4,
    spikes: 0xFFA000,
    accent: 0xFFB300,
    blush: 0xFF8A65,
    eyes: 0x3E2723,
    mouth: 0xD84315
  },
  matcha_dino: {
    name: 'Matcha Dino',
    body: 0x9CCC65,
    belly: 0xF1F8E9,
    spikes: 0x689F38,
    accent: 0x8BC34A,
    blush: 0xF48FB1,
    eyes: 0x33691E,
    mouth: 0xE27567
  },
  berry_blossom: {
    name: 'Berry Blossom',
    body: 0xF48FB1,
    belly: 0xFCE4EC,
    spikes: 0xEC407A,
    accent: 0xF06292,
    blush: 0xD81B60,
    eyes: 0x880E4F,
    mouth: 0xC2185B
  },
  lavender_spirit: {
    name: 'Lavender Spirit',
    body: 0xBA68C8,
    belly: 0xF3E5F5,
    spikes: 0x8E24AA,
    accent: 0xAB47BC,
    blush: 0x7B1FA2,
    eyes: 0x4A148C,
    mouth: 0xAB47BC
  }
};

export class GolumoluCharacter {
  constructor(skinKey = 'honey_dino') {
    this.group = new THREE.Group();
    this.skinKey = skinKey;
    this.skin = SKINS[skinKey] || SKINS.honey_dino;

    this.walkCycle = 0;
    this.isMoving = false;
    this.eatAnim = 0;

    // Scale up to Hero Size (1.9x) so Golumolu is prominent and clearly visible!
    this.group.scale.set(1.9, 1.9, 1.9);

    this.buildMesh();
    this.loadGLBModel();
  }

  loadGLBModel() {
    gltfLoader.load(
      'models/golumolu.glb',
      (gltf) => {
        const glb = gltf.scene;
        const box = new THREE.Box3().setFromObject(glb);
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const targetSize = 1.0;
        const s = targetSize / (maxDim || 1);
        glb.scale.set(s, s, s);
        glb.position.set(0, 0.42, 0);

        glb.traverse(c => {
          if (c.isMesh) {
            c.castShadow = true;
            c.receiveShadow = true;
          }
        });

        // Hide procedural mesh and show GLB
        if (this.proceduralRoot) {
          this.proceduralRoot.visible = false;
        }
        this.glbMesh = glb;
        this.modelRoot.add(glb);
      },
      undefined,
      (err) => {
        console.log('Using procedural Golumolu model');
      }
    );
  }

  setSkin(skinKey) {
    if (!SKINS[skinKey]) return;
    this.skinKey = skinKey;
    this.skin = SKINS[skinKey];

    this.matBody.color.setHex(this.skin.body);
    this.matBelly.color.setHex(this.skin.belly);
    this.matSpikes.color.setHex(this.skin.spikes);
    this.matAccent.color.setHex(this.skin.accent);
    this.matBlush.color.setHex(this.skin.blush);
    this.matEyes.color.setHex(this.skin.eyes);
    this.matMouth.color.setHex(this.skin.mouth);
  }

  buildMesh() {
    this.matBody = new THREE.MeshStandardMaterial({
      color: this.skin.body,
      roughness: 0.75,
      metalness: 0.05
    });

    this.matBelly = new THREE.MeshStandardMaterial({
      color: this.skin.belly,
      roughness: 0.8,
      metalness: 0.05
    });

    this.matSpikes = new THREE.MeshStandardMaterial({
      color: this.skin.spikes,
      roughness: 0.7,
      metalness: 0.1
    });

    this.matAccent = new THREE.MeshStandardMaterial({
      color: this.skin.accent,
      roughness: 0.8,
      metalness: 0.05
    });

    this.matBlush = new THREE.MeshBasicMaterial({
      color: this.skin.blush
    });

    this.matEyes = new THREE.MeshStandardMaterial({
      color: this.skin.eyes,
      roughness: 0.25,
      metalness: 0.15
    });

    this.matEyeWhite = new THREE.MeshBasicMaterial({
      color: 0xFFFFFF
    });

    this.matMouth = new THREE.MeshBasicMaterial({
      color: this.skin.mouth
    });

    // Root model container
    this.modelRoot = new THREE.Group();
    this.group.add(this.modelRoot);

    // 1. Chubby Main Body (radius 0.44, squished Y: 0.94)
    const bodyGeo = new THREE.SphereGeometry(0.44, 28, 24);
    bodyGeo.scale(1.0, 0.94, 0.94);
    this.bodyMesh = new THREE.Mesh(bodyGeo, this.matBody);
    this.bodyMesh.position.y = 0.44;
    this.bodyMesh.castShadow = true;
    this.bodyMesh.receiveShadow = true;
    this.modelRoot.add(this.bodyMesh);

    // 2. Soft Cream Belly Oval Patch
    const bellyGeo = new THREE.SphereGeometry(0.38, 20, 16);
    bellyGeo.scale(0.85, 0.85, 0.35);
    const belly = new THREE.Mesh(bellyGeo, this.matBelly);
    belly.position.set(0, 0.38, 0.28);
    this.modelRoot.add(belly);

    // 3. Cute Dinosaur Dorsal Spikes (Godzilla Spikes 1..4 on back/head from Blender)
    this.spikes = [];
    const spikeConfigs = [
      { y: 0.80, z: -0.05, s: 0.11, rot: 0.15 }, // Front head spike
      { y: 0.78, z: -0.22, s: 0.13, rot: -0.15 }, // Mid back spike (largest)
      { y: 0.62, z: -0.38, s: 0.11, rot: -0.35 }, // Lower back spike
      { y: 0.44, z: -0.46, s: 0.08, rot: -0.55 }  // Base tail spike
    ];

    spikeConfigs.forEach(cfg => {
      const spGeo = new THREE.ConeGeometry(cfg.s, cfg.s * 2.2, 12);
      const sp = new THREE.Mesh(spGeo, this.matSpikes);
      sp.position.set(0, cfg.y, cfg.z);
      sp.rotation.x = cfg.rot;
      sp.castShadow = true;
      this.modelRoot.add(sp);
      this.spikes.push(sp);
    });

    // 4. Ears (rounded peach nubs tilted forward)
    const earGeo = new THREE.SphereGeometry(0.12, 16, 12);
    earGeo.scale(0.8, 1.25, 0.8);

    this.leftEar = new THREE.Mesh(earGeo, this.matAccent);
    this.leftEar.position.set(-0.27, 0.74, 0.08);
    this.leftEar.rotation.set(0.15, 0, 0.35);
    this.leftEar.castShadow = true;
    this.modelRoot.add(this.leftEar);

    this.rightEar = new THREE.Mesh(earGeo, this.matAccent);
    this.rightEar.position.set(0.27, 0.74, 0.08);
    this.rightEar.rotation.set(0.15, 0, -0.35);
    this.rightEar.castShadow = true;
    this.modelRoot.add(this.rightEar);

    // 5. Expressive Happy Eyes with double sparkle glints
    const eyeGeo = new THREE.SphereGeometry(0.065, 16, 12);
    eyeGeo.scale(0.85, 1.15, 0.4);

    const leftEye = new THREE.Mesh(eyeGeo, this.matEyes);
    leftEye.position.set(-0.15, 0.48, 0.39);
    this.modelRoot.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, this.matEyes);
    rightEye.position.set(0.15, 0.48, 0.39);
    this.modelRoot.add(rightEye);

    // Major & minor sparkles in eyes
    const glint1Geo = new THREE.SphereGeometry(0.022, 10, 8);
    const glint2Geo = new THREE.SphereGeometry(0.012, 8, 6);

    const glint1L = new THREE.Mesh(glint1Geo, this.matEyeWhite);
    glint1L.position.set(-0.13, 0.51, 0.42);
    this.modelRoot.add(glint1L);

    const glint2L = new THREE.Mesh(glint2Geo, this.matEyeWhite);
    glint2L.position.set(-0.165, 0.46, 0.42);
    this.modelRoot.add(glint2L);

    const glint1R = new THREE.Mesh(glint1Geo, this.matEyeWhite);
    glint1R.position.set(0.17, 0.51, 0.42);
    this.modelRoot.add(glint1R);

    const glint2R = new THREE.Mesh(glint2Geo, this.matEyeWhite);
    glint2R.position.set(0.135, 0.46, 0.42);
    this.modelRoot.add(glint2R);

    // 6. Vibrant Rosy Blush Discs
    const blushGeo = new THREE.CircleGeometry(0.075, 16);
    const leftBlush = new THREE.Mesh(blushGeo, this.matBlush);
    leftBlush.position.set(-0.27, 0.37, 0.35);
    leftBlush.rotation.y = -0.42;
    this.modelRoot.add(leftBlush);

    const rightBlush = new THREE.Mesh(blushGeo, this.matBlush);
    rightBlush.position.set(0.27, 0.37, 0.35);
    rightBlush.rotation.y = 0.42;
    this.modelRoot.add(rightBlush);

    // 7. Tiny Nose & Cute Open Mouth with Tongue
    const noseGeo = new THREE.SphereGeometry(0.026, 12, 10);
    const nose = new THREE.Mesh(noseGeo, this.matEyes);
    nose.position.set(0, 0.44, 0.42);
    this.modelRoot.add(nose);

    const mouthGeo = new THREE.SphereGeometry(0.055, 12, 10);
    mouthGeo.scale(1.0, 0.75, 0.5);
    this.mouth = new THREE.Mesh(mouthGeo, this.matMouth);
    this.mouth.position.set(0, 0.35, 0.40);
    this.modelRoot.add(this.mouth);

    // 8. Front Paws (hands)
    const pawGeo = new THREE.SphereGeometry(0.095, 14, 12);
    pawGeo.scale(0.85, 1.1, 0.9);

    this.leftArm = new THREE.Mesh(pawGeo, this.matAccent);
    this.leftArm.position.set(-0.38, 0.38, 0.16);
    this.leftArm.rotation.set(0.2, 0, 0.4);
    this.modelRoot.add(this.leftArm);

    this.rightArm = new THREE.Mesh(pawGeo, this.matAccent);
    this.rightArm.position.set(0.38, 0.38, 0.16);
    this.rightArm.rotation.set(0.2, 0, -0.4);
    this.modelRoot.add(this.rightArm);

    // 9. Sturdy Feet (splayed outward)
    const footGeo = new THREE.SphereGeometry(0.13, 16, 12);
    footGeo.scale(0.95, 0.65, 1.3);

    this.leftFoot = new THREE.Mesh(footGeo, this.matAccent);
    this.leftFoot.position.set(-0.20, 0.08, 0.08);
    this.leftFoot.castShadow = true;
    this.modelRoot.add(this.leftFoot);

    this.rightFoot = new THREE.Mesh(footGeo, this.matAccent);
    this.rightFoot.position.set(0.20, 0.08, 0.08);
    this.rightFoot.castShadow = true;
    this.modelRoot.add(this.rightFoot);

    // 10. Fluffy Dino Tail with peach tip
    const tailGeo = new THREE.SphereGeometry(0.12, 14, 12);
    tailGeo.scale(0.85, 0.85, 1.4);
    const tail = new THREE.Mesh(tailGeo, this.matBody);
    tail.position.set(0, 0.24, -0.42);
    tail.rotation.x = -0.25;
    this.modelRoot.add(tail);

    const tipGeo = new THREE.SphereGeometry(0.075, 12, 10);
    const tip = new THREE.Mesh(tipGeo, this.matAccent);
    tip.position.set(0, 0.28, -0.56);
    this.modelRoot.add(tip);

    // Warm friendly lantern light following Golumolu
    this.glowLight = new THREE.PointLight(0xFFE082, 1.8, 5.5);
    this.glowLight.position.set(0, 0.8, 0);
    this.group.add(this.glowLight);
  }

  triggerEat() {
    this.eatAnim = 1.0;
  }

  update(delta) {
    if (this.eatAnim > 0) {
      this.eatAnim -= delta * 3.5;
      if (this.eatAnim < 0) this.eatAnim = 0;
      const hop = Math.sin(this.eatAnim * Math.PI) * 0.24;
      this.bodyMesh.scale.set(1.0 + hop * 0.25, 0.94 + hop * 0.45, 0.94 - hop * 0.15);
      this.mouth.scale.set(1.0 + hop * 1.6, 1.0 + hop * 1.6, 1.0);
    }

    if (this.isMoving) {
      this.walkCycle += delta * 12;
      const bob = Math.abs(Math.sin(this.walkCycle)) * 0.1;
      const tilt = Math.sin(this.walkCycle) * 0.14;

      this.bodyMesh.position.y = 0.44 + bob;
      this.modelRoot.rotation.z = tilt;

      // Waddling feet animation
      this.leftFoot.position.y = 0.08 + Math.max(0, -Math.sin(this.walkCycle) * 0.12);
      this.rightFoot.position.y = 0.08 + Math.max(0, Math.sin(this.walkCycle) * 0.12);

      // Arm swing
      this.leftArm.rotation.x = 0.2 + Math.sin(this.walkCycle) * 0.55;
      this.rightArm.rotation.x = 0.2 - Math.sin(this.walkCycle) * 0.55;

      // Ear & spike bounce
      this.leftEar.rotation.z = 0.35 + Math.sin(this.walkCycle) * 0.12;
      this.rightEar.rotation.z = -0.35 - Math.sin(this.walkCycle) * 0.12;

      this.spikes.forEach((sp, idx) => {
        sp.rotation.z = Math.sin(this.walkCycle + idx * 0.5) * 0.1;
      });
    } else {
      // Idle breathing bounce
      this.walkCycle += delta * 2.8;
      const breath = Math.sin(this.walkCycle) * 0.03;
      this.bodyMesh.scale.set(1.0 + breath * 0.5, 0.94 - breath, 0.94 + breath * 0.5);
      this.leftFoot.position.y = 0.08;
      this.rightFoot.position.y = 0.08;
      this.modelRoot.rotation.z = 0;
      this.leftArm.rotation.x = 0.2;
      this.rightArm.rotation.x = 0.2;
    }
  }
}
