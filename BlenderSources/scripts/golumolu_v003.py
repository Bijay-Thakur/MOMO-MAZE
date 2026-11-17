"""
MOMO MAZE – Golumolu v003 (Expression Fix)
===========================================
Key fixes from v002 QA:
  1. Eyes: proper happy OPEN eyes — white sclera + brown iris/pupil
     The concept shows OPEN round eyes with shine, NOT closed crescents.
     Golumolu's "happy" expression = wide open round eyes with downward
     eyelid curve at top (Principled happy = open, not squinting).
  2. Eyes spaced wider apart, positioned higher on face
  3. Mouth: wider open shape, slightly lower, inner pink visible
  4. Eyebrow arcs above eyes (subtle dark brown) for expression
  5. Keep all v002 warmth and cheek improvements
"""

import bpy, math, os, sys

try:
    THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
    ROOT       = os.path.abspath(os.path.join(THIS_DIR, ".."))
    SCENE_DIR  = os.path.join(ROOT, "scenes");   os.makedirs(SCENE_DIR,  exist_ok=True)
    FBX_DIR    = os.path.join(ROOT, "exports", "fbx"); os.makedirs(FBX_DIR, exist_ok=True)
    RENDER_DIR = os.path.join(ROOT, "renders", "golumolu"); os.makedirs(RENDER_DIR, exist_ok=True)

    BLEND_PATH = os.path.join(SCENE_DIR,  "golumolu_v003.blend")
    FBX_PATH   = os.path.join(FBX_DIR,    "golumolu_v003.fbx")

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

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    M_BODY   = mat("M_Body",   CREAM, rough=0.92)
    M_ACCENT = mat("M_Accent", PEACH, rough=0.86)
    M_BLUSH  = mat("M_Blush",  BLUSH, rough=0.95)
    M_EYE    = mat("M_Eye",    BROWN, rough=0.45, spec=0.4)
    M_MOUTH  = mat("M_Mouth",  MOUTH, rough=0.88)
    M_WHITE  = mat("M_White",  WHITE, rough=0.65, spec=0.3)
    M_SHINE  = mat("M_Shine",  WHITE, rough=0.20, spec=0.8)

    def sphere(name, radius, loc, scale=(1,1,1), mat_ref=None, segs=24, rings=16):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=segs, ring_count=rings, radius=radius, location=loc)
        obj = bpy.context.active_object
        obj.name = name; obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear()
            obj.data.materials.append(mat_ref)
        return obj

    # ── BUILD GOLUMOLU v003 ───────────────────────────────────────────────────
    print("=== Golumolu v003 build starting ===")

    # Body
    body = sphere("Golumolu_Body", 1.0, (0,0,0), (1.00,0.92,0.88), M_BODY, segs=32, rings=24)

    # Ears (peach, top-sides)
    ear_r  = sphere("Ear_R",   0.28, ( 0.72,-0.15, 0.78), (0.90,0.70,1.00), M_ACCENT)
    ear_l  = sphere("Ear_L",   0.28, (-0.72,-0.15, 0.78), (0.90,0.70,1.00), M_ACCENT)
    # Inner ear blush
    iear_r = sphere("EarIn_R", 0.14, ( 0.72,-0.33, 0.80), (0.90,0.28,0.90), M_BLUSH)
    iear_l = sphere("EarIn_L", 0.14, (-0.72,-0.33, 0.80), (0.90,0.28,0.90), M_BLUSH)

    # Cheeks at jaw level (v002 fix kept)
    chk_r  = sphere("Cheek_R", 0.22, ( 0.52,-0.93,-0.12), (1.00,0.22,0.65), M_BLUSH)
    chk_l  = sphere("Cheek_L", 0.22, (-0.52,-0.93,-0.12), (1.00,0.22,0.65), M_BLUSH)

    # ── EYES v003: OPEN round eyes (concept-accurate) ─────────────────────────
    # The concept shows Golumolu with WIDE OPEN happy eyes:
    # large white sclera sphere + brown iris overlay + tiny white shine dot
    # Eyes spaced wider: X ±0.38 (was ±0.33), higher: Z 0.28 (was 0.24)
    EYE_X = 0.38; EYE_Y = -0.94; EYE_Z = 0.28

    # Sclera (white, full round)
    ewh_r = sphere("EyeWh_R", 0.145, ( EYE_X, EYE_Y, EYE_Z), (1.00,0.32,1.05), M_WHITE)
    ewh_l = sphere("EyeWh_L", 0.145, (-EYE_X, EYE_Y, EYE_Z), (1.00,0.32,1.05), M_WHITE)

    # Iris/Pupil (brown, slightly smaller, sits in front of sclera)
    pup_r = sphere("Pupil_R", 0.11, ( EYE_X, EYE_Y-0.04, EYE_Z), (1.00,0.28,1.00), M_EYE)
    pup_l = sphere("Pupil_L", 0.11, (-EYE_X, EYE_Y-0.04, EYE_Z), (1.00,0.28,1.00), M_EYE)

    # Shine dots (white highlight — the "sparkle")
    shi_r = sphere("Shine_R", 0.038, ( EYE_X+0.04, EYE_Y-0.07, EYE_Z+0.05), mat_ref=M_SHINE)
    shi_l = sphere("Shine_L", 0.038, (-EYE_X+0.04, EYE_Y-0.07, EYE_Z+0.05), mat_ref=M_SHINE)

    # Eyelid curve: thin dark brown arc at top of each eye (the happy curve)
    # Approximated as a very flat squashed sphere at the TOP of the eye
    lid_r = sphere("Lid_R", 0.12, ( EYE_X, EYE_Y-0.045, EYE_Z+0.09), (1.10,0.22,0.35), M_EYE)
    lid_l = sphere("Lid_L", 0.12, (-EYE_X, EYE_Y-0.045, EYE_Z+0.09), (1.10,0.22,0.35), M_EYE)

    # ── NOSE ─────────────────────────────────────────────────────────────────
    nose  = sphere("Nose", 0.07, (0.00,-1.02, 0.04), (1.00,0.38,0.70), M_EYE)

    # ── MOUTH v003: wider open, happy curve ───────────────────────────────────
    # Main pink oval (wider, pushed forward, slightly larger)
    mouth = sphere("Mouth", 0.17, (0.00,-1.06,-0.17), (1.50,0.30,0.60), M_MOUTH)
    # Lower lip nub
    llip  = sphere("LowerLip", 0.08, (0.00,-1.04,-0.27), (1.20,0.30,0.45), M_ACCENT)

    # ── TAIL NUB (back) ───────────────────────────────────────────────────────
    tail  = sphere("Tail", 0.18, (0.00, 0.96,-0.10), (0.80,0.90,0.80), M_BODY)

    # ── ARMS ─────────────────────────────────────────────────────────────────
    arm_r  = sphere("Arm_R",  0.22, ( 1.00,-0.20,-0.30), (0.60,0.55,0.55), M_ACCENT)
    arm_l  = sphere("Arm_L",  0.22, (-1.00,-0.20,-0.30), (0.60,0.55,0.55), M_ACCENT)

    # ── FEET ─────────────────────────────────────────────────────────────────
    foot_r = sphere("Foot_R", 0.23, ( 0.44,-0.08,-0.94), (0.60,0.52,0.42), M_ACCENT)
    foot_l = sphere("Foot_L", 0.23, (-0.44,-0.08,-0.94), (0.60,0.52,0.42), M_ACCENT)

    parts = [
        ear_r, ear_l, iear_r, iear_l,
        chk_r, chk_l,
        ewh_r, ewh_l, pup_r, pup_l, shi_r, shi_l, lid_r, lid_l,
        nose, mouth, llip, tail,
        arm_r, arm_l, foot_r, foot_l,
    ]

    # Collection
    col = bpy.data.collections.new("Golumolu")
    scene.collection.children.link(col)
    for obj in [body] + parts:
        for c2 in list(obj.users_collection):
            c2.objects.unlink(obj)
        col.objects.link(obj)
    for p in parts:
        p.parent = body

    print("Mesh built – open eyes, wider spacing.")

    # ── LIGHTING (keep v002 warmth) ───────────────────────────────────────────
    bpy.ops.object.light_add(type='AREA', location=(2.5,-2.5, 3.0))
    key = bpy.context.active_object; key.name="Light_Key"
    key.data.energy=350; key.data.color=(1.0,0.92,0.75); key.data.size=2.0
    key.rotation_euler=(RAD(50), 0, RAD(30))

    bpy.ops.object.light_add(type='AREA', location=(-1.5,-1.0, 1.0))
    fill = bpy.context.active_object; fill.name="Light_Fill"
    fill.data.energy=120; fill.data.color=(1.0,0.88,0.75); fill.data.size=3.5

    bpy.ops.object.light_add(type='AREA', location=(0.0, 2.5, 2.5))
    rim = bpy.context.active_object; rim.name="Light_Rim"
    rim.data.energy=60; rim.data.color=(1.0,0.95,0.85); rim.data.size=2.0

    world = bpy.data.worlds.new("World_v003")
    scene.world = world
    if not world.use_nodes:
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value   = hex_rgba("#FFE8CC")
        bg.inputs["Strength"].default_value = 0.9

    # ── RENDER SETTINGS ───────────────────────────────────────────────────────
    scene.render.engine        = 'CYCLES'
    scene.cycles.device        = 'CPU'
    scene.cycles.samples       = 128
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

    print("Rendering 4 views …")
    for vname, loc, rot in VIEWS:
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object
        cam.name = f"Cam_{vname}"
        cam.rotation_euler = rot
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 2.8
        scene.camera = cam
        out = os.path.join(RENDER_DIR, f"golumolu_v003_{vname}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ {vname}")

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
        use_mesh_modifiers=True, add_leaf_bones=False,
    )
    print(f"FBX: {FBX_PATH}")
    print("=== Golumolu v003 COMPLETE ===")

except Exception:
    import traceback; traceback.print_exc()
    sys.exit(1)
