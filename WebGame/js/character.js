// Golumolu 3D Character Model & Animation Rig for Three.js
// Faithfully matches Reference Concept Sheet: 02_Golumolu_Character_Concept.png
// Chubby, fluffy creature who loves momos! Cream fur (#FCEEDD), peach ears & paws (#FFC189), rosy cheeks (#FFB3B0)

import * as THREE from './three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const gltfLoader = new GLTFLoader();

export const SKINS = {
  cream: {
    name: 'Classic Cream (Original)',
    body: 0xFCEEDD,     // Warm fluffy cream fur
    belly: 0xFFFBF2,    // Soft white-cream belly
    accent: 0xFFC189,   // Soft peach ears, paws, feet, tail
    blush: 0xFFB3B0,    // Rosy pink blush cheeks
    eyes: 0x6B4226,     // Dark glossy brown eyes
    mouth: 0xE27567     // Soft peach-red mouth
  },
  golden_momo: {
    name: 'Golden Momo',
    body: 0xFFE082,
    belly: 0xFFF8E1,
    accent: 0xFFA726,
    blush: 0xFFAB91,
    eyes: 0x4E342E,
    mouth: 0xE64A19
  },
  berry_blossom: {
    name: 'Berry Blossom',
    body: 0xF8BBD0,
    belly: 0xFCE4EC,
    accent: 0xF48FB1,
    blush: 0xE91E63,
    eyes: 0x880E4F,
    mouth: 0xC2185B
  },
  matcha: {
    name: 'Matcha Meadow',
    body: 0xC5E1A5,
    belly: 0xF1F8E9,
    accent: 0x8BC34A,
    blush: 0xF48FB1,
    eyes: 0x33691E,
    mouth: 0xE27567
  }
};

export class GolumoluCharacter {
  constructor(skinKey = 'cream') {
    this.group = new THREE.Group();
    this.skinKey = skinKey;
    this.skin = SKINS[skinKey] || SKINS.cream;

    this.walkCycle = 0;
    this.isMoving = false;
    this.eatAnim = 0;

    // Scale to fit corridor width (1.0m) comfortably while remaining cute & prominent
    this.group.scale.set(1.0, 1.0, 1.0);

    this.buildMesh();
    this.loadGLBModel();
  }

  loadGLBModel() {
    gltfLoader.load(
      'models/golumolu.glb',
      (gltf) => {
        const glb = gltf.scene;
        glb.traverse(c => {
          if (c.isMesh) {
            c.castShadow = true;
            c.receiveShadow = true;
          }
        });

        // 1:1 scale matching corridor width 1.0m
        glb.scale.set(1.0, 1.0, 1.0);
        glb.position.set(0, 0, 0);

        if (this.proceduralRoot) {
          this.proceduralRoot.visible = false;
        }
        this.glbMesh = glb;
        this.modelRoot.add(glb);
      },
      undefined,
      (err) => {
        console.log('Using procedural Golumolu matching concept art');
      }
    );
  }

  setSkin(skinKey) {
    if (!SKINS[skinKey]) return;
    this.skinKey = skinKey;
    this.skin = SKINS[skinKey];

    this.matBody.color.setHex(this.skin.body);
    this.matBelly.color.setHex(this.skin.belly);
    this.matAccent.color.setHex(this.skin.accent);
    this.matBlush.color.setHex(this.skin.blush);
    this.matEyes.color.setHex(this.skin.eyes);
    this.matMouth.color.setHex(this.skin.mouth);
  }

