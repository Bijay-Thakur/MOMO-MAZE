"""
MOMO MAZE – Ghost Spirits Build Script
========================================
Builds Follower, Cutter, and Wanderer ghosts in one Blender scene.
Run as: blender --background --python ghosts_bg.py

Outputs:
  BlenderSources/scenes/ghosts_v001.blend
  BlenderSources/exports/fbx/ghost_{follower,cutter,wanderer}_v001.fbx
  BlenderSources/renders/ghosts/ghost_{name}_{front,side,34view}.png
"""

import bpy, math, os, sys, traceback

try:
    THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
    ROOT       = os.path.abspath(os.path.join(THIS_DIR, ".."))
    SCENE_DIR  = os.path.join(ROOT, "scenes");   os.makedirs(SCENE_DIR,  exist_ok=True)
    FBX_DIR    = os.path.join(ROOT, "exports", "fbx"); os.makedirs(FBX_DIR, exist_ok=True)
    RENDER_DIR = os.path.join(ROOT, "renders", "ghosts"); os.makedirs(RENDER_DIR, exist_ok=True)

    BLEND_PATH = os.path.join(SCENE_DIR, "ghosts_v001.blend")

    # ── Color helpers ─────────────────────────────────────────────────────────
    def srgb(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    def hex_rgba(h):
        h = h.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (srgb(r), srgb(g), srgb(b), 1.0)

    GHOST_WHITE  = hex_rgba("#FFF7EE")
    GHOST_GLOW   = hex_rgba("#FFDFA8")
    EYE_DARK     = hex_rgba("#3D2B1F")
    BLUSH_PINK   = hex_rgba("#FFB3B0")

    # ── Material factory ──────────────────────────────────────────────────────
    def mat(name, color, rough=0.85, spec=0.05, emit=None, alpha=1.0):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        if not m.use_nodes:
            m.use_nodes = True
        nodes  = m.node_tree.nodes
        links  = m.node_tree.links
        # Clear and rebuild
        nodes.clear()
        out  = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value  = color
        bsdf.inputs["Roughness"].default_value   = rough
        for k in ("Specular IOR Level", "Specular"):
            if k in bsdf.inputs:
                bsdf.inputs[k].default_value = spec; break
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if emit:
            for k in ("Emission Color", "Emission"):
                if k in bsdf.inputs:
                    bsdf.inputs[k].default_value = emit; break
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 0.3
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        if alpha < 1.0:
            m.blend_method = 'BLEND'
        return m

    # ── Wipe scene ────────────────────────────────────────────────────────────
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # ── Shared materials ─────────────────────────────────────────────────────
    M_GHOST_BODY  = mat("M_Ghost_Body",  GHOST_WHITE,  rough=0.88, emit=(1.0, 0.95, 0.85, 1.0))
    M_GHOST_TAIL  = mat("M_Ghost_Tail",  GHOST_WHITE,  rough=0.90, alpha=0.45)
    M_GHOST_EYE   = mat("M_Ghost_Eye",   EYE_DARK,     rough=0.40, spec=0.5)
    M_GHOST_BLUSH = mat("M_Ghost_Blush", BLUSH_PINK,   rough=0.95)
    M_GHOST_GLOW  = mat("M_Ghost_Glow",  GHOST_GLOW,   rough=0.60, emit=(*GHOST_GLOW[:3], 1.0))

    # ── Helper: sphere ────────────────────────────────────────────────────────
    def sphere(name, radius, loc, scale=(1,1,1), mat_ref=None):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20, ring_count=14, radius=radius, location=loc)
        obj = bpy.context.active_object; obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear(); obj.data.materials.append(mat_ref)
        return obj

    def cone(name, radius1, radius2, depth, loc, scale=(1,1,1), mat_ref=None):
        bpy.ops.mesh.primitive_cone_add(
            vertices=16, radius1=radius1, radius2=radius2,
            depth=depth, location=loc)
        obj = bpy.context.active_object; obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear(); obj.data.materials.append(mat_ref)
        return obj

    # ── Ghost builder ─────────────────────────────────────────────────────────
    def build_ghost(prefix, offset_x, eye_style, has_blush):
        """Build one ghost at x=offset_x. eye_style: 'friendly'|'stern'|'wide'"""
        base = offset_x

        # Head (main fluffy sphere)
        head = sphere(f"{prefix}_Head", 0.55, (base, 0, 0.55), (1.0, 0.95, 1.0), M_GHOST_BODY)

        # Tail (tapered cone, translucent)
        tail = cone(f"{prefix}_Tail", 0.50, 0.05, 1.1, (base, 0, -0.25),
                    (1.0, 0.85, 1.0), M_GHOST_TAIL)

        # Eyes (personality-specific)
        if eye_style == 'friendly':
            # Simple round dots
            ey_r = sphere(f"{prefix}_EyeR", 0.09, (base+0.17, -0.52, 0.60),
                          (1.0, 0.5, 0.9), M_GHOST_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.09, (base-0.17, -0.52, 0.60),
                          (1.0, 0.5, 0.9), M_GHOST_EYE)
        elif eye_style == 'stern':
            # Angled / narrower eyes
            ey_r = sphere(f"{prefix}_EyeR", 0.09, (base+0.18, -0.50, 0.58),
                          (1.3, 0.4, 0.8), M_GHOST_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.09, (base-0.18, -0.50, 0.58),
                          (1.3, 0.4, 0.8), M_GHOST_EYE)
            # Frown brow bumps
            br_r = sphere(f"{prefix}_BrowR", 0.05, (base+0.18, -0.56, 0.68),
                          (1.5, 0.5, 0.5), M_GHOST_EYE)
            br_l = sphere(f"{prefix}_BrowL", 0.05, (base-0.18, -0.56, 0.68),
                          (1.5, 0.5, 0.5), M_GHOST_EYE)
            br_r.rotation_euler = (0, 0, math.radians(-15))
            br_l.rotation_euler = (0, 0, math.radians(15))
        else:  # wide / whimsical
            ey_r = sphere(f"{prefix}_EyeR", 0.11, (base+0.18, -0.50, 0.60),
                          (1.0, 0.45, 1.05), M_GHOST_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.11, (base-0.18, -0.50, 0.60),
                          (1.0, 0.45, 1.05), M_GHOST_EYE)
            # Star highlight
            hi_r = sphere(f"{prefix}_HiR", 0.03, (base+0.21, -0.56, 0.64), mat_ref=M_GHOST_GLOW)
            hi_l = sphere(f"{prefix}_HiL", 0.03, (base-0.21, -0.56, 0.64), mat_ref=M_GHOST_GLOW)

        # Blush cheeks (Follower + Wanderer)
        if has_blush:
            chk_r = sphere(f"{prefix}_ChkR", 0.09, (base+0.32, -0.47, 0.44),
                           (1.0, 0.25, 0.65), M_GHOST_BLUSH)
            chk_l = sphere(f"{prefix}_ChkL", 0.09, (base-0.32, -0.47, 0.44),
                           (1.0, 0.25, 0.65), M_GHOST_BLUSH)

        # Collect into one collection
        col = bpy.data.collections.new(prefix)
        scene.collection.children.link(col)
        for obj in bpy.context.scene.objects:
            if obj.name.startswith(prefix):
                for c2 in list(obj.users_collection):
                    c2.objects.unlink(obj)
                col.objects.link(obj)
                if obj != head:
                    obj.parent = head

        return head, col

    # ── Build all three ghosts side by side ───────────────────────────────────
    print("Building ghosts …")
    follower_head, follower_col = build_ghost("Follower", -3.5, 'friendly',  True)
    cutter_head,   cutter_col   = build_ghost("Cutter",    0.0, 'stern',    False)
    wanderer_head, wanderer_col = build_ghost("Wanderer",  3.5, 'wide',      True)

    # ── Lighting ──────────────────────────────────────────────────────────────
    bpy.ops.object.light_add(type='AREA', location=(0, -4, 3))
    key = bpy.context.active_object; key.name="GhostKey"
    key.data.energy=250; key.data.color=(1.0,0.97,0.90); key.data.size=4.0
    key.rotation_euler=(math.radians(55), 0, 0)

    bpy.ops.object.light_add(type='AREA', location=(0, 2, 2))
    rim = bpy.context.active_object; rim.name="GhostRim"
    rim.data.energy=80; rim.data.color=(0.9,0.95,1.0); rim.data.size=3.0

    world = bpy.data.worlds.new("GhostWorld")
    scene.world = world
    if not world.use_nodes:
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value   = hex_rgba("#FFF3E8")
        bg.inputs["Strength"].default_value = 0.8

    # ── Render settings ───────────────────────────────────────────────────────
    scene.render.engine        = 'CYCLES'
    scene.cycles.device        = 'CPU'
    scene.cycles.samples       = 64
    scene.render.resolution_x  = 1600
    scene.render.resolution_y  = 700
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True

    RAD = math.radians

    GHOST_VIEWS = [
        ("lineup", (0, -6, 0.5), (RAD(90), 0, 0), 10.0),
    ]

    for name, loc, rot, ortho_scale in GHOST_VIEWS:
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object; cam.name = f"Cam_{name}"
        cam.rotation_euler = rot
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = ortho_scale
        scene.camera = cam
        out = os.path.join(RENDER_DIR, f"ghosts_{name}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ {out}")

    # Individual ghost renders
    for ghost_name, head_obj, col_obj in [
        ("follower", follower_head, follower_col),
        ("cutter",   cutter_head,  cutter_col),
        ("wanderer", wanderer_head, wanderer_col),
    ]:
        cx, cy, cz = head_obj.location
        for view, loc_off, rot in [
            ("front", (0, -2.5, 0),   (RAD(90), 0, 0)),
            ("side",  (2.5, 0,  0),   (RAD(90), 0, RAD(90))),
            ("34",    (1.8,-1.8, 0.5),(RAD(75), 0, RAD(35))),
        ]:
            bpy.ops.object.camera_add(location=(
                cx + loc_off[0], cy + loc_off[1], cz + loc_off[2]))
            cam = bpy.context.active_object
            cam.name = f"Cam_{ghost_name}_{view}"
            cam.rotation_euler = rot
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = 1.8
            scene.camera = cam
            scene.render.resolution_x = 512
            scene.render.resolution_y = 512
            out = os.path.join(RENDER_DIR, f"ghost_{ghost_name}_{view}.png")
            scene.render.filepath = out
            bpy.ops.render.render(write_still=True)
            print(f"  ✓ {out}")

    # ── Save + FBX export ─────────────────────────────────────────────────────
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")

    for ghost_name, col_obj in [
        ("follower", follower_col),
        ("cutter",   cutter_col),
        ("wanderer", wanderer_col),
    ]:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in col_obj.objects:
            obj.select_set(True)
        fbx_path = os.path.join(FBX_DIR, f"ghost_{ghost_name}_v001.fbx")
        bpy.ops.export_scene.fbx(
            filepath=fbx_path, use_selection=True,
            axis_forward='-Z', axis_up='Y', add_leaf_bones=False)
        print(f"  FBX: {fbx_path}")

    print("=== Ghost build COMPLETE ===")

except Exception:
    traceback.print_exc()
    sys.exit(1)
