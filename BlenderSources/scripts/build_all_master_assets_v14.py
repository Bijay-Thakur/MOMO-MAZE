import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for item in b:
            b.remove(item)

# ==============================================================================
# PART 1: GOLUMOLU V14 (Rich Peach-Orange, Fluffy, Happy Eyes, Godzilla Spikes)
# ==============================================================================

def create_golumolu_materials():
    m_fur = bpy.data.materials.new("M_Golumolu_Fluffy_Fur")
    m_fur.use_nodes = True
    nodes = m_fur.node_tree.nodes
    links = m_fur.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    # Warm peach-orange vertical gradient
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")
    # Bottom: Warm Cream (#FFF2E6)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (1.0, 0.949, 0.902, 1.0)
    # Top/Back: Rich Peach-Orange (#FF9B5E)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (1.0, 0.608, 0.369, 1.0)
    
    links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.50
    bsdf.inputs["Subsurface Weight"].default_value = 0.40
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.65, 0.45)
    bsdf.inputs["Subsurface Scale"].default_value = 0.10
    bsdf.inputs["Sheen Weight"].default_value = 1.0
    bsdf.inputs["Sheen Roughness"].default_value = 0.40
    bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.85, 0.70, 1.0)

    # Micro fur bump
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 110.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.02
    links.new(tc.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Vibrant Peach Accent
    m_peach = bpy.data.materials.new("M_Golumolu_Peach_Accent")
    m_peach.use_nodes = True
    b_p = m_peach.node_tree.nodes.get("Principled BSDF")
    b_p.inputs["Base Color"].default_value = (1.0, 0.58, 0.35, 1.0)
    b_p.inputs["Roughness"].default_value = 0.45
    b_p.inputs["Subsurface Weight"].default_value = 0.45
    b_p.inputs["Sheen Weight"].default_value = 0.85

    # Rosy Blush Cheeks (#FF7F8C)
    m_blush = bpy.data.materials.new("M_Golumolu_Cheeks")
    m_blush.use_nodes = True
    b_b = m_blush.node_tree.nodes.get("Principled BSDF")
    b_b.inputs["Base Color"].default_value = (1.0, 0.50, 0.55, 1.0)
    b_b.inputs["Roughness"].default_value = 0.65
    b_b.inputs["Subsurface Weight"].default_value = 0.60

    # Eyes & Shine
    m_eye = bpy.data.materials.new("M_Golumolu_Eyes")
    m_eye.use_nodes = True
    b_e = m_eye.node_tree.nodes.get("Principled BSDF")
    b_e.inputs["Base Color"].default_value = (0.04, 0.035, 0.035, 1.0)
    b_e.inputs["Roughness"].default_value = 0.05

    m_shine = bpy.data.materials.new("M_Golumolu_Eye_Shine")
    m_shine.use_nodes = True
    b_s = m_shine.node_tree.nodes.get("Principled BSDF")
    b_s.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_s.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_s.inputs["Emission Strength"].default_value = 2.0

    # Mouth & Tongue
    m_mouth = bpy.data.materials.new("M_Golumolu_Mouth")
    m_mouth.use_nodes = True
    b_m = m_mouth.node_tree.nodes.get("Principled BSDF")
    b_m.inputs["Base Color"].default_value = (0.75, 0.16, 0.20, 1.0)
    b_m.inputs["Roughness"].default_value = 0.35

    m_tongue = bpy.data.materials.new("M_Golumolu_Tongue")
    m_tongue.use_nodes = True
    b_t = m_tongue.node_tree.nodes.get("Principled BSDF")
    b_t.inputs["Base Color"].default_value = (1.0, 0.52, 0.56, 1.0)
    b_t.inputs["Roughness"].default_value = 0.25

    return m_fur, m_peach, m_blush, m_eye, m_shine, m_mouth, m_tongue

def build_golumolu():
    m_fur, m_peach, m_blush, m_eye, m_shine, m_mouth, m_tongue = create_golumolu_materials()

    root = bpy.data.objects.new("Golumolu_v14_Master", None)
    bpy.context.collection.objects.link(root)

    # 1. Main Chubby Body
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=1.0)
    body = bpy.context.active_object
    body.name = "golumolu_body"
    body.scale = (1.10, 1.02, 0.98)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_fur)
    body.parent = root
    sub = body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    bpy.ops.object.shade_smooth()

    # 2. Dinosaur Tail (Subdivided cone curving upward)
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

    # Peach ball tip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=16, ring_count=12)
    tail_tip = bpy.context.active_object
    tail_tip.name = "golumolu_tail_tip"
    tail_tip.location = (0.0, -1.68, 0.32)
    tail_tip.data.materials.append(m_peach)
    tail_tip.parent = root
    bpy.ops.object.shade_smooth()

    # 3. 4 Stepped Godzilla Dorsal Spikes
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

    # 4. Cute Peach Ears
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

    # 5. Facial Features: Big glossy black eyes with upper white catchlight shine
    for side, x in [("L", -0.36), ("R", 0.36)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.155, segments=24, ring_count=20)
        eye = bpy.context.active_object
        eye.name = f"golumolu_eye_{side}"
        eye.location = (x, 0.94, 0.16)
        eye.scale = (0.85, 0.36, 1.25)
        eye.rotation_euler = (math.radians(-12), 0, math.radians(5 if side=="L" else -5))
        eye.data.materials.append(m_eye)
        eye.parent = root

        # Big Upper White Catchlight Shine Patch (~45% of eye)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, segments=16, ring_count=12)
        sh_main = bpy.context.active_object
        sh_main.name = f"golumolu_shine_main_{side}"
        sh_main.location = (x + (0.02 if side=="L" else -0.02), 0.99, 0.24)
        sh_main.scale = (0.88, 0.32, 0.85)
        sh_main.data.materials.append(m_shine)
        sh_main.parent = root

        # Twinkle Dot
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.038, segments=12, ring_count=8)
        sh_sub = bpy.context.active_object
        sh_sub.name = f"golumolu_shine_sub_{side}"
        sh_sub.location = (x - (0.035 if side=="L" else -0.035), 0.98, 0.10)
        sh_sub.scale = (0.8, 0.3, 0.8)
        sh_sub.data.materials.append(m_shine)
        sh_sub.parent = root

    # Rosy Blush Cheeks
    for side, x in [("L", -0.64), ("R", 0.64)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.165, segments=20, ring_count=16)
        bl = bpy.context.active_object
        bl.name = f"golumolu_blush_{side}"
        bl.location = (x, 0.74, -0.02)
        bl.scale = (1.15, 0.35, 0.75)
        bl.rotation_euler = (math.radians(-15), 0, math.radians(15 if side=="L" else -15))
        bl.data.materials.append(m_blush)
        bl.parent = root

    # Happy Open Smiling Arch Mouth with Pink Tongue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, segments=20, ring_count=16)
    mouth = bpy.context.active_object
    mouth.name = "golumolu_mouth"
    mouth.location = (0.0, 1.02, -0.04)
    mouth.scale = (1.10, 0.35, 0.85)
    mouth.data.materials.append(m_mouth)
    mouth.parent = root

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=16, ring_count=12)
    tongue = bpy.context.active_object
    tongue.name = "golumolu_tongue"
    tongue.location = (0.0, 1.05, -0.08)
    tongue.scale = (0.95, 0.3, 0.65)
    tongue.data.materials.append(m_tongue)
    tongue.parent = root

    # 6. Tiny Chubby Paws & Feet
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

    return root

