# MOMO MAZE – Asset Specification v1.0
# Derived from approved concept sheets (Nov 16 2026)

---

## 1. Project Overview

| Field | Value |
|---|---|
| Game Title | MOMO MAZE |
| Genre | Cozy 3D maze chase game |
| Engine | Unreal Engine 5.x |
| DCC | Blender 5.2 |
| Art Style | Low-mid poly, stylized, fluffy/matte materials |
| Maze Size | 31 × 31 cell grid (target, extendable from approved 12×12 small layout) |
| Player Character | Golumolu |
| Enemies | 3 Ghost spirits (Follower, Cutter, Wanderer) |
| Collectible | Momo (dumpling) |

---

## 2. Golumolu – Character Spec

### 2.1 Silhouette & Proportions
- **Shape:** Near-perfect sphere body, slightly squished vertically (Y scale ≈ 0.92, Z scale ≈ 0.88)
- **Ears:** Small rounded peach nubs, positioned upper-left/right of body, slight forward tilt
- **Cheeks:** Prominent rosy blush discs, center-left and center-right of face
- **Eyes:** Small, wide dark-brown happy-arc shapes; white sclera visible
- **Nose:** Tiny dark brown rounded triangle/nub, center face
- **Mouth:** Open happy curve, inner mouth visible (peach-red)
- **Arms:** Tiny rounded peach nubs at mid-sides, slightly forward
- **Feet:** Slightly larger rounded peach nubs at bottom, splayed outward
- **Tail:** Small cream nub at the back

### 2.2 Color Palette

| Part | Hex | Use |
|---|---|---|
| Cream | `#FCEEDD` | Main body fur |
| Peach | `#FFC189` | Ears, arms, feet, accents |
| Blush | `#FFB3B0` | Cheeks, ear inner |
| Brown | `#6B4226` | Eyes, nose, face lines |
| Mouth Inner | `#E27567` | Open mouth |
| White | `#FFFFFF` | Eye sclera |

### 2.3 Material Properties
- Soft matte fluffy look (Roughness 0.85–0.95)
- Minimal specular (IOR Level ≈ 0.05 on body)
- Eyes: moderate gloss (Roughness 0.5, Specular 0.3)
- No PBR texture maps needed for initial build – vertex color / material slots

### 2.4 Topology Targets
- Body sphere: 24 rings × 32 segments → subdivide ×1 at render
- Total tris budget: 2,000–4,000 (game-ready)
- Clean edge loops for rigging (waist, neck, arm bases)
- Ears and limbs: simple spheres, no internal geometry

### 2.5 Facial Expressions (Blend Shapes / Shape Keys)
| Expression | Description |
|---|---|
| Happy (default) | Eyes arc up, mouth open wide |
| Excited | Sparkle pupils, wide mouth |
| Scared | Round white eyes, O-mouth |
| Determined | Furrowed brows, set mouth |

### 2.6 Action/Animation Poses
- Idle (breathing bounce, subtle)
- Waddling Run
- Eating Momo (collect)
- Surprised (notice event)

---

## 3. Ghost Spirits – Character Spec

### 3.1 Shared Shape Language
- Round, fluffy head (larger than body, center of mass)
- Misty/airy tapered lower body (translucent, wispy tail)
- Small dark expressive eyes (personality-specific)
- Rosy cheeks on Follower/Wanderer
- Soft bloom + gentle glow (emissive material, additive)
- Gentle sparkle particle trail (VFX)

### 3.2 Color & Material

| Element | Value |
|---|---|
| Body base | Warm white `#FFF7EE` → `#FFF0D6` |
| Glow/FX | Warm yellow `#FFDFA8` → `#FFE8C7` (additive/bloom) |
| Tail | Translucent white, soft alpha falloff |
| Eyes | Small dark brown `#3D2B1F` |

Material notes:
- Soft matte top + additive emissive bloom layer
- Tail: translucent shader (Alpha Blend, low opacity)
- Particle trail: sparkle sprite, additive blend

### 3.3 Three Ghost Personalities

| Ghost | Eye Style | Personality Cue | Tail Motion |
|---|---|---|---|
| **Follower** | Simple round dots, friendly | Curious, steady | Gentle wave |
| **Cutter** | Angled, stern/mischievous | Clever, quick | Sharp flick |
| **Wanderer** | Wide, whimsical + star highlights | Dreamy/energetic | Swirling loop |

