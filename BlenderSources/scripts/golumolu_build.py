"""
MOMO MAZE – Golumolu Character Build Script
============================================
Blender 5.2 Python script.
Run via: blender --background --python golumolu_build.py
Or paste into Blender's Script Editor and run.

Produces:
  - Golumolu base mesh (low-mid poly, game-ready)
  - Material assignments matching the approved color palette
  - Saves BlenderSources/scenes/golumolu_v001.blend
  - Exports FBX to BlenderSources/exports/fbx/golumolu_v001.fbx

Color Palette (from Character Concept Sheet):
  Cream  / Fur Body   : #FCEEDD
  Peach  / Accents    : #FFC189
  Blush  / Cheeks     : #FFB3B0
  Brown  / Face+Eyes  : #6B4226
  Mouth Inner         : #E27567
"""

import bpy
import bmesh
import math
import os

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCENE_DIR    = os.path.join(PROJECT_ROOT, "scenes")
FBX_DIR      = os.path.join(PROJECT_ROOT, "exports", "fbx")
RENDER_DIR   = os.path.join(PROJECT_ROOT, "renders", "golumolu")

for d in (SCENE_DIR, FBX_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

BLEND_PATH = os.path.join(SCENE_DIR, "golumolu_v001.blend")
FBX_PATH   = os.path.join(FBX_DIR,   "golumolu_v001.fbx")

# ── Helpers ───────────────────────────────────────────────────────────────────
def hex_to_linear(hex_str):
    """Convert #RRGGBB to Blender linear-space RGB tuple."""
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    def srgb(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (srgb(r), srgb(g), srgb(b), 1.0)

PALETTE = {
    "cream":  hex_to_linear("#FCEEDD"),
    "peach":  hex_to_linear("#FFC189"),
    "blush":  hex_to_linear("#FFB3B0"),
    "brown":  hex_to_linear("#6B4226"),
    "mouth":  hex_to_linear("#E27567"),
    "white":  (1.0, 1.0, 1.0, 1.0),
}

def new_mat(name, color, roughness=0.85, specular=0.05):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value  = color
    bsdf.inputs["Roughness"].default_value   = roughness
    # Blender 5.x uses "Specular IOR Level" or legacy "Specular"
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = specular
    return mat

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def add_object(name, mesh_data=None):
    if mesh_data is None:
        mesh_data = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh_data)
    bpy.context.collection.objects.link(obj)
    return obj

def apply_smooth(obj, angle_deg=30):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    mod = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    mod.split_angle = math.radians(angle_deg)

def add_subdiv(obj, levels=2):
    mod = obj.modifiers.new("Subdivision", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels

# ── Materials ─────────────────────────────────────────────────────────────────
def build_materials():
    mats = {}
    mats["body"]   = new_mat("M_Golumolu_Body",   PALETTE["cream"],  roughness=0.90)
    mats["accent"] = new_mat("M_Golumolu_Accent",  PALETTE["peach"],  roughness=0.85)
    mats["blush"]  = new_mat("M_Golumolu_Blush",   PALETTE["blush"],  roughness=0.95)
    mats["eye"]    = new_mat("M_Golumolu_Eye",     PALETTE["brown"],  roughness=0.60, specular=0.3)
    mats["mouth"]  = new_mat("M_Golumolu_Mouth",   PALETTE["mouth"],  roughness=0.90)
    mats["white"]  = new_mat("M_Golumolu_White",   PALETTE["white"],  roughness=0.80)
    return mats

# ── Body ──────────────────────────────────────────────────────────────────────
def build_body(mats):
    """Large cream sphere = Golumolu's fluffy round body."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32, ring_count=24,
        radius=1.0, location=(0, 0, 0)
    )
    body = bpy.context.active_object
    body.name = "Golumolu_Body"
    # Squish slightly vertically for chubby look
    body.scale = (1.0, 0.92, 0.88)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(body)
    body.data.materials.append(mats["body"])
    return body

# ── Ears ──────────────────────────────────────────────────────────────────────
def build_ear(mats, side):
    """Small rounded peach ear nub."""
    x = 0.72 * side  # +1 right, -1 left
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=12,
        radius=0.28, location=(x, -0.15, 0.78)
    )
    ear = bpy.context.active_object
    ear.name = f"Golumolu_Ear_{'R' if side > 0 else 'L'}"
    ear.scale = (0.9, 0.7, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(ear)
    ear.data.materials.append(mats["accent"])
    # Inner ear (blush) – flat disc
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8,
        radius=0.15, location=(x, -0.28, 0.80)
    )
    inner = bpy.context.active_object
    inner.name = f"Golumolu_EarInner_{'R' if side > 0 else 'L'}"
    inner.scale = (0.9, 0.3, 0.9)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(inner)
    inner.data.materials.append(mats["blush"])
    return ear, inner

# ── Cheeks ────────────────────────────────────────────────────────────────────
def build_cheek(mats, side):
    """Rosy blush circle on each cheek."""
    x = 0.52 * side
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8,
        radius=0.22, location=(x, -0.92, 0.0)
    )
    cheek = bpy.context.active_object
    cheek.name = f"Golumolu_Cheek_{'R' if side > 0 else 'L'}"
    cheek.scale = (1.0, 0.25, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(cheek)
    cheek.data.materials.append(mats["blush"])
    return cheek

# ── Eyes ──────────────────────────────────────────────────────────────────────
def build_eye(mats, side):
    """Small dark brown happy-arc eyes (simple sphere, UV-mapped expression)."""
    x = 0.32 * side
    # Eye white
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8,
        radius=0.14, location=(x, -0.95, 0.20)
    )
    white = bpy.context.active_object
    white.name = f"Golumolu_EyeWhite_{'R' if side > 0 else 'L'}"
    white.scale = (1.0, 0.3, 0.9)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(white)
    white.data.materials.append(mats["white"])
    # Pupil
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=6,
        radius=0.09, location=(x, -1.0, 0.20)
    )
    pupil = bpy.context.active_object
    pupil.name = f"Golumolu_Pupil_{'R' if side > 0 else 'L'}"
    pupil.scale = (1.0, 0.25, 0.9)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(pupil)
    pupil.data.materials.append(mats["eye"])
    return white, pupil

# ── Nose / Mouth ──────────────────────────────────────────────────────────────
def build_nose_mouth(mats):
    # Small brown nose
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6,
        radius=0.07, location=(0, -1.0, 0.04)
    )
    nose = bpy.context.active_object
    nose.name = "Golumolu_Nose"
    nose.scale = (1.0, 0.4, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(nose)
    nose.data.materials.append(mats["eye"])
    # Mouth – small squished sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6,
        radius=0.14, location=(0, -1.0, -0.14)
    )
    mouth = bpy.context.active_object
    mouth.name = "Golumolu_Mouth"
    mouth.scale = (1.0, 0.3, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(mouth)
    mouth.data.materials.append(mats["mouth"])
    return nose, mouth

# ── Limbs ─────────────────────────────────────────────────────────────────────
def build_limb(mats, name, loc, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8,
        radius=0.22, location=loc
    )
    limb = bpy.context.active_object
    limb.name = name
    limb.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(limb)
    limb.data.materials.append(mats["accent"])
    return limb

def build_all_limbs(mats):
    limbs = []
    # Arms (tiny rounded nubs, peach)
    limbs.append(build_limb(mats, "Golumolu_ArmR", ( 1.00, -0.20, -0.30), (0.60, 0.55, 0.55)))
    limbs.append(build_limb(mats, "Golumolu_ArmL", (-1.00, -0.20, -0.30), (0.60, 0.55, 0.55)))
    # Feet
    limbs.append(build_limb(mats, "Golumolu_FootR", ( 0.42, -0.10, -0.92), (0.55, 0.50, 0.42)))
    limbs.append(build_limb(mats, "Golumolu_FootL", (-0.42, -0.10, -0.92), (0.55, 0.50, 0.42)))
    return limbs

# ── Tail nub ──────────────────────────────────────────────────────────────────
def build_tail(mats):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8,
        radius=0.18, location=(0, 0.95, -0.10)
    )
    tail = bpy.context.active_object
    tail.name = "Golumolu_Tail"
    tail.scale = (0.8, 0.9, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(tail)
    tail.data.materials.append(mats["cream"])
    return tail

# ── Collection & Parenting ───────────────────────────────────────────────────
def collect_all(body, all_parts):
    col = bpy.data.collections.new("Golumolu")
    bpy.context.scene.collection.children.link(col)
    # Move everything into the collection
    for obj in [body] + all_parts:
        for old_col in obj.users_collection:
            old_col.objects.unlink(obj)
        col.objects.link(obj)
        if obj != body:
            obj.parent = body

# ── Camera & Lighting for Validation Renders ─────────────────────────────────
def setup_render_scene():
    scene = bpy.context.scene
    scene.render.engine        = 'CYCLES'
    scene.cycles.samples       = 128
    scene.render.resolution_x  = 1024
    scene.render.resolution_y  = 1024
    scene.render.image_settings.file_format = 'PNG'

    # World – warm ambient
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = hex_to_linear("#FFF3E8")
        bg.inputs["Strength"].default_value = 1.2

    # Key light
    bpy.ops.object.light_add(type='AREA', location=(2.5, -2.5, 3.0))
    key = bpy.context.active_object
    key.name = "Light_Key"
    key.data.energy = 300
    key.data.color  = (1.0, 0.95, 0.85)
    key.data.size   = 2.0
    key.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-2.0, -1.5, 1.5))
    fill = bpy.context.active_object
    fill.name = "Light_Fill"
    fill.data.energy = 100
    fill.data.color  = (0.9, 0.95, 1.0)
    fill.data.size   = 3.0

def add_camera(name, location, rotation_euler):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    cam.rotation_euler = rotation_euler
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 2.8
    return cam

def render_view(cam_obj, filepath):
    bpy.context.scene.camera = cam_obj
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

# ── Main Build ────────────────────────────────────────────────────────────────
def main():
    print("=== MOMO MAZE: Building Golumolu ===")
    clear_scene()

    mats = build_materials()

    body  = build_body(mats)
    ear_r, ear_ri = build_ear(mats,  1)
    ear_l, ear_li = build_ear(mats, -1)
    cheek_r = build_cheek(mats,  1)
    cheek_l = build_cheek(mats, -1)
    eye_wr, pupil_r = build_eye(mats,  1)
    eye_wl, pupil_l = build_eye(mats, -1)
    nose, mouth     = build_nose_mouth(mats)
    tail            = build_tail(mats)
    limbs           = build_all_limbs(mats)

    all_parts = [
        ear_r, ear_ri, ear_l, ear_li,
        cheek_r, cheek_l,
        eye_wr, pupil_r, eye_wl, pupil_l,
        nose, mouth, tail
    ] + limbs

    collect_all(body, all_parts)

    # ── Save .blend ──
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")

    # ── Render four validation views ──
    setup_render_scene()

    RAD = math.radians
    cameras = {
        "front": add_camera(
            "Cam_Front",
            location=(0, -4.5, 0),
            rotation_euler=(RAD(90), 0, 0)
        ),
        "34view": add_camera(
            "Cam_34",
            location=(3.0, -3.5, 1.2),
            rotation_euler=(RAD(72), 0, RAD(40))
        ),
        "side": add_camera(
            "Cam_Side",
            location=(4.5, 0, 0),
            rotation_euler=(RAD(90), 0, RAD(90))
        ),
        "back": add_camera(
            "Cam_Back",
            location=(0, 4.5, 0),
            rotation_euler=(RAD(90), 0, RAD(180))
        ),
    }

    for view_name, cam in cameras.items():
        out = os.path.join(RENDER_DIR, f"golumolu_{view_name}.png")
        print(f"Rendering {view_name} → {out}")
        render_view(cam, out)

    # ── Export FBX ──
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if "Golumolu" in obj.name:
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
        add_leaf_bones=False,
    )
    print(f"Exported FBX: {FBX_PATH}")
    print("=== Golumolu Build Complete ===")

if __name__ == "__main__":
    main()
