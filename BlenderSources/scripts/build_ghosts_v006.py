"""
MOMO MAZE – Ghost Spirits Master Production (v006 - Definitive Release)
=======================================================================
Faithful 3D reproduction of the Spirits of Momo Maze from approved concept sheet:
- Follower (Curious, loyal, vertical dark eyes, bright sparkle, blush)
- Cutter (Clever, tricky, sharp inward angled eyes \ /, dynamic crest)
- Wanderer (Dreamy, whimsical, sparkling wide eyes, open smile mouth :D, golden magical halo)
- Clean local coordinates & hierarchy (all parts move with parent head)
- Hero Lineup render matching concept banner
- Front, 3/4, and Side validation renders for each of the 3 spirits
- Saves scenes/ghosts_master.blend & exports 3 game-ready FBXs
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

# ── Colors ─────────────────────────────────────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_to_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), alpha)

GHOST_WHITE = hex_to_rgba("#FFF7EE")  # Warm white body
GHOST_GLOW  = hex_to_rgba("#FFDFA8")  # Warm yellow bloom
GOLD_SWIRL  = hex_to_rgba("#FFE28A")  # Wanderer golden aura
EYE_DARK    = hex_to_rgba("#3D2B1F")  # Dark expressive eyes
BLUSH_PINK  = hex_to_rgba("#FFB3B0")  # Soft cheek blush
MOUTH_RED   = hex_to_rgba("#E27567")  # Wanderer open smile
WHITE_SHINE = (1.0, 1.0, 1.0, 1.0)
STUDIO_BG   = hex_to_rgba("#F6EDE4")

RAD = math.radians

def create_ghost_mat(name, alpha=1.0, emit_str=0.20):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = GHOST_WHITE
    bsdf.inputs["Roughness"].default_value = 0.82

    for spec_name in ("Specular IOR Level", "Specular"):
        if spec_name in bsdf.inputs:
            bsdf.inputs[spec_name].default_value = 0.08
            break

    for ek in ("Emission Color", "Emission"):
        if ek in bsdf.inputs:
            bsdf.inputs[ek].default_value = GHOST_WHITE
            break
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = emit_str

    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = GHOST_GLOW
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.25

    if alpha < 1.0 and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
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

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

mat_body  = create_ghost_mat("M_Ghost_Body", alpha=1.0, emit_str=0.20)
mat_tail  = create_ghost_mat("M_Ghost_Tail", alpha=0.75, emit_str=0.25)
mat_eye   = create_solid_mat("M_Ghost_Eye", EYE_DARK, roughness=0.35)
mat_shine = create_solid_mat("M_Ghost_Shine", WHITE_SHINE, roughness=0.1, emit=0.9)
mat_blush = create_solid_mat("M_Ghost_Blush", BLUSH_PINK, roughness=0.95)
mat_mouth = create_solid_mat("M_Ghost_Mouth", MOUTH_RED, roughness=0.75)
mat_gold  = create_solid_mat("M_Ghost_GoldAura", GOLD_SWIRL, roughness=0.2, emit=2.0)

# ── Base Spirit Mesh (Built at 0, 0, 0) ────────────────────────────────────
def build_spirit_base(name):
    # Head: UV Sphere (radius 0.50, smooth quad front)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=36, ring_count=24, radius=0.50, location=(0, 0, 0)
    )
    head = bpy.context.active_object
    head.name = name + "_Head"
    head.scale = (1.02, 0.98, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    head.data.materials.append(mat_body)

    # Tapering flowing tail
    bm = bmesh.new()
    profiles = [
        (0.18,  0.00,  0.46, 0.44),
        (0.45, -0.02,  0.38, 0.35),
        (0.75, -0.01,  0.28, 0.24),
        (1.05,  0.04,  0.18, 0.14),
        (1.35,  0.14,  0.09, 0.06),
        (1.55,  0.22,  0.02, 0.01),
    ]

    n_segs = 20
    rings = []
    for y, z, rx, rz in profiles:
        r_verts = []
        for i in range(n_segs):
            ang = 2 * math.pi * i / n_segs
            x = rx * math.cos(ang)
            z_val = z + rz * math.sin(ang)
            r_verts.append(bm.verts.new((x, y, z_val)))
        rings.append(r_verts)

    for r in range(len(rings) - 1):
        r1 = rings[r]
        r2 = rings[r + 1]
        for i in range(n_segs):
            i_next = (i + 1) % n_segs
            bm.faces.new([r1[i], r1[i_next], r2[i_next], r2[i]])

    tip_vert = bm.verts.new((0, 1.62, 0.25))
    for i in range(n_segs):
        i_next = (i + 1) % n_segs
        bm.faces.new([rings[-1][i_next], rings[-1][i], tip_vert])

    tail_mesh = bpy.data.meshes.new(name + "_Tail_Mesh")
    bm.to_mesh(tail_mesh)
    bm.free()

    tail = bpy.data.objects.new(name + "_Tail", tail_mesh)
    bpy.context.collection.objects.link(tail)
    bpy.context.view_layer.objects.active = tail
    tail.select_set(True)
    bpy.ops.object.shade_smooth()
    sub = tail.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    tail.data.materials.append(mat_tail)
    tail.parent = head

    # Head Crest / Tuft
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=0.17,
        location=(0, 0.12, 0.48)
    )
    tuft = bpy.context.active_object
    tuft.name = name + "_Crest"
    tuft.scale = (0.75, 1.7, 0.60)
    tuft.rotation_euler = (RAD(-24), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    tuft.data.materials.append(mat_body)
    tuft.parent = head

    return head, [tail, tuft]

# ── 1. FOLLOWER ────────────────────────────────────────────────────────────
def build_follower():
    col = bpy.data.collections.new("Ghost_Follower")
    scene.collection.children.link(col)

    head, subparts = build_spirit_base("Ghost_Follower")
    col.objects.link(head)
    scene.collection.objects.unlink(head)
    for sp in subparts:
        col.objects.link(sp)
        scene.collection.objects.unlink(sp)

    parts = []
    EYE_Y = -0.495
    EYE_Z =  0.08

    for side, s_name in [(1.0, "R"), (-1.0, "L")]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24, ring_count=16, radius=0.075,
            location=(side * 0.15, EYE_Y, EYE_Z)
        )
        eye = bpy.context.active_object
        eye.name = f"Follower_Eye_{s_name}"
        eye.scale = (0.75, 0.28, 1.25)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_eye)
        col.objects.link(eye)
        scene.collection.objects.unlink(eye)
        parts.append(eye)

        # Highlight sparkle
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=0.026,
            location=(side * 0.15 + 0.022, EYE_Y - 0.022, EYE_Z + 0.045)
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
            location=(side * 0.28, -0.435, -0.06)
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

    for p in parts:
        p.parent = head

    return head, col

# ── 2. CUTTER ──────────────────────────────────────────────────────────────
def build_cutter():
    col = bpy.data.collections.new("Ghost_Cutter")
    scene.collection.children.link(col)

    head, subparts = build_spirit_base("Ghost_Cutter")
    col.objects.link(head)
    scene.collection.objects.unlink(head)
    for sp in subparts:
        col.objects.link(sp)
        scene.collection.objects.unlink(sp)

    parts = []
    EYE_Y = -0.495
    EYE_Z =  0.08

    for side, s_name in [(1.0, "R"), (-1.0, "L")]:
        curve_data = bpy.data.curves.new(name=f"Cutter_Eye_{s_name}_Curve", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.026
        curve_data.bevel_resolution = 4
        curve_data.use_fill_caps = True

        polyline = curve_data.splines.new('BEZIER')
        polyline.bezier_points.add(2)

        ox = side * 0.15
        oy = EYE_Y
        oz = EYE_Z

        p0 = polyline.bezier_points[0]
        p0.co = (ox - side * 0.08, oy + 0.03, oz - 0.04)
        p0.handle_left = (ox - side * 0.10, oy + 0.04, oz - 0.05)
        p0.handle_right = (ox - side * 0.03, oy + 0.01, oz - 0.01)

        p1 = polyline.bezier_points[1]
        p1.co = (ox, oy - 0.01, oz + 0.01)
        p1.handle_left = (ox - side * 0.03, oy, oz)
        p1.handle_right = (ox + side * 0.03, oy, oz + 0.02)

        p2 = polyline.bezier_points[2]
        p2.co = (ox + side * 0.09, oy + 0.03, oz + 0.065)
        p2.handle_left = (ox + side * 0.04, oy + 0.01, oz + 0.04)
        p2.handle_right = (ox + side * 0.11, oy + 0.04, oz + 0.08)

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

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.05,
            location=(ox, oy + 0.012, oz)
        )
        pup = bpy.context.active_object
        pup.name = f"Cutter_Pupil_{s_name}"
        pup.scale = (1.2, 0.25, 0.75)
        pup.rotation_euler = (0, 0, side * RAD(24))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        pup.data.materials.append(mat_eye)
        col.objects.link(pup)
        scene.collection.objects.unlink(pup)
        parts.append(pup)

    for p in parts:
        p.parent = head

    return head, col

# ── 3. WANDERER ────────────────────────────────────────────────────────────
def build_wanderer():
    col = bpy.data.collections.new("Ghost_Wanderer")
    scene.collection.children.link(col)

    head, subparts = build_spirit_base("Ghost_Wanderer")
    col.objects.link(head)
    scene.collection.objects.unlink(head)
    for sp in subparts:
        col.objects.link(sp)
        scene.collection.objects.unlink(sp)

    parts = []
    EYE_Y = -0.495
    EYE_Z =  0.08

    for side, s_name in [(1.0, "R"), (-1.0, "L")]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24, ring_count=16, radius=0.08,
            location=(side * 0.15, EYE_Y, EYE_Z)
        )
        eye = bpy.context.active_object
        eye.name = f"Wanderer_Eye_{s_name}"
        eye.scale = (0.80, 0.28, 1.15)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_eye)
        col.objects.link(eye)
        scene.collection.objects.unlink(eye)
        parts.append(eye)

        # Primary shine
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=0.030,
            location=(side * 0.15 + 0.024, EYE_Y - 0.022, EYE_Z + 0.045)
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

        # Secondary star shine
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10, ring_count=6, radius=0.016,
            location=(side * 0.15 - 0.020, EYE_Y - 0.020, EYE_Z - 0.028)
        )
        shine2 = bpy.context.active_object
        shine2.name = f"Wanderer_Shine2_{s_name}"
        shine2.scale = (1.0, 0.35, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        shine2.data.materials.append(mat_gold)
        col.objects.link(shine2)
        scene.collection.objects.unlink(shine2)
        parts.append(shine2)

        # Cheek blush
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.08,
            location=(side * 0.28, -0.435, -0.06)
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

    # Open happy smile mouth (:D)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=0.075,
        location=(0, -0.495, -0.07)
    )
    mouth = bpy.context.active_object
    mouth.name = "Wanderer_Mouth"
    mouth.scale = (1.15, 0.28, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mat_mouth)
    col.objects.link(mouth)
    scene.collection.objects.unlink(mouth)
    parts.append(mouth)

    # Orbiting Golden Magical Swirl Halo Ring
    curve_data = bpy.data.curves.new(name="Wanderer_Aura_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.024
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True

    polyline = curve_data.splines.new('BEZIER')
    n_pts = 7
    polyline.bezier_points.add(n_pts - 1)

    r_x = 0.85
    r_y = 0.95
    z_mid = 0.05

    for i in range(n_pts):
        ang = 2 * math.pi * i / (n_pts - 1)
        bx = r_x * math.cos(ang)
        by = r_y * math.sin(ang)
        bz = z_mid + 0.35 * math.sin(ang) + 0.15 * math.cos(2 * ang)

        pt = polyline.bezier_points[i]
        pt.co = (bx, by, bz)
        pt.handle_left  = (bx - 0.25 * math.sin(ang), by + 0.25 * math.cos(ang), bz)
        pt.handle_right = (bx + 0.25 * math.sin(ang), by - 0.25 * math.cos(ang), bz)

    aura_obj = bpy.data.objects.new("Wanderer_Aura_Ring", curve_data)
    bpy.context.collection.objects.link(aura_obj)
    bpy.context.view_layer.objects.active = aura_obj
    aura_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.shade_smooth()
    aura_obj.data.materials.append(mat_gold)
    col.objects.link(aura_obj)
    scene.collection.objects.unlink(aura_obj)
    parts.append(aura_obj)

    # Golden spark stars
    for i, (sx, sy, sz) in enumerate([
        ( 0.70, -0.35,  0.35),
        (-0.75,  0.45,  0.10),
        ( 0.25,  0.85, -0.15)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10, ring_count=8, radius=0.04,
            location=(sx, sy, sz)
        )
        star = bpy.context.active_object
        star.name = f"Wanderer_Star_{i}"
        star.scale = (1.4, 0.6, 1.4)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        star.data.materials.append(mat_gold)
        col.objects.link(star)
        scene.collection.objects.unlink(star)
        parts.append(star)

    for p in parts:
        p.parent = head

    return head, col

# ── Construct Spirits ──────────────────────────────────────────────────────
print("Building 3 Spirits of Momo Maze locally...")
follower_head, follower_col = build_follower()
cutter_head,   cutter_col   = build_cutter()
wanderer_head, wanderer_col = build_wanderer()

# Position the spirits in world space
follower_head.location = (-3.2, 0, 0)
cutter_head.location   = ( 0.0, 0, 0)
wanderer_head.location = ( 3.2, 0, 0)

# Set 35-degree rotation for the Hero Lineup render matching concept sheet banner!
follower_head.rotation_euler = (0, 0, RAD(35))
cutter_head.rotation_euler   = (0, 0, RAD(35))
wanderer_head.rotation_euler = (0, 0, RAD(35))

# ── Studio Lighting ────────────────────────────────────────────────────────
bpy.ops.object.light_add(type='AREA', location=(2.5, -4.5, 4.0))
key = bpy.context.active_object
key.name = "Spirits_Key"
key.data.energy = 550
key.data.color = (1.0, 0.95, 0.88)
key.data.size = 5.0
key.rotation_euler = (RAD(50), 0, RAD(25))

bpy.ops.object.light_add(type='AREA', location=(-3.5, -3.0, 2.0))
fill = bpy.context.active_object
fill.name = "Spirits_Fill"
fill.data.energy = 220
fill.data.color = (1.0, 0.90, 0.84)
fill.data.size = 6.0

bpy.ops.object.light_add(type='AREA', location=(0.0, 4.0, 3.2))
rim = bpy.context.active_object
rim.name = "Spirits_Rim"
rim.data.energy = 260
rim.data.color = (1.0, 0.96, 0.90)
rim.data.size = 6.0
rim.rotation_euler = (RAD(-45), 0, RAD(180))

world = bpy.data.worlds.new("SpiritsStudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = STUDIO_BG
    bg.inputs["Strength"].default_value = 0.85

# ── Render Settings ────────────────────────────────────────────────────────
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True

# 1. HERO LINEUP RENDER
scene.render.resolution_x = 1600
scene.render.resolution_y = 650

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

# Reset rotations for clean turnarounds
follower_head.rotation_euler = (0, 0, 0)
cutter_head.rotation_euler   = (0, 0, 0)
wanderer_head.rotation_euler = (0, 0, 0)

# 2. INDIVIDUAL TURNAROUNDS (Front, 3/4, Side)
scene.render.resolution_x = 768
scene.render.resolution_y = 768

ghosts_data = [
    ("follower", -3.2, follower_head),
    ("cutter",    0.0, cutter_head),
    ("wanderer",  3.2, wanderer_head),
]

for g_name, ox, g_head in ghosts_data:
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

for g_name, col in [
    ("follower", follower_col),
    ("cutter",   cutter_col),
    ("wanderer", wanderer_col),
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