### 3.4 Topology Targets
- 800–2,500 tris per ghost
- Base mesh: UV sphere head + displaced/sculpted wispy tail
- All three share one base mesh; personality via shape keys and materials

### 3.5 Ghost Count in Gameplay
- Default: 2 ghosts active
- Optional: 3rd ghost toggle (Game Setup screen)

---

## 4. Environment – Maze Assets

### 4.1 Modular Piece List

| Piece | Tris Budget | Notes |
|---|---|---|
| Hedge Wall (Straight) | 150–400 | 1 m × 1 m tile, vertex wind WPO |
| Hedge Corner (90°) | 200–500 | Matching height/radius |
| Path Tile (Grass Ground) | 20–80 | Simple subdivided plane |
| Flower Patch (Decor) | 20–80 each | Daisy / pink flowers |
| Clover Patch | 20–80 | Small decal/mesh |
| Momo Spawn Pedestal | 300–600 | Warm stone base, glow point |
| Leaf Gate / Arch | 600–1,200 | Animated open/close |

### 4.2 Maze Structure
- Grid: 31 × 31 cells (each cell = 1 m in Unreal)
- Hedge wall unit: 1 m wide, 1.5 m tall
- Path width: 1 cell (1 m) — fits Golumolu + ghosts
- Entrance: Leaf Arch gate (south wall, center)
- Central area: open courtyard with Momo pedestals
- Outer border: solid hedge ring

### 4.3 Color Palette (Environment)

| Element | Hex |
|---|---|
| Hedge / Bush | `#7DC257` → `#5A9B3A` (gradient) |
| Path / Soil | `#C49A6C` → `#A07850` |
| Flower pink | `#F4A7B9` |
| Flower white | `#FFF5EE` |
| Flower center | `#F9D56E` |
| Stone arch | `#C8A882` |
| Momo glow | `#FFE08A` |

### 4.4 Living Maze – Animation
- Hedge vertex wind shader (subtle sway, amplitude 2 cm)
- Flowers: gentle bloom open/close loop
- Magic particle motes (ambient, additive glow)
- Leaf Gate: open on player approach, 1.5 s animation

---

## 5. UI Concept Spec

### 5.1 Style
- Warm cream background (`#FFF3E6`)
- Rounded rect panels (border-radius ≈ 24 px equivalent)
- Brown serif headings + warm-green accents
- Peach/amber CTA buttons

### 5.2 Screens
1. **Main Menu** – Logo, Play button, Settings / Character / Ghosts / Maze Select
2. **Game Setup** – Ghost Count (2/3), Maze Size (Small/Medium/Large) with preview icons
3. **In-Game HUD** – Lives (hearts, top-left), Momo counter (top-left), Objective (top-center), Pause (top-right)

---

## 6. Validation Render Checklist

### 6.1 Golumolu
- [ ] Front orthographic render
- [ ] 3/4 view render
- [ ] Side render
- [ ] Back render
- [ ] Compare silhouette against concept sheet
- [ ] Verify cream body, peach accents, blush cheeks

### 6.2 Ghosts
- [ ] Follower: front, side, 3/4
- [ ] Cutter: front, side, 3/4
- [ ] Wanderer: front, side, 3/4
- [ ] Tail translucency visible
- [ ] Glow/bloom visible

### 6.3 Environment
- [ ] Single Hedge Wall render
- [ ] Path tile + 2 flowers render
- [ ] Leaf Gate closed + open render
- [ ] Small 5×5 test maze render from isometric camera

---

## 7. File Structure

```
D:\Projects\MOMO MAZE\
├── Refrence image\          ← Approved concept sheets (read-only)
├── BlenderSources\
│   ├── scenes\              ← .blend files
│   ├── scripts\             ← Python build scripts
│   ├── exports\
│   │   ├── fbx\             ← Game-ready FBX exports
│   │   └── gltf\
│   └── renders\
│       ├── golumolu\        ← Validation renders
│       ├── ghosts\
│       └── environment\
├── UnrealProject\           ← UE5 project files
└── Docs\
    └── ASSET_SPEC.md        ← This file
```

---

## 8. Versioning Convention

| Version | Meaning |
|---|---|
| `_v001` | Initial build, unvalidated |
| `_v002` | Post-review corrections applied |
| `_vFINAL` | Approved, ready for engine import |

---

*Last updated: 2026-11-16 by Antigravity (Technical Lead)*
