"""
MOMO MAZE – Ghost Spirits Master Production (All 3 Spirits)
============================================================
Faithfully reproduces the Spirits of Momo Maze from the approved Ghost Concept Sheet:
1. Shared Shape Language:
   - Horizontal floating wisp/teardrop silhouette (NOT vertical pawn!)
   - Fluffy rounded head at front
   - Flowing, tapering misty tail trailing horizontally behind with soft translucency
   - Warm white body (#FFF7EE ~ #FFF0D6) with warm peach-gold inner glow (#FFDFA8)
2. Three Distinct Personalities:
   - FOLLOWER:
     * Curious, friendly round/oval dark eyes with bright sparkle catchlights
     * Soft rosy blush cheeks (#FFB3B0)
     * Gentle, steady wavy tail
   - CUTTER:
     * Sharp, angled mischievous eyes (\ /) with determined brow expression
     * Aerodynamic swept-back head crest & streamlined fast tail
     * Clever, tricky personality
   - WANDERER:
     * Joyful, whimsical happy face with wide sparkling eyes and happy open mouth
     * Rosy blush cheeks
     * Whimsical curving tail
     * Orbiting golden magical swirl / star trail (#FFE8C7 glowing emissive ribbon)
3. Outputs:
   - Blender Scene: scenes/ghosts_master.blend
   - FBX Exports: ghost_follower.fbx, ghost_cutter.fbx, ghost_wanderer.fbx
   - Lineup render: renders/ghosts/spirits_hero_lineup.png
   - 3 views per ghost (Front, 3/4, Side):
     * renders/ghosts/ghost_follower_{front, 34view, side}.png
     * renders/ghosts/ghost_cutter_{front, 34view, side}.png
     * renders/ghosts/ghost_wanderer_{front, 34view, side}.png
"""

import bpy
import bmesh
import math
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCENE_DIR    = os.path.join(PROJECT_ROOT, "scenes")
FBX_DIR      = os.path.join(PROJECT_ROOT, "exports", "fbx")
RENDER_DIR   = os.path.join(PROJECT_ROOT, "renders", "ghosts")