  buildMesh() {
    this.matBody = new THREE.MeshStandardMaterial({
      color: this.skin.body,
      roughness: 0.85,
      metalness: 0.02
    });

    this.matBelly = new THREE.MeshStandardMaterial({
      color: this.skin.belly,
      roughness: 0.88,
      metalness: 0.02
    });

    this.matAccent = new THREE.MeshStandardMaterial({
      color: this.skin.accent,
      roughness: 0.80,
      metalness: 0.02
    });

    this.matBlush = new THREE.MeshBasicMaterial({
      color: this.skin.blush
    });

    this.matEyes = new THREE.MeshStandardMaterial({
      color: this.skin.eyes,
      roughness: 0.15,
      metalness: 0.05
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

    this.proceduralRoot = new THREE.Group();
    this.modelRoot.add(this.proceduralRoot);

    // 1. Chubby Main Body (radius 0.44, squished Y: 0.94)
    const bodyGeo = new THREE.SphereGeometry(0.44, 28, 24);
    bodyGeo.scale(1.02, 0.94, 0.92);
    this.bodyMesh = new THREE.Mesh(bodyGeo, this.matBody);
    this.bodyMesh.position.y = 0.44;
    this.bodyMesh.castShadow = true;
    this.bodyMesh.receiveShadow = true;
    this.proceduralRoot.add(this.bodyMesh);

    // 2. Soft Cream Belly Patch
    const bellyGeo = new THREE.SphereGeometry(0.38, 20, 16);
    bellyGeo.scale(0.85, 0.85, 0.35);
    const belly = new THREE.Mesh(bellyGeo, this.matBelly);
    belly.position.set(0, 0.38, 0.28);
    this.proceduralRoot.add(belly);

    // 3. Peach Ears (Small rounded nubs with slight forward tilt)
    const earGeo = new THREE.SphereGeometry(0.12, 16, 12);
    earGeo.scale(0.85, 0.70, 0.95);

    this.leftEar = new THREE.Mesh(earGeo, this.matAccent);
    this.leftEar.position.set(-0.28, 0.76, 0.05);
    this.leftEar.rotation.z = 0.35;
    this.proceduralRoot.add(this.leftEar);

    this.rightEar = new THREE.Mesh(earGeo, this.matAccent);
    this.rightEar.position.set(0.28, 0.76, 0.05);
    this.rightEar.rotation.z = -0.35;
    this.proceduralRoot.add(this.rightEar);

    // 4. Prominent Rosy Blush Cheeks
    const blushGeo = new THREE.CircleGeometry(0.09, 16);
    const leftBlush = new THREE.Mesh(blushGeo, this.matBlush);
    leftBlush.position.set(-0.28, 0.42, 0.38);
    leftBlush.rotation.y = -0.28;
    this.proceduralRoot.add(leftBlush);

    const rightBlush = new THREE.Mesh(blushGeo, this.matBlush);
    rightBlush.position.set(0.28, 0.42, 0.38);
    rightBlush.rotation.y = 0.28;
    this.proceduralRoot.add(rightBlush);

    // 5. Dark Glossy Brown Happy Eyes & Glints
    const eyeGeo = new THREE.SphereGeometry(0.055, 14, 10);
    eyeGeo.scale(0.85, 0.35, 1.15);

    this.leftEye = new THREE.Mesh(eyeGeo, this.matEyes);
    this.leftEye.position.set(-0.15, 0.50, 0.40);
    this.proceduralRoot.add(this.leftEye);

    this.rightEye = new THREE.Mesh(eyeGeo, this.matEyes);
    this.rightEye.position.set(0.15, 0.50, 0.40);
    this.proceduralRoot.add(this.rightEye);

    // Sparkle catchlights
    const glintGeo = new THREE.SphereGeometry(0.02, 8, 8);
    const glintL = new THREE.Mesh(glintGeo, this.matEyeWhite);
    glintL.position.set(-0.13, 0.53, 0.43);
    this.proceduralRoot.add(glintL);

    const glintR = new THREE.Mesh(glintGeo, this.matEyeWhite);
    glintR.position.set(0.17, 0.53, 0.43);
    this.proceduralRoot.add(glintR);

    // 6. Tiny Cute Nose
    const noseGeo = new THREE.SphereGeometry(0.025, 8, 8);
    const nose = new THREE.Mesh(noseGeo, this.matEyes);
    nose.position.set(0, 0.47, 0.43);
    this.proceduralRoot.add(nose);

    // 7. Open Smiling Mouth
    const mouthGeo = new THREE.SphereGeometry(0.06, 12, 10);
    mouthGeo.scale(1.2, 0.4, 0.8);
    this.mouth = new THREE.Mesh(mouthGeo, this.matMouth);
    this.mouth.position.set(0, 0.39, 0.41);
    this.proceduralRoot.add(this.mouth);

    // 8. Tiny Rounded Peach Paws (Hands)
    const armGeo = new THREE.SphereGeometry(0.09, 12, 10);
    armGeo.scale(0.85, 1.10, 0.75);

    this.leftArm = new THREE.Mesh(armGeo, this.matAccent);
    this.leftArm.position.set(-0.35, 0.32, 0.22);
    this.leftArm.rotation.x = 0.2;
    this.proceduralRoot.add(this.leftArm);

    this.rightArm = new THREE.Mesh(armGeo, this.matAccent);
    this.rightArm.position.set(0.35, 0.32, 0.22);
    this.rightArm.rotation.x = 0.2;
    this.proceduralRoot.add(this.rightArm);

    // 9. Tiny Rounded Peach Feet
    const footGeo = new THREE.SphereGeometry(0.11, 14, 10);
    footGeo.scale(0.90, 1.35, 0.65);

    this.leftFoot = new THREE.Mesh(footGeo, this.matAccent);
    this.leftFoot.position.set(-0.19, 0.08, 0.06);
    this.leftFoot.castShadow = true;
    this.proceduralRoot.add(this.leftFoot);

    this.rightFoot = new THREE.Mesh(footGeo, this.matAccent);
    this.rightFoot.position.set(0.19, 0.08, 0.06);
    this.rightFoot.castShadow = true;
    this.proceduralRoot.add(this.rightFoot);

    // 10. Cute Rounded Peach Tail at the back
    const tailGeo = new THREE.SphereGeometry(0.14, 14, 10);
    tailGeo.scale(0.90, 1.25, 0.85);
    this.tailMesh = new THREE.Mesh(tailGeo, this.matAccent);
    this.tailMesh.position.set(0, 0.28, -0.42);
    this.proceduralRoot.add(this.tailMesh);

    // Warm friendly lantern light following Golumolu
    this.glowLight = new THREE.PointLight(0xFFE082, 1.5, 4.5);
    this.glowLight.position.set(0, 0.6, 0);
    this.group.add(this.glowLight);
  }

  triggerEat() {
    this.eatAnim = 1.0;
  }

  update(delta) {
    if (this.eatAnim > 0) {
      this.eatAnim -= delta * 4.0;
      if (this.eatAnim < 0) this.eatAnim = 0;
      const hop = Math.sin(this.eatAnim * Math.PI) * 0.22;
      this.bodyMesh.scale.set(1.02 + hop * 0.25, 0.94 + hop * 0.40, 0.92 - hop * 0.15);
      this.mouth.scale.set(1.0 + hop * 1.5, 1.0 + hop * 1.5, 1.0);
    }

    if (this.isMoving) {
      this.walkCycle += delta * 12;
      const bob = Math.abs(Math.sin(this.walkCycle)) * 0.08;
      const tilt = Math.sin(this.walkCycle) * 0.12;

      this.bodyMesh.position.y = 0.44 + bob;
      this.modelRoot.rotation.z = tilt;

      // Waddling feet animation
      this.leftFoot.position.y = 0.08 + Math.max(0, -Math.sin(this.walkCycle) * 0.10);
      this.rightFoot.position.y = 0.08 + Math.max(0, Math.sin(this.walkCycle) * 0.10);

      // Arm swing
      this.leftArm.rotation.x = 0.2 + Math.sin(this.walkCycle) * 0.50;
      this.rightArm.rotation.x = 0.2 - Math.sin(this.walkCycle) * 0.50;

      // Ear bounce
      this.leftEar.rotation.z = 0.35 + Math.sin(this.walkCycle) * 0.10;
      this.rightEar.rotation.z = -0.35 - Math.sin(this.walkCycle) * 0.10;

      // Tail wag
      this.tailMesh.rotation.y = Math.sin(this.walkCycle * 1.5) * 0.25;

      if (this.glbMesh) {
        this.glbMesh.position.y = 0.05 + bob;
        this.glbMesh.rotation.z = tilt;
      }
    } else {
      // Idle breathing bounce
      this.walkCycle += delta * 2.8;
      const breath = Math.sin(this.walkCycle) * 0.025;
      this.bodyMesh.scale.set(1.02 + breath * 0.4, 0.94 - breath, 0.92 + breath * 0.4);
      this.leftFoot.position.y = 0.08;
      this.rightFoot.position.y = 0.08;
      this.modelRoot.rotation.z = 0;
      this.leftArm.rotation.x = 0.2;
      this.rightArm.rotation.x = 0.2;
      this.tailMesh.rotation.y = 0;

      if (this.glbMesh) {
        this.glbMesh.position.y = 0.05;
        this.glbMesh.rotation.z = 0;
      }
    }
  }
}
