import bpy
import bmesh
import math
from mathutils import Vector, Euler

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for item in b:
            b.remove(item)

def create_golumolu_materials():
    # 1. Fluffy Peach-Orange Fur Material
    m_fur = bpy.data.materials.new("M_Golumolu_Fluffy_Fur")
    m_fur.use_nodes = True
    nodes = m_fur.node_tree.nodes
    links = m_fur.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    # Warm peach/orange-cream base color gradient
    tex_coord = nodes.new("ShaderNodeTexCoord")
    sep_xyz = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")
    
    # Bottom: Warm Cream (#FCEEDD -> 0.988, 0.933, 0.867)
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.988, 0.933, 0.867, 1.0)
    # Top/Back: Soft Peach-Orange (#FFB388 -> 1.0, 0.702, 0.533)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (1.0, 0.702, 0.533, 1.0)
    
    links.new(tex_coord.outputs["Generated"], sep_xyz.inputs["Vector"])
    links.new(sep_xyz.outputs["Z"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    # Fluffy parameters
    bsdf.inputs["Roughness"].default_value = 0.55
    # Subsurface scattering
    bsdf.inputs["Subsurface Weight"].default_value = 0.45
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.65, 0.45)
    bsdf.inputs["Subsurface Scale"].default_value = 0.1
    # Velvet peach fuzz sheen
    bsdf.inputs["Sheen Weight"].default_value = 1.0
    bsdf.inputs["Sheen Roughness"].default_value = 0.4
    bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.85, 0.75, 1.0)

    # Procedural micro-strand hair bump
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 95.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.7
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.02
    
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # 2. Accent Peach (Ears, spikes, tail tip)
    m_peach = bpy.data.materials.new("M_Golumolu_Peach_Accent")
    m_peach.use_nodes = True
    b_p = m_peach.node_tree.nodes.get("Principled BSDF")
    b_p.inputs["Base Color"].default_value = (1.0, 0.68, 0.48, 1.0)
    b_p.inputs["Roughness"].default_value = 0.45
    b_p.inputs["Subsurface Weight"].default_value = 0.45
    b_p.inputs["Sheen Weight"].default_value = 0.8

    # 3. Soft Pink Blush Cheeks
    m_blush = bpy.data.materials.new("M_Golumolu_Cheeks")
    m_blush.use_nodes = True
    b_b = m_blush.node_tree.nodes.get("Principled BSDF")
    b_b.inputs["Base Color"].default_value = (1.0, 0.62, 0.62, 1.0)
    b_b.inputs["Roughness"].default_value = 0.65
    b_b.inputs["Subsurface Weight"].default_value = 0.6

    # 4. Eyes (Deep glossy anime black)
    m_eye = bpy.data.materials.new("M_Golumolu_Eyes")
    m_eye.use_nodes = True
    b_e = m_eye.node_tree.nodes.get("Principled BSDF")
    b_e.inputs["Base Color"].default_value = (0.05, 0.04, 0.04, 1.0)
    b_e.inputs["Roughness"].default_value = 0.05

    # 5. Upper Shine Patch (Pure white happy catchlight)
    m_shine = bpy.data.materials.new("M_Golumolu_Eye_Shine")
    m_shine.use_nodes = True
    b_s = m_shine.node_tree.nodes.get("Principled BSDF")
    b_s.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_s.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_s.inputs["Emission Strength"].default_value = 2.0
    b_s.inputs["Roughness"].default_value = 0.0

    # 6. Mouth & Tongue
    m_mouth = bpy.data.materials.new("M_Golumolu_Mouth")
    m_mouth.use_nodes = True
    b_m = m_mouth.node_tree.nodes.get("Principled BSDF")
    b_m.inputs["Base Color"].default_value = (0.68, 0.22, 0.25, 1.0)
    b_m.inputs["Roughness"].default_value = 0.35

    m_tongue = bpy.data.materials.new("M_Golumolu_Tongue")
    m_tongue.use_nodes = True
    b_t = m_tongue.node_tree.nodes.get("Principled BSDF")
    b_t.inputs["Base Color"].default_value = (1.0, 0.55, 0.58, 1.0)
    b_t.inputs["Roughness"].default_value = 0.25

    return m_fur, m_peach, m_blush, m_eye, m_shine, m_mouth, m_tongue

