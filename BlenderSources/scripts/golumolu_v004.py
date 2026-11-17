"""
MOMO MAZE – Golumolu Accurate 3D Model (v004)
==============================================
Faithfully reproduces Golumolu from the approved Character Concept Sheet:
- Accurate pear/sphere body silhouette with soft fluffy feel
- Peach rounded ears with inner blush
- Cheeks: Rosy soft blush ovals at the correct height/spread
- Eyes: Beautiful happy curved arcs ⌒ ⌒ in #6B4226 (conforming to face curvature)
- Mouth: Open happy smiling mouth with #E27567 interior and dark outline
- NO NOSE (as per concept sheet)
- Tiny rounded peach hands and feet
- Cute tail at the rear
- Warm studio lighting and backdrop matching the concept sheet
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
RENDER_DIR   = os.path.join(PROJECT_ROOT, "renders", "golumolu")

for d in (SCENE_DIR, FBX_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

BLEND_PATH = os.path.join(SCENE_DIR, "golumolu_v004.blend")
FBX_PATH   = os.path.join(FBX_DIR,   "golumolu_v004.fbx")

# ── Color Palette (Approved hex values) ────────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_to_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), alpha)

CREAM_BODY   = hex_to_rgba("#FCEEDD")  # Fur / Body
PEACH_ACCENT = hex_to_rgba("#FFC189")  # Ears / Limbs
BLUSH_PINK   = hex_to_rgba("#FFB3B0")  # Cheeks
BROWN_FACE   = hex_to_rgba("#6B4226")  # Eyes / Mouth outline
MOUTH_INNER  = hex_to_rgba("#E27567")  # Mouth inside
BG_WARM      = hex_to_rgba("#F7EFE6")  # Warm background tone

RAD = math.radians

# ── Materials ──────────────────────────────────────────────────────────────
def create_material(name, base_color, roughness=0.85, sss_weight=0.08, sss_color=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness

    # Specular
    for spec_name in ("Specular IOR Level", "Specular"):
        if spec_name in bsdf.inputs:
            bsdf.inputs[spec_name].default_value = 0.08
            break

    # Subsurface for soft organic fluffy appearance
    if sss_weight > 0:
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = sss_weight
            if sss_color and "Subsurface Color" in bsdf.inputs:
                bsdf.inputs["Subsurface Color"].default_value = sss_color
        elif "Subsurface" in bsdf.inputs:
            bsdf.inputs["Subsurface"].default_value = sss_weight

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

# ── Scene Cleanup ──────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Build materials
mat_body   = create_material("M_Golumolu_Body",   CREAM_BODY,   roughness=0.92, sss_weight=0.15, sss_color=PEACH_ACCENT)
mat_peach  = create_material("M_Golumolu_Peach",  PEACH_ACCENT, roughness=0.88, sss_weight=0.10, sss_color=BLUSH_PINK)
mat_blush  = create_material("M_Golumolu_Blush",  BLUSH_PINK,   roughness=0.95, sss_weight=0.05)
mat_brown  = create_material("M_Golumolu_Brown",  BROWN_FACE,   roughness=0.60)
mat_mouth  = create_material("M_Golumolu_Mouth",  MOUTH_INNER,  roughness=0.85)

# ── Geometry Generation ────────────────────────────────────────────────────
parts = []

# 1. BODY - Pear-shaped sphere
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0, location=(0, 0, 0))
body = bpy.context.active_object
body.name = "Golumolu_Body"
# Chubby pear shape: slightly wider at bottom, squashed vertically
body.scale = (1.04, 0.98, 0.92)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth()
body.data.materials.append(mat_body)

# 2. EARS - Rounded peach ears with forward tilt
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    # Outer peach ear
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.28,
        location=(side * 0.65, -0.10, 0.76)
    )
    ear = bpy.context.active_object
    ear.name = f"Golumolu_Ear_{s_name}"
    ear.scale = (0.85, 0.65, 0.95)
    ear.rotation_euler = (RAD(-12), side * RAD(22), side * RAD(-10))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    ear.data.materials.append(mat_peach)
    parts.append(ear)

    # Inner soft blush tint
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=12, radius=0.16,
        location=(side * 0.64, -0.21, 0.76)
    )
    inear = bpy.context.active_object
    inear.name = f"Golumolu_EarInner_{s_name}"
    inear.scale = (0.75, 0.25, 0.85)
    inear.rotation_euler = (RAD(-12), side * RAD(22), side * RAD(-10))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    inear.data.materials.append(mat_blush)
    parts.append(inear)

# 3. CHEEKS - Soft blush discs
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.20,
        location=(side * 0.50, -0.84, -0.06)
    )
    chk = bpy.context.active_object
    chk.name = f"Golumolu_Cheek_{s_name}"
    chk.scale = (1.0, 0.22, 0.70)
    chk.rotation_euler = (RAD(15), side * RAD(-15), side * RAD(8))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    chk.data.materials.append(mat_blush)
    parts.append(chk)

# 4. EYES - Happy curved arcs ⌒ ⌒
def build_happy_eye_arc(name, side):
    """Creates a smooth curved crescent arch sitting flush on the head."""
    curve_data = bpy.data.curves.new(name=name + "_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.026  # Thickness of the eye stroke
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True

    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(2)  # 3 points total

    ox = side * 0.32
    oy = -0.92
    oz = 0.20

    # P0: Inner corner
    p0 = polyline.bezier_points[0]
    p0.co = (ox - side * 0.10, oy + 0.05, oz - 0.04)
    p0.handle_left = (ox - side * 0.12, oy + 0.06, oz - 0.06)
    p0.handle_right = (ox - side * 0.05, oy + 0.02, oz + 0.02)

    # P1: Arch peak
    p1 = polyline.bezier_points[1]
    p1.co = (ox, oy - 0.02, oz + 0.04)
    p1.handle_left = (ox - side * 0.05, oy + 0.01, oz + 0.04)
    p1.handle_right = (ox + side * 0.05, oy + 0.01, oz + 0.04)

    # P2: Outer corner (slight downward taper)
    p2 = polyline.bezier_points[2]
    p2.co = (ox + side * 0.10, oy + 0.04, oz - 0.03)
    p2.handle_left = (ox + side * 0.05, oy + 0.02, oz + 0.02)
    p2.handle_right = (ox + side * 0.12, oy + 0.05, oz - 0.05)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)

    # Convert to mesh for clean export
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat_brown)
    return obj

eye_r = build_happy_eye_arc("Golumolu_Eye_R", 1.0)
eye_l = build_happy_eye_arc("Golumolu_Eye_L", -1.0)
parts.extend([eye_r, eye_l])

# 5. MOUTH - Open happy mouth (curved upper arch, round lower bowl, pink inside)
# Outer dark brown rim
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24, ring_count=16, radius=0.15,
    location=(0, -0.96, -0.12)
)
mouth_rim = bpy.context.active_object
mouth_rim.name = "Golumolu_Mouth_Rim"
mouth_rim.scale = (1.20, 0.28, 0.85)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth()
mouth_rim.data.materials.append(mat_brown)
parts.append(mouth_rim)

# Inner pink mouth cavity
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.13,
    location=(0, -0.97, -0.12)
)
mouth_in = bpy.context.active_object
mouth_in.name = "Golumolu_Mouth_Inner"
mouth_in.scale = (1.10, 0.25, 0.78)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth()
mouth_in.data.materials.append(mat_mouth)
parts.append(mouth_in)

# 6. ARMS / HANDS - Tiny rounded peach stubs
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=0.18,
        location=(side * 0.88, -0.22, -0.20)
    )
    arm = bpy.context.active_object
    arm.name = f"Golumolu_Hand_{s_name}"
    arm.scale = (0.75, 0.65, 0.65)
    arm.rotation_euler = (RAD(20), side * RAD(-25), side * RAD(-15))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    arm.data.materials.append(mat_peach)
    parts.append(arm)

# 7. FEET - Tiny rounded peach foot pads
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=0.20,
        location=(side * 0.40, -0.05, -0.88)
    )
    foot = bpy.context.active_object
    foot.name = f"Golumolu_Foot_{s_name}"
    foot.scale = (0.70, 0.85, 0.45)
    foot.rotation_euler = (RAD(-10), side * RAD(12), side * RAD(15))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    foot.data.materials.append(mat_peach)
    parts.append(foot)

# 8. TAIL - Rounded cute tail nub at back
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.17,
    location=(0, 0.90, -0.08)
)
tail = bpy.context.active_object
tail.name = "Golumolu_Tail"
tail.scale = (0.85, 0.95, 0.80)
tail.rotation_euler = (RAD(-15), 0, 0)
bpy.ops.object.transform_apply(scale=True, rotation=True)
bpy.ops.object.shade_smooth()
tail.data.materials.append(mat_body)
parts.append(tail)

# ── Hierarchy & Parenting ──────────────────────────────────────────────────
col = bpy.data.collections.new("Golumolu_Character")
scene.collection.children.link(col)

for obj in [body] + parts:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    if obj != body:
        obj.parent = body

# ── Lighting & Studio Setup ────────────────────────────────────────────────
# Key Light - warm sunlight
bpy.ops.object.light_add(type='AREA', location=(3.0, -3.2, 3.5))
key = bpy.context.active_object
key.name = "Light_Key_Sun"
key.data.energy = 450
key.data.color = (1.0, 0.94, 0.86)
key.data.size = 2.5
key.rotation_euler = (RAD(48), 0, RAD(38))

# Fill Light - soft warm ambient fill
bpy.ops.object.light_add(type='AREA', location=(-2.8, -2.0, 1.8))
fill = bpy.context.active_object
fill.name = "Light_Fill_Warm"
fill.data.energy = 160
fill.data.color = (1.0, 0.90, 0.82)
fill.data.size = 4.0
fill.rotation_euler = (RAD(30), 0, RAD(-45))

# Rim Light - back-top highlight to pop silhouette
bpy.ops.object.light_add(type='AREA', location=(0.0, 3.2, 2.8))
rim = bpy.context.active_object
rim.name = "Light_Rim_Highlight"
rim.data.energy = 140
rim.data.color = (1.0, 0.96, 0.90)
rim.data.size = 3.0
rim.rotation_euler = (RAD(-45), 0, RAD(180))

# World Background - warm cozy studio tone
world = bpy.data.worlds.new("CozyStudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = BG_WARM
    bg.inputs["Strength"].default_value = 0.85

# ── Render Settings ────────────────────────────────────────────────────────
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True

# ── Four Orthographic Views ────────────────────────────────────────────────
VIEWS = [
    ("front",  (0.0, -4.5,  0.0), (RAD(90), 0, 0)),
    ("34view", (3.2, -3.2,  0.8), (RAD(76), 0, RAD(45))),
    ("side",   (4.5,  0.0,  0.0), (RAD(90), 0, RAD(90))),
    ("back",   (0.0,  4.5,  0.0), (RAD(90), 0, RAD(180))),
]

print("Rendering 4 validation views...")
for vname, loc, rot in VIEWS:
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = f"Camera_{vname}"
    cam.rotation_euler = rot
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 2.85
    scene.camera = cam

    out_path = os.path.join(RENDER_DIR, f"golumolu_v004_{vname}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered {vname} -> {out_path}")

# ── Save .blend file ───────────────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved .blend: {BLEND_PATH}")

# ── Export FBX for Unreal Engine ───────────────────────────────────────────
bpy.ops.object.select_all(action='DESELECT')
for obj in col.objects:
    obj.select_set(True)

bpy.ops.export_scene.fbx(
    filepath=FBX_PATH,
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
print(f"Exported FBX: {FBX_PATH}")
print("=== Golumolu v004 Production Finished Successfully ===")
