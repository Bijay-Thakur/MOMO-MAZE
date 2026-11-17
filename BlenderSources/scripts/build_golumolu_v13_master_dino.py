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
    # 1. Fluffy Peach-Orange Fur Material (matching Ref 2 and user prompt)
    m_fur = bpy.data.materials.new("M_Golumolu_Fluffy_Fur")
    m_fur.use_nodes = True
    nodes = m_fur.node_tree.nodes
    links = m_fur.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    # Warm peach/orange-cream vertical gradient
    tex_coord = nodes.new("ShaderNodeTexCoord")
    sep_xyz = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")
    
    # Bottom: Warm Cream (#FFF0E2)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (1.0, 0.94, 0.88, 1.0)
    # Top/Back: Rich Peach-Orange (#FFA46B)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (1.0, 0.64, 0.42, 1.0)
    
    links.new(tex_coord.outputs["Generated"], sep_xyz.inputs["Vector"])
    links.new(sep_xyz.outputs["Z"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    # Fluffy parameters
    bsdf.inputs["Roughness"].default_value = 0.52
    # Subsurface scattering
    bsdf.inputs["Subsurface Weight"].default_value = 0.50
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.65, 0.45)
    bsdf.inputs["Subsurface Scale"].default_value = 0.12
    # Velvet peach fuzz sheen
    bsdf.inputs["Sheen Weight"].default_value = 1.0
    bsdf.inputs["Sheen Roughness"].default_value = 0.40
    bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.85, 0.70, 1.0)

    # Procedural micro-strand hair bump
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 110.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.02
    
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # 2. Vibrant Peach Accent (Ears, Godzilla spikes, tail tip)
    m_peach = bpy.data.materials.new("M_Golumolu_Peach_Accent")
    m_peach.use_nodes = True
    b_p = m_peach.node_tree.nodes.get("Principled BSDF")
    b_p.inputs["Base Color"].default_value = (1.0, 0.62, 0.40, 1.0)
    b_p.inputs["Roughness"].default_value = 0.45
    b_p.inputs["Subsurface Weight"].default_value = 0.50
    b_p.inputs["Subsurface Radius"].default_value = (1.0, 0.6, 0.4)
    b_p.inputs["Sheen Weight"].default_value = 0.85

    # 3. Soft Rosy Blush Cheeks (#FF8A96)
    m_blush = bpy.data.materials.new("M_Golumolu_Cheeks")
    m_blush.use_nodes = True
    b_b = m_blush.node_tree.nodes.get("Principled BSDF")
    b_b.inputs["Base Color"].default_value = (1.0, 0.54, 0.58, 1.0)
    b_b.inputs["Roughness"].default_value = 0.65
    b_b.inputs["Subsurface Weight"].default_value = 0.65

    # 4. Deep Glossy Anime Black Eyes
    m_eye = bpy.data.materials.new("M_Golumolu_Eyes")
    m_eye.use_nodes = True
    b_e = m_eye.node_tree.nodes.get("Principled BSDF")
    b_e.inputs["Base Color"].default_value = (0.04, 0.035, 0.035, 1.0)
    b_e.inputs["Roughness"].default_value = 0.05

    # 5. Pure White Catchlight Shine
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
    b_m.inputs["Base Color"].default_value = (0.72, 0.18, 0.22, 1.0)
    b_m.inputs["Roughness"].default_value = 0.35

    m_tongue = bpy.data.materials.new("M_Golumolu_Tongue")
    m_tongue.use_nodes = True
    b_t = m_tongue.node_tree.nodes.get("Principled BSDF")
    b_t.inputs["Base Color"].default_value = (1.0, 0.52, 0.56, 1.0)
    b_t.inputs["Roughness"].default_value = 0.25

    return m_fur, m_peach, m_blush, m_eye, m_shine, m_mouth, m_tongue