# ==============================================================================
# PART 2: GHOST SPIRITS V14 (Seamless Organic Multi-Tail, Soft Fluff & Fuzz)
# ==============================================================================

def create_fluffy_ghost_materials():
    m_ghost = bpy.data.materials.new("M_Spirit_Fluffy_Master")
    m_ghost.use_nodes = True
    nodes = m_ghost.node_tree.nodes
    links = m_ghost.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    bsdf.inputs["Base Color"].default_value = (0.985, 0.965, 0.935, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    bsdf.inputs["Subsurface Weight"].default_value = 0.55
    bsdf.inputs["Subsurface Radius"].default_value = (0.95, 0.80, 0.65)
    bsdf.inputs["Subsurface Scale"].default_value = 0.14
    bsdf.inputs["Sheen Weight"].default_value = 1.0
    bsdf.inputs["Sheen Roughness"].default_value = 0.35
    bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.95, 0.88, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.97, 0.92, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 0.08

    # Procedural micro hair bump
    tc = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 110.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.75
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.02
    links.new(tc.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Facial materials
    m_eye = bpy.data.materials.new("M_Spirit_Eyes")
    m_eye.use_nodes = True
    m_eye.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.04, 0.035, 0.035, 1.0)

    m_shine = bpy.data.materials.new("M_Spirit_Catchlight")
    m_shine.use_nodes = True
    b_sh = m_shine.node_tree.nodes.get("Principled BSDF")
    b_sh.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_sh.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_sh.inputs["Emission Strength"].default_value = 2.0

    m_blush = bpy.data.materials.new("M_Spirit_Blush")
    m_blush.use_nodes = True
    m_blush.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (1.0, 0.62, 0.60, 1.0)

    m_mouth = bpy.data.materials.new("M_Spirit_Mouth")
    m_mouth.use_nodes = True
    m_mouth.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.70, 0.20, 0.24, 1.0)

    m_tongue = bpy.data.materials.new("M_Spirit_Tongue")
    m_tongue.use_nodes = True
    m_tongue.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (1.0, 0.55, 0.58, 1.0)

    m_halo = bpy.data.materials.new("M_Spirit_Golden_Halo")
    m_halo.use_nodes = True
    b_h = m_halo.node_tree.nodes.get("Principled BSDF")
    b_h.inputs["Base Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    b_h.inputs["Emission Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    b_h.inputs["Emission Strength"].default_value = 4.5

    return m_ghost, m_eye, m_shine, m_blush, m_mouth, m_tongue, m_halo

def create_smooth_tail_wisp(name, control_points, base_thickness=0.36, mat=None):
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_depth = base_thickness
    curve_data.bevel_resolution = 6
    curve_data.use_fill_caps = True
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(control_points) - 1)
    for i, pt in enumerate(control_points):
        bp = spline.bezier_points[i]
        bp.co = pt["co"]
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        t = i / (len(control_points) - 1)
        bp.radius = max(0.06, (1.0 - t)**1.25)
        
    c_obj = bpy.data.objects.new(f"{name}_Obj", curve_data)
    bpy.context.collection.objects.link(c_obj)
    bpy.context.view_layer.objects.active = c_obj
    c_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    m_obj = bpy.context.active_object
    m_obj.name = name
    if mat:
        m_obj.data.materials.append(mat)
    sub = m_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    bpy.ops.object.shade_smooth()
    return m_obj

