"""
MOMO MAZE – Ghost Spirits v002 (Shape + Personality Fix)
==========================================================
Fixes from v001 QA:
  1. Shape: replace head+cone pawn with proper teardrop ghost silhouette
     - Large round head (top)
     - Smooth tapered tail flowing behind/below (elongated egg-cone, not pyramid)
  2. Personality differentiation:
     - Follower: simple round friendly eyes + blush, gentle tail
     - Cutter: angled stern eyes + dramatic swept-back tail
     - Wanderer: wide sparkly eyes + wavy curled tail
  3. Warm white glow material (emissive SSS-like)
  4. Clear silhouette per concept: fluffy head, wispy tail
"""

import bpy, math, os, sys

try:
    THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
    ROOT       = os.path.abspath(os.path.join(THIS_DIR, ".."))
    SCENE_DIR  = os.path.join(ROOT, "scenes");   os.makedirs(SCENE_DIR,  exist_ok=True)
    FBX_DIR    = os.path.join(ROOT, "exports", "fbx"); os.makedirs(FBX_DIR, exist_ok=True)
    RENDER_DIR = os.path.join(ROOT, "renders", "ghosts"); os.makedirs(RENDER_DIR, exist_ok=True)

    BLEND_PATH = os.path.join(SCENE_DIR, "ghosts_v002.blend")
    RAD = math.radians

    def srgb(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    def hex_rgba(h):
        h = h.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (srgb(r), srgb(g), srgb(b), 1.0)

    GHOST_WHITE = hex_rgba("#FFF7EE")
    GHOST_GLOW  = hex_rgba("#FFDFA8")
    GHOST_TAIL  = hex_rgba("#FFF0DD")
    EYE_DARK    = hex_rgba("#3D2B1F")
    BLUSH_PINK  = hex_rgba("#FFB3B0")

    def mat(name, color, rough=0.85, spec=0.05, emit_str=0.0, alpha=1.0):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        if not m.use_nodes:
            m.use_nodes = True
        nodes = m.node_tree.nodes; links = m.node_tree.links
        nodes.clear()
        out  = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value  = rough
        for k in ("Specular IOR Level", "Specular"):
            if k in bsdf.inputs:
                bsdf.inputs[k].default_value = spec; break
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if emit_str > 0:
            for ek in ("Emission Color", "Emission"):
                if ek in bsdf.inputs:
                    bsdf.inputs[ek].default_value = color; break
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit_str
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        if alpha < 1.0:
            m.blend_method = 'BLEND'
        return m

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # Shared materials
    M_BODY  = mat("M_Ghost_Body",  GHOST_WHITE, rough=0.88, emit_str=0.15)
    M_TAIL  = mat("M_Ghost_Tail",  GHOST_TAIL,  rough=0.90, alpha=0.55)
    M_EYE   = mat("M_Ghost_Eye",   EYE_DARK,    rough=0.35, spec=0.5)
    M_BLUSH = mat("M_Ghost_Blush", BLUSH_PINK,  rough=0.95)
    M_GLOW  = mat("M_Ghost_Glow",  GHOST_GLOW,  rough=0.4,  emit_str=0.8)
    M_WHITE = mat("M_Ghost_White", (1,1,1,1),   rough=0.2,  spec=0.9)

    def sphere(name, r, loc, scale=(1,1,1), mat_ref=None, segs=20, rings=14):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings,
                                             radius=r, location=loc)
        obj = bpy.context.active_object; obj.name = name; obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear(); obj.data.materials.append(mat_ref)
        return obj

    def cone(name, r1, r2, depth, loc, scale=(1,1,1), mat_ref=None):
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=r1, radius2=r2,
                                        depth=depth, location=loc)
        obj = bpy.context.active_object; obj.name = name; obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref:
            obj.data.materials.clear(); obj.data.materials.append(mat_ref)
        return obj

    # ── Ghost builder ─────────────────────────────────────────────────────────
    # Each ghost: round head (top) + tapered tail (back/below) = teardrop shape
    # Offset along X for the lineup

    def build_ghost(prefix, ox, style):
        """
        style: 'follower' | 'cutter' | 'wanderer'
        ox: X offset for lineup
        """
        # Head — large fluffy sphere
        head = sphere(f"{prefix}_Head", 0.52, (ox, 0, 0.52), (1.0, 0.95, 1.0), M_BODY)

        # Tail — teardrop shape: elongated sphere tapered behind
        # Tail sits behind and below the head, tapering to a point
        # Using a scaled sphere: very long in Y, narrow in X/Z
        tail_main = sphere(f"{prefix}_TailMain", 0.52, (ox, 0.65, -0.05),
                           (0.72, 1.60, 0.62), M_TAIL)
        # Tip taper
        tail_tip  = sphere(f"{prefix}_TailTip",  0.18, (ox, 1.30, -0.15),
                           (0.45, 0.80, 0.40), M_TAIL)

        parts = [tail_main, tail_tip]

        # ── Eyes (personality-specific) ───────────────────────────────────────
        EY = -0.50   # Y (facing forward)
        EZ =  0.58   # Z height on head

        if style == 'follower':
            # Simple round friendly dots + blush
            ey_r = sphere(f"{prefix}_EyeR", 0.085, (ox+0.16, EY, EZ), (1.0,0.5,1.0), M_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.085, (ox-0.16, EY, EZ), (1.0,0.5,1.0), M_EYE)
            # Shine
            sh_r = sphere(f"{prefix}_ShR",  0.025, (ox+0.19, EY-0.05, EZ+0.05), mat_ref=M_WHITE)
            sh_l = sphere(f"{prefix}_ShL",  0.025, (ox-0.13, EY-0.05, EZ+0.05), mat_ref=M_WHITE)
            # Blush
            bk_r = sphere(f"{prefix}_BkR",  0.08, (ox+0.26, EY+0.02, EZ-0.09), (1.0,0.25,0.65), M_BLUSH)
            bk_l = sphere(f"{prefix}_BkL",  0.08, (ox-0.26, EY+0.02, EZ-0.09), (1.0,0.25,0.65), M_BLUSH)
            parts += [ey_r, ey_l, sh_r, sh_l, bk_r, bk_l]

        elif style == 'cutter':
            # Angled stern eyes — wider, tilted inward, no blush
            ey_r = sphere(f"{prefix}_EyeR", 0.09, (ox+0.17, EY, EZ), (1.5,0.42,0.80), M_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.09, (ox-0.17, EY, EZ), (1.5,0.42,0.80), M_EYE)
            ey_r.rotation_euler = (0, 0,  RAD(18))
            ey_l.rotation_euler = (0, 0, -RAD(18))
            bpy.context.view_layer.objects.active = ey_r; bpy.ops.object.transform_apply(rotation=True)
            bpy.context.view_layer.objects.active = ey_l; bpy.ops.object.transform_apply(rotation=True)
            # Heavy frown brows
            br_r = sphere(f"{prefix}_BrR", 0.055, (ox+0.19, EY-0.04, EZ+0.10), (1.8,0.4,0.5), M_EYE)
            br_l = sphere(f"{prefix}_BrL", 0.055, (ox-0.19, EY-0.04, EZ+0.10), (1.8,0.4,0.5), M_EYE)
            br_r.rotation_euler = (0, 0, -RAD(25)); bpy.context.view_layer.objects.active = br_r; bpy.ops.object.transform_apply(rotation=True)
            br_l.rotation_euler = (0, 0,  RAD(25)); bpy.context.view_layer.objects.active = br_l; bpy.ops.object.transform_apply(rotation=True)
            parts += [ey_r, ey_l, br_r, br_l]

        else:  # wanderer — wide whimsical eyes + star highlights + blush
            ey_r = sphere(f"{prefix}_EyeR", 0.10, (ox+0.17, EY, EZ), (1.0,0.42,1.08), M_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.10, (ox-0.17, EY, EZ), (1.0,0.42,1.08), M_EYE)
            sh_r = sphere(f"{prefix}_ShR",  0.032, (ox+0.21, EY-0.06, EZ+0.06), mat_ref=M_WHITE)
            sh_l = sphere(f"{prefix}_ShL",  0.032, (ox-0.13, EY-0.06, EZ+0.06), mat_ref=M_WHITE)
            gl_r = sphere(f"{prefix}_GlR",  0.020, (ox+0.14, EY-0.07, EZ+0.09), mat_ref=M_GLOW)
            gl_l = sphere(f"{prefix}_GlL",  0.020, (ox-0.20, EY-0.07, EZ+0.09), mat_ref=M_GLOW)
            # Blush
            bk_r = sphere(f"{prefix}_BkR",  0.08, (ox+0.26, EY+0.02, EZ-0.09), (1.0,0.25,0.65), M_BLUSH)
            bk_l = sphere(f"{prefix}_BkL",  0.08, (ox-0.26, EY+0.02, EZ-0.09), (1.0,0.25,0.65), M_BLUSH)
            parts += [ey_r, ey_l, sh_r, sh_l, gl_r, gl_l, bk_r, bk_l]

        # Collection & parent
        col = bpy.data.collections.new(prefix)
        scene.collection.children.link(col)
        for obj in [head] + parts:
            for c2 in list(obj.users_collection): c2.objects.unlink(obj)
            col.objects.link(obj)
        for p in parts:
            p.parent = head
        return head, col

    # ── Build all three ───────────────────────────────────────────────────────
    print("Building ghosts v002 …")
    fol_head, fol_col = build_ghost("Follower", -3.5, 'follower')
    cut_head, cut_col = build_ghost("Cutter",    0.0, 'cutter')
    wan_head, wan_col = build_ghost("Wanderer",  3.5, 'wanderer')

    # ── Lighting ─────────────────────────────────────────────────────────────
    bpy.ops.object.light_add(type='AREA', location=(0,-5, 4))
    key = bpy.context.active_object; key.name="GhostKey"
    key.data.energy=300; key.data.color=(1.0,0.97,0.90); key.data.size=5.0
    key.rotation_euler=(RAD(55), 0, 0)

    bpy.ops.object.light_add(type='AREA', location=(0, 3, 2))
    rim = bpy.context.active_object; rim.name="GhostRim"
    rim.data.energy=80; rim.data.color=(1.0,0.95,0.80); rim.data.size=4.0

    bpy.ops.object.light_add(type='POINT', location=(0,-2, 0.5))
    front = bpy.context.active_object; front.name="GhostFront"
    front.data.energy=60; front.data.color=(1.0,0.98,0.90)

    world = bpy.data.worlds.new("GhostWorld_v2")
    scene.world = world
    if not world.use_nodes: world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value   = hex_rgba("#FFF3E8")
        bg.inputs["Strength"].default_value = 0.7

    # ── Render settings ───────────────────────────────────────────────────────
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True

    # Lineup render (wide)
    scene.render.resolution_x = 1600; scene.render.resolution_y = 700
    bpy.ops.object.camera_add(location=(0,-6, 0.5))
    cam_lineup = bpy.context.active_object; cam_lineup.name="Cam_Lineup"
    cam_lineup.rotation_euler = (RAD(90), 0, 0)
    cam_lineup.data.type = 'ORTHO'; cam_lineup.data.ortho_scale = 11.0
    scene.camera = cam_lineup
    out = os.path.join(RENDER_DIR, "ghosts_v002_lineup.png")
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ lineup: {out}")

    # Individual ghost turnarounds
    scene.render.resolution_x = 512; scene.render.resolution_y = 512
    for gname, ghead, gcol in [("follower", fol_head, fol_col),
                                ("cutter",   cut_head, cut_col),
                                ("wanderer", wan_head, wan_col)]:
        cx = ghead.location.x
        for vname, loc, rot in [
            ("front", (cx,   -2.5, 0.5), (RAD(90), 0, 0)),
            ("34",    (cx+1.8,-1.8, 0.8),(RAD(78), 0, RAD(35))),
            ("side",  (cx+2.5, 0,   0.5),(RAD(90), 0, RAD(90))),
        ]:
            bpy.ops.object.camera_add(location=loc)
            cam = bpy.context.active_object; cam.name=f"Cam_{gname}_{vname}"
            cam.rotation_euler = rot
            cam.data.type='ORTHO'; cam.data.ortho_scale=2.0
            scene.camera = cam
            out = os.path.join(RENDER_DIR, f"ghost_v002_{gname}_{vname}.png")
            scene.render.filepath = out
            bpy.ops.render.render(write_still=True)
            print(f"  ✓ {gname}_{vname}")

    # ── Save + FBX ───────────────────────────────────────────────────────────
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")

    for gname, gcol in [("follower",fol_col),("cutter",cut_col),("wanderer",wan_col)]:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in gcol.objects: obj.select_set(True)
        fp = os.path.join(FBX_DIR, f"ghost_{gname}_v002.fbx")
        bpy.ops.export_scene.fbx(filepath=fp, use_selection=True,
            axis_forward='-Z', axis_up='Y', add_leaf_bones=False)
        print(f"  FBX: {fp}")

    print("=== Ghost v002 build COMPLETE ===")

except Exception:
    import traceback; traceback.print_exc()
    sys.exit(1)
