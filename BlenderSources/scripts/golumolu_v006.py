"""
MOMO MAZE – Golumolu Final Validated Model (v006)
=================================================
Faithfully matches the approved art direction from the concept sheet:
1. Silhouette: Chubby cream body, pear-shaped rounded volume
2. Face:
   - Happy curved arc eyes ⌒ ⌒ in #6B4226
   - Open smiling mouth :D clearly visible (coral #E27567 interior with dark brown #6B4226 outline)
   - Rosy blush cheek ovals #FFB3B0 under the eyes
   - Strictly NO NOSE (as per concept sheet)
3. Limbs:
   - Tiny peach rounded paws #FFC189 poking forward adorably
   - Peach feet supporting the body
   - Peach rounded ears with soft inner blush
   - Chubby cream tail at the back
4. 4 Orthographic validation renders (Front, 3/4, Side, Back)
5. Export game-ready FBX
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

BLEND_PATH = os.path.join(SCENE_DIR, "golumolu_v006.blend")
FBX_PATH   = os.path.join(FBX_DIR,   "golumolu_v006.fbx")

# ── Approved Colors ────────────────────────────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_to_rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), alpha)

CREAM_BODY   = hex_to_rgba("#FCEEDD")  # Body cream fur
PEACH_ACCENT = hex_to_rgba("#FFC189")  # Peach ears & limbs
BLUSH_PINK   = hex_to_rgba("#FFB3B0")  # Rosy cheeks & inner ear
BROWN_FACE   = hex_to_rgba("#6B4226")  # Eyes & mouth border
MOUTH_INNER  = hex_to_rgba("#E27567")  # Mouth interior
BG_WARM      = hex_to_rgba("#F7EFE6")  # Warm background tone

RAD = math.radians

def create_material(name, base_color, roughness=0.88, sss_weight=0.10, sss_color=None):
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
            bsdf.inputs[spec_name].default_value = 0.08
            break

    if sss_weight > 0:
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = sss_weight
            if sss_color and "Subsurface Color" in bsdf.inputs:
                bsdf.inputs["Subsurface Color"].default_value = sss_color
        elif "Subsurface" in bsdf.inputs:
            bsdf.inputs["Subsurface"].default_value = sss_weight

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

mat_body   = create_material("M_Golumolu_Body",   CREAM_BODY,   roughness=0.92, sss_weight=0.15, sss_color=PEACH_ACCENT)
mat_peach  = create_material("M_Golumolu_Peach",  PEACH_ACCENT, roughness=0.88, sss_weight=0.10, sss_color=BLUSH_PINK)
mat_blush  = create_material("M_Golumolu_Blush",  BLUSH_PINK,   roughness=0.95, sss_weight=0.06)
mat_brown  = create_material("M_Golumolu_Brown",  BROWN_FACE,   roughness=0.55)
mat_mouth  = create_material("M_Golumolu_Mouth",  MOUTH_INNER,  roughness=0.75, sss_weight=0.05)

parts = []

# ── 1. BODY ────────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0, location=(0, 0, 0))
body = bpy.context.active_object
body.name = "Golumolu_Body"
body.scale = (1.04, 0.98, 0.92)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth()
body.data.materials.append(mat_body)

# ── 2. EARS ────────────────────────────────────────────────────────────────
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
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

# ── 3. CHEEKS ──────────────────────────────────────────────────────────────
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.21,
        location=(side * 0.52, -0.84, -0.04)
    )
    chk = bpy.context.active_object
    chk.name = f"Golumolu_Cheek_{s_name}"
    chk.scale = (1.0, 0.22, 0.70)
    chk.rotation_euler = (RAD(14), side * RAD(-16), side * RAD(8))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    chk.data.materials.append(mat_blush)
    parts.append(chk)

# ── 4. HAPPY ARCH EYES ⌒ ⌒ ────────────────────────────────────────────────
def build_happy_eye(name, side):
    curve_data = bpy.data.curves.new(name=name + "_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.034
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True

    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(2)

    ox = side * 0.33
    oy = -0.92
    oz = 0.22

    p0 = polyline.bezier_points[0]
    p0.co = (ox - side * 0.11, oy + 0.06, oz - 0.045)
    p0.handle_left = (ox - side * 0.13, oy + 0.07, oz - 0.06)
    p0.handle_right = (ox - side * 0.05, oy + 0.02, oz + 0.025)

    p1 = polyline.bezier_points[1]
    p1.co = (ox, oy - 0.022, oz + 0.045)
    p1.handle_left = (ox - side * 0.05, oy + 0.01, oz + 0.045)
    p1.handle_right = (ox + side * 0.05, oy + 0.01, oz + 0.045)

    p2 = polyline.bezier_points[2]
    p2.co = (ox + side * 0.11, oy + 0.05, oz - 0.035)
    p2.handle_left = (ox + side * 0.05, oy + 0.02, oz + 0.025)
    p2.handle_right = (ox + side * 0.13, oy + 0.06, oz - 0.055)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat_brown)
    return obj

eye_r = build_happy_eye("Golumolu_Eye_R", 1.0)
eye_l = build_happy_eye("Golumolu_Eye_L", -1.0)
parts.extend([eye_r, eye_l])

# ── 5. OPEN HAPPY MOUTH (Prominent & clearly visible) ──────────────────────
# A classic open anime smile :D sitting flush on the front face
def build_happy_smile_mouth():
    mouth_col = []

    # Outer border (dark brown)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.15, depth=0.06,
        location=(0, -1.00, -0.04)
    )
    border = bpy.context.active_object
    border.name = "Golumolu_Mouth_Border"
    border.scale = (1.25, 0.45, 0.95)
    border.rotation_euler = (RAD(14), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    border.data.materials.append(mat_brown)
    mouth_col.append(border)

    # Inner cavity (coral/peach red)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.125, depth=0.07,
        location=(0, -1.015, -0.04)
    )
    inner = bpy.context.active_object
    inner.name = "Golumolu_Mouth_Inner"
    inner.scale = (1.18, 0.42, 0.88)
    inner.rotation_euler = (RAD(14), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    inner.data.materials.append(mat_mouth)
    mouth_col.append(inner)

    return mouth_col

mouth_parts = build_happy_smile_mouth()
parts.extend(mouth_parts)

# ── 6. HANDS (poking forward adorably, clearly visible from front) ────────
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.20,
        location=(side * 0.86, -0.32, -0.16)
    )
    arm = bpy.context.active_object
    arm.name = f"Golumolu_Hand_{s_name}"
    arm.scale = (0.75, 0.80, 0.65)
    arm.rotation_euler = (RAD(28), side * RAD(-35), side * RAD(-15))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    arm.data.materials.append(mat_peach)
    parts.append(arm)

# ── 7. FEET ────────────────────────────────────────────────────────────────
for side, s_name in [(1.0, "R"), (-1.0, "L")]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=0.21,
        location=(side * 0.38, -0.10, -0.88)
    )
    foot = bpy.context.active_object
    foot.name = f"Golumolu_Foot_{s_name}"
    foot.scale = (0.72, 0.88, 0.44)
    foot.rotation_euler = (RAD(-12), side * RAD(14), side * RAD(16))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    foot.data.materials.append(mat_peach)
    parts.append(foot)

# ── 8. TAIL ────────────────────────────────────────────────────────────────
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

# ── Hierarchy ──────────────────────────────────────────────────────────────
col = bpy.data.collections.new("Golumolu_Character")
scene.collection.children.link(col)

for obj in [body] + parts:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    if obj != body:
        obj.parent = body

# ── Lighting Setup (Warm Sunlight & Cozy Studio) ───────────────────────────
bpy.ops.object.light_add(type='AREA', location=(3.2, -3.2, 3.6))
key = bpy.context.active_object
key.name = "Light_Key_Sun"
key.data.energy = 480
key.data.color = (1.0, 0.94, 0.86)
key.data.size = 2.5
key.rotation_euler = (RAD(48), 0, RAD(38))

bpy.ops.object.light_add(type='AREA', location=(-3.0, -2.0, 1.8))
fill = bpy.context.active_object
fill.name = "Light_Fill_Warm"
fill.data.energy = 180
fill.data.color = (1.0, 0.90, 0.82)
fill.data.size = 4.0
fill.rotation_euler = (RAD(30), 0, RAD(-45))

bpy.ops.object.light_add(type='AREA', location=(0.0, 3.2, 2.8))
rim = bpy.context.active_object
rim.name = "Light_Rim_Highlight"
rim.data.energy = 150
rim.data.color = (1.0, 0.96, 0.90)
rim.data.size = 3.0
rim.rotation_euler = (RAD(-45), 0, RAD(180))

# World Background
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

    out_path = os.path.join(RENDER_DIR, f"golumolu_v006_{vname}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered {vname} -> {out_path}")

# ── Save .blend & Export FBX ───────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved .blend: {BLEND_PATH}")

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
print("=== Golumolu v006 Production Finished Successfully ===")
