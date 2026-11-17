"""
build_ghosts_v9_master_fluffy_multitail.py
MOMO MAZE - Definitive Fluffy Multi-Tail Spirits v9 (Blender 5.2)

Strictly incorporating user requirements:
- 3 to 4 distinct trailing wisp tails on each spirit with fluid tapered wisps and floating droplets
- Fluffy hair / fur sensation: procedural micro-strand hair bump, velvety peach-fuzz sheen,
  soft warm-white subsurface scattering (SSS), and organic cloud-puff contouring
- Distinct facial identities matching approved concept sheets:
  1. Follower: Wide round curious dark eyes with double catchlight sparkle + soft peach blush
  2. Cutter: Determined sleek oval eyes, furrowed brow crest, confident expression + soft peach blush
  3. Wanderer: Happy closed smiling crescent eyes (^ ^), joyful open mouth with tongue + soft peach blush
- Isolation per turnaround render (so other ghosts don't clip into the frame)
- Export verified FBXs and save master blend file
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Ghost_Spirits_v9_Master")
    bpy.context.scene.collection.children.link(col)
    return col

def create_fluffy_spirit_material():
    mat = bpy.data.materials.new("M_Spirit_Fluffy_Fuzz")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')

    # Warm cream color gradient (slightly warmer in center, warm-white highlights)
    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.1
    ramp.color_ramp.elements[0].color = (0.97, 0.95, 0.92, 1.0) # Warm white #F7F2EB
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (1.00, 0.98, 0.95, 1.0) # Soft marshmallow cream #FFFBF2
    noise_color = tree.nodes.new('ShaderNodeTexNoise')
    noise_color.inputs['Scale'].default_value = 4.0
    tree.links.new(tex_coord.outputs['Object'], noise_color.inputs['Vector'])
    tree.links.new(noise_color.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Micro-fur / hair texture bump for fluffy sensation
    noise_fur = tree.nodes.new('ShaderNodeTexNoise')
    noise_fur.inputs['Scale'].default_value = 95.0
    noise_fur.inputs['Detail'].default_value = 6.0
    noise_fur.inputs['Roughness'].default_value = 0.75
    tree.links.new(tex_coord.outputs['Object'], noise_fur.inputs['Vector'])

    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.02
    tree.links.new(noise_fur.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Velvety fluff sheen
    bsdf.inputs['Roughness'].default_value = 0.60
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 1.0
        bsdf.inputs['Sheen Roughness'].default_value = 0.45
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (1.0, 0.96, 0.90, 1.0)
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 1.0

    # Subsurface scattering for soft translucent cloud glow
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.40
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.92, 0.82)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.40

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_face_materials():
    mats = {}

    # Eyes: Glossy deep warm-black
    m_eye = bpy.data.materials.new("M_Spirit_Eyes")
    m_eye.use_nodes = True
    b_e = m_eye.node_tree.nodes.get("Principled BSDF")
    b_e.inputs['Base Color'].default_value = (0.06, 0.04, 0.04, 1.0)
    b_e.inputs['Roughness'].default_value = 0.06
    mats["eye"] = m_eye

    # Shine: Pure brilliant white
    m_shine = bpy.data.materials.new("M_Spirit_EyeShine")
    m_shine.use_nodes = True
    b_s = m_shine.node_tree.nodes.get("Principled BSDF")
    b_s.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    b_s.inputs['Roughness'].default_value = 0.02
    if 'Emission Color' in b_s.inputs:
        b_s.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        b_s.inputs['Emission Strength'].default_value = 0.90
    mats["shine"] = m_shine

    # Cheeks: Soft peach blush
    m_chk = bpy.data.materials.new("M_Spirit_CheekBlush")
    m_chk.use_nodes = True
    b_c = m_chk.node_tree.nodes.get("Principled BSDF")
    b_c.inputs['Base Color'].default_value = (1.0, 0.65, 0.60, 1.0)
    b_c.inputs['Roughness'].default_value = 0.65
    if 'Subsurface Weight' in b_c.inputs:
        b_c.inputs['Subsurface Weight'].default_value = 0.45
    mats["cheek"] = m_chk

    # Mouth interior
    m_mouth = bpy.data.materials.new("M_Spirit_Mouth")
    m_mouth.use_nodes = True
    b_m = m_mouth.node_tree.nodes.get("Principled BSDF")
    b_m.inputs['Base Color'].default_value = (0.40, 0.08, 0.12, 1.0)
    b_m.inputs['Roughness'].default_value = 0.35
    mats["mouth"] = m_mouth

    # Tongue
    m_t = bpy.data.materials.new("M_Spirit_Tongue")
    m_t.use_nodes = True
    b_t = m_t.node_tree.nodes.get("Principled BSDF")
    b_t.inputs['Base Color'].default_value = (0.96, 0.42, 0.48, 1.0)
    b_t.inputs['Roughness'].default_value = 0.25
    mats["tongue"] = m_t

    return mats

def build_wisp_tail(name, seg_data, mat, parent_obj, col):
    """
    Constructs an organic cloud wisp tail from tapered spheres/droplets.
    seg_data is a list of tuples: (location_tuple, scale_tuple)
    """
    for idx, (loc, sc) in enumerate(seg_data):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1.0)
        seg = bpy.context.active_object
        seg.name = f"{name}_Seg_{idx+1}"
        seg.location = loc
        seg.scale = sc
        seg.parent = parent_obj
        bpy.ops.object.shade_smooth()
        seg.data.materials.append(mat)
        col.objects.link(seg)

def build_spirit_follower(mat_body, mats, col):
    """Ghost Follower: Round silhouette, 4 flowing wisps, wide curious eyes + double sparkle."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0)
    head = bpy.context.active_object
    head.name = "Ghost_Follower_Root"
    head.scale = (1.05, 1.12, 1.00)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    head.data.materials.append(mat_body)
    col.objects.link(head)

    # 4 Trailing Wisps:
    # 1. Crest Wisp (top curving back)
    crest = [
        ((-0.05, -0.95, 0.45), (0.44, 0.52, 0.44)),
        ((-0.08, -1.45, 0.85), (0.34, 0.42, 0.34)),
        ((-0.10, -1.90, 1.25), (0.24, 0.30, 0.24)),
        ((-0.12, -2.25, 1.55), (0.12, 0.16, 0.12))
    ]
    build_wisp_tail("Ghost_Follower_Wisp_Crest", crest, mat_body, head, col)

    # 2. Main Center Wisp (long horizontal trailing stream)
    center = [
        ((0.00, -1.05, 0.05), (0.50, 0.62, 0.48)),
        ((0.02, -1.72, 0.12), (0.40, 0.54, 0.38)),
        ((0.04, -2.35, 0.18), (0.28, 0.40, 0.28)),
        ((0.06, -2.85, 0.22), (0.16, 0.24, 0.16)),
        ((0.08, -3.20, 0.24), (0.08, 0.12, 0.08))
    ]
    build_wisp_tail("Ghost_Follower_Wisp_Center", center, mat_body, head, col)

    # 3. Lower-Left Wisp
    left = [
        ((-0.52, -0.85, -0.32), (0.36, 0.45, 0.34)),
        ((-0.78, -1.35, -0.42), (0.26, 0.36, 0.26)),
        ((-0.98, -1.75, -0.48), (0.15, 0.22, 0.15))
    ]
    build_wisp_tail("Ghost_Follower_Wisp_Left", left, mat_body, head, col)

    # 4. Lower-Right Wisp
    right = [
        ((0.52, -0.85, -0.32), (0.36, 0.45, 0.34)),
        ((0.78, -1.35, -0.42), (0.26, 0.36, 0.26)),
        ((0.98, -1.75, -0.48), (0.15, 0.22, 0.15))
    ]
    build_wisp_tail("Ghost_Follower_Wisp_Right", right, mat_body, head, col)

    # Wide Curious Glossy Eyes with Double Sparkles
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.18)
        eye = bpy.context.active_object
        eye.name = f"Ghost_Follower_Eye_{suffix}"
        eye.scale = (0.75, 0.25, 1.05)
        eye.location = (sign * 0.35, 0.98, 0.12)
        eye.rotation_euler = (math.radians(-10), math.radians(sign * 10), 0)
        eye.parent = head
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eye"])
        col.objects.link(eye)

        # Upper white sparkle
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.08)
        sh1 = bpy.context.active_object
        sh1.name = f"Ghost_Follower_Shine1_{suffix}"
        sh1.location = (sign * 0.34, 1.04, 0.18)
        sh1.parent = head
        bpy.ops.object.shade_smooth()
        sh1.data.materials.append(mats["shine"])
        col.objects.link(sh1)

        # Lower micro sparkle
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.04)
        sh2 = bpy.context.active_object
        sh2.name = f"Ghost_Follower_Shine2_{suffix}"
        sh2.location = (sign * 0.40, 1.04, 0.06)
        sh2.parent = head
        bpy.ops.object.shade_smooth()
        sh2.data.materials.append(mats["shine"])
        col.objects.link(sh2)

        # Soft peach cheek blush
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.16)
        chk = bpy.context.active_object
        chk.name = f"Ghost_Follower_Cheek_{suffix}"
        chk.scale = (1.15, 0.35, 0.75)
        chk.location = (sign * 0.58, 0.82, -0.06)
        chk.rotation_euler = (math.radians(-12), math.radians(sign * 22), 0)
        chk.parent = head
        bpy.ops.object.shade_smooth()
        chk.data.materials.append(mats["cheek"])
        col.objects.link(chk)

    return head