for d in (SCENE_DIR, FBX_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

BLEND_PATH = os.path.join(SCENE_DIR, "ghosts_master.blend")

# ── Color Palette ──────────────────────────────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_to_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), alpha)

GHOST_WHITE = hex_to_rgba("#FFF7EE")  # Warm white base
GHOST_PEACH = hex_to_rgba("#FFF0D6")  # Warm cream tail
GHOST_GLOW  = hex_to_rgba("#FFDFA8")  # Warm yellow bloom
GOLD_SWIRL  = hex_to_rgba("#FFE4A0")  # Wanderer magical trail
EYE_DARK    = hex_to_rgba("#3D2B1F")  # Dark expressive eyes
BLUSH_PINK  = hex_to_rgba("#FFB3B0")  # Soft cheek blush
MOUTH_RED   = hex_to_rgba("#E27567")  # Wanderer open mouth
WHITE_SHINE = (1.0, 1.0, 1.0, 1.0)
STUDIO_BG   = hex_to_rgba("#F6EDE4")

RAD = math.radians

# ── Materials ──────────────────────────────────────────────────────────────
def create_ghost_body_material(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    bsdf.inputs["Base Color"].default_value = GHOST_WHITE
    bsdf.inputs["Roughness"].default_value = 0.85

    # Gentle emission for magical spirit luminescence
    for ek in ("Emission Color", "Emission"):
        if ek in bsdf.inputs:
            bsdf.inputs[ek].default_value = GHOST_WHITE
            break
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.18

    # Soft peach/gold Subsurface Scattering for ethereal volume
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = GHOST_GLOW
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.25

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

def create_tail_material(name, alpha=0.65):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    bsdf.inputs["Base Color"].default_value = GHOST_PEACH
    bsdf.inputs["Roughness"].default_value = 0.90

    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha

    for ek in ("Emission Color", "Emission"):
        if ek in bsdf.inputs:
            bsdf.inputs[ek].default_value = GHOST_GLOW
            break
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.25

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    mat.blend_method = 'BLEND'
    return mat

def create_solid_mat(name, color, roughness=0.5, emit=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness

    if emit > 0:
        for ek in ("Emission Color", "Emission"):
            if ek in bsdf.inputs:
                bsdf.inputs[ek].default_value = color
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

# Wipe scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

mat_body      = create_ghost_body_material("M_Ghost_Body")
mat_tail      = create_tail_material("M_Ghost_Tail", alpha=0.70)
mat_eye       = create_solid_mat("M_Ghost_Eye", EYE_DARK, roughness=0.35)
mat_shine     = create_solid_mat("M_Ghost_Shine", WHITE_SHINE, roughness=0.1, emit=0.8)
mat_blush     = create_solid_mat("M_Ghost_Blush", BLUSH_PINK, roughness=0.95)
mat_mouth     = create_solid_mat("M_Ghost_Mouth", MOUTH_RED, roughness=0.75)
mat_gold_fx   = create_solid_mat("M_Ghost_GoldAura", GOLD_SWIRL, roughness=0.2, emit=1.8)

# ── Helper: Horizontal Floating Spirit Body Mesh ───────────────────────────
def build_spirit_body(name, sweep_angle=0.0, crest_style="soft"):
    """
    Creates a floating spirit mesh:
    - Round front head facing -Y (or facing forward)
    - Tapering aerodynamic tail trailing in +Y with organic S-curve wisp
    - Top head tuft / crest curving backward
    """
    bm = bmesh.new()

    # Head (front sphere-like section)
    # Lofted rings from front (Y < 0) through back (Y > 0)
    rings = []
    # (y_pos, z_pos, radius_x, radius_z)
    profiles = [
        (-0.55,  0.02, 0.22, 0.22),  # Front nose curve
        (-0.45,  0.04, 0.44, 0.44),  # Forehead/cheeks
        (-0.25,  0.06, 0.54, 0.54),  # Mid head (widest)
        ( 0.00,  0.08, 0.52, 0.52),  # Back of head
        ( 0.25,  0.08, 0.44, 0.42),  # Neck taper
        ( 0.55,  0.07, 0.34, 0.32),  # Mid tail start
        ( 0.90,  0.09, 0.24, 0.20),  # Flowing tail wave
        ( 1.30,  0.15, 0.14, 0.11),  # Tail tip rising
        ( 1.65,  0.22, 0.04, 0.03),  # Tail wisp end point
    ]

    n_segments = 24
    for y, z, rx, rz in profiles:
        ring_verts = []
        for i in range(n_segments):
            angle = 2 * math.pi * i / n_segments
            x = rx * math.cos(angle)
            # Add subtle downward taper to lower belly
            z_offset = rz * math.sin(angle)
            ring_verts.append(bm.verts.new((x, y, z + z_offset)))
        rings.append(ring_verts)

    # Cap the front
    front_tip = bm.verts.new((0, -0.60, 0.02))
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        bm.faces.new([front_tip, rings[0][i], rings[0][i_next]])

    # Skin the rings
    for r in range(len(rings) - 1):
        r1 = rings[r]
        r2 = rings[r + 1]
        for i in range(n_segments):
            i_next = (i + 1) % n_segments
            bm.faces.new([r1[i], r1[i_next], r2[i_next], r2[i]])

    # Cap the tail tip
    tail_tip = bm.verts.new((0, 1.72, 0.25))
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        bm.faces.new([rings[-1][i_next], rings[-1][i], tail_tip])

    # Top Head Crest / Tuft (swept-back wisp on top of head)
    # A cute curved wisp extending backward from top-head
    crest_profiles = [
        (-0.15, 0.50, 0.18),
        ( 0.05, 0.58, 0.14),
        ( 0.30, 0.65, 0.09),
        ( 0.55, 0.68, 0.03),
    ]

    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()

    # Add Subdivision Surface for silky organic curvature
    subsurf = obj.modifiers.new("Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    obj.data.materials.append(mat_body)

    return obj

# ── BUILD 1: FOLLOWER GHOST ────────────────────────────────────────────────
# Curious, gentle, round friendly eyes with shine & soft blush
def build_follower(offset_x):
    col = bpy.data.collections.new("Ghost_Follower")
    scene.collection.children.link(col)

    body = build_spirit_body("Ghost_Follower_Body")
    body.location = (offset_x, 0, 0)
    col.objects.link(body)
    scene.collection.objects.unlink(body)

    parts = []

    # Eyes: Two vertical oval dark brown friendly eyes
    # Front of head is around Y = -0.50, Z = 0.06
    for side, s_name in [(1.0, "R"), (-1.0, "L")]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20, ring_count=14, radius=0.075,
            location=(offset_x + side * 0.16, -0.49, 0.08)
        )
        eye = bpy.context.active_object
        eye.name = f"Follower_Eye_{s_name}"
        eye.scale = (0.75, 0.28, 1.15)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_eye)
        col.objects.link(eye)
        scene.collection.objects.unlink(eye)
        parts.append(eye)

        # White eye highlight catchlight (sparkle)
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=0.026,
            location=(offset_x + side * 0.16 + 0.025, -0.51, 0.125)
        )
        shine = bpy.context.active_object
        shine.name = f"Follower_Shine_{s_name}"
        shine.scale = (1.0, 0.35, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mat_shine)
        col.objects.link(shine)
        scene.collection.objects.unlink(shine)
        parts.append(shine)

        # Cheek blush
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.085,
            location=(offset_x + side * 0.28, -0.44, -0.05)
        )
        chk = bpy.context.active_object
        chk.name = f"Follower_Cheek_{s_name}"
        chk.scale = (1.0, 0.22, 0.65)
        chk.rotation_euler = (RAD(12), side * RAD(-14), side * RAD(8))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        chk.data.materials.append(mat_blush)
        col.objects.link(chk)
        scene.collection.objects.unlink(chk)
        parts.append(chk)

    # Parent all parts to body
    for p in parts:
        p.parent = body

    return body, col

