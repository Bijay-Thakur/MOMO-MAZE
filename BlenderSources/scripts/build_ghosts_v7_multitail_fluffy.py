"""
build_ghosts_v7_multitail_fluffy.py
MOMO MAZE - Refined Multi-Tail Fluffy Ghost Spirits (Blender 5.2)

Refinements:
- 3 to 4 distinct trailing wisp tails (top crest wisp, main center wisp, lower-left wisp, lower-right wisp)
- Fluffy hair / fur texture with velvety sheen, micro-hair bump, and soft misty translucency (SSS)
- Distinct facial personalities matching the concept sheet:
  * Follower: Curious vertical oval eyes with glossy catchlights
  * Cutter: Mischievous angled eyes with focused eyebrows (:>)
  * Wanderer: Joyful happy crescent arc eyes and open D-smile (:D)
- Hero lineup render + individual turnarounds + master blend + FBX exports
"""

import bpy
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Ghosts_Refined")
    bpy.context.scene.collection.children.link(col)
    return col

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

def create_fluffy_ghost_material():
    mat = bpy.data.materials.new("M_Ghost_FluffyCloud")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    # Object-space micro-fur noise
    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 3.5
    noise.inputs['Roughness'].default_value = 0.55
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    # Warm white fluffy gradient
    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.96, 0.94, 0.91, 1.0) # Soft shadow cream
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (1.00, 0.98, 0.95, 1.0) # Pure warm cloud white
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Subsurface scattering for misty airy cloud body
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = (0.7, 0.55, 0.4)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.45

    # Velvety Sheen for peach-fuzz / hair fluff sensation
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.95
        bsdf.inputs['Sheen Roughness'].default_value = 0.35
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.95

    bsdf.inputs['Roughness'].default_value = 0.50

    # Micro bump for fluffy hair texture
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Gentle warm inner emission
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.92, 0.78, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.4
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.92, 0.78, 1.0)

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_face_materials():
    # Glossy dark chocolate/black for eyes
    mat_eyes = bpy.data.materials.new("M_Ghost_Eyes")
    mat_eyes.use_nodes = True
    bsdf = get_principled_bsdf(mat_eyes)
    bsdf.inputs['Base Color'].default_value = (0.10, 0.06, 0.04, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.95

    # White catchlight shine
    mat_shine = bpy.data.materials.new("M_Ghost_EyeCatchlight")
    mat_shine.use_nodes = True
    bsdf_sh = get_principled_bsdf(mat_shine)
    bsdf_sh.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_sh.inputs['Roughness'].default_value = 0.02
    if 'Emission Color' in bsdf_sh.inputs:
        bsdf_sh.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf_sh.inputs['Emission Strength'].default_value = 1.8

    # Mouth dark cavity
    mat_mouth = bpy.data.materials.new("M_Ghost_Mouth")
    mat_mouth.use_nodes = True
    bsdf_m = get_principled_bsdf(mat_mouth)
    bsdf_m.inputs['Base Color'].default_value = (0.50, 0.12, 0.12, 1.0)
    bsdf_m.inputs['Roughness'].default_value = 0.35

    # Mouth pink tongue
    mat_tongue = bpy.data.materials.new("M_Ghost_Tongue")
    mat_tongue.use_nodes = True
    bsdf_t = get_principled_bsdf(mat_tongue)
    bsdf_t.inputs['Base Color'].default_value = (1.0, 0.45, 0.45, 1.0)
    bsdf_t.inputs['Roughness'].default_value = 0.3

    return {"eyes": mat_eyes, "shine": mat_shine, "mouth": mat_mouth, "tongue": mat_tongue}

def build_multitail_ghost_body(prefix, offset_x, ghost_mat):
    """
    Constructs the horizontal aerodynamic wisp body with 3 to 4 distinct trailing tails:
    - Head sphere at (0, 0, 0)
    - Top crest wisp (Tail 1) flowing back from the top of the head
    - Main center tail wisp (Tail 2) extending longest with a gentle wave
    - Lower-left tail wisp (Tail 3)
    - Lower-right tail wisp (Tail 4)
    """
    # 1. Main Head (Round front)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=28, radius=0.85, location=(0, 0, 0))
    head = bpy.context.active_object
    head.name = f"{prefix}_Head"
    head.scale = (1.0, 1.15, 0.95)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    head.data.materials.append(ghost_mat)
    bpy.ops.object.shade_smooth()

    # 2. Tail 1: Top Crest Wisp (swept back from upper head)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(0, 0.70, 0.55))
    t1 = bpy.context.active_object
    t1.scale = (0.75, 1.6, 0.65)
    t1.rotation_euler = (math.radians(-25), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 1.25, 0.75))
    t1_tip = bpy.context.active_object
    t1_tip.scale = (0.6, 1.4, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # 3. Tail 2: Main Center Wisp (Longest trailing tail)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, location=(0, 0.90, 0.05))
    t2 = bpy.context.active_object
    t2.scale = (0.85, 1.8, 0.75)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0, 1.65, 0.12))
    t2_mid = bpy.context.active_object
    t2_mid.scale = (0.70, 1.6, 0.60)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 2.25, 0.18))
    t2_tip = bpy.context.active_object
    t2_tip.scale = (0.5, 1.5, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # 4. Tail 3: Lower-Left Tail Wisp
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(-0.35, 0.85, -0.32))
    t3 = bpy.context.active_object
    t3.scale = (0.75, 1.5, 0.65)
    t3.rotation_euler = (math.radians(15), math.radians(-20), math.radians(-15))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(-0.55, 1.45, -0.42))
    t3_tip = bpy.context.active_object
    t3_tip.scale = (0.6, 1.3, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # 5. Tail 4: Lower-Right Tail Wisp
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(0.35, 0.85, -0.32))
    t4 = bpy.context.active_object
    t4.scale = (0.75, 1.5, 0.65)
    t4.rotation_euler = (math.radians(15), math.radians(20), math.radians(15))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.55, 1.45, -0.42))
    t4_tip = bpy.context.active_object
    t4_tip.scale = (0.6, 1.3, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Join all tail lobes and head into one seamless continuous spirit mesh
    all_parts = [head, t1, t1_tip, t2, t2_mid, t2_tip, t3, t3_tip, t4, t4_tip]
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()

    # Voxel remesh to seamlessly fuse all 4 tail wisps into one smooth organic body
    remesh = head.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.038
    remesh.adaptivity = 0.0
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    # Smooth
    smooth = head.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.70
    smooth.iterations = 4
    bpy.ops.object.modifier_apply(modifier="Smooth")

    # Organic cloud displacement
    tex = bpy.data.textures.new(f"{prefix}_CloudDisplace", 'CLOUDS')
    tex.noise_scale = 0.35
    tex.noise_depth = 2
    disp = head.modifiers.new("Displace", 'DISPLACE')
    disp.texture = tex
    disp.strength = 0.022
    bpy.ops.object.modifier_apply(modifier="Displace")

    # Subdiv
    subdiv = head.modifiers.new("Subdiv", 'SUBSURF')
    subdiv.levels = 1
    subdiv.render_levels = 1

    bpy.ops.object.shade_smooth()
    head.data.materials.clear()
    head.data.materials.append(ghost_mat)

    # Position at offset
    head.location = (offset_x, 0, 0)
    return head

def add_follower_face(head, mats, collection):
    """Follower: Curious vertical dark oval eyes with glossy white catchlights"""
    eye_x = 0.24
    eye_y = -0.80
    eye_z = 0.08
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(sign * eye_x, eye_y, eye_z))
        eye = bpy.context.active_object
        eye.name = f"Ghost_Follower_Eye_{side}"
        eye.scale = (0.75, 0.40, 1.25)
        eye.rotation_euler = (math.radians(15), 0, 0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eyes"])
        eye.parent = head
        collection.objects.link(eye)

        # Upper white catchlight shine patch
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.055,
            location=(sign * (eye_x - 0.025 * sign), eye_y - 0.045, eye_z + 0.055)
        )
        shine = bpy.context.active_object
        shine.name = f"Ghost_Follower_Shine_{side}"
        shine.scale = (1.0, 0.25, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mats["shine"])
        shine.parent = head
        collection.objects.link(shine)

