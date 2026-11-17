"""
MOMO MAZE – Full Environment & Beauty Scene Production
======================================================
Faithfully recreates the Beauty View (Panel 1) and Top-Down Maze Plan (Panel 2)
from the approved Environment Concept Sheet (Image 4):
- 12x12 Square Modular Living Maze
- Soft rounded puffy hedges with lush green gradient shader
- Grass ground pathway
- Raised earthen/cobblestone retaining border trim
- The Living Leaf Gate Arch at the North exit with glowing Momo emblem
- Golden glowing Momo collectible dumplings with warm point lights & sparkle
- Golumolu navigating the pathway
- Floating Ghost Spirits drifting through the maze
- Blooming pink & white daisies and green clover patches along hedge corners
- Warm golden sunlight, soft shadows, cozy atmospheric lighting
- Outputs:
  * scenes/maze_beauty_environment.blend
  * renders/environment/maze_beauty_view.png (Isometric Gameplay Angle)
  * renders/environment/maze_topdown_plan.png (Orthographic Top-Down Layout)
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
RENDER_DIR   = os.path.join(PROJECT_ROOT, "renders", "environment")

for d in (SCENE_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

BLEND_PATH = os.path.join(SCENE_DIR, "maze_beauty_environment.blend")

# ── Approved Colors ────────────────────────────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_to_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), alpha)

HEDGE_TOP    = hex_to_rgba("#7DC257")  # Bright sunny leaf green
HEDGE_BASE   = hex_to_rgba("#5A9B3A")  # Rich shadow green
GRASS_PATH   = hex_to_rgba("#8AC95B")  # Path grass green
PATH_EARTH   = hex_to_rgba("#C49A6C")  # Soil / Stone border
GATE_WOOD    = hex_to_rgba("#9C744D")  # Arch stone/wood
GATE_LEAF    = hex_to_rgba("#6AB845")  # Arch canopy leaves
MOMO_DOUGH   = hex_to_rgba("#FFF5E6")  # Warm dumpling
MOMO_GLOW    = hex_to_rgba("#FFE08A")  # Golden glow
FLOWER_PINK  = hex_to_rgba("#F4A7B9")  # Pink petal
FLOWER_WHITE = hex_to_rgba("#FFFDF8")  # White petal
FLOWER_GOLD  = hex_to_rgba("#F9D56E")  # Pollen center
CLOVER_GREEN = hex_to_rgba("#64B53A")  # Clover leaf
MEADOW_GREEN = hex_to_rgba("#78B84D")  # Outer ground
STUDIO_BG    = hex_to_rgba("#F4E8DB")

RAD = math.radians

# ── Materials ──────────────────────────────────────────────────────────────
def create_material(name, base_color, roughness=0.85, sss_weight=0.0, sss_color=None, emit=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness

    for spec_name in ("Specular IOR Level", "Specular"):
        if spec_name in bsdf.inputs:
            bsdf.inputs[spec_name].default_value = 0.06
            break

    if sss_weight > 0:
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = sss_weight
            if sss_color and "Subsurface Color" in bsdf.inputs:
                bsdf.inputs["Subsurface Color"].default_value = sss_color
        elif "Subsurface" in bsdf.inputs:
            bsdf.inputs["Subsurface"].default_value = sss_weight

    if emit > 0:
        for ek in ("Emission Color", "Emission"):
            if ek in bsdf.inputs:
                bsdf.inputs[ek].default_value = base_color
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

mat_hedge      = create_material("M_Hedge", HEDGE_TOP, roughness=0.88, sss_weight=0.18, sss_color=HEDGE_BASE)
mat_path       = create_material("M_Path", GRASS_PATH, roughness=0.92)
mat_earth      = create_material("M_Earth_Border", PATH_EARTH, roughness=0.85)
mat_gate_wood  = create_material("M_Gate_Wood", GATE_WOOD, roughness=0.80)
mat_gate_leaf  = create_material("M_Gate_Leaf", GATE_LEAF, roughness=0.88, sss_weight=0.15)
mat_momo       = create_material("M_Momo", MOMO_DOUGH, roughness=0.65, emit=0.3)
mat_momo_glow  = create_material("M_Momo_Glow", MOMO_GLOW, roughness=0.20, emit=3.0)
mat_flower_p   = create_material("M_Flower_Pink", FLOWER_PINK, roughness=0.80)
mat_flower_w   = create_material("M_Flower_White", FLOWER_WHITE, roughness=0.80)
mat_flower_c   = create_material("M_Flower_Center", FLOWER_GOLD, roughness=0.50, emit=0.5)
mat_clover     = create_material("M_Clover", CLOVER_GREEN, roughness=0.82)
mat_meadow     = create_material("M_Meadow", MEADOW_GREEN, roughness=0.95)

# Ghost materials
GHOST_WHITE = hex_to_rgba("#FFF7EE")
EYE_DARK    = hex_to_rgba("#3D2B1F")
BLUSH_PINK  = hex_to_rgba("#FFB3B0")
mat_ghost_body = create_material("M_Ghost_White", GHOST_WHITE, roughness=0.85, sss_weight=0.25, emit=0.20)
mat_ghost_eye  = create_material("M_Ghost_Eye", EYE_DARK, roughness=0.35)
mat_ghost_blush= create_material("M_Ghost_Blush", BLUSH_PINK, roughness=0.95)

# Golumolu materials
CREAM_BODY   = hex_to_rgba("#FCEEDD")
PEACH_ACCENT = hex_to_rgba("#FFC189")
MOUTH_INNER  = hex_to_rgba("#E27567")
mat_golu_body  = create_material("M_Golu_Body", CREAM_BODY, roughness=0.92, sss_weight=0.15, sss_color=PEACH_ACCENT)
mat_golu_peach = create_material("M_Golu_Peach", PEACH_ACCENT, roughness=0.88)
mat_golu_eye   = create_material("M_Golu_Eye", EYE_DARK, roughness=0.55)
mat_golu_mouth = create_material("M_Golu_Mouth", MOUTH_INNER, roughness=0.75)

col_maze = bpy.data.collections.new("Momo_Living_Maze")
scene.collection.children.link(col_maze)

# ── 12x12 Maze Grid Definition ─────────────────────────────────────────────
# 1 = Hedge Wall, 0 = Grass Path, 2 = Leaf Gate Opening
MAZE_GRID = [
    [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # Row 0 (North, Gate at center)
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # Row 1
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],  # Row 2
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],  # Row 3
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1],  # Row 4
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # Row 5
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1],  # Row 6
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 7 (Central crossroad)
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],  # Row 8
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],  # Row 9
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],  # Row 10
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Row 11 (South)
]

ROWS = len(MAZE_GRID)
COLS = len(MAZE_GRID[0])
CELL_SIZE = 1.0  # 1 meter per cell

# Convert grid (r, c) to world coordinates (centered around 0, 0)
def grid_to_world(r, c):
    wx = (c - (COLS - 1) / 2.0) * CELL_SIZE
    wy = ((ROWS - 1) / 2.0 - r) * CELL_SIZE  # Row 0 is North (+Y)
    return wx, wy

print(f"Building 12x12 Maze Grid ({ROWS}x{COLS} cells)...")

# ── 1. GROUND BED & EARTHEN RETAINING CURB ─────────────────────────────────
# 1. Outer Meadow Plane
bpy.ops.mesh.primitive_plane_add(size=36.0, location=(0, 0, -0.05))
meadow = bpy.context.active_object
meadow.name = "Environment_Outer_Meadow"
meadow.data.materials.append(mat_meadow)
col_maze.objects.link(meadow); scene.collection.objects.unlink(meadow)

# 2. Raised Maze Bed Soil/Stone Curb
# Width = 12.8m, Length = 12.8m, Height = 0.25m
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
curb = bpy.context.active_object
curb.name = "Maze_Raised_Curb"
curb.scale = (12.8, 12.8, 0.22)
bpy.ops.object.transform_apply(scale=True)
bevel = curb.modifiers.new("Bevel", type='BEVEL')
bevel.width = 0.15; bevel.segments = 3
bpy.ops.object.shade_smooth()
curb.data.materials.append(mat_earth)
col_maze.objects.link(curb); scene.collection.objects.unlink(curb)

# 3. Grass Pathway Bed Surface
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.18))
grass_bed = bpy.context.active_object
grass_bed.name = "Maze_Grass_Bed"
grass_bed.scale = (12.1, 12.1, 0.06)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth()
grass_bed.data.materials.append(mat_path)
col_maze.objects.link(grass_bed); scene.collection.objects.unlink(grass_bed)

# ── 2. HEDGE WALLS ─────────────────────────────────────────────────────────
# Master Hedge Block Builder
def create_master_hedge_mesh():
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.65))
    h = bpy.context.active_object
    h.scale = (0.94, 0.94, 1.15)
    bpy.ops.object.transform_apply(scale=True)
    b = h.modifiers.new("Bevel", type='BEVEL')
    b.width = 0.22; b.segments = 4; b.profile = 0.70
    s = h.modifiers.new("Subsurf", type='SUBSURF')
    s.levels = 1; s.render_levels = 1
    bpy.ops.object.shade_smooth()
    h.data.materials.append(mat_hedge)
    return h

master_hedge = create_master_hedge_mesh()
master_hedge.name = "Master_Hedge_Mesh"
master_hedge.hide_render = True
master_hedge.hide_viewport = True

# Place hedge walls across the grid
for r in range(ROWS):
    for c in range(COLS):
        val = MAZE_GRID[r][c]
        if val == 1:
            wx, wy = grid_to_world(r, c)
            # Create a linked duplicate for optimal performance
            h_inst = master_hedge.copy()
            h_inst.name = f"Hedge_r{r}_c{c}"
            h_inst.location = (wx, wy, 0.18)
            h_inst.hide_render = False
            h_inst.hide_viewport = False
            col_maze.objects.link(h_inst)

# ── 3. LIVING LEAF GATE ARCH ───────────────────────────────────────────────
# Placed at North Exit: Row 0, Col 5.5
gx, gy = grid_to_world(0, 5.5)
gate_parts = []

# Left Pillar
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, radius=0.20, depth=1.65, location=(gx - 0.75, gy, 0.95)
)
p_l = bpy.context.active_object; p_l.name = "Gate_Pillar_L"
bpy.ops.object.shade_smooth(); p_l.data.materials.append(mat_gate_wood)
gate_parts.append(p_l)

# Right Pillar
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, radius=0.20, depth=1.65, location=(gx + 0.75, gy, 0.95)
)
p_r = bpy.context.active_object; p_r.name = "Gate_Pillar_R"
bpy.ops.object.shade_smooth(); p_r.data.materials.append(mat_gate_wood)
gate_parts.append(p_r)

# Curved Timber Beam
curve_data = bpy.data.curves.new(name="Gate_Arch_Curve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.16; curve_data.bevel_resolution = 4
polyline = curve_data.splines.new('BEZIER')
polyline.bezier_points.add(2)
polyline.bezier_points[0].co = (gx - 0.75, gy, 1.65)
polyline.bezier_points[0].handle_left = (gx - 0.75, gy, 1.45)
polyline.bezier_points[0].handle_right = (gx - 0.75, gy, 2.05)
polyline.bezier_points[1].co = (gx, gy, 2.15)
polyline.bezier_points[1].handle_left = (gx - 0.45, gy, 2.15)
polyline.bezier_points[1].handle_right = (gx + 0.45, gy, 2.15)
polyline.bezier_points[2].co = (gx + 0.75, gy, 1.65)
polyline.bezier_points[2].handle_left = (gx + 0.75, gy, 2.05)
polyline.bezier_points[2].handle_right = (gx + 0.75, gy, 1.45)

arch_obj = bpy.data.objects.new("Gate_Arch_Beam", curve_data)
bpy.context.collection.objects.link(arch_obj)
bpy.context.view_layer.objects.active = arch_obj; arch_obj.select_set(True)
bpy.ops.object.convert(target='MESH'); bpy.ops.object.shade_smooth()
arch_obj.data.materials.append(mat_gate_wood)
gate_parts.append(arch_obj)

# Lush Leaf Canopy Clumps
canopy_offsets = [
    (-0.70, 0, 1.80, 0.32),
    (-0.40, 0, 2.10, 0.38),
    ( 0.00, 0, 2.25, 0.44),
    ( 0.40, 0, 2.10, 0.38),
    ( 0.70, 0, 1.80, 0.32),
    (-0.20, 0.10, 2.15, 0.30),
    ( 0.20, -0.10, 2.15, 0.30),
]
for i, (cx, cy, cz, cr) in enumerate(canopy_offsets):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=12, radius=cr, location=(gx + cx, gy + cy, cz)
    )
    cb = bpy.context.active_object; cb.name = f"Gate_Canopy_{i}"
    cb.scale = (1.1, 1.1, 0.9); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth(); cb.data.materials.append(mat_gate_leaf)
    gate_parts.append(cb)

# Glowing Momo Emblem in the Archway
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.20, location=(gx, gy, 1.70)
)
g_emblem = bpy.context.active_object; g_emblem.name = "Gate_Momo_Emblem"
g_emblem.scale = (1.1, 0.7, 0.9); bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth(); g_emblem.data.materials.append(mat_momo_glow)
gate_parts.append(g_emblem)

# Warm point light inside the gate
bpy.ops.object.light_add(type='POINT', location=(gx, gy, 1.70))
gate_light = bpy.context.active_object; gate_light.name = "Gate_Warm_Glow"
gate_light.data.energy = 85; gate_light.data.color = (1.0, 0.88, 0.60)
gate_parts.append(gate_light)

for gp in gate_parts:
    col_maze.objects.link(gp); scene.collection.objects.unlink(gp)

# ── 4. MOMO COLLECTIBLE DUMPLINGS (With magical lights) ─────────────────────
# Collectibles placed at key path intersections:
momo_locs = [
    (7, 7),  # Central highlight (as seen in concept sheet beauty view!)
    (3, 5),  # North path
    (7, 1),  # West clearing
    (9, 6),  # South path
]

def spawn_momo_collectible(r, c, is_hero=False):
    mx, my = grid_to_world(r, c)
    mz = 0.22

    # Stone pedestal ring
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.32, depth=0.04, location=(mx, my, mz + 0.02)
    )
    ped = bpy.context.active_object; ped.name = f"Momo_Pedestal_{r}_{c}"
    bpy.ops.object.shade_smooth(); ped.data.materials.append(mat_earth)
    col_maze.objects.link(ped); scene.collection.objects.unlink(ped)

    # Dumpling body
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.22, location=(mx, my, mz + 0.16)
    )
    dumpling = bpy.context.active_object; dumpling.name = f"Momo_Dumpling_{r}_{c}"
    dumpling.scale = (1.10, 1.10, 0.88); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth(); dumpling.data.materials.append(mat_momo)
    col_maze.objects.link(dumpling); scene.collection.objects.unlink(dumpling)

    # Top pleat swirl
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.08, radius2=0.01, depth=0.10, location=(mx, my, mz + 0.32)
    )
    pleat = bpy.context.active_object; pleat.name = f"Momo_Pleat_{r}_{c}"
    pleat.rotation_euler = (0, 0, RAD(25)); bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.shade_smooth(); pleat.data.materials.append(mat_momo)
    col_maze.objects.link(pleat); scene.collection.objects.unlink(pleat)

    # Golden light rays / point light
    bpy.ops.object.light_add(type='POINT', location=(mx, my, mz + 0.28))
    momo_lt = bpy.context.active_object; momo_lt.name = f"Momo_Light_{r}_{c}"
    momo_lt.data.energy = 120 if is_hero else 65
    momo_lt.data.color = (1.0, 0.88, 0.55)
    col_maze.objects.link(momo_lt); scene.collection.objects.unlink(momo_lt)

    # Soft glowing sparkle rays (3 small motes around hero Momo)
    if is_hero:
        for p_idx, (sx, sy, sz) in enumerate([
            (-0.25, -0.15, 0.38),
            ( 0.22, -0.18, 0.42),
            ( 0.00,  0.25, 0.45)
        ]):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=10, ring_count=8, radius=0.035,
                location=(mx + sx, my + sy, mz + sz)
            )
            spark = bpy.context.active_object; spark.name = f"Momo_Sparkle_{p_idx}"
            spark.data.materials.append(mat_momo_glow)
            col_maze.objects.link(spark); scene.collection.objects.unlink(spark)

spawn_momo_collectible(7, 7, is_hero=True)
for r, c in momo_locs[1:]:
    spawn_momo_collectible(r, c, is_hero=False)

# ── 5. FLOWER & CLOVER CLUSTERS ALONG PATHS ────────────────────────────────
# Scatter cheerful flower blossoms & clovers at path corners (matching concept art!)
flower_spots = [
    (1, 1), (1, 10), (3, 3), (3, 8), (5, 3), (5, 8),
    (7, 3), (7, 8), (9, 3), (9, 8), (10, 1), (10, 10),
    (6, 0), (6, 11), (0, 3), (0, 8)
]

def spawn_flower_bunch(wx, wy):
    for i, (dx, dy, p_mat) in enumerate([
        (-0.15, -0.12, mat_flower_p),
        ( 0.14, -0.08, mat_flower_w),
        (-0.02,  0.15, mat_flower_p),
        ( 0.16,  0.12, mat_flower_w),
    ]):
        # 5 petals
        for p in range(5):
            ang = 2 * math.pi * p / 5
            px = wx + dx + 0.05 * math.cos(ang)
            py = wy + dy + 0.05 * math.sin(ang)
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=10, ring_count=8, radius=0.032,
                location=(px, py, 0.22)
            )
            pet = bpy.context.active_object; pet.scale = (0.9, 1.4, 0.4)
            pet.rotation_euler = (0, 0, ang); bpy.ops.object.transform_apply(scale=True, rotation=True)
            bpy.ops.object.shade_smooth(); pet.data.materials.append(p_mat)
            col_maze.objects.link(pet); scene.collection.objects.unlink(pet)

        # Center disc
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8, ring_count=6, radius=0.028,
            location=(wx + dx, wy + dy, 0.235)
        )
        cen = bpy.context.active_object; cen.scale = (1.0, 1.0, 0.5)
        bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()
        cen.data.materials.append(mat_flower_c)
        col_maze.objects.link(cen); scene.collection.objects.unlink(cen)

for r, c in flower_spots:
    wx, wy = grid_to_world(r, c)
    # Offset slightly towards the corner
    spawn_flower_bunch(wx + 0.25, wy - 0.25)

# ── 6. GOLUMOLU IN PATHWAY ─────────────────────────────────────────────────
# Place Golumolu running happily in the main central corridor (Row 7, Col 4.2)
gx, gy = grid_to_world(7, 4.2)
gz = 0.56

# Chubby body
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32, ring_count=20, radius=0.38, location=(gx, gy, gz)
)
golu_body = bpy.context.active_object; golu_body.name = "Scene_Golumolu_Body"
golu_body.scale = (1.04, 0.98, 0.92); bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth(); golu_body.data.materials.append(mat_golu_body)
col_maze.objects.link(golu_body); scene.collection.objects.unlink(golu_body)

# Peach ears
for side in (1.0, -1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=12, radius=0.11,
        location=(gx + side * 0.25, gy - 0.04, gz + 0.29)
    )
    g_ear = bpy.context.active_object; g_ear.scale = (0.85, 0.65, 0.95)
    bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()
    g_ear.data.materials.append(mat_golu_peach)
    col_maze.objects.link(g_ear); scene.collection.objects.unlink(g_ear)

# Cheeks
for side in (1.0, -1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=14, ring_count=10, radius=0.08,
        location=(gx + side * 0.20, gy - 0.32, gz - 0.02)
    )
    g_chk = bpy.context.active_object; g_chk.scale = (1.0, 0.25, 0.70)
    bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()
    g_chk.data.materials.append(mat_ghost_blush)
    col_maze.objects.link(g_chk); scene.collection.objects.unlink(g_chk)

# Happy eyes (curved arch)
for side in (1.0, -1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.045,
        location=(gx + side * 0.12, gy - 0.35, gz + 0.08)
    )
    g_ey = bpy.context.active_object; g_ey.scale = (1.2, 0.25, 0.55)
    bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()
    g_ey.data.materials.append(mat_golu_eye)
    col_maze.objects.link(g_ey); scene.collection.objects.unlink(g_ey)

# Happy open smile mouth
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=14, ring_count=10, radius=0.065,
    location=(gx, gy - 0.36, gz - 0.03)
)
g_mth = bpy.context.active_object; g_mth.scale = (1.2, 0.25, 0.75)
bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()
g_mth.data.materials.append(mat_golu_mouth)
col_maze.objects.link(g_mth); scene.collection.objects.unlink(g_mth)

# ── 7. SPIRIT GHOSTS FLOATING IN MAZE ──────────────────────────────────────
# Place the 3 spirits drifting through the maze pathways:
# 1. Follower Ghost in Western corridor (Row 3, Col 1.5)
# 2. Cutter Ghost in Eastern corridor (Row 3, Col 9.5)
# 3. Wanderer Ghost in Southern corridor (Row 9, Col 1.5)
def spawn_scene_ghost(name, r, c, rot_z, style="follower"):
    sx, sy = grid_to_world(r, c)
    sz = 0.85

    # Spirit head
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.28, location=(sx, sy, sz)
    )
    head = bpy.context.active_object; head.name = f"Scene_{name}_Head"
    bpy.ops.object.shade_smooth(); head.data.materials.append(mat_ghost_body)
    col_maze.objects.link(head); scene.collection.objects.unlink(head)

    # Wispy floating tail
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.24, radius2=0.02, depth=0.85,
        location=(sx + 0.40 * math.cos(rot_z + math.pi), sy + 0.40 * math.sin(rot_z + math.pi), sz + 0.08)
    )
    tail = bpy.context.active_object; tail.name = f"Scene_{name}_Tail"
    tail.rotation_euler = (0, RAD(75), rot_z)
    bpy.ops.object.transform_apply(rotation=True); bpy.ops.object.shade_smooth()
    tail.data.materials.append(mat_ghost_body)
    col_maze.objects.link(tail); scene.collection.objects.unlink(tail)

    # Eyes
    for side in (1.0, -1.0):
        ex = sx + 0.09 * side * math.sin(rot_z) + 0.26 * math.cos(rot_z)
        ey = sy - 0.09 * side * math.cos(rot_z) + 0.26 * math.sin(rot_z)
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=0.042, location=(ex, ey, sz + 0.05)
        )
        s_eye = bpy.context.active_object; s_eye.scale = (0.7, 0.3, 1.2)
        bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()
        s_eye.data.materials.append(mat_ghost_eye)
        col_maze.objects.link(s_eye); scene.collection.objects.unlink(s_eye)

spawn_scene_ghost("Follower", 3, 2.0, RAD(25), style="follower")
spawn_scene_ghost("Cutter",   3, 9.5, RAD(-45), style="cutter")
spawn_scene_ghost("Wanderer", 8.5, 1.5, RAD(90), style="wanderer")

# ── 8. LIGHTING & ENVIRONMENT SHADING ──────────────────────────────────────
# Key Sunlight (Warm golden hour sun shining from upper-left, exactly like concept art!)
bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
sun = bpy.context.active_object
sun.name = "Sun_Cozy_Golden"
sun.data.energy = 4.5
sun.data.color = (1.0, 0.95, 0.86)
sun.data.angle = RAD(4.0)  # Soft shadow edges
sun.rotation_euler = (RAD(48), RAD(-18), RAD(42))
col_maze.objects.link(sun); scene.collection.objects.unlink(sun)

# Soft ambient fill
bpy.ops.object.light_add(type='AREA', location=(-8.0, 6.0, 8.0))
sky_fill = bpy.context.active_object
sky_fill.name = "Sky_Ambient_Fill"
sky_fill.data.energy = 300
sky_fill.data.color = (0.90, 0.96, 1.0)
sky_fill.data.size = 12.0
col_maze.objects.link(sky_fill); scene.collection.objects.unlink(sky_fill)

world = bpy.data.worlds.new("CozyMazeSky")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = STUDIO_BG
    bg.inputs["Strength"].default_value = 0.90

# ── 9. CAMERA & RENDERING ──────────────────────────────────────────────────
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False

# ── Render 1: BEAUTY VIEW (Isometric Gameplay Angle from Concept Sheet Panel 1)
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100

bpy.ops.object.camera_add(location=(10.5, -13.5, 12.0))
cam_beauty = bpy.context.active_object
cam_beauty.name = "Camera_Beauty_View"
cam_beauty.rotation_euler = (RAD(54), 0, RAD(38))
cam_beauty.data.lens = 55
cam_beauty.data.dof.use_dof = False
scene.camera = cam_beauty

beauty_path = os.path.join(RENDER_DIR, "maze_beauty_view.png")
scene.render.filepath = beauty_path
bpy.ops.render.render(write_still=True)
print(f"  ✓ Rendered Maze Beauty View -> {beauty_path}")

# ── Render 2: TOP-DOWN MAZE PLAN (Matching Concept Sheet Panel 2)
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024

bpy.ops.object.camera_add(location=(0, 0, 18.0))
cam_top = bpy.context.active_object
cam_top.name = "Camera_TopDown_Plan"
cam_top.rotation_euler = (0, 0, 0)
cam_top.data.type = 'ORTHO'
cam_top.data.ortho_scale = 14.5
scene.camera = cam_top

topdown_path = os.path.join(RENDER_DIR, "maze_topdown_plan.png")
scene.render.filepath = topdown_path
bpy.ops.render.render(write_still=True)
print(f"  ✓ Rendered Top-Down Maze Plan -> {topdown_path}")

# ── Save Master Blend ──────────────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved master maze scene: {BLEND_PATH}")
print("=== Full Environment & Maze Beauty Scene Production Complete ===")
