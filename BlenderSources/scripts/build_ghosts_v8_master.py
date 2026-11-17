"""
build_ghosts_v8_master.py
MOMO MAZE - Master Multi-Tail Fluffy Ghost Spirits (Blender 5.2)

Fixed parenting & transforms + Big Expressive Chibi Eyes:
- 4 distinct trailing wisp tails (top crest, main center, lower-left, lower-right)
- Big expressive dark eyes with prominent white catchlight shine patches:
  * Follower: Big curious glossy oval eyes with double catchlights
  * Cutter: Mischievous slanted eyes with focused brow ridges (:>)
  * Wanderer: Joyful crescent arc eyes and wide open D-smile (:D) with tongue
- Velvety cloud-fuzz texture with peach-fuzz sheen and warm translucent SSS
- Dynamic 3/4 floating hero lineup render matching Reference Image 3 Hero Banner
- Turnaround renders + master blend + FBX exports
"""

import bpy
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Ghosts_Master")
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

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 3.5
    noise.inputs['Roughness'].default_value = 0.55
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.97, 0.95, 0.92, 1.0)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (1.00, 0.99, 0.97, 1.0)
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = (0.7, 0.55, 0.4)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.45

    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.95
        bsdf.inputs['Sheen Roughness'].default_value = 0.35
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.95

    bsdf.inputs['Roughness'].default_value = 0.48

    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.92, 0.78, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.35
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.92, 0.78, 1.0)

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_face_materials():
    mat_eyes = bpy.data.materials.new("M_Ghost_Eyes")
    mat_eyes.use_nodes = True
    bsdf = get_principled_bsdf(mat_eyes)
    bsdf.inputs['Base Color'].default_value = (0.08, 0.05, 0.03, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.95

    mat_shine = bpy.data.materials.new("M_Ghost_EyeCatchlight")
    mat_shine.use_nodes = True
    bsdf_sh = get_principled_bsdf(mat_shine)
    bsdf_sh.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_sh.inputs['Roughness'].default_value = 0.02
    if 'Emission Color' in bsdf_sh.inputs:
        bsdf_sh.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf_sh.inputs['Emission Strength'].default_value = 2.0

    mat_mouth = bpy.data.materials.new("M_Ghost_Mouth")
    mat_mouth.use_nodes = True
    bsdf_m = get_principled_bsdf(mat_mouth)
    bsdf_m.inputs['Base Color'].default_value = (0.50, 0.12, 0.12, 1.0)
    bsdf_m.inputs['Roughness'].default_value = 0.35

    mat_tongue = bpy.data.materials.new("M_Ghost_Tongue")
    mat_tongue.use_nodes = True
    bsdf_t = get_principled_bsdf(mat_tongue)
    bsdf_t.inputs['Base Color'].default_value = (1.0, 0.45, 0.45, 1.0)
    bsdf_t.inputs['Roughness'].default_value = 0.3

    return {"eyes": mat_eyes, "shine": mat_shine, "mouth": mat_mouth, "tongue": mat_tongue}

def build_multitail_ghost_mesh(prefix, ghost_mat):
    """
    Constructs the horizontal aerodynamic wisp body centered at origin (0,0,0) with 4 distinct trailing wisp tails.
    """
    # 1. Main Head
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=28, radius=0.85, location=(0, 0, 0))
    head = bpy.context.active_object
    head.name = f"{prefix}_Head"
    head.scale = (1.0, 1.15, 0.95)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    head.data.materials.append(ghost_mat)
    bpy.ops.object.shade_smooth()

    # 2. Tail 1: Top Crest Wisp
    t1_segments = [
        (0, 0.70, 0.55, 0.36),
        (0, 1.25, 0.78, 0.26),
        (0, 1.75, 0.95, 0.16),
        (0, 2.15, 1.05, 0.08)
    ]
    t1_objs = []
    for i, (tx, ty, tz, tr) in enumerate(t1_segments):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=tr, location=(tx, ty, tz))
        obj = bpy.context.active_object
        obj.scale = (0.8, 1.4, 0.7)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        t1_objs.append(obj)

    # 3. Tail 2: Main Center Wisp
    t2_segments = [
        (0, 0.90, 0.05, 0.46),
        (0, 1.60, 0.12, 0.34),
        (0, 2.25, 0.20, 0.22),
        (0, 2.85, 0.26, 0.12),
        (0, 3.30, 0.30, 0.05)
    ]
    t2_objs = []
    for i, (tx, ty, tz, tr) in enumerate(t2_segments):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=tr, location=(tx, ty, tz))
        obj = bpy.context.active_object
        obj.scale = (0.85, 1.5, 0.75)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        t2_objs.append(obj)

    # 4. Tail 3: Lower-Left Tail Wisp
    t3_segments = [
        (-0.35, 0.85, -0.30, 0.32),
        (-0.60, 1.45, -0.42, 0.22),
        (-0.80, 2.00, -0.52, 0.13),
        (-0.95, 2.45, -0.58, 0.06)
    ]
    t3_objs = []
    for i, (tx, ty, tz, tr) in enumerate(t3_segments):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=tr, location=(tx, ty, tz))
        obj = bpy.context.active_object
        obj.scale = (0.8, 1.4, 0.7)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        t3_objs.append(obj)

    # 5. Tail 4: Lower-Right Tail Wisp
    t4_segments = [
        (0.35, 0.85, -0.30, 0.32),
        (0.60, 1.45, -0.42, 0.22),
        (0.80, 2.00, -0.52, 0.13),
        (0.95, 2.45, -0.58, 0.06)
    ]
    t4_objs = []
    for i, (tx, ty, tz, tr) in enumerate(t4_segments):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=tr, location=(tx, ty, tz))
        obj = bpy.context.active_object
        obj.scale = (0.8, 1.4, 0.7)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        t4_objs.append(obj)

    all_parts = [head] + t1_objs + t2_objs + t3_objs + t4_objs
    bpy.ops.object.select_all(action='DESELECT')
    for p in all_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()

    remesh = head.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.034
    remesh.adaptivity = 0.0
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    smooth = head.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.75
    smooth.iterations = 4
    bpy.ops.object.modifier_apply(modifier="Smooth")

    tex = bpy.data.textures.new(f"{prefix}_CloudDisplace", 'CLOUDS')
    tex.noise_scale = 0.32
    tex.noise_depth = 2
    disp = head.modifiers.new("Displace", 'DISPLACE')
    disp.texture = tex
    disp.strength = 0.020
    bpy.ops.object.modifier_apply(modifier="Displace")

    subdiv = head.modifiers.new("Subdiv", 'SUBSURF')
    subdiv.levels = 1
    subdiv.render_levels = 1

    bpy.ops.object.shade_smooth()
    head.data.materials.clear()
    head.data.materials.append(ghost_mat)

    return head