def build_spirit_v14(spirit_type="follower", position=(0,0,0), yaw_deg=0):
    m_ghost, m_eye, m_shine, m_blush, m_mouth, m_tongue, m_halo = create_fluffy_ghost_materials()

    root = bpy.data.objects.new(f"Spirit_{spirit_type.capitalize()}_Root", None)
    root.location = position
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    bpy.context.collection.objects.link(root)

    # 1. Main Droplet Body (Face at +Y, tail at -Y)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.92)
    body = bpy.context.active_object
    body.name = f"{spirit_type}_body"
    body.scale = (0.95, 1.05, 0.98)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_ghost)
    body.parent = root
    sub = body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    bpy.ops.object.shade_smooth()

    # 2. 3 to 4 Graceful Wisps trailing towards -Y (backwards)
    tails_data = []
    if spirit_type == "follower":
        tails_data = [
            {"name": "tail_main", "thick": 0.40, "pts": [
                {"co": Vector((0.0, -0.6, 0.05))}, {"co": Vector((0.0, -1.2, 0.0))},
                {"co": Vector((0.05, -1.8, -0.1))}, {"co": Vector((0.12, -2.4, -0.18))}]},
            {"name": "tail_upper", "thick": 0.28, "pts": [
                {"co": Vector((0.0, -0.5, 0.45))}, {"co": Vector((0.0, -1.0, 0.65))},
                {"co": Vector((-0.05, -1.5, 0.90))}, {"co": Vector((0.0, -1.9, 1.15))}]},
            {"name": "tail_left", "thick": 0.24, "pts": [
                {"co": Vector((-0.45, -0.5, -0.2))}, {"co": Vector((-0.70, -1.0, -0.3))},
                {"co": Vector((-0.90, -1.4, -0.36))}, {"co": Vector((-1.05, -1.8, -0.40))}]},
            {"name": "tail_right", "thick": 0.24, "pts": [
                {"co": Vector((0.45, -0.5, -0.2))}, {"co": Vector((0.70, -1.0, -0.3))},
                {"co": Vector((0.90, -1.4, -0.36))}, {"co": Vector((1.05, -1.8, -0.40))}]},
            {"name": "head_crest", "thick": 0.20, "pts": [
                {"co": Vector((0.0, 0.2, 0.90))}, {"co": Vector((0.0, -0.2, 1.12))},
                {"co": Vector((0.0, -0.50, 1.22))}]},
        ]
    elif spirit_type == "cutter":
        tails_data = [
            {"name": "tail_crest", "thick": 0.30, "pts": [
                {"co": Vector((0.0, 0.25, 0.88))}, {"co": Vector((0.0, -0.35, 1.12))},
                {"co": Vector((0.0, -1.0, 1.20))}, {"co": Vector((0.0, -1.6, 1.10))}]},
            {"name": "tail_center", "thick": 0.42, "pts": [
                {"co": Vector((0.0, -0.6, 0.0))}, {"co": Vector((0.0, -1.3, -0.05))},
                {"co": Vector((0.0, -2.0, -0.1))}, {"co": Vector((0.0, -2.6, -0.15))}]},
            {"name": "tail_wing_left", "thick": 0.28, "pts": [
                {"co": Vector((-0.50, -0.3, 0.1))}, {"co": Vector((-0.85, -0.8, 0.15))},
                {"co": Vector((-1.20, -1.3, 0.2))}, {"co": Vector((-1.50, -1.7, 0.22))}]},
            {"name": "tail_wing_right", "thick": 0.28, "pts": [
                {"co": Vector((0.50, -0.3, 0.1))}, {"co": Vector((0.85, -0.8, 0.15))},
                {"co": Vector((1.20, -1.3, 0.2))}, {"co": Vector((1.50, -1.7, 0.22))}]},
        ]
    elif spirit_type == "wanderer":
        tails_data = [
            {"name": "tail_upper_curl", "thick": 0.28, "pts": [
                {"co": Vector((0.0, -0.5, 0.4))}, {"co": Vector((0.15, -1.0, 0.70))},
                {"co": Vector((0.28, -1.5, 0.98))}, {"co": Vector((0.18, -1.9, 1.22))}]},
            {"name": "tail_mid_wave", "thick": 0.36, "pts": [
                {"co": Vector((0.0, -0.6, 0.0))}, {"co": Vector((-0.18, -1.2, -0.05))},
                {"co": Vector((0.12, -1.7, 0.0))}, {"co": Vector((-0.08, -2.2, -0.05))}]},
            {"name": "tail_low_left", "thick": 0.24, "pts": [
                {"co": Vector((-0.45, -0.5, -0.25))}, {"co": Vector((-0.65, -0.9, -0.38))},
                {"co": Vector((-0.55, -1.4, -0.50))}, {"co": Vector((-0.30, -1.7, -0.58))}]},
            {"name": "tail_low_right", "thick": 0.24, "pts": [
                {"co": Vector((0.45, -0.5, -0.25))}, {"co": Vector((0.70, -0.9, -0.35))},
                {"co": Vector((0.88, -1.4, -0.4))}, {"co": Vector((0.98, -1.8, -0.42))}]},
        ]

    for td in tails_data:
        wisp = create_smooth_tail_wisp(
            name=f"{spirit_type}_{td['name']}",
            control_points=td["pts"],
            base_thickness=td["thick"],
            mat=m_ghost
        )
        wisp.parent = root

    # 3. Facial Features (+Y is front face)
    if spirit_type == "follower":
        for side, x in [("L", -0.28), ("R", 0.28)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, segments=20, ring_count=16)
            eye = bpy.context.active_object
            eye.name = f"{spirit_type}_eye_{side}"
            eye.location = (x, 0.98, 0.12)
            eye.scale = (0.75, 0.35, 1.25)
            eye.rotation_euler = (math.radians(-10), 0, math.radians(4 if side=="L" else -4))
            eye.data.materials.append(m_eye)
            eye.parent = root
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=12, ring_count=8)
            sh = bpy.context.active_object
            sh.location = (x + (0.02 if side=="L" else -0.02), 1.01, 0.17)
            sh.scale = (0.8, 0.3, 0.8)
            sh.data.materials.append(m_shine)
            sh.parent = root
            
        for side, x in [("L", -0.48), ("R", 0.48)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, segments=16, ring_count=12)
            bl = bpy.context.active_object
            bl.location = (x, 0.86, -0.06)
            bl.scale = (1.1, 0.3, 0.7)
            bl.rotation_euler = (math.radians(-15), 0, math.radians(12 if side=="L" else -12))
            bl.data.materials.append(m_blush)
            bl.parent = root

    elif spirit_type == "cutter":
        for side, x in [("L", -0.28), ("R", 0.28)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, segments=20, ring_count=16)
            eye = bpy.context.active_object
            eye.name = f"{spirit_type}_eye_{side}"
            eye.location = (x, 0.98, 0.10)
            eye.scale = (0.9, 0.35, 1.1)
            eye.rotation_euler = (math.radians(-10), math.radians(-28 if side=="L" else 28), 0)
            eye.data.materials.append(m_eye)
            eye.parent = root
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, segments=12, ring_count=8)
            sh = bpy.context.active_object
            sh.location = (x + (0.02 if side=="L" else -0.02), 1.01, 0.13)
            sh.scale = (0.8, 0.3, 0.8)
            sh.data.materials.append(m_shine)
            sh.parent = root
            
        for side, x in [("L", -0.48), ("R", 0.48)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=16, ring_count=12)
            bl = bpy.context.active_object
            bl.location = (x, 0.88, -0.07)
            bl.scale = (1.0, 0.3, 0.6)
            bl.rotation_euler = (math.radians(-15), 0, math.radians(10 if side=="L" else -10))
            bl.data.materials.append(m_blush)
            bl.parent = root

    elif spirit_type == "wanderer":
        for side, x in [("L", -0.28), ("R", 0.28)]:
            curve_data = bpy.data.curves.new(name=f"eye_curve_{side}", type='CURVE')
            curve_data.dimensions = '3D'
            spline = curve_data.splines.new('BEZIER')
            spline.bezier_points.add(2)
            spline.bezier_points[0].co = Vector((-0.07, -0.04, -0.04))
            spline.bezier_points[1].co = Vector((0.0, 0.0, 0.05))
            spline.bezier_points[2].co = Vector((0.07, -0.04, -0.04))
            for bp in spline.bezier_points:
                bp.handle_left_type = 'AUTO'
                bp.handle_right_type = 'AUTO'
            curve_data.bevel_depth = 0.024
            curve_data.bevel_resolution = 4
            c_obj = bpy.data.objects.new(f"{spirit_type}_eye_{side}", curve_data)
            bpy.context.collection.objects.link(c_obj)
            c_obj.location = (x, 0.98, 0.12)
            c_obj.rotation_euler = (math.radians(-15), 0, 0)
            c_obj.data.materials.append(m_eye)
            c_obj.parent = root
            
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=20, ring_count=16)
        mouth = bpy.context.active_object
        mouth.location = (0.0, 1.05, -0.06)
        mouth.scale = (0.75, 0.4, 0.95)
        mouth.data.materials.append(m_mouth)
        mouth.parent = root
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=12, ring_count=10)
        tongue = bpy.context.active_object
        tongue.location = (0.0, 1.08, -0.09)
        tongue.scale = (0.8, 0.3, 0.6)
        tongue.data.materials.append(m_tongue)
        tongue.parent = root

        for side, x in [("L", -0.48), ("R", 0.48)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, segments=16, ring_count=12)
            bl = bpy.context.active_object
            bl.location = (x, 0.86, -0.06)
            bl.scale = (1.1, 0.3, 0.7)
            bl.rotation_euler = (math.radians(-15), 0, math.radians(12 if side=="L" else -12))
            bl.data.materials.append(m_blush)
            bl.parent = root

        # Golden Halo Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=1.25, minor_radius=0.028, major_segments=32, minor_segments=12)
        halo = bpy.context.active_object
        halo.name = "wanderer_golden_halo"
        halo.location = (0.0, 0.0, 0.15)
        halo.rotation_euler = (math.radians(35), math.radians(25), math.radians(-15))
        halo.data.materials.append(m_halo)
        halo.parent = root

    return root

# ==============================================================================
# PART 3: MASTER DIORAMA V9 (Rich Moss/Forest Green, Warm Sunlight, 1500 Grass)
# ==============================================================================