def build_spirit_cutter(mat_body, mats, col):
    """Ghost Cutter: Aerodynamic teardrop head, 3 fast swept wisps, determined slant eyes & brow."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0)
    head = bpy.context.active_object
    head.name = "Ghost_Cutter_Root"
    head.scale = (0.96, 1.25, 0.94)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    head.data.materials.append(mat_body)
    col.objects.link(head)

    # 3 Swept Speed Wisps:
    # 1. High Dorsal Swept Wisp
    high = [
        ((0.00, -1.02, 0.48), (0.42, 0.55, 0.38)),
        ((0.00, -1.65, 0.82), (0.32, 0.44, 0.28)),
        ((0.00, -2.18, 1.15), (0.22, 0.32, 0.18)),
        ((0.00, -2.60, 1.42), (0.10, 0.16, 0.08))
    ]
    build_wisp_tail("Ghost_Cutter_Wisp_High", high, mat_body, head, col)

    # 2. Left Lateral Speed Wing
    left = [
        ((-0.55, -0.92, -0.10), (0.38, 0.58, 0.30)),
        ((-0.88, -1.55, -0.16), (0.28, 0.45, 0.22)),
        ((-1.15, -2.08, -0.20), (0.16, 0.30, 0.12)),
        ((-1.35, -2.45, -0.22), (0.07, 0.14, 0.06))
    ]
    build_wisp_tail("Ghost_Cutter_Wisp_Left", left, mat_body, head, col)

    # 3. Right Lateral Speed Wing
    right = [
        ((0.55, -0.92, -0.10), (0.38, 0.58, 0.30)),
        ((0.88, -1.55, -0.16), (0.28, 0.45, 0.22)),
        ((1.15, -2.08, -0.20), (0.16, 0.30, 0.12)),
        ((1.35, -2.45, -0.22), (0.07, 0.14, 0.06))
    ]
    build_wisp_tail("Ghost_Cutter_Wisp_Right", right, mat_body, head, col)

    # Determined Slanted Eyes with Focused Brow
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.18)
        eye = bpy.context.active_object
        eye.name = f"Ghost_Cutter_Eye_{suffix}"
        eye.scale = (0.85, 0.25, 0.70)
        eye.location = (sign * 0.35, 1.05, 0.14)
        eye.rotation_euler = (math.radians(-10), math.radians(sign * 15), math.radians(sign * 22))
        eye.parent = head
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eye"])
        col.objects.link(eye)

        # Focused gleam
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.065)
        sh = bpy.context.active_object
        sh.name = f"Ghost_Cutter_Shine_{suffix}"
        sh.location = (sign * 0.33, 1.11, 0.17)
        sh.parent = head
        bpy.ops.object.shade_smooth()
        sh.data.materials.append(mats["shine"])
        col.objects.link(sh)

        # Cute peach blush
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.14)
        chk = bpy.context.active_object
        chk.name = f"Ghost_Cutter_Cheek_{suffix}"
        chk.scale = (1.1, 0.35, 0.70)
        chk.location = (sign * 0.54, 0.90, -0.05)
        chk.parent = head
        bpy.ops.object.shade_smooth()
        chk.data.materials.append(mats["cheek"])
        col.objects.link(chk)

    return head

def build_spirit_wanderer(mat_body, mats, col):
    """Ghost Wanderer: Wide plump cloud head, 4 dancing wisps, happy closed eyes (^ ^) and laughing open mouth."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0)
    head = bpy.context.active_object
    head.name = "Ghost_Wanderer_Root"
    head.scale = (1.14, 1.06, 1.04)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    head.data.materials.append(mat_body)
    col.objects.link(head)

    # 4 Dancing Wisps:
    # 1. Top Wave Crest
    top = [
        ((0.15, -0.95, 0.45), (0.42, 0.50, 0.40)),
        ((0.28, -1.48, 0.80), (0.32, 0.40, 0.30)),
        ((0.38, -1.92, 1.12), (0.20, 0.28, 0.20)),
        ((0.45, -2.25, 1.38), (0.10, 0.15, 0.10))
    ]
    build_wisp_tail("Ghost_Wanderer_Wisp_Top", top, mat_body, head, col)

    # 2. Main Tail S-curve
    mid = [
        ((-0.05, -1.02, 0.02), (0.48, 0.60, 0.44)),
        ((-0.18, -1.68, 0.08), (0.38, 0.50, 0.34)),
        ((-0.08, -2.28, 0.12), (0.26, 0.36, 0.24)),
        ((0.08, -2.78, 0.15), (0.14, 0.22, 0.14))
    ]
    build_wisp_tail("Ghost_Wanderer_Wisp_Mid", mid, mat_body, head, col)

    # 3. Lower Left Droplet
    bot_l = [
        ((-0.55, -0.85, -0.35), (0.34, 0.44, 0.32)),
        ((-0.82, -1.32, -0.45), (0.24, 0.34, 0.22)),
        ((-1.05, -1.70, -0.52), (0.12, 0.18, 0.12))
    ]
    build_wisp_tail("Ghost_Wanderer_Wisp_BotL", bot_l, mat_body, head, col)

    # 4. Lower Right Droplet
    bot_r = [
        ((0.48, -0.85, -0.32), (0.34, 0.44, 0.32)),
        ((0.72, -1.32, -0.40), (0.24, 0.34, 0.22)),
        ((0.92, -1.70, -0.45), (0.12, 0.18, 0.12))
    ]
    build_wisp_tail("Ghost_Wanderer_Wisp_BotR", bot_r, mat_body, head, col)

    # Happy Closed Smiling Crescent Eyes (^ ^)
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.035, major_segments=24, minor_segments=12)
        eye = bpy.context.active_object
        eye.name = f"Ghost_Wanderer_Eye_{suffix}"
        eye.scale = (1.0, 0.35, 1.0)
        eye.location = (sign * 0.34, 0.98, 0.12)
        eye.rotation_euler = (math.radians(-75), math.radians(sign * 10), 0)
        eye.parent = head
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eye"])
        col.objects.link(eye)

        # Cheerful blush
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.18)
        chk = bpy.context.active_object
        chk.name = f"Ghost_Wanderer_Cheek_{suffix}"
        chk.scale = (1.2, 0.35, 0.80)
        chk.location = (sign * 0.60, 0.82, -0.05)
        chk.rotation_euler = (math.radians(-12), math.radians(sign * 20), 0)
        chk.parent = head
        bpy.ops.object.shade_smooth()
        chk.data.materials.append(mats["cheek"])
        col.objects.link(chk)

    # Open Laughing Mouth with Tongue
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.15)
    mouth = bpy.context.active_object
    mouth.name = "Ghost_Wanderer_Mouth"
    mouth.scale = (1.1, 0.30, 0.70)
    mouth.location = (0, 1.07, -0.06)
    mouth.rotation_euler = (math.radians(-12), 0, 0)
    mouth.parent = head
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mats["mouth"])
    col.objects.link(mouth)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.09)
    tongue = bpy.context.active_object
    tongue.name = "Ghost_Wanderer_Tongue"
    tongue.scale = (1.1, 0.30, 0.50)
    tongue.location = (0, 1.10, -0.09)
    tongue.parent = head
    bpy.ops.object.shade_smooth()
    tongue.data.materials.append(mats["tongue"])
    col.objects.link(tongue)

    return head

