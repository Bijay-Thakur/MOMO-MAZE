import bpy
import bmesh
import math
from mathutils import Vector, Euler

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for item in b:
            b.remove(item)

def create_fluffy_ghost_material():
    mat = bpy.data.materials.new("M_Spirit_Fluffy_Master")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    # Warm fluffy white with soft translucent SSS
    bsdf.inputs["Base Color"].default_value = (0.985, 0.965, 0.935, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    
    # Subsurface scattering for soft translucent inner glow
    bsdf.inputs["Subsurface Weight"].default_value = 0.55
    bsdf.inputs["Subsurface Radius"].default_value = (0.95, 0.80, 0.65)
    bsdf.inputs["Subsurface Scale"].default_value = 0.14
    
    # Sheen / Velvet peach fuzz
    bsdf.inputs["Sheen Weight"].default_value = 1.0
    bsdf.inputs["Sheen Roughness"].default_value = 0.35
    bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.95, 0.88, 1.0)
    
    # Soft emission for ethereal presence
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.97, 0.92, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 0.08

    # Procedural micro hair/fuzz bump
    tex_coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 110.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.75
    
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.02
    
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

def create_face_materials():
    # Eyes
    m_eye = bpy.data.materials.new("M_Spirit_Eyes")
    m_eye.use_nodes = True
    b_eye = m_eye.node_tree.nodes.get("Principled BSDF")
    b_eye.inputs["Base Color"].default_value = (0.04, 0.035, 0.035, 1.0)
    b_eye.inputs["Roughness"].default_value = 0.08

    # Catchlight
    m_shine = bpy.data.materials.new("M_Spirit_Catchlight")
    m_shine.use_nodes = True
    b_sh = m_shine.node_tree.nodes.get("Principled BSDF")
    b_sh.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_sh.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    b_sh.inputs["Emission Strength"].default_value = 2.0
    b_sh.inputs["Roughness"].default_value = 0.0

    # Rosy Blush
    m_blush = bpy.data.materials.new("M_Spirit_Blush")
    m_blush.use_nodes = True
    b_bl = m_blush.node_tree.nodes.get("Principled BSDF")
    b_bl.inputs["Base Color"].default_value = (1.0, 0.62, 0.60, 1.0)
    b_bl.inputs["Roughness"].default_value = 0.65
    b_bl.inputs["Subsurface Weight"].default_value = 0.55

    # Mouth
    m_mouth = bpy.data.materials.new("M_Spirit_Mouth")
    m_mouth.use_nodes = True
    b_m = m_mouth.node_tree.nodes.get("Principled BSDF")
    b_m.inputs["Base Color"].default_value = (0.70, 0.20, 0.24, 1.0)
    b_m.inputs["Roughness"].default_value = 0.35

    # Tongue
    m_tongue = bpy.data.materials.new("M_Spirit_Tongue")
    m_tongue.use_nodes = True
    b_t = m_tongue.node_tree.nodes.get("Principled BSDF")
    b_t.inputs["Base Color"].default_value = (1.0, 0.55, 0.58, 1.0)
    b_t.inputs["Roughness"].default_value = 0.25

    # Golden Halo Glow
    m_halo = bpy.data.materials.new("M_Spirit_Golden_Halo")
    m_halo.use_nodes = True
    b_h = m_halo.node_tree.nodes.get("Principled BSDF")
    b_h.inputs["Base Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    b_h.inputs["Emission Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    b_h.inputs["Emission Strength"].default_value = 4.5

    return m_eye, m_shine, m_blush, m_mouth, m_tongue, m_halo

def create_organic_wisp_mesh(name, control_points, base_thickness=0.38, mat=None):
    """Creates a smooth lofted wisp tail mesh along 3D spline control points with tapering thickness and closed caps."""
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
        
    curve_obj = bpy.data.objects.new(name=f"{name}_Obj", object_data=curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    
    mesh_obj = bpy.context.active_object
    mesh_obj.name = name
    if mat:
        mesh_obj.data.materials.append(mat)
    
    sub = mesh_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.shade_smooth()
    
    return mesh_obj

def build_spirit(spirit_type="follower", position=(0,0,0), yaw_deg=0):
    m_ghost = create_fluffy_ghost_material()
    m_eye, m_shine, m_blush, m_mouth, m_tongue, m_halo = create_face_materials()
    
    root = bpy.data.objects.new(f"Spirit_{spirit_type.capitalize()}_Root", None)
    root.location = position
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    bpy.context.collection.objects.link(root)
    
    # 1. Main Droplet Body (+Y is front face, -Y is tail attachment)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.92)
    body = bpy.context.active_object
    body.name = f"{spirit_type}_body"
    body.scale = (0.95, 1.05, 0.98)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_ghost)
    body.parent = root
    
    sub = body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 2. 3 to 4 Flowing Wisp Tails
    tails_data = []
    
    if spirit_type == "follower":
        tails_data = [
            # Main central flowing tail
            {
                "name": "tail_main",
                "thick": 0.40,
                "pts": [
                    {"co": Vector((0.0, -0.6, 0.05))},
                    {"co": Vector((0.0, -1.2, 0.0))},
                    {"co": Vector((0.05, -1.8, -0.1))},
                    {"co": Vector((0.12, -2.4, -0.18))},
                ]
            },
            # Upper sweeping wisp
            {
                "name": "tail_upper",
                "thick": 0.28,
                "pts": [
                    {"co": Vector((0.0, -0.5, 0.45))},
                    {"co": Vector((0.0, -1.0, 0.65))},
                    {"co": Vector((-0.05, -1.5, 0.90))},
                    {"co": Vector((0.0, -1.9, 1.15))},
                ]
            },
            # Left lower trailing wisp
            {
                "name": "tail_left",
                "thick": 0.24,
                "pts": [
                    {"co": Vector((-0.45, -0.5, -0.2))},
                    {"co": Vector((-0.70, -1.0, -0.3))},
                    {"co": Vector((-0.90, -1.4, -0.36))},
                    {"co": Vector((-1.05, -1.8, -0.40))},
                ]
            },
            # Right lower trailing wisp
            {
                "name": "tail_right",
                "thick": 0.24,
                "pts": [
                    {"co": Vector((0.45, -0.5, -0.2))},
                    {"co": Vector((0.70, -1.0, -0.3))},
                    {"co": Vector((0.90, -1.4, -0.36))},
                    {"co": Vector((1.05, -1.8, -0.40))},
                ]
            },
            # Head crest
            {
                "name": "head_crest",
                "thick": 0.20,
                "pts": [
                    {"co": Vector((0.0, 0.2, 0.90))},
                    {"co": Vector((0.0, -0.2, 1.12))},
                    {"co": Vector((0.0, -0.50, 1.22))},
                ]
            }
        ]
    elif spirit_type == "cutter":
        tails_data = [
            # Top speed crest
            {
                "name": "tail_top_crest",
                "thick": 0.30,
                "pts": [
                    {"co": Vector((0.0, 0.25, 0.88))},
                    {"co": Vector((0.0, -0.35, 1.12))},
                    {"co": Vector((0.0, -1.0, 1.20))},
                    {"co": Vector((0.0, -1.6, 1.10))},
                ]
            },
            # Main central speed stream
            {
                "name": "tail_center",
                "thick": 0.42,
                "pts": [
                    {"co": Vector((0.0, -0.6, 0.0))},
                    {"co": Vector((0.0, -1.3, -0.05))},
                    {"co": Vector((0.0, -2.0, -0.1))},
                    {"co": Vector((0.0, -2.6, -0.15))},
                ]
            },
            # Left speed wing
            {
                "name": "tail_wing_left",
                "thick": 0.28,
                "pts": [
                    {"co": Vector((-0.50, -0.3, 0.1))},
                    {"co": Vector((-0.85, -0.8, 0.15))},
                    {"co": Vector((-1.20, -1.3, 0.2))},
                    {"co": Vector((-1.50, -1.7, 0.22))},
                ]
            },
            # Right speed wing
            {
                "name": "tail_wing_right",
                "thick": 0.28,
                "pts": [
                    {"co": Vector((0.50, -0.3, 0.1))},
                    {"co": Vector((0.85, -0.8, 0.15))},
                    {"co": Vector((1.20, -1.3, 0.2))},
                    {"co": Vector((1.50, -1.7, 0.22))},
                ]
            }
        ]
    elif spirit_type == "wanderer":
        tails_data = [
            # Upper curled dance wisp
            {
                "name": "tail_upper_curl",
                "thick": 0.28,
                "pts": [
                    {"co": Vector((0.0, -0.5, 0.4))},
                    {"co": Vector((0.15, -1.0, 0.70))},
                    {"co": Vector((0.28, -1.5, 0.98))},
                    {"co": Vector((0.18, -1.9, 1.22))},
                ]
            },
            # Central wavy tail
            {
                "name": "tail_mid_wave",
                "thick": 0.36,
                "pts": [
                    {"co": Vector((0.0, -0.6, 0.0))},
                    {"co": Vector((-0.18, -1.2, -0.05))},
                    {"co": Vector((0.12, -1.7, 0.0))},
                    {"co": Vector((-0.08, -2.2, -0.05))},
                ]
            },
            # Lower left curled wisp
            {
                "name": "tail_low_left",
                "thick": 0.24,
                "pts": [
                    {"co": Vector((-0.45, -0.5, -0.25))},
                    {"co": Vector((-0.65, -0.9, -0.38))},
                    {"co": Vector((-0.55, -1.4, -0.50))},
                    {"co": Vector((-0.30, -1.7, -0.58))},
                ]
            },
            # Lower right curled wisp
            {
                "name": "tail_low_right",
                "thick": 0.24,
                "pts": [
                    {"co": Vector((0.45, -0.5, -0.25))},
                    {"co": Vector((0.70, -0.9, -0.35))},
                    {"co": Vector((0.88, -1.4, -0.4))},
                    {"co": Vector((0.98, -1.8, -0.42))},
                ]
            }
        ]

    for td in tails_data:
        wisp = create_organic_wisp_mesh(
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
            sh.name = f"{spirit_type}_shine_{side}"
            sh.location = (x + (0.02 if side=="L" else -0.02), 1.01, 0.17)
            sh.scale = (0.8, 0.3, 0.8)
            sh.data.materials.append(m_shine)
            sh.parent = root
            
        for side, x in [("L", -0.48), ("R", 0.48)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, segments=16, ring_count=12)
            bl = bpy.context.active_object
            bl.name = f"{spirit_type}_blush_{side}"
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
            sh.name = f"{spirit_type}_shine_{side}"
            sh.location = (x + (0.02 if side=="L" else -0.02), 1.01, 0.13)
            sh.scale = (0.8, 0.3, 0.8)
            sh.data.materials.append(m_shine)
            sh.parent = root
            
        for side, x in [("L", -0.48), ("R", 0.48)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=16, ring_count=12)
            bl = bpy.context.active_object
            bl.name = f"{spirit_type}_blush_{side}"
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
        mouth.name = f"{spirit_type}_mouth"
        mouth.location = (0.0, 1.05, -0.06)
        mouth.scale = (0.75, 0.4, 0.95)
        mouth.data.materials.append(m_mouth)
        mouth.parent = root
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=12, ring_count=10)
        tongue = bpy.context.active_object
        tongue.name = f"{spirit_type}_tongue"
        tongue.location = (0.0, 1.08, -0.09)
        tongue.scale = (0.8, 0.3, 0.6)
        tongue.data.materials.append(m_tongue)
        tongue.parent = root

        for side, x in [("L", -0.48), ("R", 0.48)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, segments=16, ring_count=12)
            bl = bpy.context.active_object
            bl.name = f"{spirit_type}_blush_{side}"
            bl.location = (x, 0.86, -0.06)
            bl.scale = (1.1, 0.3, 0.7)
            bl.rotation_euler = (math.radians(-15), 0, math.radians(12 if side=="L" else -12))
            bl.data.materials.append(m_blush)
            bl.parent = root

        # Golden Halo Sparkle Loop for Wanderer
        bpy.ops.mesh.primitive_torus_add(major_radius=1.25, minor_radius=0.028, major_segments=32, minor_segments=12)
        halo = bpy.context.active_object
        halo.name = "wanderer_golden_halo"
        halo.location = (0.0, 0.0, 0.15)
        halo.rotation_euler = (math.radians(35), math.radians(25), math.radians(-15))
        halo.data.materials.append(m_halo)
        halo.parent = root

    return root

def render_hero_lineup():
    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    # Soft warm peach-cream studio background
    bg.inputs["Color"].default_value = (0.985, 0.955, 0.92, 1.0)
    bg.inputs["Strength"].default_value = 0.95

    # Key Light (Warm golden sunlight)
    sun = bpy.data.lights.new("Sun_Key", 'SUN')
    sun.energy = 3.8
    sun.color = (1.0, 0.94, 0.86)
    sun.angle = math.radians(15)
    sun_obj = bpy.data.objects.new("Sun_Key", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(-40))
    bpy.context.collection.objects.link(sun_obj)

    # Soft Fill Light
    fill = bpy.data.lights.new("Fill_Light", 'POINT')
    fill.energy = 160.0
    fill.color = (0.9, 0.95, 1.0)
    fill.shadow_soft_size = 1.0
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    fill_obj.location = (-3.5, 5.0, 2.0)
    bpy.context.collection.objects.link(fill_obj)

    # Golden Rim Light
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.energy = 240.0
    rim.color = (1.0, 0.88, 0.65)
    rim.shadow_soft_size = 0.8
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.0, -4.5, 3.0)
    bpy.context.collection.objects.link(rim_obj)

    # Camera looking along -Y towards (+Y front).
    # Ghosts rotated by 155 degrees so their face (+Y) points at the camera (-Y)
    # and their tails stream gracefully to the left/backwards!
    s_fol = build_spirit("follower", position=(-2.6, 0.0, 0.0), yaw_deg=155)
    s_cut = build_spirit("cutter", position=(0.0, 0.0, 0.15), yaw_deg=150)
    s_wan = build_spirit("wanderer", position=(2.6, 0.0, -0.05), yaw_deg=160)

    # Camera Target
    target = bpy.data.objects.new("Cam_Target", None)
    target.location = (0.0, 0.0, 0.10)
    bpy.context.collection.objects.link(target)

    # Lineup Camera placed at Y=10.5m with 52mm lens for complete framing
    cam_data = bpy.data.cameras.new("Cam_Lineup")
    cam_data.type = 'PERSP'
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("Cam_Lineup", cam_data)
    cam_obj.location = (0.0, 10.5, 0.85)
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
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 960

    lineup_path = "D:/Projects/MOMO MAZE/BlenderSources/renders/ghosts/spirits_hero_lineup_v6_definitive.png"
    scene.render.filepath = lineup_path
    print(f"Rendering Master Hero Lineup v6 -> {lineup_path}")
    bpy.ops.render.render(write_still=True)
    print("  ✓ Hero Lineup v6 Rendered Successfully!")

    # Save Blend file
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved Validated Ghosts Blend -> {blend_path}")

    # Export individual FBXs
    for s_name, s_root in [("ghost_follower_validated", s_fol), ("ghost_cutter_validated", s_cut), ("ghost_wanderer_validated", s_wan)]:
        bpy.ops.object.select_all(action='DESELECT')
        s_root.select_set(True)
        for child in s_root.children_recursive:
            child.select_set(True)
        fbx_path = f"D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/{s_name}.fbx"
        bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, apply_scale_options='FBX_SCALE_ALL')
        print(f"  ✓ Exported {fbx_path}")

if __name__ == "__main__":
    reset_scene()
    render_hero_lineup()