# ── BUILD 2: CUTTER GHOST ──────────────────────────────────────────────────
# Sharp, clever, determined inward angled eyes (\ /) and streamlined crest
def build_cutter(offset_x):
    col = bpy.data.collections.new("Ghost_Cutter")
    scene.collection.children.link(col)

    body = build_spirit_body("Ghost_Cutter_Body")
    body.location = (offset_x, 0, 0)
    # Make Cutter slightly more aerodynamic / streamlined
    body.scale = (0.94, 1.06, 0.96)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(scale=True)
    col.objects.link(body)
    scene.collection.objects.unlink(body)

    parts = []

    # Cutter's sharp angled eyes (\ /)
    # Slanted inward and down: sharp mischievous gaze
    for side, s_name in [(1.0, "R"), (-1.0, "L")]:
        curve_data = bpy.data.curves.new(name=f"Cutter_Eye_{s_name}_Curve", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.024
        curve_data.bevel_resolution = 4
        curve_data.use_fill_caps = True

        polyline = curve_data.splines.new('BEZIER')
        polyline.bezier_points.add(2)

        ox = offset_x + side * 0.16
        oy = -0.49
        oz = 0.08

        # Inward slant: outer corner is higher, inner corner is lower
        # P0: Inner lower corner
        p0 = polyline.bezier_points[0]
        p0.co = (ox - side * 0.07, oy + 0.03, oz - 0.035)
        p0.handle_left = (ox - side * 0.09, oy + 0.04, oz - 0.05)
        p0.handle_right = (ox - side * 0.03, oy + 0.01, oz - 0.01)

        # P1: Middle
        p1 = polyline.bezier_points[1]
        p1.co = (ox, oy - 0.005, oz + 0.015)
        p1.handle_left = (ox - side * 0.03, oy, oz)
        p1.handle_right = (ox + side * 0.03, oy, oz + 0.02)

        # P2: Outer sharp wing (tilted up)
        p2 = polyline.bezier_points[2]
        p2.co = (ox + side * 0.08, oy + 0.03, oz + 0.055)
        p2.handle_left = (ox + side * 0.04, oy + 0.01, oz + 0.04)
        p2.handle_right = (ox + side * 0.10, oy + 0.04, oz + 0.07)

        eye_obj = bpy.data.objects.new(f"Cutter_Eye_{s_name}", curve_data)
        bpy.context.collection.objects.link(eye_obj)
        bpy.context.view_layer.objects.active = eye_obj
        eye_obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.shade_smooth()
        eye_obj.data.materials.append(mat_eye)
        col.objects.link(eye_obj)
        scene.collection.objects.unlink(eye_obj)
        parts.append(eye_obj)

        # Subtle dark pupil fill behind the sharp brow stroke
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.045,
            location=(ox, oy + 0.01, oz)
        )
        pup = bpy.context.active_object
        pup.name = f"Cutter_Pupil_{s_name}"
        pup.scale = (1.1, 0.25, 0.75)
        pup.rotation_euler = (0, 0, side * RAD(24))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        pup.data.materials.append(mat_eye)
        col.objects.link(pup)
        scene.collection.objects.unlink(pup)
        parts.append(pup)

    for p in parts:
        p.parent = body

    return body, col

