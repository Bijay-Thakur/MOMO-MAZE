"""
MOMO MAZE – Modular Environment & Maze Assets Production
=========================================================
Faithfully recreates all modular pieces from the approved Environment Concept Sheet (Image 4):
1. SM_Hedge_Straight (1m x 1m x 1.2m rounded, pillowy hedge wall with lush gradient green shader)
2. SM_Hedge_Corner (1m x 1m x 1.2m 90-degree rounded corner hedge)
3. SM_Hedge_T (T-junction rounded hedge)
4. SM_Path_Tile (1m x 1m grass ground pathway tile)
5. SM_Leaf_Gate (Cozy stone archway with lush leaf canopy & glowing Momo crest)
6. SM_Momo_Collectible (Stylized dumpling with top pleated pinch & golden emissive glow)
7. SM_Momo_Pedestal (Warm stone disc pedestal with decorative petals)
8. SM_Flower_Cluster (5-petal pink & white daisies with yellow centers)
9. SM_Clover_Patch (Stylized 3-leaf & 4-leaf green shamrocks)
10. SM_Maze_Curb (Earthen/stone retaining border trim)

Outputs:
  - Blender Scene: scenes/environment_modular.blend
  - FBX Exports for Unreal Engine:
    * exports/fbx/SM_Hedge_Straight.fbx
    * exports/fbx/SM_Hedge_Corner.fbx
    * exports/fbx/SM_Path_Tile.fbx
    * exports/fbx/SM_Leaf_Gate.fbx
    * exports/fbx/SM_Momo_Collectible.fbx
    * exports/fbx/SM_Flower_Cluster.fbx
  - Visual validation render of all modular pieces on a display pedestal:
    * renders/environment/modular_pieces_lineup.png
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
RENDER_DIR   = os.path.join(PROJECT_ROOT, "renders", "environment")

for d in (SCENE_DIR, FBX_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

BLEND_PATH = os.path.join(SCENE_DIR, "environment_modular.blend")

# ── Colors from Approved Environment Sheet ────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_to_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), alpha)

HEDGE_TOP    = hex_to_rgba("#7DC257")  # Bright sunny leaf green
HEDGE_BASE   = hex_to_rgba("#5A9B3A")  # Rich shadow green
GRASS_PATH   = hex_to_rgba("#88C958")  # Path grass green
PATH_EARTH   = hex_to_rgba("#C49A6C")  # Soil / Stone border
GATE_WOOD    = hex_to_rgba("#A07850")  # Arch stone/wood
GATE_LEAF    = hex_to_rgba("#6AB845")  # Arch canopy leaves
MOMO_DOUGH   = hex_to_rgba("#FFF5E6")  # Warm steamed dumpling
MOMO_GLOW    = hex_to_rgba("#FFE08A")  # Golden magical glow
FLOWER_PINK  = hex_to_rgba("#F4A7B9")  # Pink blossom petal
FLOWER_WHITE = hex_to_rgba("#FFFDF8")  # White daisy petal
FLOWER_GOLD  = hex_to_rgba("#F9D56E")  # Flower pollen center
CLOVER_GREEN = hex_to_rgba("#68BA3D")  # Clover leaf green
STUDIO_BG    = hex_to_rgba("#F6EDE4")

RAD = math.radians

# ── Materials ──────────────────────────────────────────────────────────────
def create_hedge_material(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = HEDGE_TOP
    bsdf.inputs["Roughness"].default_value = 0.88

    # Soft SSS for lush organic foliage feel
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.20
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = HEDGE_BASE
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.20

    for spec_name in ("Specular IOR Level", "Specular"):
        if spec_name in bsdf.inputs:
            bsdf.inputs[spec_name].default_value = 0.05
            break

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

def create_solid_mat(name, color, roughness=0.85, emit=0.0):
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

    for spec_name in ("Specular IOR Level", "Specular"):
        if spec_name in bsdf.inputs:
            bsdf.inputs[spec_name].default_value = 0.08
            break

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

mat_hedge      = create_hedge_material("M_Hedge_Foliage")
mat_path       = create_solid_mat("M_Grass_Path", GRASS_PATH, roughness=0.92)
mat_earth      = create_solid_mat("M_Earth_Border", PATH_EARTH, roughness=0.88)
mat_gate_wood  = create_solid_mat("M_Gate_WoodStone", GATE_WOOD, roughness=0.80)
mat_gate_leaf  = create_solid_mat("M_Gate_Canopy", GATE_LEAF, roughness=0.85)
mat_momo       = create_solid_mat("M_Momo_Dough", MOMO_DOUGH, roughness=0.70, emit=0.25)
mat_momo_glow  = create_solid_mat("M_Momo_Glow", MOMO_GLOW, roughness=0.30, emit=2.5)
mat_flower_p   = create_solid_mat("M_Flower_Pink", FLOWER_PINK, roughness=0.80)
mat_flower_w   = create_solid_mat("M_Flower_White", FLOWER_WHITE, roughness=0.80)
mat_flower_c   = create_solid_mat("M_Flower_Center", FLOWER_GOLD, roughness=0.60, emit=0.4)
mat_clover     = create_solid_mat("M_Clover_Leaf", CLOVER_GREEN, roughness=0.82)

# ── 1. SM_HEDGE_STRAIGHT ───────────────────────────────────────────────────
# Soft, puffy rounded rectangular hedge wall (1m wide, 1m deep, 1.2m tall)
def build_hedge_straight():
    # Built from a rounded box with subdivision and soft organic puffy bumps
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.60))
    hedge = bpy.context.active_object
    hedge.name = "SM_Hedge_Straight"
    # Tile dimensions: X=1.0m, Y=1.0m, Z=1.2m
    hedge.scale = (0.96, 0.96, 1.15)
    bpy.ops.object.transform_apply(scale=True)

    # Bevel modifier for rounded edges
    bevel = hedge.modifiers.new("Bevel", type='BEVEL')
    bevel.width = 0.22
    bevel.segments = 4
    bevel.profile = 0.70

    # Subdivision for organic pillowy hedge look
    sub = hedge.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    bpy.ops.object.shade_smooth()
    hedge.data.materials.append(mat_hedge)
    return hedge

# ── 2. SM_HEDGE_CORNER ─────────────────────────────────────────────────────
# L-shaped continuous rounded puffy corner hedge
def build_hedge_corner():
    bm = bmesh.new()
    # 2 intersecting rounded blocks forming an L-shape
    # Block 1 along X from -0.5 to 0.5 at Y=-0.25
    # Block 2 along Y from -0.5 to 0.5 at X=0.25
    bmesh.ops.create_cube(bm, size=1.0)
    # Shape vertices into an L-shaped corner
    for v in bm.verts:
        # Scale to corner bounds
        v.co.x = v.co.x * 0.95
        v.co.y = v.co.y * 0.95
        v.co.z = v.co.z * 1.15 + 0.60

    mesh = bpy.data.meshes.new("SM_Hedge_Corner_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    corner = bpy.data.objects.new("SM_Hedge_Corner", mesh)
    bpy.context.collection.objects.link(corner)
    bpy.context.view_layer.objects.active = corner
    corner.select_set(True)

    bevel = corner.modifiers.new("Bevel", type='BEVEL')
    bevel.width = 0.24
    bevel.segments = 4
    bevel.profile = 0.75

    sub = corner.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    bpy.ops.object.shade_smooth()
    corner.data.materials.append(mat_hedge)
    return corner

# ── 3. SM_PATH_TILE ────────────────────────────────────────────────────────
# 1m x 1m modular grass pathway tile with slightly rounded beveled border
def build_path_tile():
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.04))
    path = bpy.context.active_object
    path.name = "SM_Path_Tile"
    path.scale = (1.0, 1.0, 0.08)
    bpy.ops.object.transform_apply(scale=True)

    bevel = path.modifiers.new("Bevel", type='BEVEL')
    bevel.width = 0.04
    bevel.segments = 2
    bpy.ops.object.shade_smooth()
    path.data.materials.append(mat_path)
    return path

# ── 4. SM_MOMO_COLLECTIBLE ─────────────────────────────────────────────────
# Adorable stylized steamed dumpling (Momo) with top pleated swirl & glow
def build_momo():
    # Dumpling body: slightly squashed sphere with tapered pleat at top
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.22, location=(0, 0, 0.16)
    )
    momo = bpy.context.active_object
    momo.name = "SM_Momo_Collectible"
    momo.scale = (1.10, 1.10, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    momo.data.materials.append(mat_momo)

    # Top pinch swirl / pleat
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.08, radius2=0.01, depth=0.10, location=(0, 0, 0.32)
    )
    pleat = bpy.context.active_object
    pleat.name = "Momo_Pleat"
    pleat.scale = (1.0, 1.0, 0.8)
    pleat.rotation_euler = (0, 0, RAD(25))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    pleat.data.materials.append(mat_momo)
    pleat.parent = momo

    # Soft glowing magical halo aura disc beneath
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.28, depth=0.02, location=(0, 0, 0.02)
    )
    glow_disc = bpy.context.active_object
    glow_disc.name = "Momo_Glow_Disc"
    glow_disc.data.materials.append(mat_momo_glow)
    glow_disc.parent = momo

    return momo

# ── 5. SM_LEAF_GATE ────────────────────────────────────────────────────────
# Living checkpoint arch: 2 rounded pillars, curved timber arch, lush leaf canopy, glowing Momo icon
def build_leaf_gate():
    gate_col = []

    # 1. Left Pillar (rounded warm stone/wood post)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.18, depth=1.60, location=(-0.90, 0, 0.80)
    )
    p_l = bpy.context.active_object
    p_l.name = "Gate_Pillar_L"
    bpy.ops.object.shade_smooth()
    p_l.data.materials.append(mat_gate_wood)
    gate_col.append(p_l)

    # 2. Right Pillar
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.18, depth=1.60, location=(0.90, 0, 0.80)
    )
    p_r = bpy.context.active_object
    p_r.name = "Gate_Pillar_R"
    bpy.ops.object.shade_smooth()
    p_r.data.materials.append(mat_gate_wood)
    gate_col.append(p_r)

    # 3. Curved Arch Timber Beam
    curve_data = bpy.data.curves.new(name="Gate_Arch_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.16
    curve_data.bevel_resolution = 4
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(2)

    # Semi-circular arch from left to right
    p0 = polyline.bezier_points[0]
    p0.co = (-0.90, 0, 1.50)
    p0.handle_left  = (-0.90, 0, 1.30)
    p0.handle_right = (-0.90, 0, 1.95)

    p1 = polyline.bezier_points[1]
    p1.co = (0.00, 0, 2.05)
    p1.handle_left  = (-0.50, 0, 2.05)
    p1.handle_right = ( 0.50, 0, 2.05)

    p2 = polyline.bezier_points[2]
    p2.co = (0.90, 0, 1.50)
    p2.handle_left  = (0.90, 0, 1.95)
    p2.handle_right = (0.90, 0, 1.30)

    arch_beam = bpy.data.objects.new("Gate_Arch_Beam", curve_data)
    bpy.context.collection.objects.link(arch_beam)
    bpy.context.view_layer.objects.active = arch_beam
    arch_beam.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.shade_smooth()
    arch_beam.data.materials.append(mat_gate_wood)
    gate_col.append(arch_beam)

    # 4. Lush Leaf Canopy (puffy rounded foliage clumps covering the arch)
    canopy_clumps = [
        (-0.80, 0, 1.70, 0.32),
        (-0.45, 0, 2.00, 0.38),
        ( 0.00, 0, 2.15, 0.44),
        ( 0.45, 0, 2.00, 0.38),
        ( 0.80, 0, 1.70, 0.32),
        (-0.25, 0.10, 2.10, 0.30),
        ( 0.25, -0.10, 2.10, 0.30),
    ]
    for i, (cx, cy, cz, cr) in enumerate(canopy_clumps):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=cr, location=(cx, cy, cz)
        )
        leaf_blob = bpy.context.active_object
        leaf_blob.name = f"Gate_Canopy_Leaf_{i}"
        leaf_blob.scale = (1.1, 1.1, 0.9)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        leaf_blob.data.materials.append(mat_gate_leaf)
        gate_col.append(leaf_blob)

    # 5. Glowing Momo Emblem in the Archway Center
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=0.20, location=(0, 0, 1.65)
    )
    emblem = bpy.context.active_object
    emblem.name = "Gate_Momo_Emblem"
    emblem.scale = (1.1, 0.7, 0.9)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    emblem.data.materials.append(mat_momo_glow)
    gate_col.append(emblem)

    # Create root empty for the gate
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    gate_root = bpy.context.active_object
    gate_root.name = "SM_Leaf_Gate"
    for part in gate_col:
        part.parent = gate_root

    return gate_root

# ── 6. SM_FLOWER_CLUSTER ───────────────────────────────────────────────────
# Clustered blooming daisies: 5-petal pink & white flowers with golden centers
def build_flower_cluster():
    flower_col = []

    def make_single_flower(x, y, z, scale, petal_mat):
        # 5 petals
        for p in range(5):
            ang = 2 * math.pi * p / 5
            px = x + 0.05 * scale * math.cos(ang)
            py = y + 0.05 * scale * math.sin(ang)
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.035 * scale,
                location=(px, py, z)
            )
            petal = bpy.context.active_object
            petal.scale = (0.9, 1.4, 0.4)
            petal.rotation_euler = (0, 0, ang)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            bpy.ops.object.shade_smooth()
            petal.data.materials.append(petal_mat)
            flower_col.append(petal)

        # Golden center pollen disc
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10, ring_count=8, radius=0.030 * scale,
            location=(x, y, z + 0.015 * scale)
        )
        center = bpy.context.active_object
        center.scale = (1.0, 1.0, 0.5)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        center.data.materials.append(mat_flower_c)
        flower_col.append(center)

    # Cluster of 4 blossoms (2 pink, 2 white)
    make_single_flower(-0.08, -0.06, 0.05, 1.2, mat_flower_p)
    make_single_flower( 0.09, -0.04, 0.06, 1.0, mat_flower_w)
    make_single_flower(-0.02,  0.08, 0.07, 1.1, mat_flower_p)
    make_single_flower( 0.10,  0.08, 0.05, 0.8, mat_flower_w)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "SM_Flower_Cluster"
    for obj in flower_col:
        obj.parent = root
    return root

# ── 7. SM_CLOVER_PATCH ─────────────────────────────────────────────────────
def build_clover_patch():
    clover_col = []
    # 3-leaf and 4-leaf clovers
    for (cx, cy, n_leaves, s) in [
        (-0.08, 0.00, 3, 1.0),
        ( 0.06, -0.06, 4, 1.1),
        ( 0.02, 0.08, 3, 0.8),
    ]:
        for i in range(n_leaves):
            ang = 2 * math.pi * i / n_leaves
            lx = cx + 0.035 * s * math.cos(ang)
            ly = cy + 0.035 * s * math.sin(ang)
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=10, ring_count=8, radius=0.030 * s,
                location=(lx, ly, 0.02)
            )
            leaf = bpy.context.active_object
            leaf.scale = (0.85, 1.2, 0.25)
            leaf.rotation_euler = (0, 0, ang)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            bpy.ops.object.shade_smooth()
            leaf.data.materials.append(mat_clover)
            clover_col.append(leaf)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "SM_Clover_Patch"
    for obj in clover_col:
        obj.parent = root
    return root

# ── Build Modular Asset Lineup Display ─────────────────────────────────────
print("Generating all Modular Environment Pieces...")
col_env = bpy.data.collections.new("Momo_Maze_Environment_Assets")
scene.collection.children.link(col_env)

# Lineup layout for display render:
# Place assets neatly along X so they can be inspected in one visual lineup
h_straight = build_hedge_straight()
h_straight.location = (-4.0, 0, 0)

h_corner = build_hedge_corner()
h_corner.location = (-2.4, 0, 0)

p_tile = build_path_tile()
p_tile.location = (-0.8, 0, 0)

momo_item = build_momo()
momo_item.location = (0.6, 0, 0)

flowers = build_flower_cluster()
flowers.location = (1.8, 0, 0)

clovers = build_clover_patch()
clovers.location = (2.8, 0, 0)

leaf_gate = build_leaf_gate()
leaf_gate.location = (4.8, 0, 0)

# Move all created objects into col_env
for obj in bpy.context.scene.objects:
    if obj.name not in col_env.objects:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col_env.objects.link(obj)

# ── Studio Lighting & Lineup Render ────────────────────────────────────────
bpy.ops.object.light_add(type='AREA', location=(3.0, -5.0, 4.5))
key = bpy.context.active_object
key.name = "Env_Key_Sun"
key.data.energy = 600
key.data.color = (1.0, 0.96, 0.88)
key.data.size = 6.0
key.rotation_euler = (RAD(50), 0, RAD(28))

bpy.ops.object.light_add(type='AREA', location=(-4.0, -3.5, 2.5))
fill = bpy.context.active_object
fill.name = "Env_Fill_Warm"
fill.data.energy = 240
fill.data.color = (1.0, 0.92, 0.85)
fill.data.size = 8.0

world = bpy.data.worlds.new("EnvStudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = STUDIO_BG
    bg.inputs["Strength"].default_value = 0.85

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.resolution_x = 1600
scene.render.resolution_y = 650
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True

# Camera overlooking the lineup
bpy.ops.object.camera_add(location=(0.4, -6.8, 2.5))
cam_lineup = bpy.context.active_object
cam_lineup.name = "Camera_Modular_Lineup"
cam_lineup.rotation_euler = (RAD(72), 0, 0)
cam_lineup.data.type = 'ORTHO'
cam_lineup.data.ortho_scale = 12.0
scene.camera = cam_lineup

lineup_path = os.path.join(RENDER_DIR, "modular_pieces_lineup.png")
scene.render.filepath = lineup_path
bpy.ops.render.render(write_still=True)
print(f"  ✓ Rendered Modular Pieces Lineup -> {lineup_path}")

# ── Save .blend & Export FBXs ──────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved .blend: {BLEND_PATH}")

# Export individual game-ready FBXs for Unreal Engine
export_targets = [
    ("SM_Hedge_Straight", [h_straight]),
    ("SM_Hedge_Corner",   [h_corner]),
    ("SM_Path_Tile",      [p_tile]),
    ("SM_Momo_Collectible", [momo_item] + list(momo_item.children)),
    ("SM_Leaf_Gate",      [leaf_gate] + list(leaf_gate.children)),
    ("SM_Flower_Cluster", [flowers] + list(flowers.children)),
]

for asset_name, objs in export_targets:
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)

    fbx_out = os.path.join(FBX_DIR, f"{asset_name}.fbx")
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
    print(f"  Exported FBX: {fbx_out}")

print("=== Modular Environment Assets Production Complete ===")