def create_diorama_materials():
    # 1. Authentic Moss/Forest Green Living Hedge
    m_hedge = bpy.data.materials.new("M_Living_Hedge_Master")
    m_hedge.use_nodes = True
    nodes = m_hedge.node_tree.nodes
    links = m_hedge.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    # Fine Noise Color Ramp (Rich, velvety foliage, NO circular spots!)
    tc = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 28.0
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.65

    ramp = nodes.new("ShaderNodeValToRGB")
    # Crevice / Deep Moss Green (#234E1A)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.137, 0.306, 0.102, 1.0)
    # Mid Lush Hedge Green (#387822)
    ramp.color_ramp.elements.new(0.55)
    ramp.color_ramp.elements[1].color = (0.220, 0.471, 0.133, 1.0)
    # Sunlit Golden-Lime Tips (#78B228)
    ramp.color_ramp.elements[2].position = 0.85
    ramp.color_ramp.elements[2].color = (0.471, 0.698, 0.157, 1.0)

    links.new(tc.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.55
    bsdf.inputs["Subsurface Weight"].default_value = 0.25
    bsdf.inputs["Subsurface Radius"].default_value = (0.4, 0.8, 0.2)
    bsdf.inputs["Subsurface Scale"].default_value = 0.08
    bsdf.inputs["Sheen Weight"].default_value = 0.70
    bsdf.inputs["Sheen Tint"].default_value = (0.65, 0.90, 0.35, 1.0)

    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.14
    bump.inputs["Distance"].default_value = 0.03
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # 2. Rich Lawn Grass Blade Material
    m_grass = bpy.data.materials.new("M_Lawn_Grass_Master")
    m_grass.use_nodes = True
    n_g = m_grass.node_tree.nodes
    l_g = m_grass.node_tree.links
    n_g.clear()
    out_g = n_g.new("ShaderNodeOutputMaterial")
    b_g = n_g.new("ShaderNodeBsdfPrincipled")
    tc_g = n_g.new("ShaderNodeTexCoord")
    sep_g = n_g.new("ShaderNodeSeparateXYZ")
    ramp_g = n_g.new("ShaderNodeValToRGB")
    # Base: Deep forest green (#1E3F14)
    ramp_g.color_ramp.elements[0].position = 0.0
    ramp_g.color_ramp.elements[0].color = (0.118, 0.247, 0.078, 1.0)
    # Tip: Vibrant sunlit lime gold (#7CB528)
    ramp_g.color_ramp.elements[1].position = 1.0
    ramp_g.color_ramp.elements[1].color = (0.486, 0.710, 0.157, 1.0)
    l_g.new(tc_g.outputs["Generated"], sep_g.inputs["Vector"])
    l_g.new(sep_g.outputs["Z"], ramp_g.inputs["Fac"])
    l_g.new(ramp_g.outputs["Color"], b_g.inputs["Base Color"])
    b_g.inputs["Roughness"].default_value = 0.38
    b_g.inputs["Subsurface Weight"].default_value = 0.40
    b_g.inputs["Subsurface Radius"].default_value = (0.4, 0.8, 0.2)
    b_g.inputs["Sheen Weight"].default_value = 0.85
    l_g.new(b_g.outputs["BSDF"], out_g.inputs["Surface"])

    # 3. Ground Earth & Lawn Substrate
    m_ground = bpy.data.materials.new("M_Ground_Lawn")
    m_ground.use_nodes = True
    b_gr = m_ground.node_tree.nodes.get("Principled BSDF")
    b_gr.inputs["Base Color"].default_value = (0.18, 0.32, 0.12, 1.0)
    b_gr.inputs["Roughness"].default_value = 0.85

    # 4. Terracotta / Sandstone Raised Curb (#B8754E)
    m_curb = bpy.data.materials.new("M_Raised_Curb")
    m_curb.use_nodes = True
    b_c = m_curb.node_tree.nodes.get("Principled BSDF")
    b_c.inputs["Base Color"].default_value = (0.72, 0.46, 0.31, 1.0)
    b_c.inputs["Roughness"].default_value = 0.70

    # 5. Flowers (Pink, White, Yellow Pistil)
    m_pink = bpy.data.materials.new("M_Flower_Pink")
    m_pink.use_nodes = True
    b_pk = m_pink.node_tree.nodes.get("Principled BSDF")
    b_pk.inputs["Base Color"].default_value = (1.0, 0.58, 0.68, 1.0)
    b_pk.inputs["Subsurface Weight"].default_value = 0.5
    b_pk.inputs["Roughness"].default_value = 0.35

    m_white = bpy.data.materials.new("M_Flower_White")
    m_white.use_nodes = True
    b_wh = m_white.node_tree.nodes.get("Principled BSDF")
    b_wh.inputs["Base Color"].default_value = (0.98, 0.98, 0.96, 1.0)
    b_wh.inputs["Subsurface Weight"].default_value = 0.4
    b_wh.inputs["Roughness"].default_value = 0.35

    m_yellow = bpy.data.materials.new("M_Flower_Center")
    m_yellow.use_nodes = True
    b_yl = m_yellow.node_tree.nodes.get("Principled BSDF")
    b_yl.inputs["Base Color"].default_value = (1.0, 0.78, 0.15, 1.0)
    b_yl.inputs["Roughness"].default_value = 0.30

    m_clover = bpy.data.materials.new("M_Clover_Leaf")
    m_clover.use_nodes = True
    b_cl = m_clover.node_tree.nodes.get("Principled BSDF")
    b_cl.inputs["Base Color"].default_value = (0.25, 0.58, 0.15, 1.0)
    b_cl.inputs["Subsurface Weight"].default_value = 0.45

    m_wood = bpy.data.materials.new("M_Cozy_Wood")
    m_wood.use_nodes = True
    b_wd = m_wood.node_tree.nodes.get("Principled BSDF")
    b_wd.inputs["Base Color"].default_value = (0.52, 0.34, 0.20, 1.0)
    b_wd.inputs["Roughness"].default_value = 0.65

    m_momo = bpy.data.materials.new("M_Momo_Golden_Master")
    m_momo.use_nodes = True
    b_mo = m_momo.node_tree.nodes.get("Principled BSDF")
    b_mo.inputs["Base Color"].default_value = (1.0, 0.90, 0.60, 1.0)
    b_mo.inputs["Subsurface Weight"].default_value = 0.60
    b_mo.inputs["Subsurface Radius"].default_value = (1.0, 0.7, 0.4)
    b_mo.inputs["Emission Color"].default_value = (1.0, 0.85, 0.40, 1.0)
    b_mo.inputs["Emission Strength"].default_value = 1.6

    m_sparkle = bpy.data.materials.new("M_Gold_Sparkle")
    m_sparkle.use_nodes = True
    b_sp = m_sparkle.node_tree.nodes.get("Principled BSDF")
    b_sp.inputs["Base Color"].default_value = (1.0, 0.9, 0.35, 1.0)
    b_sp.inputs["Emission Color"].default_value = (1.0, 0.9, 0.35, 1.0)
    b_sp.inputs["Emission Strength"].default_value = 6.0

    return {
        "hedge": m_hedge, "grass": m_grass, "ground": m_ground, "curb": m_curb,
        "pink": m_pink, "white": m_white, "yellow": m_yellow, "clover": m_clover,
        "wood": m_wood, "momo": m_momo, "sparkle": m_sparkle
    }

def build_straight_hedge_block(name, length=1.8, width=0.55, height=1.35, mats=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (length, width, height)
    bpy.ops.object.transform_apply(scale=True)
    obj.location.z = height / 2.0
    bpy.ops.object.transform_apply(location=True)
    
    bevel = obj.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.16
    bevel.segments = 3
    
    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    bpy.ops.object.shade_smooth()
    if mats:
        obj.data.materials.append(mats["hedge"])
    return obj

def create_flower_sprig(name, petal_color='pink', mats=None):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)

    p_mat = mats["pink"] if petal_color == 'pink' else mats["white"]
    for i in range(5):
        angle = i * (2.0 * math.pi / 5.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, segments=12, ring_count=8)
        pet = bpy.context.active_object
        pet.scale = (0.7, 1.25, 0.35)
        rad = 0.085
        pet.location = (rad * math.cos(angle), rad * math.sin(angle), 0.02)
        pet.rotation_euler = (0, 0, angle + math.pi/2)
        pet.data.materials.append(p_mat)
        pet.parent = root
        bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, segments=12, ring_count=8)
    pistil = bpy.context.active_object
    pistil.scale = (1.0, 1.0, 0.6)
    pistil.location = (0, 0, 0.04)
    pistil.data.materials.append(mats["yellow"])
    pistil.parent = root
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=12, ring_count=8)
    leaf = bpy.context.active_object
    leaf.scale = (0.6, 1.3, 0.25)
    leaf.location = (0.12, -0.06, -0.01)
    leaf.rotation_euler = (math.radians(10), math.radians(-15), math.radians(45))
    leaf.data.materials.append(mats["clover"])
    leaf.parent = root
    bpy.ops.object.shade_smooth()

    return root

