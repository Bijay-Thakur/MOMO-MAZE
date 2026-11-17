"""
MOMO MAZE – Golumolu MCP Build Script
======================================
Paste this into Blender's Script Editor (Text > Run Script) while the
Blender MCP addon server is running. It builds Golumolu and fires four
orthographic validation renders through Blender's render engine.

This version is designed to run INTERACTIVELY inside Blender's Python
environment (not --background) so the MCP addon stays connected.
"""

import bpy, bmesh, math, os

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = r"D:\Projects\MOMO MAZE\BlenderSources"
SCENE_DIR    = os.path.join(PROJECT_ROOT, "scenes")
FBX_DIR      = os.path.join(PROJECT_ROOT, "exports", "fbx")
RENDER_DIR   = os.path.join(PROJECT_ROOT, "renders", "golumolu")
for d in (SCENE_DIR, FBX_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

BLEND_PATH = os.path.join(SCENE_DIR, "golumolu_v001.blend")
FBX_PATH   = os.path.join(FBX_DIR,   "golumolu_v001.fbx")

# ── Color helpers ─────────────────────────────────────────────────────────────
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hex_rgba(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    return (srgb(r), srgb(g), srgb(b), 1.0)

CREAM  = hex_rgba("#FCEEDD")
PEACH  = hex_rgba("#FFC189")
BLUSH  = hex_rgba("#FFB3B0")
BROWN  = hex_rgba("#6B4226")
MOUTH  = hex_rgba("#E27567")
WHITE  = (1.0, 1.0, 1.0, 1.0)

# ── Material factory ──────────────────────────────────────────────────────────
def mat(name, color, rough=0.88, spec=0.05):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    b = nodes.get("Principled BSDF") or nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value  = rough
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    return m

# ── Scene prep ────────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ── Materials ─────────────────────────────────────────────────────────────────
M_BODY   = mat("M_Body",   CREAM)
M_ACCENT = mat("M_Accent", PEACH)
M_BLUSH  = mat("M_Blush",  BLUSH, rough=0.95)
M_EYE    = mat("M_Eye",    BROWN, rough=0.5, spec=0.3)
M_MOUTH  = mat("M_Mouth",  MOUTH)
M_WHITE  = mat("M_White",  WHITE, rough=0.75)

# ── Helper: add sphere ────────────────────────────────────────────────────────
def sphere(name, radius, loc, scale=(1,1,1), mat_ref=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16,
                                          radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    if mat_ref:
        obj.data.materials.clear()
        obj.data.materials.append(mat_ref)
    return obj

# ── Build Golumolu ────────────────────────────────────────────────────────────
# Body – large cream sphere, slightly squished
body = sphere("Golumolu_Body", 1.0, (0,0,0), scale=(1.0, 0.92, 0.88), mat_ref=M_BODY)

# Ears (peach nubs)
ear_r  = sphere("Ear_R",      0.28, ( 0.72,-0.15, 0.78), (0.90, 0.70, 1.00), M_ACCENT)
ear_l  = sphere("Ear_L",      0.28, (-0.72,-0.15, 0.78), (0.90, 0.70, 1.00), M_ACCENT)
# Inner ear blush
iear_r = sphere("EarIn_R",    0.14, ( 0.72,-0.30, 0.80), (0.90, 0.28, 0.90), M_BLUSH)
iear_l = sphere("EarIn_L",    0.14, (-0.72,-0.30, 0.80), (0.90, 0.28, 0.90), M_BLUSH)

# Cheeks (blush discs)
chk_r = sphere("Cheek_R",    0.22, ( 0.52,-0.93, 0.0), (1.0, 0.22, 0.65), M_BLUSH)
chk_l = sphere("Cheek_L",    0.22, (-0.52,-0.93, 0.0), (1.0, 0.22, 0.65), M_BLUSH)

# Eyes
ewh_r  = sphere("EyeWh_R",   0.14, ( 0.32,-0.96, 0.22), (1.0, 0.28, 0.90), M_WHITE)
ewh_l  = sphere("EyeWh_L",   0.14, (-0.32,-0.96, 0.22), (1.0, 0.28, 0.90), M_WHITE)
pup_r  = sphere("Pupil_R",   0.09, ( 0.32,-1.02, 0.22), (1.0, 0.22, 0.90), M_EYE)
pup_l  = sphere("Pupil_L",   0.09, (-0.32,-1.02, 0.22), (1.0, 0.22, 0.90), M_EYE)

# Nose
nose   = sphere("Nose",       0.07, (0.0, -1.02, 0.04), (1.0, 0.38, 0.70), M_EYE)

# Mouth (happy open)
mouth  = sphere("Mouth",      0.14, (0.0, -1.02,-0.15), (1.0, 0.28, 0.55), M_MOUTH)

# Tail nub (back)
tail   = sphere("Tail",       0.18, (0.0,  0.96,-0.10), (0.8, 0.9, 0.8), M_BODY)

# Arms (tiny peach nubs at sides)
arm_r  = sphere("Arm_R",      0.22, ( 1.00,-0.20,-0.30), (0.60, 0.55, 0.55), M_ACCENT)
arm_l  = sphere("Arm_L",      0.22, (-1.00,-0.20,-0.30), (0.60, 0.55, 0.55), M_ACCENT)

# Feet
foot_r = sphere("Foot_R",     0.22, ( 0.42,-0.10,-0.93), (0.55, 0.50, 0.42), M_ACCENT)
foot_l = sphere("Foot_L",     0.22, (-0.42,-0.10,-0.93), (0.55, 0.50, 0.42), M_ACCENT)

# ── Collection & parent to body ───────────────────────────────────────────────
parts = [ear_r, ear_l, iear_r, iear_l, chk_r, chk_l,
         ewh_r, ewh_l, pup_r, pup_l, nose, mouth, tail,
         arm_r, arm_l, foot_r, foot_l]

col = bpy.data.collections.get("Golumolu") or bpy.data.collections.new("Golumolu")
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)

for obj in [body] + parts:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

for p in parts:
    p.parent = body

# ── Lighting ──────────────────────────────────────────────────────────────────
bpy.ops.object.light_add(type='AREA', location=(2.5,-2.5, 3.0))
key = bpy.context.active_object; key.name="Light_Key"
key.data.energy=300; key.data.color=(1.0,0.95,0.85); key.data.size=2.0
key.rotation_euler=(math.radians(50), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-2.0,-1.5, 1.5))
fill = bpy.context.active_object; fill.name="Light_Fill"
fill.data.energy=100; fill.data.color=(0.90,0.95,1.0); fill.data.size=3.0

# World warm tint
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value   = hex_rgba("#FFF3E8")
    bg.inputs["Strength"].default_value = 1.2

# ── Render settings ───────────────────────────────────────────────────────────
sc = bpy.context.scene
sc.render.engine       = 'CYCLES'
sc.cycles.samples      = 128
sc.render.resolution_x = 1024
sc.render.resolution_y = 1024
sc.render.image_settings.file_format = 'PNG'

RAD = math.radians

VIEWS = {
    "front":  {"loc": (0,   -4.5,  0),   "rot": (RAD(90), 0, 0)},
    "34view": {"loc": (3.0, -3.5,  1.2), "rot": (RAD(72), 0, RAD(40))},
    "side":   {"loc": (4.5,  0,    0),   "rot": (RAD(90), 0, RAD(90))},
    "back":   {"loc": (0,    4.5,  0),   "rot": (RAD(90), 0, RAD(180))},
}

for name, v in VIEWS.items():
    bpy.ops.object.camera_add(location=v["loc"])
    cam = bpy.context.active_object
    cam.name = f"Cam_{name}"
    cam.rotation_euler = v["rot"]
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 2.8
    sc.camera = cam
    sc.render.filepath = os.path.join(RENDER_DIR, f"golumolu_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: golumolu_{name}.png")

# ── Save .blend ───────────────────────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved: {BLEND_PATH}")

# ── Export FBX ───────────────────────────────────────────────────────────────
for obj in bpy.data.objects:
    obj.select_set("Golumolu" in obj.name or obj.name in
                   [o.name for o in col.objects])
bpy.ops.export_scene.fbx(
    filepath=FBX_PATH,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z', axis_up='Y',
    mesh_smooth_type='FACE',
    use_mesh_modifiers=True,
    add_leaf_bones=False,
)
print(f"FBX exported: {FBX_PATH}")
print("=== Golumolu build complete! ===")