def build_golumolu_v12():
    m_fur, m_peach, m_blush, m_eye, m_shine, m_mouth, m_tongue = create_golumolu_materials()

    root = bpy.data.objects.new("Golumolu_v12_Master", None)
    bpy.context.collection.objects.link(root)

    # 1. Main Chubby Body (Slightly squished pear/sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=1.0)
    body = bpy.context.active_object
    body.name = "golumolu_body"
    body.scale = (1.08, 0.98, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_fur)
    body.parent = root
    
    sub = body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 2. Cute Chubby Dinosaur Tail
    # Elegant curved cone tapering backwards and curving up
    curve_data = bpy.data.curves.new(name="tail_curve", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(2)
    
    spline.bezier_points[0].co = Vector((0.0, -0.65, -0.15))
    spline.bezier_points[0].radius = 0.45
    spline.bezier_points[1].co = Vector((0.0, -1.25, 0.0))
    spline.bezier_points[1].radius = 0.30
    spline.bezier_points[2].co = Vector((0.0, -1.85, 0.25))
    spline.bezier_points[2].radius = 0.10
    
    for bp in spline.bezier_points:
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    curve_data.bevel_depth = 1.0
    curve_data.bevel_resolution = 8
    tail_obj = bpy.data.objects.new("golumolu_tail", curve_data)
    bpy.context.collection.objects.link(tail_obj)
    tail_obj.parent = root
    
    # Convert to mesh
    bpy.context.view_layer.objects.active = tail_obj
    tail_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    tail_mesh = bpy.context.active_object
    tail_mesh.data.materials.append(m_fur)
    tail_sub = tail_mesh.modifiers.new("Subsurf", 'SUBSURF')
    tail_sub.levels = 1
    bpy.ops.object.shade_smooth()

    # Soft round ball tip on tail
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, segments=16, ring_count=12)
    tail_tip = bpy.context.active_object
    tail_tip.name = "golumolu_tail_tip"
    tail_tip.location = (0.0, -1.90, 0.28)
    tail_tip.data.materials.append(m_peach)
    tail_tip.parent = root
    bpy.ops.object.shade_smooth()

    # 3. Godzilla Dorsal Spikes (4 stepped soft triangular fin plates along spine)
    spikes_config = [
        {"y": 0.25,  "z": 0.98, "scale": (0.06, 0.16, 0.24), "rot_x": 12},
        {"y": -0.15, "z": 0.96, "scale": (0.06, 0.18, 0.28), "rot_x": 5},
        {"y": -0.55, "z": 0.82, "scale": (0.05, 0.16, 0.24), "rot_x": -10},
        {"y": -0.95, "z": 0.58, "scale": (0.04, 0.13, 0.18), "rot_x": -25},
    ]
    for i, sc in enumerate(spikes_config):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=16, ring_count=12)
        sp = bpy.context.active_object
        sp.name = f"godzilla_spike_{i+1}"
        sp.location = (0.0, sc["y"], sc["z"])
        sp.scale = sc["scale"]
        sp.rotation_euler = (math.radians(sc["rot_x"]), 0, 0)
        sp.data.materials.append(m_peach)
        sp.parent = root
        bpy.ops.object.shade_smooth()

    # 4. Adorable Peach Ears
    for side, x in [("L", -0.58), ("R", 0.58)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, segments=20, ring_count=16)
        ear = bpy.context.active_object
        ear.name = f"golumolu_ear_{side}"
        ear.location = (x, 0.12, 0.85)
        ear.scale = (0.85, 0.75, 1.1)
        ear.rotation_euler = (math.radians(-10), math.radians(-22 if side=="L" else 22), 0)
        ear.data.materials.append(m_peach)
        ear.parent = root
        bpy.ops.object.shade_smooth()

    # 5. Facial Features:
    # Big glossy anime black eyes with white upper patch + secondary twinkle
    for side, x in [("L", -0.36), ("R", 0.36)]:
        # Eye base
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=24, ring_count=20)
        eye = bpy.context.active_object
        eye.name = f"golumolu_eye_{side}"
        eye.location = (x, 0.90, 0.16)
        eye.scale = (0.85, 0.38, 1.25)
        eye.rotation_euler = (math.radians(-12), 0, math.radians(5 if side=="L" else -5))
        eye.data.materials.append(m_eye)
        eye.parent = root

        # Large Upper White Shine Patch (covering upper half)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=16, ring_count=12)
        sh_main = bpy.context.active_object
        sh_main.name = f"golumolu_shine_main_{side}"
        sh_main.location = (x + (0.02 if side=="L" else -0.02), 0.96, 0.24)
        sh_main.scale = (0.9, 0.35, 0.85)
        sh_main.data.materials.append(m_shine)
        sh_main.parent = root

        # Tiny Secondary Twinkle Dot
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, segments=12, ring_count=8)
        sh_sub = bpy.context.active_object
        sh_sub.name = f"golumolu_shine_sub_{side}"
        sh_sub.location = (x - (0.03 if side=="L" else -0.03), 0.95, 0.10)
        sh_sub.scale = (0.8, 0.3, 0.8)
        sh_sub.data.materials.append(m_shine)
        sh_sub.parent = root

    # Rosy Cheeks (Soft blush ovals)
    for side, x in [("L", -0.62), ("R", 0.62)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, segments=20, ring_count=16)
        bl = bpy.context.active_object
        bl.name = f"golumolu_blush_{side}"
        bl.location = (x, 0.72, -0.02)
        bl.scale = (1.1, 0.35, 0.75)
        bl.rotation_euler = (math.radians(-15), 0, math.radians(15 if side=="L" else -15))
        bl.data.materials.append(m_blush)
        bl.parent = root

    # Happy Open Mouth with Pink Tongue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, segments=20, ring_count=16)
    mouth = bpy.context.active_object
    mouth.name = "golumolu_mouth"
    mouth.location = (0.0, 0.99, -0.04)
    mouth.scale = (0.95, 0.35, 0.95)
    mouth.data.materials.append(m_mouth)
    mouth.parent = root

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, segments=16, ring_count=12)
    tongue = bpy.context.active_object
    tongue.name = "golumolu_tongue"
    tongue.location = (0.0, 1.02, -0.08)
    tongue.scale = (0.9, 0.3, 0.7)
    tongue.data.materials.append(m_tongue)
    tongue.parent = root

    # 6. Tiny Chubby Paws and Feet
    # Paws (hands reaching forward playfully)
    for side, x in [("L", -0.45), ("R", 0.45)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, segments=16, ring_count=12)
        paw = bpy.context.active_object
        paw.name = f"golumolu_paw_{side}"
        paw.location = (x, 0.75, -0.32)
        paw.scale = (0.85, 1.15, 0.75)
        paw.rotation_euler = (math.radians(-25), 0, math.radians(12 if side=="L" else -12))
        paw.data.materials.append(m_peach)
        paw.parent = root
        bpy.ops.object.shade_smooth()

    # Feet (little round pads underneath)
    for side, x in [("L", -0.38), ("R", 0.38)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, segments=16, ring_count=12)
        foot = bpy.context.active_object
        foot.name = f"golumolu_foot_{side}"
        foot.location = (x, -0.10, -0.88)
        foot.scale = (0.95, 1.25, 0.65)
        foot.data.materials.append(m_peach)
        foot.parent = root
        bpy.ops.object.shade_smooth()

    return root