def create_grass_tuft_prototype(name, mats=None):
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 4
    curve_data.bevel_depth = 0.035
    curve_data.bevel_resolution = 3
    curve_data.use_fill_caps = True

    angles = [0, 60, 120, 180, 240, 300]
    heights = [0.42, 0.48, 0.38, 0.45, 0.36, 0.44]
    bends = [0.18, 0.22, 0.16, 0.20, 0.15, 0.21]

    for a_deg, h, b in zip(angles, heights, bends):
        rad = math.radians(a_deg)
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        spline.bezier_points[0].co = Vector((0.02 * math.cos(rad), 0.02 * math.sin(rad), 0.0))
        spline.bezier_points[0].radius = 1.0
        spline.bezier_points[1].co = Vector((0.08 * math.cos(rad), 0.08 * math.sin(rad), h * 0.55))
        spline.bezier_points[1].radius = 0.65
        spline.bezier_points[2].co = Vector(((0.08 + b) * math.cos(rad), ((0.08 + b)) * math.sin(rad), h))
        spline.bezier_points[2].radius = 0.08
        for bp in spline.bezier_points:
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

    c_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(c_obj)
    bpy.context.view_layer.objects.active = c_obj
    c_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    m_obj = bpy.context.active_object
    if mats:
        m_obj.data.materials.append(mats["grass"])
    bpy.ops.object.shade_smooth()
    return m_obj

def build_leaf_gate(mats):
    root = bpy.data.objects.new("Leaf_Gate_Master", None)
    bpy.context.collection.objects.link(root)
    root.location = (0.0, 5.75, 0.0)

    for side, x in [("L", -1.1), ("R", 1.1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.4, vertices=16)
        post = bpy.context.active_object
        post.location = (x, 0, 1.2)
        post.data.materials.append(mats["wood"])
        post.parent = root
        bpy.ops.object.shade_smooth()

        bpy.ops.mesh.primitive_cube_add(size=0.55)
        plinth = bpy.context.active_object
        plinth.location = (x, 0, 0.22)
        plinth.scale = (1.0, 1.0, 0.8)
        plinth.data.materials.append(mats["curb"])
        plinth.parent = root
        bevel = plinth.modifiers.new("Bevel", 'BEVEL')
        bevel.width = 0.08
        bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=2.4, vertices=16)
    lintel = bpy.context.active_object
    lintel.location = (0, 0, 2.35)
    lintel.rotation_euler = (0, math.radians(90), 0)
    lintel.data.materials.append(mats["wood"])
    lintel.parent = root
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, segments=20, ring_count=16)
    crest = bpy.context.active_object
    crest.location = (0, 0, 2.35)
    crest.scale = (1.1, 0.8, 1.0)
    crest.data.materials.append(mats["momo"])
    crest.parent = root
    bpy.ops.object.shade_smooth()

    leaf_clusters = [
        {"loc": (0, 0, 2.85), "scale": (0.85, 0.65, 0.45)},
        {"loc": (-0.45, 0, 2.75), "scale": (0.75, 0.60, 0.40)},
        {"loc": (0.45, 0, 2.75), "scale": (0.75, 0.60, 0.40)},
        {"loc": (-0.95, 0, 2.55), "scale": (0.70, 0.55, 0.38)},
        {"loc": (0.95, 0, 2.55), "scale": (0.70, 0.55, 0.38)},
        {"loc": (-1.35, 0, 2.25), "scale": (0.60, 0.50, 0.35)},
        {"loc": (1.35, 0, 2.25), "scale": (0.60, 0.50, 0.35)},
    ]
    for i, lc in enumerate(leaf_clusters):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, segments=16, ring_count=12)
        lobe = bpy.context.active_object
        lobe.location = lc["loc"]
        lobe.scale = lc["scale"]
        lobe.data.materials.append(mats["clover"])
        lobe.parent = root
        bpy.ops.object.shade_smooth()

    f1 = create_flower_sprig("gate_fl_1", petal_color='pink', mats=mats)
    f1.location = (-0.75, -0.25, 2.65)
    f1.parent = root
    f2 = create_flower_sprig("gate_fl_2", petal_color='white', mats=mats)
    f2.location = (0.75, -0.25, 2.65)
    f2.parent = root

    return root

