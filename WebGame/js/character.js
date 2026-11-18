// Golumolu 3D Character Model & Animation Rig for Three.js
import * as THREE from './three.module.js';

export const SKINS = {
  cream: {
    name: 'Classic Cream',
    body: 0xFCEEDD,
    accent: 0xFFC189,
    blush: 0xFFB3B0,
    eyes: 0x5C381E,
    mouth: 0xE27567
  },
  gold: {
    name: 'Golden Momo',
    body: 0xFFE599,
    accent: 0xFFA000,
    blush: 0xFFAB91,
    eyes: 0x4E342E,
    mouth: 0xD84315
  },
  matcha: {
    name: 'Matcha Dino',
    body: 0xDcedc8,
    accent: 0x8BC34A,
    blush: 0xF8BBD0,
    eyes: 0x33691E,
    mouth: 0xE27567
  },
  berry: {
    name: 'Berry Blossom',
    body: 0xFCE4EC,
    accent: 0xF48FB1,
    blush: 0xF06292,
    eyes: 0x880E4F,
    mouth: 0xC2185B
  },
  lavender: {
    name: 'Lavender Spirit',
    body: 0xF3E5F5,
    accent: 0xCE93D8,
    blush: 0xBA68C8,
    eyes: 0x4A148C,
    mouth: 0xAB47BC
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

    this.buildMesh();
  }

  setSkin(skinKey) {
    if (!SKINS[skinKey]) return;
    this.skinKey = skinKey;
    this.skin = SKINS[skinKey];

    // Update material colors
    this.matBody.color.setHex(this.skin.body);
    this.matAccent.color.setHex(this.skin.accent);
    this.matBlush.color.setHex(this.skin.blush);
    this.matEyes.color.setHex(this.skin.eyes);
    this.matMouth.color.setHex(this.skin.mouth);
  }

  buildMesh() {
    // Materials
    this.matBody = new THREE.MeshStandardMaterial({
      color: this.skin.body,
      roughness: 0.88,
      metalness: 0.05
    });

    this.matAccent = new THREE.MeshStandardMaterial({
      color: this.skin.accent,
      roughness: 0.85,
      metalness: 0.05
    });

    this.matBlush = new THREE.MeshBasicMaterial({
      color: this.skin.blush
    });

    this.matEyes = new THREE.MeshStandardMaterial({
      color: this.skin.eyes,
      roughness: 0.4,
      metalness: 0.1
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

    // 1. Chubby Body (slightly squished sphere: radius 0.42, squished Y: 0.92, Z: 0.88)
    const bodyGeo = new THREE.SphereGeometry(0.42, 28, 24);
    bodyGeo.scale(1.0, 0.92, 0.92);
    this.bodyMesh = new THREE.Mesh(bodyGeo, this.matBody);
    this.bodyMesh.position.y = 0.42;
    this.bodyMesh.castShadow = true;
    this.bodyMesh.receiveShadow = true;
    this.modelRoot.add(this.bodyMesh);

    // 2. Ears (peach rounded nubs tilted forward)
    const earGeo = new THREE.SphereGeometry(0.12, 16, 12);
    earGeo.scale(0.8, 1.2, 0.8);

    this.leftEar = new THREE.Mesh(earGeo, this.matAccent);
    this.leftEar.position.set(-0.25, 0.72, 0.05);
    this.leftEar.rotation.set(0.15, 0, 0.35);
    this.modelRoot.add(this.leftEar);

    this.rightEar = new THREE.Mesh(earGeo, this.matAccent);
    this.rightEar.position.set(0.25, 0.72, 0.05);
    this.rightEar.rotation.set(0.15, 0, -0.35);
    this.modelRoot.add(this.rightEar);

    // 3. Eyes (happy curves with white sparkle highlight)
    const eyeGeo = new THREE.SphereGeometry(0.055, 16, 12);
    eyeGeo.scale(0.85, 1.1, 0.4);

    const leftEye = new THREE.Mesh(eyeGeo, this.matEyes);
    leftEye.position.set(-0.13, 0.46, 0.36);
    this.modelRoot.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, this.matEyes);
    rightEye.position.set(0.13, 0.46, 0.36);
    this.modelRoot.add(rightEye);

    // Sparkles in eyes
    const sparkleGeo = new THREE.SphereGeometry(0.018, 8, 8);
    const leftSparkle = new THREE.Mesh(sparkleGeo, this.matEyeWhite);
    leftSparkle.position.set(-0.115, 0.485, 0.385);
    this.modelRoot.add(leftSparkle);

    const rightSparkle = new THREE.Mesh(sparkleGeo, this.matEyeWhite);
    rightSparkle.position.set(0.145, 0.485, 0.385);
    this.modelRoot.add(rightSparkle);

    // 4. Rosy Cheeks (blush discs)
    const blushGeo = new THREE.CircleGeometry(0.065, 16);
    const leftBlush = new THREE.Mesh(blushGeo, this.matBlush);
    leftBlush.position.set(-0.24, 0.36, 0.33);
    leftBlush.rotation.y = -0.4;
    this.modelRoot.add(leftBlush);

    const rightBlush = new THREE.Mesh(blushGeo, this.matBlush);
    rightBlush.position.set(0.24, 0.36, 0.33);
    rightBlush.rotation.y = 0.4;
    this.modelRoot.add(rightBlush);

    // 5. Tiny Nose & Happy Open Mouth
    const noseGeo = new THREE.SphereGeometry(0.024, 12, 10);
    const nose = new THREE.Mesh(noseGeo, this.matEyes);
    nose.position.set(0, 0.42, 0.39);
    this.modelRoot.add(nose);

    const mouthGeo = new THREE.SphereGeometry(0.05, 12, 10);
    mouthGeo.scale(1.0, 0.7, 0.5);
    this.mouth = new THREE.Mesh(mouthGeo, this.matMouth);
    this.mouth.position.set(0, 0.33, 0.37);
    this.modelRoot.add(this.mouth);

    // 6. Arms (side peach nubs)
    const armGeo = new THREE.SphereGeometry(0.09, 14, 12);
    armGeo.scale(0.8, 1.2, 0.9);

    this.leftArm = new THREE.Mesh(armGeo, this.matAccent);
    this.leftArm.position.set(-0.38, 0.38, 0.1);
    this.leftArm.rotation.z = 0.4;
    this.modelRoot.add(this.leftArm);

    this.rightArm = new THREE.Mesh(armGeo, this.matAccent);
    this.rightArm.position.set(0.38, 0.38, 0.1);
    this.rightArm.rotation.z = -0.4;
    this.modelRoot.add(this.rightArm);

    // 7. Feet (bottom splayed nubs)
    const footGeo = new THREE.SphereGeometry(0.12, 14, 12);
    footGeo.scale(0.9, 0.65, 1.25);

    this.leftFoot = new THREE.Mesh(footGeo, this.matAccent);
    this.leftFoot.position.set(-0.18, 0.08, 0.08);
    this.modelRoot.add(this.leftFoot);

    this.rightFoot = new THREE.Mesh(footGeo, this.matAccent);
    this.rightFoot.position.set(0.18, 0.08, 0.08);
    this.modelRoot.add(this.rightFoot);

    // 8. Fluffy Tail
    const tailGeo = new THREE.SphereGeometry(0.085, 14, 12);
    const tail = new THREE.Mesh(tailGeo, this.matAccent);
    tail.position.set(0, 0.22, -0.38);
    this.modelRoot.add(tail);

    // Soft lantern glow light following Golumolu
    this.glowLight = new THREE.PointLight(0xFFE8B0, 1.5, 4.5);
    this.glowLight.position.set(0, 0.7, 0);
    this.group.add(this.glowLight);
  }

  triggerEat() {
    this.eatAnim = 1.0;
  }

  update(delta) {
    if (this.eatAnim > 0) {
      this.eatAnim -= delta * 3.5;
      if (this.eatAnim < 0) this.eatAnim = 0;
      const hop = Math.sin(this.eatAnim * Math.PI) * 0.22;
      this.bodyMesh.scale.set(1.0 + hop * 0.3, 0.92 + hop * 0.5, 0.92 - hop * 0.2);
      this.mouth.scale.set(1.0 + hop * 1.5, 1.0 + hop * 1.5, 1.0);
    }

    if (this.isMoving) {
      this.walkCycle += delta * 12;
      const bob = Math.abs(Math.sin(this.walkCycle)) * 0.08;
      const tilt = Math.sin(this.walkCycle) * 0.12;

      this.bodyMesh.position.y = 0.42 + bob;
      this.modelRoot.rotation.z = tilt;

      // Waddling feet
      this.leftFoot.position.y = 0.08 + Math.max(0, -Math.sin(this.walkCycle) * 0.1);
      this.rightFoot.position.y = 0.08 + Math.max(0, Math.sin(this.walkCycle) * 0.1);

      // Arm swing
      this.leftArm.rotation.x = Math.sin(this.walkCycle) * 0.45;
      this.rightArm.rotation.x = -Math.sin(this.walkCycle) * 0.45;

      // Ear wobble
      this.leftEar.rotation.z = 0.35 + Math.sin(this.walkCycle) * 0.1;
      this.rightEar.rotation.z = -0.35 - Math.sin(this.walkCycle) * 0.1;
    } else {
      // Idle gentle breath
      this.walkCycle += delta * 2.5;
      const breath = Math.sin(this.walkCycle) * 0.025;
      this.bodyMesh.scale.set(1.0 + breath * 0.5, 0.92 - breath, 0.92 + breath * 0.5);
      this.leftFoot.position.y = 0.08;
      this.rightFoot.position.y = 0.08;
      this.modelRoot.rotation.z = 0;
      this.leftArm.rotation.x = 0;
      this.rightArm.rotation.x = 0;
    }
  }
}