def build_golumolu_v13():
    m_fur, m_peach, m_blush, m_eye, m_shine, m_mouth, m_tongue = create_golumolu_materials()

    root = bpy.data.objects.new("Golumolu_v13_Master", None)
    bpy.context.collection.objects.link(root)

    # 1. Main Chubby Pear Body
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=1.0)
    body = bpy.context.active_object
    body.name = "golumolu_body"
    body.scale = (1.10, 1.02, 0.98)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_fur)
    body.parent = root
    
    sub = body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 2. Cute Chubby Dinosaur Tail (Curving upward playfully)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.48, radius2=0.08, depth=1.35)
    tail = bpy.context.active_object
    tail.name = "golumolu_tail"
    tail.location = (0.0, -1.05, 0.05)
    tail.rotation_euler = (math.radians(-115), 0, 0)
    tail.data.materials.append(m_fur)
    tail.parent = root
    tail_sub = tail.modifiers.new("Subsurf", 'SUBSURF')
    tail_sub.levels = 2
    bpy.ops.object.shade_smooth()

    # Soft round peach ball tip on tail
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=16, ring_count=12)
    tail_tip = bpy.context.active_object
    tail_tip.name = "golumolu_tail_tip"
    tail_tip.location = (0.0, -1.68, 0.32)
    tail_tip.data.materials.append(m_peach)
    tail_tip.parent = root
    bpy.ops.object.shade_smooth()

    # 3. Godzilla Dorsal Spikes (4 stepped soft rounded triangular fin plates)
    spikes_config = [
        {"y": 0.28,  "z": 1.02, "scale": (0.07, 0.18, 0.26), "rot_x": 15},
        {"y": -0.15, "z": 1.00, "scale": (0.07, 0.20, 0.30), "rot_x": 5},
        {"y": -0.58, "z": 0.85, "scale": (0.06, 0.18, 0.26), "rot_x": -15},
        {"y": -0.98, "z": 0.58, "scale": (0.05, 0.15, 0.20), "rot_x": -35},
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

    # 4. Cute Peach Ears (Round with peach interior)
    for side, x in [("L", -0.58), ("R", 0.58)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, segments=20, ring_count=16)
        ear = bpy.context.active_object
        ear.name = f"golumolu_ear_{side}"
        ear.location = (x, 0.15, 0.88)
        ear.scale = (0.85, 0.75, 1.10)
        ear.rotation_euler = (math.radians(-10), math.radians(-22 if side=="L" else 22), 0)
        ear.data.materials.append(m_peach)
        ear.parent = root
        bpy.ops.object.shade_smooth()

    # 5. Facial Features:
    # Big glossy anime black eyes with white upper patch + secondary twinkle
    for side, x in [("L", -0.36), ("R", 0.36)]:
        # Eye base
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.155, segments=24, ring_count=20)
        eye = bpy.context.active_object
        eye.name = f"golumolu_eye_{side}"
        eye.location = (x, 0.94, 0.16)
        eye.scale = (0.85, 0.36, 1.25)
        eye.rotation_euler = (math.radians(-12), 0, math.radians(5 if side=="L" else -5))
        eye.data.materials.append(m_eye)
        eye.parent = root

        # Large Upper White Shine Patch (covering top ~45%)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, segments=16, ring_count=12)
        sh_main = bpy.context.active_object
        sh_main.name = f"golumolu_shine_main_{side}"
        sh_main.location = (x + (0.02 if side=="L" else -0.02), 0.99, 0.24)
        sh_main.scale = (0.88, 0.32, 0.85)
        sh_main.data.materials.append(m_shine)
        sh_main.parent = root

        # Secondary Twinkle Dot
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.038, segments=12, ring_count=8)
        sh_sub = bpy.context.active_object
        sh_sub.name = f"golumolu_shine_sub_{side}"
        sh_sub.location = (x - (0.035 if side=="L" else -0.035), 0.98, 0.10)
        sh_sub.scale = (0.8, 0.3, 0.8)
        sh_sub.data.materials.append(m_shine)
        sh_sub.parent = root

    # Rosy Cheeks (Soft blush ovals)
    for side, x in [("L", -0.64), ("R", 0.64)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.165, segments=20, ring_count=16)
        bl = bpy.context.active_object
        bl.name = f"golumolu_blush_{side}"
        bl.location = (x, 0.74, -0.02)
        bl.scale = (1.15, 0.35, 0.75)
        bl.rotation_euler = (math.radians(-15), 0, math.radians(15 if side=="L" else -15))
        bl.data.materials.append(m_blush)
        bl.parent = root

    # Happy Open Smiling Arch Mouth
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, segments=20, ring_count=16)
    mouth = bpy.context.active_object
    mouth.name = "golumolu_mouth"
    mouth.location = (0.0, 1.02, -0.04)
    mouth.scale = (1.10, 0.35, 0.85)
    mouth.data.materials.append(m_mouth)
    mouth.parent = root

    # Cute Pink Tongue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=16, ring_count=12)
    tongue = bpy.context.active_object
    tongue.name = "golumolu_tongue"
    tongue.location = (0.0, 1.05, -0.08)
    tongue.scale = (0.95, 0.3, 0.65)
    tongue.data.materials.append(m_tongue)
    tongue.parent = root

    # 6. Tiny Chubby Paws and Feet
    for side, x in [("L", -0.46), ("R", 0.46)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=16, ring_count=12)
        paw = bpy.context.active_object
        paw.name = f"golumolu_paw_{side}"
        paw.location = (x, 0.78, -0.32)
        paw.scale = (0.85, 1.15, 0.75)
        paw.rotation_euler = (math.radians(-25), 0, math.radians(12 if side=="L" else -12))
        paw.data.materials.append(m_peach)
        paw.parent = root
        bpy.ops.object.shade_smooth()

    for side, x in [("L", -0.38), ("R", 0.38)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, segments=16, ring_count=12)
        foot = bpy.context.active_object
        foot.name = f"golumolu_foot_{side}"
        foot.location = (x, -0.10, -0.92)
        foot.scale = (0.95, 1.25, 0.65)
        foot.data.materials.append(m_peach)
        foot.parent = root
        bpy.ops.object.shade_smooth()

    # Soft round ground shadow disc
    bpy.ops.mesh.primitive_circle_add(radius=1.1, fill_type='NGON')
    shadow_disc = bpy.context.active_object
    shadow_disc.name = "soft_ground_shadow"
    shadow_disc.location = (0.0, -0.1, -1.02)
    
    m_shad = bpy.data.materials.new("M_Shadow_Disc")
    m_shad.use_nodes = True
    b_shd = m_shad.node_tree.nodes.get("Principled BSDF")
    b_shd.inputs["Base Color"].default_value = (0.82, 0.74, 0.68, 1.0)
    b_shd.inputs["Roughness"].default_value = 0.95
    shadow_disc.data.materials.append(m_shad)
    shadow_disc.parent = root

    return root