def build_momo_collectible(mats):
    root = bpy.data.objects.new("Momo_Collectible_Master", None)
    bpy.context.collection.objects.link(root)
    root.location = (2.2, 0.0, 0.0)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.25, vertices=24)
    ped = bpy.context.active_object
    ped.location = (0, 0, 0.125)
    ped.data.materials.append(mats["curb"])
    ped.parent = root
    bevel = ped.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.05
    bpy.ops.object.shade_smooth()

    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, segments=12, ring_count=8)
        lf = bpy.context.active_object
        lf.scale = (0.8, 1.4, 0.3)
        rad = 0.28
        lf.location = (rad * math.cos(ang), rad * math.sin(ang), 0.22)
        lf.rotation_euler = (0, 0, ang + math.pi/2)
        lf.data.materials.append(mats["clover"])
        lf.parent = root
        bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, segments=24, ring_count=18)
    dumpling = bpy.context.active_object
    dumpling.name = "momo_dumpling"
    dumpling.location = (0, 0, 0.52)
    dumpling.scale = (1.15, 1.15, 0.90)
    dumpling.data.materials.append(mats["momo"])
    dumpling.parent = root
    sub = dumpling.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.10, radius2=0.01, depth=0.18)
    swirl = bpy.context.active_object
    swirl.location = (0, 0, 0.82)
    swirl.data.materials.append(mats["momo"])
    swirl.parent = root
    bpy.ops.object.shade_smooth()

    sparkle_coords = [(-0.45, -0.25, 0.85), (0.48, -0.20, 0.92), (0.0, 0.45, 1.05), (-0.35, 0.35, 0.65)]
    for j, sc in enumerate(sparkle_coords):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=10, ring_count=8)
        spk = bpy.context.active_object
        spk.location = sc
        spk.data.materials.append(mats["sparkle"])
        spk.parent = root

    pt = bpy.data.lights.new("Momo_Inner_Glow", 'POINT')
    pt.energy = 55.0
    pt.color = (1.0, 0.85, 0.40)
    pt.shadow_soft_size = 0.4
    pt_obj = bpy.data.objects.new("Momo_Inner_Glow", pt)
    pt_obj.location = (0, 0, 0.6)
    bpy.context.collection.objects.link(pt_obj)
    pt_obj.parent = root

    return root

def build_puffy_cloud_tree(name, position=(0,0,0), mats=None):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = position

    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=3.2, vertices=16)
    trunk = bpy.context.active_object
    trunk.location = (0, 0, 1.6)
    trunk.data.materials.append(mats["wood"])
    trunk.parent = root
    bpy.ops.object.shade_smooth()

    lobes = [
        {"loc": (0, 0, 3.4), "scale": (1.8, 1.8, 1.2)},
        {"loc": (-0.6, 0.4, 4.1), "scale": (1.5, 1.4, 1.1)},
        {"loc": (0.5, -0.4, 4.3), "scale": (1.5, 1.5, 1.1)},
        {"loc": (0, 0, 5.0), "scale": (1.2, 1.2, 1.0)},
    ]
    for i, lb in enumerate(lobes):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=20, ring_count=16)
        fol = bpy.context.active_object
        fol.location = lb["loc"]
        fol.scale = lb["scale"]
        fol.data.materials.append(mats["hedge"])
        fol.parent = root
        sub = fol.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        bpy.ops.object.shade_smooth()

    return root

# ==============================================================================
# EXECUTION & PIPELINE AUTOMATION
# ==============================================================================