def add_cutter_face(head, mats, collection):
    """Cutter: Mischievous angled eyes with focused eyebrows (:>)"""
    eye_x = 0.25
    eye_y = -0.80
    eye_z = 0.10
    for side, sign in [("L", -1), ("R", 1)]:
        # Angled focused eyeball
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(sign * eye_x, eye_y, eye_z))
        eye = bpy.context.active_object
        eye.name = f"Ghost_Cutter_Eye_{side}"
        eye.scale = (0.85, 0.35, 1.1)
        eye.rotation_euler = (math.radians(15), 0, sign * math.radians(-25)) # Slanted inwards
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eyes"])
        eye.parent = head
        collection.objects.link(eye)

        # Upper catchlight
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.05,
            location=(sign * (eye_x - 0.02 * sign), eye_y - 0.04, eye_z + 0.04)
        )
        shine = bpy.context.active_object
        shine.name = f"Ghost_Cutter_Shine_{side}"
        shine.scale = (1.0, 0.25, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mats["shine"])
        shine.parent = head
        collection.objects.link(shine)

        # Focused brow ridge
        bpy.ops.mesh.primitive_cube_add(
            size=0.14,
            location=(sign * eye_x, eye_y - 0.02, eye_z + 0.12)
        )
        brow = bpy.context.active_object
        brow.name = f"Ghost_Cutter_Brow_{side}"
        brow.scale = (1.1, 0.3, 0.35)
        brow.rotation_euler = (math.radians(15), 0, sign * math.radians(-32))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        brow.data.materials.append(mats["eyes"])
        brow.parent = head
        collection.objects.link(brow)

