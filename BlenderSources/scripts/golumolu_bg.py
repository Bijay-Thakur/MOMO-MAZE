"""
MOMO MAZE – Golumolu Background Build + Render
================================================
Blender 5.2 background-mode script.
Uses EEVEE_NEXT (no GPU required for headless render).

Run as:
  blender --background --python golumolu_bg.py

Outputs:
  BlenderSources/scenes/golumolu_v001.blend
  BlenderSources/exports/fbx/golumolu_v001.fbx
  BlenderSources/renders/golumolu/golumolu_{front,34view,side,back}.png
"""

import bpy, math, os, sys, traceback

try:
    # ── Paths ─────────────────────────────────────────────────────────────────
    THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
    ROOT      = os.path.abspath(os.path.join(THIS_DIR, ".."))
    SCENE_DIR  = os.path.join(ROOT, "scenes");   os.makedirs(SCENE_DIR,  exist_ok=True)
    FBX_DIR    = os.path.join(ROOT, "exports", "fbx"); os.makedirs(FBX_DIR, exist_ok=True)
    RENDER_DIR = os.path.join(ROOT, "renders", "golumolu"); os.makedirs(RENDER_DIR, exist_ok=True)

    BLEND_PATH = os.path.join(SCENE_DIR,  "golumolu_v001.blend")
    FBX_PATH   = os.path.join(FBX_DIR,    "golumolu_v001.fbx")

    # ── Color helpers ─────────────────────────────────────────────────────────
    def srgb(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def hex_rgba(h):
        h = h.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (srgb(r), srgb(g), srgb(b), 1.0)

    C  = hex_rgba  # alias
    CREAM = C("#FCEEDD"); PEACH = C("#FFC189"); BLUSH = C("#FFB3B0")
    BROWN = C("#6B4226"); MOUTH = C("#E27567"); WHITE = (1.0, 1.0, 1.0, 1.0)

    # ── Material factory ──────────────────────────────────────────────────────
    def mat(name, color, rough=0.88, spec=0.05):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        if not m.use_nodes:
            m.use_nodes = True
        nodes = m.node_tree.nodes
        b = nodes.get("Principled BSDF") or nodes.new("ShaderNodeBsdfPrincipled")
        b.inputs["Base Color"].default_value = color
        b.inputs["Roughness"].default_value  = rough
        for k in ("Specular IOR Level", "Specular"):
            if k in b.inputs:
                b.inputs[k].default_value = spec; break
        return m

    # ── Wipe scene ────────────────────────────────────────────────────────────
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Ensure we have a valid scene & view layer
    scene = bpy.context.scene
    vl    = bpy.context.view_layer

    # ── Materials ─────────────────────────────────────────────────────────────
    M_BODY   = mat("M_Body",   CREAM)
    M_ACCENT = mat("M_Accent", PEACH)
    M_BLUSH  = mat("M_Blush",  BLUSH,  rough=0.95)
    M_EYE    = mat("M_Eye",    BROWN,  rough=0.50, spec=0.3)
    M_MOUTH  = mat("M_Mouth",  MOUTH)
    M_WHITE  = mat("M_White",  WHITE,  rough=0.75)

    # ── Helper: sphere ────────────────────────────────────────────────────────
    def sphere(name, radius, loc, scale=(1,1,1), mat_ref=None):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24, ring_count=16, radius=radius, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear()
            obj.data.materials.append(mat_ref)
        return obj

    # ── Build Golumolu ────────────────────────────────────────────────────────
    print("Building Golumolu mesh …")
    body   = sphere("Golumolu_Body", 1.0, (0,0,0),            (1.00,0.92,0.88), M_BODY)

    ear_r  = sphere("Ear_R",   0.28, ( 0.72,-0.15, 0.78),    (0.90,0.70,1.00), M_ACCENT)
    ear_l  = sphere("Ear_L",   0.28, (-0.72,-0.15, 0.78),    (0.90,0.70,1.00), M_ACCENT)
    iear_r = sphere("EarIn_R", 0.14, ( 0.72,-0.30, 0.80),    (0.90,0.28,0.90), M_BLUSH)
    iear_l = sphere("EarIn_L", 0.14, (-0.72,-0.30, 0.80),    (0.90,0.28,0.90), M_BLUSH)

    chk_r  = sphere("Cheek_R", 0.22, ( 0.52,-0.93, 0.00),    (1.00,0.22,0.65), M_BLUSH)
    chk_l  = sphere("Cheek_L", 0.22, (-0.52,-0.93, 0.00),    (1.00,0.22,0.65), M_BLUSH)

    ewh_r  = sphere("EyeWh_R", 0.14, ( 0.32,-0.96, 0.22),    (1.00,0.28,0.90), M_WHITE)
    ewh_l  = sphere("EyeWh_L", 0.14, (-0.32,-0.96, 0.22),    (1.00,0.28,0.90), M_WHITE)
    pup_r  = sphere("Pupil_R", 0.09, ( 0.32,-1.02, 0.22),    (1.00,0.22,0.90), M_EYE)
    pup_l  = sphere("Pupil_L", 0.09, (-0.32,-1.02, 0.22),    (1.00,0.22,0.90), M_EYE)

    nose   = sphere("Nose",    0.07, (0.00, -1.02, 0.04),    (1.00,0.38,0.70), M_EYE)
    mouth  = sphere("Mouth",   0.14, (0.00, -1.02,-0.15),    (1.00,0.28,0.55), M_MOUTH)
    tail   = sphere("Tail",    0.18, (0.00,  0.96,-0.10),    (0.80,0.90,0.80), M_BODY)

    arm_r  = sphere("Arm_R",   0.22, ( 1.00,-0.20,-0.30),    (0.60,0.55,0.55), M_ACCENT)
    arm_l  = sphere("Arm_L",   0.22, (-1.00,-0.20,-0.30),    (0.60,0.55,0.55), M_ACCENT)
    foot_r = sphere("Foot_R",  0.22, ( 0.42,-0.10,-0.93),    (0.55,0.50,0.42), M_ACCENT)
    foot_l = sphere("Foot_L",  0.22, (-0.42,-0.10,-0.93),    (0.55,0.50,0.42), M_ACCENT)

    parts = [ear_r, ear_l, iear_r, iear_l, chk_r, chk_l,
             ewh_r, ewh_l, pup_r, pup_l, nose, mouth, tail,
             arm_r, arm_l, foot_r, foot_l]

    # Collection
    col = bpy.data.collections.new("Golumolu")
    scene.collection.children.link(col)
    for obj in [body] + parts:
        for c2 in list(obj.users_collection):
            c2.objects.unlink(obj)
        col.objects.link(obj)
    for p in parts:
        p.parent = body

    print("Mesh built – setting up lighting …")

    # ── Lighting ──────────────────────────────────────────────────────────────
    bpy.ops.object.light_add(type='AREA', location=(2.5,-2.5, 3.0))
    key = bpy.context.active_object; key.name="Light_Key"
    key.data.energy=300; key.data.color=(1.0,0.95,0.85); key.data.size=2.0
    key.rotation_euler=(math.radians(50), 0, math.radians(30))

    bpy.ops.object.light_add(type='AREA', location=(-2.0,-1.5, 1.5))
    fill = bpy.context.active_object; fill.name="Light_Fill"
    fill.data.energy=100; fill.data.color=(0.90,0.95,1.0); fill.data.size=3.0

    # Rim
    bpy.ops.object.light_add(type='AREA', location=(0.0, 2.0, 2.0))
    rim = bpy.context.active_object; rim.name="Light_Rim"
    rim.data.energy=60; rim.data.color=(1.0,0.98,0.92); rim.data.size=1.5

    # World
    world = bpy.data.worlds.new("World_Golumolu")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value   = hex_rgba("#FFF3E8")
        bg.inputs["Strength"].default_value = 1.0

    # ── Render settings – Cycles CPU (background-safe) ───────────────────────
    scene.render.engine        = 'CYCLES'
    scene.cycles.device        = 'CPU'
    scene.cycles.samples       = 64
    scene.cycles.preview_samples = 32
    scene.render.resolution_x  = 1024
    scene.render.resolution_y  = 1024
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True

    RAD = math.radians

    VIEWS = [
        ("front",  (0,   -4.5,  0),   (RAD(90), 0, 0)),
        ("34view", (3.0, -3.5,  1.2), (RAD(72), 0, RAD(40))),
        ("side",   (4.5,  0,    0),   (RAD(90), 0, RAD(90))),
        ("back",   (0,    4.5,  0),   (RAD(90), 0, RAD(180))),
    ]

    print("Starting renders …")
    for name, loc, rot in VIEWS:
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object
        cam.name = f"Cam_{name}"
        cam.rotation_euler = rot
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 2.8
        scene.camera = cam
        out = os.path.join(RENDER_DIR, f"golumolu_{name}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ Rendered: {out}")

    # ── Save .blend ───────────────────────────────────────────────────────────
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved blend: {BLEND_PATH}")

    # ── Export FBX ───────────────────────────────────────────────────────────
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)

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
    print(f"Exported FBX: {FBX_PATH}")
    print("=== Golumolu build COMPLETE ===")

except Exception:
    traceback.print_exc()
    sys.exit(1)