def add_follower_face(head, mats, collection):
    """Follower: Big curious glossy vertical oval eyes with double sparkling catchlights"""
    eye_x = 0.30
    eye_y = -0.76
    eye_z = 0.14
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(sign * eye_x, eye_y, eye_z))
        eye = bpy.context.active_object
        eye.name = f"Ghost_Follower_Eye_{side}"
        eye.scale = (0.85, 0.40, 1.35)
        eye.rotation_euler = (math.radians(15), sign * math.radians(-6), 0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eyes"])
        eye.parent = head
        collection.objects.link(eye)

        # Large Upper catchlight shine patch
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.085,
            location=(sign * (eye_x - 0.035 * sign), eye_y - 0.06, eye_z + 0.08)
        )
        shine = bpy.context.active_object
        shine.name = f"Ghost_Follower_Shine_{side}"
        shine.scale = (1.0, 0.22, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mats["shine"])
        shine.parent = head
        collection.objects.link(shine)

        # Lower twinkle
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.045,
            location=(sign * (eye_x + 0.045 * sign), eye_y - 0.05, eye_z - 0.06)
        )
        twinkle = bpy.context.active_object
        twinkle.name = f"Ghost_Follower_Twinkle_{side}"
        twinkle.scale = (1.0, 0.22, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        twinkle.data.materials.append(mats["shine"])
        twinkle.parent = head
        collection.objects.link(twinkle)

def add_cutter_face(head, mats, collection):
    """Cutter: Mischievous angled eyes with focused eyebrows (:>)"""
    eye_x = 0.32
    eye_y = -0.76
    eye_z = 0.14
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(sign * eye_x, eye_y, eye_z))
        eye = bpy.context.active_object
        eye.name = f"Ghost_Cutter_Eye_{side}"
        eye.scale = (0.90, 0.35, 1.15)
        eye.rotation_euler = (math.radians(15), 0, sign * math.radians(-28))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eyes"])
        eye.parent = head
        collection.objects.link(eye)

        # Catchlight
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.08,
            location=(sign * (eye_x - 0.025 * sign), eye_y - 0.05, eye_z + 0.06)
        )
        shine = bpy.context.active_object
        shine.name = f"Ghost_Cutter_Shine_{side}"
        shine.scale = (1.0, 0.22, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mats["shine"])
        shine.parent = head
        collection.objects.link(shine)

        # Focused brow ridge
        bpy.ops.mesh.primitive_cube_add(
            size=0.20,
            location=(sign * eye_x, eye_y - 0.03, eye_z + 0.16)
        )
        brow = bpy.context.active_object
        brow.name = f"Ghost_Cutter_Brow_{side}"
        brow.scale = (1.25, 0.30, 0.35)
        brow.rotation_euler = (math.radians(15), 0, sign * math.radians(-32))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        brow.data.materials.append(mats["eyes"])
        brow.parent = head
        collection.objects.link(brow)