def render_golumolu_validation_views():
    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    # Soft warm peach-cream background matching Ref 2
    bg.inputs["Color"].default_value = (0.985, 0.95, 0.91, 1.0)
    bg.inputs["Strength"].default_value = 0.95

    # Key Light (Warm golden sunlight)
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
    fill_obj.location = (-2.5, 3.5, 1.5)
    bpy.context.collection.objects.link(fill_obj)

    # Warm Rim Light
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.energy = 200.0
    rim.color = (1.0, 0.85, 0.68)
    rim.shadow_soft_size = 0.8
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.0, -3.5, 2.5)
    bpy.context.collection.objects.link(rim_obj)

    root = build_golumolu_v13()

    # Center Aim Target
    target = bpy.data.objects.new("Cam_Target", None)
    target.location = (0.0, 0.0, -0.05)
    bpy.context.collection.objects.link(target)

    # Camera with TRACK_TO constraint for perfect centering!
    cam_data = bpy.data.cameras.new("Cam_Validation")
    cam_data.type = 'PERSP'
    cam_data.lens = 55
    cam_obj = bpy.data.objects.new("Cam_Validation", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    
    scene.camera = cam_obj

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    # 4 Orthographic / Model Sheet views at radius 5.2m
    views = [
        {"name": "front",  "loc": (0.0, 5.2, 0.3)},
        {"name": "34view", "loc": (-3.8, 3.8, 1.1)},
        {"name": "side",   "loc": (-5.2, 0.0, 0.2)},
        {"name": "back",   "loc": (0.0, -5.2, 0.4)},
    ]

    for v in views:
        cam_obj.location = v["loc"]
        bpy.context.view_layer.update()
        out_path = f"D:/Projects/MOMO MAZE/BlenderSources/renders/golumolu/golumolu_v013_{v['name']}.png"
        scene.render.filepath = out_path
        print(f"Rendering Golumolu v13 {v['name']} -> {out_path}")
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
