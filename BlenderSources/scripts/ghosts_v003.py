"""
MOMO MAZE – Ghost Spirits v003 (Final Eye + Personality Fix)
=============================================================
Fixes from v002 QA:
  1. Eyes smaller and pushed into head surface properly
  2. Follower: round dot eyes (not large flat ovals), cheek blush
  3. Cutter: narrow angled eyes with raised brow ridges, no blush
  4. Wanderer: wide round eyes + visible sparkle highlights, blush
  5. Camera backed out slightly to show full tail
"""

import bpy, math, os, sys

try:
    THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
    ROOT       = os.path.abspath(os.path.join(THIS_DIR, ".."))
    SCENE_DIR  = os.path.join(ROOT, "scenes");   os.makedirs(SCENE_DIR,  exist_ok=True)
    FBX_DIR    = os.path.join(ROOT, "exports", "fbx"); os.makedirs(FBX_DIR, exist_ok=True)
    RENDER_DIR = os.path.join(ROOT, "renders", "ghosts"); os.makedirs(RENDER_DIR, exist_ok=True)

    BLEND_PATH = os.path.join(SCENE_DIR, "ghosts_v003.blend")
    RAD = math.radians

    def srgb(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    def hex_rgba(h):
        h = h.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (srgb(r), srgb(g), srgb(b), 1.0)

    GHOST_WHITE = hex_rgba("#FFF7EE")
    GHOST_TAIL  = hex_rgba("#FFF0DD")
    EYE_DARK    = hex_rgba("#3D2B1F")
    BLUSH_PINK  = hex_rgba("#FFB3B0")
    GLOW_GOLD   = hex_rgba("#FFDFA8")

    def mat(name, color, rough=0.85, spec=0.05, emit_str=0.0, alpha=1.0):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        if not m.use_nodes: m.use_nodes = True
        nodes = m.node_tree.nodes; links = m.node_tree.links; nodes.clear()
        out  = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value  = rough
        for k in ("Specular IOR Level","Specular"):
            if k in bsdf.inputs: bsdf.inputs[k].default_value = spec; break
        if "Alpha" in bsdf.inputs: bsdf.inputs["Alpha"].default_value = alpha
        if emit_str > 0:
            for ek in ("Emission Color","Emission"):
                if ek in bsdf.inputs: bsdf.inputs[ek].default_value = color; break
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit_str
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        if alpha < 1.0: m.blend_method = 'BLEND'
        return m

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    M_BODY  = mat("M_Ghost_Body",  GHOST_WHITE, rough=0.88, emit_str=0.12)
    M_TAIL  = mat("M_Ghost_Tail",  GHOST_TAIL,  rough=0.90, alpha=0.50)
    M_EYE   = mat("M_Ghost_Eye",   EYE_DARK,    rough=0.35, spec=0.5)
    M_BLUSH = mat("M_Ghost_Blush", BLUSH_PINK,  rough=0.95)
    M_GLOW  = mat("M_Ghost_Glow",  GLOW_GOLD,   rough=0.3,  emit_str=1.2)
    M_WHITE = mat("M_Ghost_Shine", (1,1,1,1),   rough=0.1,  spec=1.0)

    def sphere(name, r, loc, scale=(1,1,1), mat_ref=None, segs=20, rings=14):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings,
                                             radius=r, location=loc)
        obj = bpy.context.active_object; obj.name = name; obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        if mat_ref: obj.data.materials.clear(); obj.data.materials.append(mat_ref)
        return obj

    def build_ghost(prefix, ox, style):
        # Head — large warm-white sphere
        head = sphere(f"{prefix}_Head", 0.52, (ox, 0, 0.52), (1.0,0.95,1.0), M_BODY, segs=24, rings=16)

        # Tail — teardrop: elongated sphere behind/below head
        tail_body = sphere(f"{prefix}_TailA", 0.52, (ox, 0.68, -0.02),
                           (0.68, 1.65, 0.58), M_TAIL)
        tail_tip  = sphere(f"{prefix}_TailB", 0.16, (ox, 1.32, -0.14),
                           (0.42, 0.75, 0.38), M_TAIL)

        parts = [tail_body, tail_tip]

        # Eye anchor Y: surface of head (~radius 0.52 → Y≈-0.50 from center)
        EY = -0.50   # forward face of head
        EZ =  0.60   # upper face

        if style == 'follower':
            # Small friendly round dots + blush cheeks
            ey_r = sphere(f"{prefix}_EyeR", 0.065, (ox+0.14, EY, EZ), (1.0,0.55,0.95), M_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.065, (ox-0.14, EY, EZ), (1.0,0.55,0.95), M_EYE)
            sh_r = sphere(f"{prefix}_ShR",  0.020, (ox+0.17, EY-0.04, EZ+0.04), mat_ref=M_WHITE)
            sh_l = sphere(f"{prefix}_ShL",  0.020, (ox-0.11, EY-0.04, EZ+0.04), mat_ref=M_WHITE)
            bk_r = sphere(f"{prefix}_BkR",  0.065, (ox+0.23, EY+0.04, EZ-0.10), (1.0,0.28,0.60), M_BLUSH)
            bk_l = sphere(f"{prefix}_BkL",  0.065, (ox-0.23, EY+0.04, EZ-0.10), (1.0,0.28,0.60), M_BLUSH)
            parts += [ey_r, ey_l, sh_r, sh_l, bk_r, bk_l]

        elif style == 'cutter':
            # Narrow angled stern eyes — thin horizontal slits, tilted
            ey_r = sphere(f"{prefix}_EyeR", 0.075, (ox+0.15, EY, EZ), (1.6,0.35,0.75), M_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.075, (ox-0.15, EY, EZ), (1.6,0.35,0.75), M_EYE)
            # Rotate for angry inward tilt
            ey_r.rotation_euler = (0,0, RAD(20))
            ey_l.rotation_euler = (0,0,-RAD(20))
            bpy.context.view_layer.objects.active = ey_r; bpy.ops.object.transform_apply(rotation=True)
            bpy.context.view_layer.objects.active = ey_l; bpy.ops.object.transform_apply(rotation=True)
            # Visible thick brow ridges above eyes
            br_r = sphere(f"{prefix}_BrR", 0.048, (ox+0.17, EY-0.03, EZ+0.11), (2.0,0.45,0.48), M_EYE)
            br_l = sphere(f"{prefix}_BrL", 0.048, (ox-0.17, EY-0.03, EZ+0.11), (2.0,0.45,0.48), M_EYE)
            br_r.rotation_euler = (0,0,-RAD(28)); bpy.context.view_layer.objects.active=br_r; bpy.ops.object.transform_apply(rotation=True)
            br_l.rotation_euler = (0,0, RAD(28)); bpy.context.view_layer.objects.active=br_l; bpy.ops.object.transform_apply(rotation=True)
            parts += [ey_r, ey_l, br_r, br_l]

        else:  # wanderer — wide sparkly eyes, visible glow
            ey_r = sphere(f"{prefix}_EyeR", 0.085, (ox+0.15, EY, EZ), (1.0,0.48,1.08), M_EYE)
            ey_l = sphere(f"{prefix}_EyeL", 0.085, (ox-0.15, EY, EZ), (1.0,0.48,1.08), M_EYE)
            # Large bright shine dots (key feature of Wanderer)
            sh_r = sphere(f"{prefix}_ShR",  0.030, (ox+0.19, EY-0.05, EZ+0.07), mat_ref=M_WHITE)
            sh_l = sphere(f"{prefix}_ShL",  0.030, (ox-0.11, EY-0.05, EZ+0.07), mat_ref=M_WHITE)
            # Star glow dots
            gl_r = sphere(f"{prefix}_GlR",  0.018, (ox+0.12, EY-0.06, EZ+0.10), mat_ref=M_GLOW)
            gl_l = sphere(f"{prefix}_GlL",  0.018, (ox-0.18, EY-0.06, EZ+0.10), mat_ref=M_GLOW)
            # Blush
            bk_r = sphere(f"{prefix}_BkR",  0.065, (ox+0.24, EY+0.04, EZ-0.10), (1.0,0.28,0.60), M_BLUSH)
            bk_l = sphere(f"{prefix}_BkL",  0.065, (ox-0.24, EY+0.04, EZ-0.10), (1.0,0.28,0.60), M_BLUSH)
            parts += [ey_r, ey_l, sh_r, sh_l, gl_r, gl_l, bk_r, bk_l]

        col = bpy.data.collections.new(prefix)
        scene.collection.children.link(col)
        for obj in [head]+parts:
            for c2 in list(obj.users_collection): c2.objects.unlink(obj)
            col.objects.link(obj)
        for p in parts: p.parent = head
        return head, col

    print("Building ghosts v003 …")
    fol_h, fol_c = build_ghost("Follower", -3.5, 'follower')
    cut_h, cut_c = build_ghost("Cutter",    0.0, 'cutter')
    wan_h, wan_c = build_ghost("Wanderer",  3.5, 'wanderer')

    # Lighting
    bpy.ops.object.light_add(type='AREA', location=(0,-5,4))
    key=bpy.context.active_object; key.name="GKey"
    key.data.energy=320; key.data.color=(1.0,0.97,0.90); key.data.size=5.0
    key.rotation_euler=(RAD(55),0,0)
    bpy.ops.object.light_add(type='AREA', location=(0,3,2))
    rim=bpy.context.active_object; rim.name="GRim"
    rim.data.energy=90; rim.data.color=(1.0,0.95,0.80); rim.data.size=4.0
    bpy.ops.object.light_add(type='POINT', location=(0,-2,0.5))
    fp2=bpy.context.active_object; fp2.name="GFill"
    fp2.data.energy=55; fp2.data.color=(1.0,0.98,0.92)

    world=bpy.data.worlds.new("GW3"); scene.world=world
    if not world.use_nodes: world.use_nodes=True
    bg=world.node_tree.nodes.get("Background")
    if bg: bg.inputs["Color"].default_value=hex_rgba("#FFF3E8"); bg.inputs["Strength"].default_value=0.7

    scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=96
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True

    # Lineup render
    scene.render.resolution_x=1600; scene.render.resolution_y=750
    bpy.ops.object.camera_add(location=(0,-6,0.5))
    cam=bpy.context.active_object; cam.name="Cam_Lineup"
    cam.rotation_euler=(RAD(90),0,0); cam.data.type='ORTHO'; cam.data.ortho_scale=12.0
    scene.camera=cam
    scene.render.filepath=os.path.join(RENDER_DIR,"ghosts_v003_lineup.png")
    bpy.ops.render.render(write_still=True); print("  ✓ lineup")

    # Individual turnarounds
    scene.render.resolution_x=512; scene.render.resolution_y=600
    for gname, gh, gc in [("follower",fol_h,fol_c),("cutter",cut_h,cut_c),("wanderer",wan_h,wan_c)]:
        cx=gh.location.x
        for vname, loc, rot in [
            ("front", (cx,  -2.8, 0.5),(RAD(90),0,0)),
            ("34",    (cx+2.0,-2.0,0.9),(RAD(76),0,RAD(36))),
            ("side",  (cx+2.8, 0,  0.5),(RAD(90),0,RAD(90))),
        ]:
            bpy.ops.object.camera_add(location=loc)
            cam=bpy.context.active_object; cam.name=f"Cam_{gname}_{vname}"
            cam.rotation_euler=rot; cam.data.type='ORTHO'; cam.data.ortho_scale=2.2
            scene.camera=cam
            out=os.path.join(RENDER_DIR,f"ghost_v003_{gname}_{vname}.png")
            scene.render.filepath=out
            bpy.ops.render.render(write_still=True); print(f"  ✓ {gname}_{vname}")

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")

    for gname, gcol in [("follower",fol_c),("cutter",cut_c),("wanderer",wan_c)]:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in gcol.objects: obj.select_set(True)
        fp=os.path.join(FBX_DIR,f"ghost_{gname}_v003.fbx")
        bpy.ops.export_scene.fbx(filepath=fp,use_selection=True,
            axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
        print(f"  FBX: {fp}")

    print("=== Ghost v003 build COMPLETE ===")

except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