def render_golumolu_validation_views():
    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    # Soft warm peach-cream background matching Ref 2
    bg.inputs["Color"].default_value = (0.98, 0.94, 0.90, 1.0)
    bg.inputs["Strength"].default_value = 0.95

    # Key Light
    sun = bpy.data.lights.new("Sun_Key", 'SUN')
    sun.energy = 3.8
    sun.color = (1.0, 0.95, 0.88)
    sun.angle = math.radians(12)
    sun_obj = bpy.data.objects.new("Sun_Key", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    bpy.context.collection.objects.link(sun_obj)

    # Fill Light
    fill = bpy.data.lights.new("Fill_Light", 'POINT')
    fill.energy = 140.0
    fill.color = (0.92, 0.96, 1.0)
    fill.shadow_soft_size = 1.0
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    fill_obj.location = (-2.5, 3.0, 1.5)
    bpy.context.collection.objects.link(fill_obj)

    # Warm Rim Light
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.energy = 200.0
    rim.color = (1.0, 0.85, 0.68)
    rim.shadow_soft_size = 0.8
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.0, -3.0, 2.5)
    bpy.context.collection.objects.link(rim_obj)

    root = build_golumolu_v12()

    # Camera setup
    cam_data = bpy.data.cameras.new("Cam_Validation")
    cam_data.type = 'PERSP'
    cam_data.lens = 75
    cam_obj = bpy.data.objects.new("Cam_Validation", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    views = [
        {"name": "front",  "loc": (0.0, 4.2, 0.0),    "rot": (math.radians(90), 0, math.radians(180))},
        {"name": "34view", "loc": (-2.8, 3.2, 0.8),   "rot": (math.radians(80), 0, math.radians(220))},
        {"name": "side",   "loc": (-4.2, 0.0, 0.0),   "rot": (math.radians(90), 0, math.radians(270))},
        {"name": "back",   "loc": (0.0, -4.2, 0.0),   "rot": (math.radians(90), 0, math.radians(0))},
    ]

    for v in views:
        cam_obj.location = v["loc"]
        cam_obj.rotation_euler = v["rot"]
        out_path = f"D:/Projects/MOMO MAZE/BlenderSources/renders/golumolu/golumolu_v012_{v['name']}.png"
        scene.render.filepath = out_path
        print(f"Rendering Golumolu v12 {v['name']} -> {out_path}")
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ Saved {v['name']}")

    # Save Blend file & Export FBX
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved Validated Golumolu Blend -> {blend_path}")

    # Export FBX
    fbx_path = "D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/golumolu_validated.fbx"
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=False, apply_scale_options='FBX_SCALE_ALL')
    print(f"  ✓ Exported Validated Golumolu FBX -> {fbx_path}")

if __name__ == "__main__":
    reset_scene()
    render_golumolu_validation_views()