def add_wanderer_face(head, mats, collection):
    """Wanderer: Joyful happy crescent arc eyes and open D-smile (:D) with tongue"""
    eye_x = 0.25
    eye_y = -0.82
    eye_z = 0.15
    for side, sign in [("L", -1), ("R", 1)]:
        # Happy crescent arc eye
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.10, minor_radius=0.025,
            location=(sign * eye_x, eye_y, eye_z),
            rotation=(math.radians(75), 0, 0)
        )
        arc = bpy.context.active_object
        arc.name = f"Ghost_Wanderer_ArcEye_{side}"
        arc.scale = (1.0, 0.4, 0.9)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        arc.data.materials.append(mats["eyes"])
        arc.parent = head
        collection.objects.link(arc)

    # Open happy D-mouth (:D)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.14, depth=0.12,
        location=(0, -0.84, -0.05),
        rotation=(math.radians(90), 0, 0)
    )
    mouth = bpy.context.active_object
    mouth.name = "Ghost_Wanderer_Mouth"
    mouth.scale = (1.15, 0.25, 0.85)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mats["mouth"])
    mouth.parent = head
    collection.objects.link(mouth)

    # Pink tongue inside mouth
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.08,
        location=(0, -0.85, -0.09)
    )
    tongue = bpy.context.active_object
    tongue.name = "Ghost_Wanderer_Tongue"
    tongue.scale = (1.2, 0.35, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    tongue.data.materials.append(mats["tongue"])
    tongue.parent = head
    collection.objects.link(tongue)

def setup_studio_lighting(collection):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_GhostStudio")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Warm pleasant studio tint
        bg.inputs['Color'].default_value = (0.95, 0.93, 0.90, 1.0)
        bg.inputs['Strength'].default_value = 0.85

    sun_data = bpy.data.lights.new("Sun_Key", 'SUN')
    sun_data.color = (1.0, 0.96, 0.88)
    sun_data.energy = 4.8
    sun_data.angle = math.radians(10)
    sun_obj = bpy.data.objects.new("Sun_Key", sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill_data.color = (0.90, 0.95, 1.0)
    fill_data.energy = 2.0
    fill_data.angle = math.radians(25)
    fill_obj = bpy.data.objects.new("Sun_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("Rim_Light", 'POINT')
    rim_data.color = (1.0, 0.88, 0.72)
    rim_data.energy = 60.0
    rim_data.shadow_soft_size = 0.5
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (0, 3.0, 1.6)
    collection.objects.link(rim_obj)

def render_lineup_and_turnarounds(col, follower, cutter, wanderer):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.image_settings.file_format = 'PNG'

    cam_data = bpy.data.cameras.new("Cam_Lineup")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 7.8
    cam_obj = bpy.data.objects.new("Cam_Lineup", cam_data)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    # 1. Hero Lineup (All 3 side by side)
    cam_obj.location = (0, -4.8, 0.2)
    cam_obj.rotation_euler = (math.radians(85), 0, 0)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    out_lineup = "D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/spirits_hero_lineup_v2.png"
    scene.render.filepath = out_lineup
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Hero Lineup -> {out_lineup}")

    # 2. Individual Turnarounds
    ghosts = [
        ("ghost_follower", follower, -2.6),
        ("ghost_cutter", cutter, 0.0),
        ("ghost_wanderer", wanderer, 2.6)
    ]
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    cam_data.ortho_scale = 3.6

    for name, root, gx in ghosts:
        views = [
            ("front", (gx, -3.8, 0.1), (math.radians(88), 0, 0)),
            ("34view", (gx + 2.5, -2.5, 0.9), (math.radians(75), 0, math.radians(45))),
            ("side", (gx + 3.8, 0, 0.1), (math.radians(88), 0, math.radians(90))),
        ]
        for vname, loc, rot in views:
            cam_obj.location = loc
            cam_obj.rotation_euler = rot
            out_view = f"D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/{name}_{vname}_v2.png"
            scene.render.filepath = out_view
            bpy.ops.render.render(write_still=True)
            print(f"  ✓ Rendered {name}_{vname} -> {out_view}")

def export_assets(follower, cutter, wanderer):
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved master Ghosts scene: {blend_path}")

    # Export individual FBXs centered at origin
    for name, root in [("ghost_follower_validated", follower),
                       ("ghost_cutter_validated", cutter),
                       ("ghost_wanderer_validated", wanderer)]:
        orig_loc = root.location.copy()
        root.location = (0, 0, 0)
        bpy.context.view_layer.update()

        fbx_path = f"D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/{name}.fbx"
        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            use_selection=False,
            apply_scale_options='FBX_SCALE_ALL',
            bake_space_transform=True,
            axis_forward='-Z',
            axis_up='Y'
        )
        print(f"  ✓ Exported FBX: {fbx_path}")
        root.location = orig_loc

def main():
    print("=== Building Refined Multi-Tail Fluffy Ghosts (v7) ===")
    col = reset_scene()
    ghost_mat = create_fluffy_ghost_material()
    face_mats = create_face_materials()

    # Build 3 Ghosts in lineup positions (x = -2.6, 0.0, +2.6)
    follower = build_multitail_ghost_body("Ghost_Follower", -2.6, ghost_mat)
    col.objects.link(follower)
    add_follower_face(follower, face_mats, col)

    cutter = build_multitail_ghost_body("Ghost_Cutter", 0.0, ghost_mat)
    col.objects.link(cutter)
    add_cutter_face(cutter, face_mats, col)

    wanderer = build_multitail_ghost_body("Ghost_Wanderer", 2.6, ghost_mat)
    col.objects.link(wanderer)
    add_wanderer_face(wanderer, face_mats, col)

    setup_studio_lighting(col)
    export_assets(follower, cutter, wanderer)
    render_lineup_and_turnarounds(col, follower, cutter, wanderer)
    print("=== Refined Multi-Tail Fluffy Ghosts Complete ===")

if __name__ == "__main__":
    main()