def execute_all_productions():
    print("==================================================")
    print("MOMO MAZE DEFINITIVE ASSET PRODUCTION (v14)")
    print("==================================================")
    
    # --------------------------------------------------------------------------
    # 1. GOLUMOLU V14
    # --------------------------------------------------------------------------
    print("\n>>> Producing Golumolu v14 Master Character...")
    reset_scene()
    root_g = build_golumolu()

    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.985, 0.955, 0.92, 1.0)
    bg.inputs["Strength"].default_value = 0.95

    sun = bpy.data.lights.new("Sun_Key", 'SUN')
    sun.energy = 4.2
    sun.color = (1.0, 0.95, 0.88)
    sun_obj = bpy.data.objects.new("Sun_Key", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    bpy.context.collection.objects.link(sun_obj)

    fill = bpy.data.lights.new("Fill_Light", 'POINT')
    fill.energy = 140.0
    fill.color = (0.92, 0.96, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    fill_obj.location = (-2.5, 3.5, 1.5)
    bpy.context.collection.objects.link(fill_obj)

    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.energy = 220.0
    rim.color = (1.0, 0.85, 0.68)
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.0, -3.5, 2.5)
    bpy.context.collection.objects.link(rim_obj)

    target_g = bpy.data.objects.new("Cam_Target_G", None)
    target_g.location = (0, 0, -0.05)
    bpy.context.collection.objects.link(target_g)

    cam_data_g = bpy.data.cameras.new("Cam_G")
    cam_data_g.type = 'PERSP'
    cam_data_g.lens = 55
    cam_obj_g = bpy.data.objects.new("Cam_G", cam_data_g)
    bpy.context.collection.objects.link(cam_obj_g)
    tr_g = cam_obj_g.constraints.new(type='TRACK_TO')
    tr_g.target = target_g
    tr_g.track_axis = 'TRACK_NEGATIVE_Z'
    tr_g.up_axis = 'UP_Y'
    scene.camera = cam_obj_g

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    views = [
        {"name": "front",  "loc": (0.0, 5.2, 0.3)},
        {"name": "34view", "loc": (-3.8, 3.8, 1.1)},
        {"name": "side",   "loc": (-5.2, 0.0, 0.2)},
        {"name": "back",   "loc": (0.0, -5.2, 0.4)},
    ]
    for v in views:
        cam_obj_g.location = v["loc"]
        bpy.context.view_layer.update()
        out_path = f"D:/Projects/MOMO MAZE/BlenderSources/renders/golumolu/golumolu_v014_{v['name']}.png"
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ Rendered Golumolu {v['name']} -> {out_path}")

    bpy.ops.wm.save_as_mainfile(filepath="D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend")
    bpy.ops.export_scene.fbx(filepath="D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/golumolu_validated.fbx", use_selection=False, apply_scale_options='FBX_SCALE_ALL')
    print("  ✓ Saved Golumolu Blend & FBX")

    # --------------------------------------------------------------------------
    # 2. GHOST SPIRITS V14
    # --------------------------------------------------------------------------
    print("\n>>> Producing Ghost Spirits v14 Master Lineup...")
    reset_scene()

    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.985, 0.955, 0.92, 1.0)
    bg.inputs["Strength"].default_value = 0.95

    sun = bpy.data.lights.new("Sun_Key", 'SUN')
    sun.energy = 3.8
    sun.color = (1.0, 0.94, 0.86)
    sun_obj = bpy.data.objects.new("Sun_Key", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(-40))
    bpy.context.collection.objects.link(sun_obj)

    fill = bpy.data.lights.new("Fill_Light", 'POINT')
    fill.energy = 160.0
    fill.color = (0.9, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    fill_obj.location = (-3.5, 5.0, 2.0)
    bpy.context.collection.objects.link(fill_obj)

    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.energy = 240.0
    rim.color = (1.0, 0.88, 0.65)
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.0, -4.5, 3.0)
    bpy.context.collection.objects.link(rim_obj)

    # Spirits facing towards camera at 3/4 angle (+Y front):
    # Camera placed at Y=9.5, looking towards -Y.
    # Ghosts rotated by -25 degrees so they look towards camera and tails wave backwards!
    s_fol = build_spirit_v14("follower", position=(-2.6, 0.0, 0.0), yaw_deg=-25)
    s_cut = build_spirit_v14("cutter", position=(0.0, 0.0, 0.12), yaw_deg=-22)
    s_wan = build_spirit_v14("wanderer", position=(2.6, 0.0, -0.05), yaw_deg=-28)

    target_s = bpy.data.objects.new("Cam_Target_S", None)
    target_s.location = (0.0, 0.0, 0.10)
    bpy.context.collection.objects.link(target_s)

    cam_data_s = bpy.data.cameras.new("Cam_S")
    cam_data_s.type = 'PERSP'
    cam_data_s.lens = 48
    cam_obj_s = bpy.data.objects.new("Cam_S", cam_data_s)
    cam_obj_s.location = (0.0, 9.5, 0.85)
    bpy.context.collection.objects.link(cam_obj_s)
    tr_s = cam_obj_s.constraints.new(type='TRACK_TO')
    tr_s.target = target_s
    tr_s.track_axis = 'TRACK_NEGATIVE_Z'
    tr_s.up_axis = 'UP_Y'
    scene.camera = cam_obj_s

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 960
    lineup_path = "D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/spirits_hero_lineup_v7_master.png"
    scene.render.filepath = lineup_path
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Master Hero Lineup v7 -> {lineup_path}")

    bpy.ops.wm.save_as_mainfile(filepath="D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend")
    for s_name, s_root in [("ghost_follower_validated", s_fol), ("ghost_cutter_validated", s_cut), ("ghost_wanderer_validated", s_wan)]:
        bpy.ops.object.select_all(action='DESELECT')
        s_root.select_set(True)
        for child in s_root.children_recursive:
            child.select_set(True)
        fbx_path = f"D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/{s_name}.fbx"
        bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, apply_scale_options='FBX_SCALE_ALL')
        print(f"  ✓ Exported {fbx_path}")

    # --------------------------------------------------------------------------
    # 3. MASTER ENVIRONMENT & MAZE V9 (Diorama & Orthographic Plan)
    # --------------------------------------------------------------------------
    print("\n>>> Producing Master Maze Environment v9...")
    reset_scene()
    mats = create_diorama_materials()
    master_col = bpy.context.collection

    # Meadow Ground & Raised Diorama Bed
    bpy.ops.mesh.primitive_plane_add(size=36.0)
    meadow = bpy.context.active_object
    meadow.name = "meadow_ground"
    meadow.location.z = -0.40
    meadow.data.materials.append(mats["ground"])

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    curb = bpy.context.active_object
    curb.name = "raised_garden_bed"
    curb.scale = (13.6, 13.6, 0.42)
    curb.location = (0, 0, -0.21)
    bpy.ops.object.transform_apply(scale=True, location=True)
    curb.data.materials.append(mats["curb"])
    c_bev = curb.modifiers.new("Bevel", 'BEVEL')
    c_bev.width = 0.22
    c_bev.segments = 3
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_plane_add(size=13.0)
    lawn = bpy.context.active_object
    lawn.name = "maze_inner_lawn"
    lawn.location.z = 0.005
    lawn.data.materials.append(mats["ground"])

    # 12x12 Maze Walls (Matching Ref 4 Panel 2 Top-Down Plan)
    wall_segments = [
        {"x": -3.5, "y": 5.75, "sx": 4.8, "sy": 0.55},
        {"x":  3.5, "y": 5.75, "sx": 4.8, "sy": 0.55},
        {"x":  0.0, "y": -5.75, "sx": 12.0, "sy": 0.55},
        {"x": -5.75, "y":  0.0, "sx": 0.55, "sy": 12.0},
        {"x":  5.75, "y":  0.0, "sx": 0.55, "sy": 12.0},
        {"x": -2.5, "y":  3.8, "sx": 4.2, "sy": 0.55},
        {"x":  2.8, "y":  3.8, "sx": 3.6, "sy": 0.55},
        {"x": -1.2, "y":  1.9, "sx": 3.2, "sy": 0.55},
        {"x":  3.0, "y":  1.9, "sx": 3.4, "sy": 0.55},
        {"x": -3.2, "y": -0.2, "sx": 3.8, "sy": 0.55},
        {"x":  1.8, "y": -0.2, "sx": 4.2, "sy": 0.55},
        {"x": -1.8, "y": -2.1, "sx": 4.5, "sy": 0.55},
        {"x":  2.5, "y": -2.1, "sx": 3.8, "sy": 0.55},
        {"x": -0.5, "y": -4.0, "sx": 6.5, "sy": 0.55},
        {"x": -3.8, "y":  2.0, "sx": 0.55, "sy": 3.2},
        {"x": -1.8, "y": -0.5, "sx": 0.55, "sy": 3.0},
        {"x":  0.2, "y":  3.0, "sx": 0.55, "sy": 2.2},
        {"x":  0.2, "y": -1.2, "sx": 0.55, "sy": 2.2},
        {"x":  1.9, "y":  2.8, "sx": 0.55, "sy": 2.2},
        {"x":  3.8, "y": -1.2, "sx": 0.55, "sy": 2.8},
        {"x": -3.8, "y": -2.8, "sx": 0.55, "sy": 2.2},
    ]
    for idx, ws in enumerate(wall_segments):
        build_straight_hedge_block(
            name=f"Hedge_Wall_{idx+1}",
            length=ws["sx"], width=ws["sy"], height=1.35, mats=mats
        ).location = (ws["x"], ws["y"], 0.0)

    # 1,400 3D Grass Tufts
    grass_proto = create_grass_tuft_prototype("Grass_Blade_Proto", mats=mats)
    grass_proto.location = (0, 0, -20.0)
    random.seed(42)
    grass_count = 0
    for _ in range(1200):
        gx = random.uniform(-5.2, 5.2)
        gy = random.uniform(-5.2, 5.2)
        in_wall = False
        for ws in wall_segments:
            hwx = ws["sx"] / 2.0 + 0.15
            hwy = ws["sy"] / 2.0 + 0.15
            if (ws["x"] - hwx <= gx <= ws["x"] + hwx) and (ws["y"] - hwy <= gy <= ws["y"] + hwy):
                in_wall = True
                break
        if not in_wall:
            g_inst = grass_proto.copy()
            g_inst.name = f"Grass_Tuft_{grass_count+1}"
            g_inst.location = (gx, gy, 0.0)
            g_inst.scale = (random.uniform(0.65, 1.1), random.uniform(0.65, 1.1), random.uniform(0.7, 1.25))
            g_inst.rotation_euler.z = random.uniform(0, 2.0 * math.pi)
            master_col.objects.link(g_inst)
            grass_count += 1

    for _ in range(450):
        gx = random.uniform(-9.5, 9.5)
        gy = random.uniform(-9.5, 9.5)
        if abs(gx) > 6.0 or abs(gy) > 6.0:
            g_inst = grass_proto.copy()
            g_inst.name = f"Meadow_Grass_{grass_count+1}"
            g_inst.location = (gx, gy, -0.40)
            g_inst.scale = (random.uniform(0.8, 1.4), random.uniform(0.8, 1.4), random.uniform(0.8, 1.5))
            g_inst.rotation_euler.z = random.uniform(0, 2.0 * math.pi)
            master_col.objects.link(g_inst)
            grass_count += 1

    # Flowers
    flower_coords = [
        {"pos": (-3.8, 5.8, 1.35), "col": "pink"}, {"pos": ( 3.8, 5.8, 1.35), "col": "white"},
        {"pos": (-5.8, 3.8, 1.35), "col": "pink"}, {"pos": ( 5.8, 3.8, 1.35), "col": "white"},
        {"pos": (-5.8, -3.8, 1.35), "col": "white"}, {"pos": ( 5.8, -3.8, 1.35), "col": "pink"},
        {"pos": (-2.5, 3.8, 1.35), "col": "pink"}, {"pos": ( 2.8, 3.8, 1.35), "col": "white"},
        {"pos": (-1.2, 1.9, 1.35), "col": "white"}, {"pos": ( 3.0, 1.9, 1.35), "col": "pink"},
        {"pos": (-3.2, -0.2, 1.35), "col": "pink"}, {"pos": ( 1.8, -0.2, 1.35), "col": "white"},
        {"pos": (-1.8, -2.1, 1.35), "col": "pink"}, {"pos": ( 2.5, -2.1, 1.35), "col": "white"},
        {"pos": (-0.5, -4.0, 1.35), "col": "pink"},
        {"pos": (-4.5, -4.5, 0.0), "col": "white"}, {"pos": ( 4.5, -4.5, 0.0), "col": "pink"},
        {"pos": (-4.5,  4.5, 0.0), "col": "pink"}, {"pos": ( 4.5,  4.5, 0.0), "col": "white"},
        {"pos": ( 0.0, -2.8, 0.0), "col": "pink"}, {"pos": (-2.0,  0.8, 0.0), "col": "white"},
    ]
    for idx, fc in enumerate(flower_coords):
        fl = create_flower_sprig(f"Flower_Deco_{idx+1}", petal_color=fc["col"], mats=mats)
        fl.location = fc["pos"]
        fl.scale = (random.uniform(0.9, 1.3), random.uniform(0.9, 1.3), random.uniform(0.9, 1.3))
        fl.rotation_euler.z = random.uniform(0, 2 * math.pi)

    # Gate & Momo
    gate = build_leaf_gate(mats)
    momo_ped = build_momo_collectible(mats)

    # 4 Corner Cloud Trees
    for tp in [
        {"name": "Tree_NW", "pos": (-8.2,  8.2, -0.4)},
        {"name": "Tree_NE", "pos": ( 8.2,  8.2, -0.4)},
        {"name": "Tree_SW", "pos": (-8.5, -8.0, -0.4)},
        {"name": "Tree_SE", "pos": ( 8.5, -8.0, -0.4)},
    ]:
        build_puffy_cloud_tree(tp["name"], position=tp["pos"], mats=mats)

    # Link Golumolu and Spirits into maze
    try:
        with bpy.data.libraries.load("D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend") as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if "Golumolu" in name or "golumolu" in name]
        for obj in data_to.objects:
            if obj:
                master_col.objects.link(obj)
                if obj.name == "Golumolu_v14_Master":
                    obj.location = (0.2, -0.8, 0.25)
                    obj.scale = (0.46, 0.46, 0.46)
                    obj.rotation_euler = (math.radians(12), 0, math.radians(-35))
    except Exception as e:
        print(f"Notice loading Golumolu: {e}")

    try:
        with bpy.data.libraries.load("D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend") as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if "Spirit_" in name and "Root" in name]
        for s_root in data_to.objects:
            if s_root:
                master_col.objects.link(s_root)
                if "Follower" in s_root.name:
                    s_root.location = (-2.8, 0.8, 0.75)
                    s_root.scale = (0.42, 0.42, 0.42)
                    s_root.rotation_euler = (0, 0, math.radians(-40))
                elif "Cutter" in s_root.name:
                    s_root.location = (3.2, 3.0, 0.85)
                    s_root.scale = (0.42, 0.42, 0.42)
                    s_root.rotation_euler = (0, 0, math.radians(135))
                elif "Wanderer" in s_root.name:
                    s_root.location = (-2.5, -3.2, 0.70)
                    s_root.scale = (0.40, 0.40, 0.40)
                    s_root.rotation_euler = (0, 0, math.radians(25))
    except Exception as e:
        print(f"Notice loading Spirits: {e}")

    # Rich Warm Lighting with Shadows (Low ambient fill, strong golden sun)
    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    # Low ambient sky strength for high contrast and deep shadows!
    bg.inputs["Color"].default_value = (0.88, 0.94, 1.0, 1.0)
    bg.inputs["Strength"].default_value = 0.22

    # Powerful Warm Golden Sun Key Light
    sun = bpy.data.lights.new("Sun_Golden_Key", 'SUN')
    sun.energy = 5.2
    sun.color = (1.0, 0.94, 0.82)
    sun.angle = math.radians(12)
    sun_obj = bpy.data.objects.new("Sun_Golden_Key", sun)
    sun_obj.rotation_euler = (math.radians(52), math.radians(24), math.radians(-40))
    master_col.objects.link(sun_obj)

    # Gentle Sky Fill
    fill = bpy.data.lights.new("Sky_Fill", 'SUN')
    fill.energy = 0.9
    fill.color = (0.82, 0.90, 1.0)
    fill.angle = math.radians(30)
    fill_obj = bpy.data.objects.new("Sky_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    master_col.objects.link(fill_obj)

    # Warm Golden Backlight / Rim
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.color = (1.0, 0.85, 0.60)
    rim.energy = 280.0
    rim.shadow_soft_size = 1.4
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.5, 7.5, 6.5)
    master_col.objects.link(rim_obj)

    # CAMERA 1: Perspective Diorama Beauty View (56mm lens, perfectly framing the entire island)
    target_empty = bpy.data.objects.new("Cam_Target", None)
    target_empty.location = (0.0, 0.2, 0.3)
    master_col.objects.link(target_empty)

    cam_data = bpy.data.cameras.new("Cam_Beauty_Diorama")
    cam_data.type = 'PERSP'
    cam_data.lens = 56
    cam_obj = bpy.data.objects.new("Cam_Beauty_Diorama", cam_data)
    cam_obj.location = (-14.0, -19.0, 16.5)
    master_col.objects.link(cam_obj)

    cam_track = cam_obj.constraints.new(type='TRACK_TO')
    cam_track.target = target_empty
    cam_track.track_axis = 'TRACK_NEGATIVE_Z'
    cam_track.up_axis = 'UP_Y'
    scene.camera = cam_obj

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    beauty_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_beauty_view_v9_master.png"
    scene.render.filepath = beauty_out
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Master Beauty View v9 -> {beauty_out}")

    # CAMERA 2: Orthographic Top-Down Layout
    cam_data_top = bpy.data.cameras.new("Cam_TopDown")
    cam_data_top.type = 'ORTHO'
    cam_data_top.ortho_scale = 15.2
    cam_top_obj = bpy.data.objects.new("Cam_TopDown", cam_data_top)
    cam_top_obj.location = (0, 0, 18.0)
    cam_top_obj.rotation_euler = (0, 0, 0)
    master_col.objects.link(cam_top_obj)
    scene.camera = cam_top_obj

    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    top_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_topdown_plan_v9.png"
    scene.render.filepath = top_out
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Master Top-Down Plan v9 -> {top_out}")

    bpy.ops.wm.save_as_mainfile(filepath="D:/Projects/MOMO MAZE/BlenderSources/scenes/maze_beauty_environment.blend")
    print("  ✓ Saved Master Diorama Blend")

if __name__ == "__main__":
    execute_all_productions()