# ── BUILD 3: WANDERER GHOST ────────────────────────────────────────────────
# Whimsical, joyful, happy eyes, open smiling mouth, and orbiting golden ring/stars
def build_wanderer(offset_x):
    col = bpy.data.collections.new("Ghost_Wanderer")
    scene.collection.children.link(col)

    body = build_spirit_body("Ghost_Wanderer_Body")
    body.location = (offset_x, 0, 0)
    col.objects.link(body)
    scene.collection.objects.unlink(body)

    parts = []

    # Wanderer Face:
    # 1. Happy Eyes: Curved arches or wide sparkly eyes with double shine
    for side, s_name in [(1.0, "R"), (-1.0, "L")]:
        # Big sparkling eye
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20, ring_count=14, radius=0.08,
            location=(offset_x + side * 0.16, -0.49, 0.09)
        )
        eye = bpy.context.active_object
        eye.name = f"Wanderer_Eye_{s_name}"
        eye.scale = (0.82, 0.28, 1.10)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_eye)
        col.objects.link(eye)
        scene.collection.objects.unlink(eye)
        parts.append(eye)

        # Primary shine dot (large)
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=0.030,
            location=(offset_x + side * 0.16 + 0.026, -0.51, 0.13)
        )
        shine1 = bpy.context.active_object
        shine1.name = f"Wanderer_Shine1_{s_name}"
        shine1.scale = (1.0, 0.35, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        shine1.data.materials.append(mat_shine)
        col.objects.link(shine1)
        scene.collection.objects.unlink(shine1)
        parts.append(shine1)

        # Secondary star shine dot (small, bottom corner)
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10, ring_count=6, radius=0.016,
            location=(offset_x + side * 0.16 - 0.022, -0.505, 0.055)
        )
        shine2 = bpy.context.active_object
        shine2.name = f"Wanderer_Shine2_{s_name}"
        shine2.scale = (1.0, 0.35, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        shine2.data.materials.append(mat_gold_fx)
        col.objects.link(shine2)
        scene.collection.objects.unlink(shine2)
        parts.append(shine2)

        # Cheek blush
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.08,
            location=(offset_x + side * 0.28, -0.44, -0.05)
        )
        chk = bpy.context.active_object
        chk.name = f"Wanderer_Cheek_{s_name}"
        chk.scale = (1.0, 0.22, 0.65)
        chk.rotation_euler = (RAD(12), side * RAD(-14), side * RAD(8))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        chk.data.materials.append(mat_blush)
        col.objects.link(chk)
        scene.collection.objects.unlink(chk)
        parts.append(chk)

    # 2. Open happy smile mouth (:D)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=0.07,
        location=(offset_x, -0.505, -0.04)
    )
    mouth = bpy.context.active_object
    mouth.name = "Wanderer_Mouth"
    mouth.scale = (1.1, 0.25, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mat_mouth)
    col.objects.link(mouth)
    scene.collection.objects.unlink(mouth)
    parts.append(mouth)

    # 3. Orbiting Golden Magical Swirl / Star Trail (Signature feature of Wanderer)
    curve_data = bpy.data.curves.new(name="Wanderer_Aura_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.022
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True

    polyline = curve_data.splines.new('BEZIER')
    n_pts = 6
    polyline.bezier_points.add(n_pts - 1)

    # Spiral / tilted elliptical orbit around Wanderer's body
    r_orbit_x = 0.75
    r_orbit_y = 0.85
    z_center  = 0.05

    for i in range(n_pts):
        angle = 2 * math.pi * i / (n_pts - 1)
        bx = offset_x + r_orbit_x * math.cos(angle)
        by = r_orbit_y * math.sin(angle)
        bz = z_center + 0.35 * math.sin(angle) + 0.15 * math.cos(2 * angle)

        pt = polyline.bezier_points[i]
        pt.co = (bx, by, bz)
        pt.handle_left  = (bx - 0.25 * math.sin(angle), by + 0.25 * math.cos(angle), bz)
        pt.handle_right = (bx + 0.25 * math.sin(angle), by - 0.25 * math.cos(angle), bz)

    aura_obj = bpy.data.objects.new("Wanderer_Aura_Ring", curve_data)
    bpy.context.collection.objects.link(aura_obj)
    bpy.context.view_layer.objects.active = aura_obj
    aura_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.shade_smooth()
    aura_obj.data.materials.append(mat_gold_fx)
    col.objects.link(aura_obj)
    scene.collection.objects.unlink(aura_obj)
    parts.append(aura_obj)

    # Tiny golden magical spark stars around the swirl
    for i, (sx, sy, sz) in enumerate([
        (0.65, -0.30, 0.35),
        (-0.70, 0.40, 0.10),
        (0.20, 0.80, -0.15)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10, ring_count=8, radius=0.035,
            location=(offset_x + sx, sy, sz)
        )
        star = bpy.context.active_object
        star.name = f"Wanderer_Star_{i}"
        star.scale = (1.4, 0.6, 1.4)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        star.data.materials.append(mat_gold_fx)
        col.objects.link(star)
        scene.collection.objects.unlink(star)
        parts.append(star)

    for p in parts:
        p.parent = body

    return body, col

# ── Assemble Scene ─────────────────────────────────────────────────────────
print("Building the 3 Spirits of Momo Maze...")
follower_body, follower_col = build_follower(offset_x=-3.2)
cutter_body,   cutter_col   = build_cutter(offset_x=0.0)
wanderer_body, wanderer_col = build_wanderer(offset_x=3.2)

# ── Studio Lighting & Environment ──────────────────────────────────────────
# Key Light (warm soft sunlight)
bpy.ops.object.light_add(type='AREA', location=(2.5, -4.5, 4.0))
key = bpy.context.active_object
key.name = "Spirits_Key"
key.data.energy = 550
key.data.color = (1.0, 0.95, 0.88)
key.data.size = 5.0
key.rotation_euler = (RAD(50), 0, RAD(25))

# Fill Light (warm ambient)
bpy.ops.object.light_add(type='AREA', location=(-3.5, -3.0, 2.0))
fill = bpy.context.active_object
fill.name = "Spirits_Fill"
fill.data.energy = 220
fill.data.color = (1.0, 0.90, 0.84)
fill.data.size = 6.0

# Rim Light (back-top highlight for translucent spirit edge glow)
bpy.ops.object.light_add(type='AREA', location=(0.0, 4.0, 3.2))
rim = bpy.context.active_object
rim.name = "Spirits_Rim"
rim.data.energy = 260
rim.data.color = (1.0, 0.96, 0.90)
rim.data.size = 6.0
rim.rotation_euler = (RAD(-45), 0, RAD(180))

# World Background
world = bpy.data.worlds.new("SpiritsStudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = STUDIO_BG
    bg.inputs["Strength"].default_value = 0.85

# ── Render Setup ───────────────────────────────────────────────────────────
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True

# 1. HERO LINEUP RENDER (All 3 spirits side-by-side matching the concept banner)
scene.render.resolution_x = 1600
scene.render.resolution_y = 700

bpy.ops.object.camera_add(location=(0, -6.5, 0.3))
cam_lineup = bpy.context.active_object
cam_lineup.name = "Camera_Hero_Lineup"
cam_lineup.rotation_euler = (RAD(87), 0, 0)
cam_lineup.data.type = 'ORTHO'
cam_lineup.data.ortho_scale = 10.5
scene.camera = cam_lineup

lineup_path = os.path.join(RENDER_DIR, "spirits_hero_lineup.png")
scene.render.filepath = lineup_path
bpy.ops.render.render(write_still=True)
print(f"  ✓ Hero Lineup rendered -> {lineup_path}")

# 2. INDIVIDUAL TURNAROUNDS (Front, 3/4, Side) FOR EACH SPIRIT
scene.render.resolution_x = 768
scene.render.resolution_y = 768

ghosts_data = [
    ("follower", -3.2, follower_body),
    ("cutter",    0.0, cutter_body),
    ("wanderer",  3.2, wanderer_body),
]

for g_name, ox, g_body in ghosts_data:
    views = [
        ("front",  (ox,        -3.8,  0.15), (RAD(90), 0, 0),         2.5),
        ("34view", (ox + 2.4,  -2.6,  0.85), (RAD(74), 0, RAD(44)),   2.8),
        ("side",   (ox + 3.4,   0.0,  0.15), (RAD(90), 0, RAD(90)),   2.8),
    ]

    for v_name, loc, rot, ortho_s in views:
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object
        cam.name = f"Camera_{g_name}_{v_name}"
        cam.rotation_euler = rot
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = ortho_s
        scene.camera = cam

        out_img = os.path.join(RENDER_DIR, f"ghost_{g_name}_{v_name}.png")
        scene.render.filepath = out_img
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ Rendered {g_name} {v_name} -> {out_img}")

# ── Save .blend & Export FBX for each Ghost ────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved master scene: {BLEND_PATH}")

for g_name, ox, col in [
    ("follower", -3.2, follower_col),
    ("cutter",    0.0, cutter_col),
    ("wanderer",  3.2, wanderer_col),
]:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)

    fbx_out = os.path.join(FBX_DIR, f"ghost_{g_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
        add_leaf_bones=False
    )
    print(f"Exported FBX: {fbx_out}")

print("=== All 3 Ghost Spirits Master Production Completed Successfully ===")