def add_wanderer_face(head, mats, collection):
    """Wanderer: Joyful happy crescent arc eyes and open D-smile (:D) with tongue"""
    eye_x = 0.32
    eye_y = -0.80
    eye_z = 0.18
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.14, minor_radius=0.035,
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

    # Wide open happy D-mouth (:D)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.20, depth=0.15,
        location=(0, -0.82, -0.05),
        rotation=(math.radians(90), 0, 0)
    )
    mouth = bpy.context.active_object
    mouth.name = "Ghost_Wanderer_Mouth"
    mouth.scale = (1.25, 0.30, 0.95)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mats["mouth"])
    mouth.parent = head
    collection.objects.link(mouth)

    # Pink tongue
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.11,
        location=(0, -0.84, -0.10)
    )
    tongue = bpy.context.active_object
    tongue.name = "Ghost_Wanderer_Tongue"
    tongue.scale = (1.25, 0.45, 0.6)
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
        bg.inputs['Color'].default_value = (0.96, 0.94, 0.91, 1.0)
        bg.inputs['Strength'].default_value = 0.90

    sun_data = bpy.data.lights.new("Sun_Key", 'SUN')
    sun_data.color = (1.0, 0.96, 0.88)
    sun_data.energy = 5.2
    sun_data.angle = math.radians(10)
    sun_obj = bpy.data.objects.new("Sun_Key", sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill_data.color = (0.90, 0.95, 1.0)
    fill_data.energy = 2.2
    fill_data.angle = math.radians(25)
    fill_obj = bpy.data.objects.new("Sun_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("Rim_Light", 'POINT')
    rim_data.color = (1.0, 0.88, 0.72)
    rim_data.energy = 75.0
    rim_data.shadow_soft_size = 0.5
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (0, 3.2, 1.8)
    collection.objects.link(rim_obj)

def render_lineup_and_turnarounds(col, follower, cutter, wanderer):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.image_settings.file_format = 'PNG'

    cam_data = bpy.data.cameras.new("Cam_Lineup")
    cam_data.type = 'ORTHO'
    cam_obj = bpy.data.objects.new("Cam_Lineup", cam_data)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    # Lineup positions: Follower at x = -2.8, Cutter at x = 0.0, Wanderer at x = +2.8
    # Rotate each so head faces forward-right (35 deg) and tails trail back-left
    follower.location = (-2.8, 0, 0)
    cutter.location = (0.0, 0, 0)
    wanderer.location = (2.8, 0, 0)

    follower.rotation_euler = (math.radians(8), math.radians(-10), math.radians(-35))
    cutter.rotation_euler = (math.radians(10), math.radians(-8), math.radians(-35))
    wanderer.rotation_euler = (math.radians(6), math.radians(-12), math.radians(-35))
    bpy.context.view_layer.update()

    cam_data.ortho_scale = 10.5
    cam_obj.location = (0, -5.5, 1.2)
    cam_obj.rotation_euler = (math.radians(78), 0, 0)
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 900
    out_lineup = "D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/spirits_hero_lineup_v2.png"
    scene.render.filepath = out_lineup
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Hero Lineup -> {out_lineup}")

    # Reset rotations for turnarounds
    for g in [follower, cutter, wanderer]:
        g.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

    # Individual Turnarounds
    ghosts = [
        ("ghost_follower", follower, -2.8),
        ("ghost_cutter", cutter, 0.0),
        ("ghost_wanderer", wanderer, 2.8)
    ]
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    cam_data.ortho_scale = 4.2

    for name, root, gx in ghosts:
        views = [
            ("front", (gx, -4.0, 0.2), (math.radians(88), 0, 0)),
            ("34view", (gx + 2.8, -2.8, 1.2), (math.radians(75), 0, math.radians(45))),
            ("side", (gx + 4.2, 0, 0.2), (math.radians(88), 0, math.radians(90))),
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

    for name, root in [("ghost_follower_validated", follower),
                       ("ghost_cutter_validated", cutter),
                       ("ghost_wanderer_validated", wanderer)]:
        orig_loc = root.location.copy()
        orig_rot = root.rotation_euler.copy()
        root.location = (0, 0, 0)
        root.rotation_euler = (0, 0, 0)
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
        root.rotation_euler = orig_rot

def main():
    print("=== Building Master Multi-Tail Fluffy Ghosts (v8 Fixed) ===")
    col = reset_scene()
    ghost_mat = create_fluffy_ghost_material()
    face_mats = create_face_materials()

    # Build all ghosts centered at origin initially so child parenting is 100% accurate
    follower = build_multitail_ghost_mesh("Ghost_Follower", ghost_mat)
    col.objects.link(follower)
    add_follower_face(follower, face_mats, col)

    cutter = build_multitail_ghost_mesh("Ghost_Cutter", ghost_mat)
    col.objects.link(cutter)
    add_cutter_face(cutter, face_mats, col)

    wanderer = build_multitail_ghost_mesh("Ghost_Wanderer", ghost_mat)
    col.objects.link(wanderer)
    add_wanderer_face(wanderer, face_mats, col)

    # Offset positions after parenting
    follower.location = (-2.8, 0, 0)
    cutter.location = (0.0, 0, 0)
    wanderer.location = (2.8, 0, 0)
    bpy.context.view_layer.update()

    setup_studio_lighting(col)
    export_assets(follower, cutter, wanderer)
    render_lineup_and_turnarounds(col, follower, cutter, wanderer)
    print("=== Master Multi-Tail Fluffy Ghosts Complete ===")

if __name__ == "__main__":
    main()