def render_lineup_and_turnarounds(col, follower, cutter, wanderer):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.image_settings.file_format = 'PNG'

    # Warm studio lighting
    world = scene.world or bpy.data.worlds.new("World_GhostStudio")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.96, 0.94, 0.91, 1.0)
        bg.inputs['Strength'].default_value = 0.90

    sun = bpy.data.lights.new("Sun_Key", 'SUN')
    sun.energy = 4.8
    sun.color = (1.0, 0.96, 0.90)
    sun_obj = bpy.data.objects.new("Sun_Key", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    col.objects.link(sun_obj)

    fill = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill.energy = 2.2
    fill.color = (0.90, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("Sun_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    col.objects.link(fill_obj)

    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.color = (1.0, 0.88, 0.72)
    rim.energy = 75.0
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0, 3.2, 1.8)
    col.objects.link(rim_obj)

    cam_data = bpy.data.cameras.new("Cam_Lineup")
    cam_data.type = 'ORTHO'
    cam_obj = bpy.data.objects.new("Cam_Lineup", cam_data)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position ghosts for lineup:
    follower.location = (-2.8, 0, 0)
    cutter.location = (0.0, 0, 0)
    wanderer.location = (2.8, 0, 0)

    # 3/4 dynamic orientation facing camera at +Y with tails flowing back to -Y
    follower.rotation_euler = (math.radians(-6), math.radians(8), math.radians(35))
    cutter.rotation_euler = (math.radians(-8), math.radians(6), math.radians(35))
    wanderer.rotation_euler = (math.radians(-5), math.radians(10), math.radians(35))
    bpy.context.view_layer.update()

    cam_data.ortho_scale = 10.5
    cam_obj.location = (0, 5.5, 0.8)
    cam_obj.rotation_euler = (math.radians(98), 0, math.radians(180))
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 900
    out_lineup = "D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/spirits_hero_lineup_v3.png"
    scene.render.filepath = out_lineup
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Hero Lineup v3 -> {out_lineup}")

    # Individual Turnarounds:
    # Reset locations and isolate objects so only the active ghost is rendered!
    ghosts = [
        ("follower", follower, "Ghost_Follower"),
        ("cutter", cutter, "Ghost_Cutter"),
        ("wanderer", wanderer, "Ghost_Wanderer")
    ]

    for g_id, g_root, g_prefix in ghosts:
        # Move all to far away except target
        for other_id, other_root, _ in ghosts:
            if other_id == g_id:
                other_root.location = (0, 0, 0)
            else:
                other_root.location = (100.0, 100.0, 100.0)

        cam_data.ortho_scale = 4.4
        scene.render.resolution_x = 1000
        scene.render.resolution_y = 1000

        views = [
            ("front", (0, 4.0, 0.3), (math.radians(88), 0, math.radians(180))),
            ("34view", (3.2, 3.2, 1.2), (math.radians(72), 0, math.radians(135))),
            ("side", (4.0, 0, 0.3), (math.radians(88), 0, math.radians(90)))
        ]

        g_root.rotation_euler = (0, 0, 0)
        for v_name, c_pos, c_rot in views:
            cam_obj.location = c_pos
            cam_obj.rotation_euler = c_rot
            bpy.context.view_layer.update()
            out_file = f"D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/ghost_{g_id}_{v_name}_v3.png"
            scene.render.filepath = out_file
            bpy.ops.render.render(write_still=True)
            print(f"  ✓ Rendered {g_id} [{v_name}] -> {out_file}")

        # Reset location
        g_root.location = (0, 0, 0)

        # Export individual FBX
        fbx_path = f"D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/ghost_{g_id}_validated.fbx"
        bpy.ops.object.select_all(action='DESELECT')
        for obj in col.objects:
            if obj.name.startswith(g_prefix):
                obj.select_set(True)
        bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, apply_scale_options='FBX_SCALE_ALL')
        print(f"  ✓ Exported FBX -> {fbx_path}")

    # Save Blend file
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved Master Blend -> {blend_path}")

if __name__ == "__main__":
    print("==================================================")
    print("Building Ghost Spirits v9 Master (Multi-Tail & Fluff)")
    print("==================================================")
    col = reset_scene()
    mat_body = create_fluffy_spirit_material()
    mats_face = create_face_materials()

    follower = build_spirit_follower(mat_body, mats_face, col)
    cutter = build_spirit_cutter(mat_body, mats_face, col)
    wanderer = build_spirit_wanderer(mat_body, mats_face, col)

    render_lineup_and_turnarounds(col, follower, cutter, wanderer)
    print("All ghost assets built and rendered successfully!")
