"""
MOMO MAZE – Golumolu v002 (QA Corrected)
==========================================
Fixes from v001 QA review:
  1. Eyes → crescent/arc happy shape (flattened ellipse, not round dots)
  2. Mouth → wider (scale X x1.4), pushed forward
  3. Cheeks → moved below eye line (Z -0.10)
  4. Inner ear → pushed Y forward by 0.05
  5. Warmer lighting — orange key, warm fill, no cool bounce
  6. Body color pushed warmer (Roughness bump, ambient warmth)
"""

import bpy, bmesh, math, os, sys, traceback

try:
    THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
    ROOT       = os.path.abspath(os.path.join(THIS_DIR, ".."))
    SCENE_DIR  = os.path.join(ROOT, "scenes");   os.makedirs(SCENE_DIR,  exist_ok=True)
    FBX_DIR    = os.path.join(ROOT, "exports", "fbx"); os.makedirs(FBX_DIR, exist_ok=True)
    RENDER_DIR = os.path.join(ROOT, "renders", "golumolu"); os.makedirs(RENDER_DIR, exist_ok=True)

    BLEND_PATH = os.path.join(SCENE_DIR,  "golumolu_v002.blend")
    FBX_PATH   = os.path.join(FBX_DIR,    "golumolu_v002.fbx")

    # ── Color helpers ─────────────────────────────────────────────────────────
    def srgb(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    def hex_rgba(h):
        h = h.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (srgb(r), srgb(g), srgb(b), 1.0)

    CREAM = hex_rgba("#FCEEDD")
    PEACH = hex_rgba("#FFC189")
    BLUSH = hex_rgba("#FFB3B0")
    BROWN = hex_rgba("#6B4226")
    MOUTH = hex_rgba("#E27567")
    WHITE = (1.0, 1.0, 1.0, 1.0)
    RAD = math.radians

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
    scene = bpy.context.scene

    # ── Materials ─────────────────────────────────────────────────────────────
    M_BODY   = mat("M_Body",   CREAM, rough=0.92)
    M_ACCENT = mat("M_Accent", PEACH, rough=0.86)
    M_BLUSH  = mat("M_Blush",  BLUSH, rough=0.95)
    M_EYE    = mat("M_Eye",    BROWN, rough=0.45, spec=0.4)
    M_MOUTH  = mat("M_Mouth",  MOUTH, rough=0.88)
    M_WHITE  = mat("M_White",  WHITE, rough=0.70, spec=0.2)

    # ── Helper: UV sphere ─────────────────────────────────────────────────────
    def sphere(name, radius, loc, scale=(1,1,1), mat_ref=None, segs=24, rings=16):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=segs, ring_count=rings, radius=radius, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear()
            obj.data.materials.append(mat_ref)
        return obj

    # ── Helper: crescent eye using boolean-subtracted sphere ──────────────────
    def crescent_eye(name, loc, side):
        """
        Build a happy crescent / arc eye:
        - Flat dark brown ellipse representing closed-happy eye arc.
        We approximate the crescent with a heavily squashed sphere
        (very flat in Z so it reads as a horizontal arc from the front).
        """
        # Main eye disc — dark brown, very flat
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20, ring_count=12, radius=0.13, location=loc)
        eye = bpy.context.active_object
        eye.name = name
        # Flatten into a wide horizontal oval — the "happy squint" arc
        eye.scale = (1.4, 0.22, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        # Tilt slightly: outer corner up for the happy look
        eye.rotation_euler = (0, 0, side * RAD(-8))
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.clear()
        eye.data.materials.append(M_EYE)
        return eye

    # ── Build Golumolu v002 ───────────────────────────────────────────────────
    print("=== Golumolu v002 build starting ===")

    # Body – main cream sphere
    body = sphere("Golumolu_Body", 1.0, (0,0,0), (1.00, 0.92, 0.88), M_BODY, segs=32, rings=24)

    # Ears (peach nubs, upper sides)
    ear_r  = sphere("Ear_R",   0.28, ( 0.72,-0.15, 0.78), (0.90,0.70,1.00), M_ACCENT)
    ear_l  = sphere("Ear_L",   0.28, (-0.72,-0.15, 0.78), (0.90,0.70,1.00), M_ACCENT)

    # Inner ear blush – pushed forward (Y −0.33 instead of −0.30)
    iear_r = sphere("EarIn_R", 0.14, ( 0.72,-0.33, 0.80), (0.90,0.28,0.90), M_BLUSH)
    iear_l = sphere("EarIn_L", 0.14, (-0.72,-0.33, 0.80), (0.90,0.28,0.90), M_BLUSH)

    # Cheeks – moved down to Z=−0.12 (below eye line, at jaw level per concept)
    chk_r  = sphere("Cheek_R", 0.22, ( 0.52,-0.93,-0.12), (1.00,0.22,0.65), M_BLUSH)
    chk_l  = sphere("Cheek_L", 0.22, (-0.52,-0.93,-0.12), (1.00,0.22,0.65), M_BLUSH)

    # Eyes – CRESCENT SHAPE (v002 fix: happy arc, not round dots)
    eye_r = crescent_eye("Eye_R", ( 0.33,-0.95, 0.24),  1)
    eye_l = crescent_eye("Eye_L", (-0.33,-0.95, 0.24), -1)

    # Small eye-shine dots (white) – add sparkle
    shi_r = sphere("Shine_R", 0.04, ( 0.37,-0.99, 0.30), (1.0,0.5,1.0), M_WHITE)
    shi_l = sphere("Shine_L", 0.04, (-0.37,-0.99, 0.30), (1.0,0.5,1.0), M_WHITE)

    # Nose – small brown nub
    nose  = sphere("Nose",    0.07, (0.00,-1.02, 0.04), (1.00,0.38,0.70), M_EYE)

    # Mouth – v002 fix: wider (X×1.4) and pushed further forward
    mouth = sphere("Mouth",   0.14, (0.00,-1.05,-0.16), (1.40,0.28,0.55), M_MOUTH)

    # Tail nub (back)
    tail  = sphere("Tail",    0.18, (0.00, 0.96,-0.10), (0.80,0.90,0.80), M_BODY)

    # Arms (tiny peach nubs at mid-sides)
    arm_r  = sphere("Arm_R",  0.22, ( 1.00,-0.20,-0.30), (0.60,0.55,0.55), M_ACCENT)
    arm_l  = sphere("Arm_L",  0.22, (-1.00,-0.20,-0.30), (0.60,0.55,0.55), M_ACCENT)

    # Feet (slightly larger, more splayed)
    foot_r = sphere("Foot_R", 0.23, ( 0.44,-0.08,-0.94), (0.60,0.52,0.42), M_ACCENT)
    foot_l = sphere("Foot_L", 0.23, (-0.44,-0.08,-0.94), (0.60,0.52,0.42), M_ACCENT)

    parts = [
        ear_r, ear_l, iear_r, iear_l,
        chk_r, chk_l,
        eye_r, eye_l, shi_r, shi_l,
        nose, mouth, tail,
        arm_r, arm_l, foot_r, foot_l,
    ]

    # Collection & parenting
    col = bpy.data.collections.new("Golumolu")
    scene.collection.children.link(col)
    for obj in [body] + parts:
        for c2 in list(obj.users_collection):
            c2.objects.unlink(obj)
        col.objects.link(obj)
    for p in parts:
        p.parent = body

    print("Mesh built – v002 corrections applied.")

    # ── Warm lighting (v002 fix) ──────────────────────────────────────────────
    # Key – warm golden-hour light from upper-front-right
    bpy.ops.object.light_add(type='AREA', location=(2.5,-2.5, 3.0))
    key = bpy.context.active_object; key.name="Light_Key"
    key.data.energy = 350
    key.data.color  = (1.0, 0.92, 0.75)   # warm amber
    key.data.size   = 2.0
    key.rotation_euler = (RAD(50), 0, RAD(30))

    # Fill – warm peach bounce (no cool blue)
    bpy.ops.object.light_add(type='AREA', location=(-1.5,-1.0, 1.0))
    fill = bpy.context.active_object; fill.name="Light_Fill"
    fill.data.energy = 120
    fill.data.color  = (1.0, 0.88, 0.75)   # warm peach
    fill.data.size   = 3.5

    # Rim – soft warm from behind-top
    bpy.ops.object.light_add(type='AREA', location=(0.0, 2.5, 2.5))
    rim = bpy.context.active_object; rim.name="Light_Rim"
    rim.data.energy = 60
    rim.data.color  = (1.0, 0.95, 0.85)
    rim.data.size   = 2.0

    # World – warm cream ambient
    world = bpy.data.worlds.new("World_v002")
    scene.world = world
    if not world.use_nodes:
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value   = hex_rgba("#FFE8CC")   # warmer cream
        bg.inputs["Strength"].default_value = 0.9

    # ── Render settings ───────────────────────────────────────────────────────
    scene.render.engine        = 'CYCLES'
    scene.cycles.device        = 'CPU'
    scene.cycles.samples       = 96
    scene.render.resolution_x  = 1024
    scene.render.resolution_y  = 1024
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True

    VIEWS = [
        ("front",  (0,   -4.5,  0.0), (RAD(90),    0,        0)),
        ("34view", (3.2, -3.2,  0.8), (RAD(74),    0, RAD(42))),
        ("side",   (4.5,  0.0,  0.0), (RAD(90),    0, RAD(90))),
        ("back",   (0.0,  4.5,  0.0), (RAD(90),    0, RAD(180))),
    ]

    print("Rendering 4 validation views …")
    for vname, loc, rot in VIEWS:
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object
        cam.name = f"Cam_{vname}"
        cam.rotation_euler = rot
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 2.8
        scene.camera = cam
        out = os.path.join(RENDER_DIR, f"golumolu_v002_{vname}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ {vname}: {out}")

    # ── Save + Export ─────────────────────────────────────────────────────────
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")

    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=FBX_PATH, use_selection=True,
        global_scale=1.0, apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Z', axis_up='Y',
        mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
        add_leaf_bones=False,
    )
    print(f"FBX: {FBX_PATH}")
    print("=== Golumolu v002 COMPLETE ===")

except Exception:
    import traceback; traceback.print_exc()
    sys.exit(1)
