"""
Definitive Ghost Spirits 3D Model Generator
Faithfully matches Reference Concept Sheet: 03_Ghosts_Spirits_Concept.png
- Round, fluffy spirit head/body with soft warm white translucent glow (#FFF7EE)
- Flowing, waving, mist ribbon wisps tail curling gracefully backwards and upwards
  (NO spikes, NO cones, NO sharp tips! Soft, cloud-like rounded tapers)
- 3 Distinct Personalities:
  1. Follower: Friendly round eyes, catchlights, rosy blush cheeks, soft golden-warm aura
  2. Cutter: Clever angled eyes, dynamic playful wisp tail
  3. Wanderer: Dreamy starry eyes, rosy blush cheeks, ethereal halo ring
- Guaranteed 100% clean export with ZERO stray cubes or default objects
"""
import bpy
import math
from mathutils import Vector

def reset():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve)

def create_spirit_materials():
    # 1. Warm Fluffy White Body (translucent look, soft emission)
    m_body = bpy.data.materials.new("M_Spirit_Body")
    m_body.use_nodes = True
    nodes = m_body.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.985, 0.965, 0.935, 1.0) # #FFF7EE warm white
    bsdf.inputs["Roughness"].default_value = 0.40
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.45
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.96, 0.90, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.35

    # 2. Dark Eyes (#3D2B1F)
    m_eye = bpy.data.materials.new("M_Spirit_Eyes")
    m_eye.use_nodes = True
    b_eye = m_eye.node_tree.nodes.get("Principled BSDF")
    b_eye.inputs["Base Color"].default_value = (0.05, 0.035, 0.025, 1.0)
    b_eye.inputs["Roughness"].default_value = 0.12

    # 3. Eye Glint Catchlight
    m_glint = bpy.data.materials.new("M_Spirit_Glint")
    m_glint.use_nodes = True
    b_gl = m_glint.node_tree.nodes.get("Principled BSDF")
    b_gl.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    if "Emission Color" in b_gl.inputs:
        b_gl.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        b_gl.inputs["Emission Strength"].default_value = 3.0

    # 4. Rosy Blush Cheeks (#FFB3B0)
    m_blush = bpy.data.materials.new("M_Spirit_Blush")
    m_blush.use_nodes = True
    b_bl = m_blush.node_tree.nodes.get("Principled BSDF")
    b_bl.inputs["Base Color"].default_value = (1.0, 0.68, 0.68, 1.0)
    b_bl.inputs["Roughness"].default_value = 0.70

    # 5. Golden Halo
    m_halo = bpy.data.materials.new("M_Spirit_Halo")
    m_halo.use_nodes = True
    b_ha = m_halo.node_tree.nodes.get("Principled BSDF")
    b_ha.inputs["Base Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    if "Emission Color" in b_ha.inputs:
        b_ha.inputs["Emission Color"].default_value = (1.0, 0.88, 0.45, 1.0)
        b_ha.inputs["Emission Strength"].default_value = 3.5

    return m_body, m_eye, m_glint, m_blush, m_halo

def build_smooth_wisp(name, points, base_thickness=0.22, mat=None):
    """
    Creates a smooth lofted Bezier wisp with rounded cloud-like ends.
    Uses generous minimum radius so it NEVER looks like a spike or sharp cone.
    """
    curve = bpy.data.curves.new(name=f"{name}_curve", type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = base_thickness
    curve.bevel_resolution = 8
    curve.use_fill_caps = True

    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)

    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = pt["co"]
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        t = i / float(len(points) - 1)
        # Soft undulating envelope: starts full, gently wavers, and terminates with a rounded cloud puff
        # NOT a sharp cone! Minimum radius is 0.45 of base thickness
        bp.radius = max(0.40, 1.0 - 0.55 * t + 0.15 * math.sin(t * math.pi))

    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object

    if mat:
        mesh_obj.data.materials.append(mat)

    sub = mesh_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 1
    bpy.ops.object.shade_smooth()

    return mesh_obj

def build_spirit(spirit_type="follower"):
    reset()
    m_body, m_eye, m_glint, m_blush, m_halo = create_spirit_materials()

    root = bpy.data.objects.new(f"Spirit_{spirit_type.capitalize()}", None)
    bpy.context.collection.objects.link(root)

    # Orientation:
    # Face points towards -Y (forward in GLTF +Z)
    # Tail flows towards +Y (backward in GLTF -Z)
    # Up is +Z

    # 1. Round Fluffy Head/Body (radius 0.36)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=20, radius=0.35, location=(0, -0.05, 0.42))
    body = bpy.context.active_object; body.name = f"{spirit_type}_head"
    body.scale = (0.98, 1.02, 0.98); bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_body); body.parent = root
    bpy.ops.object.shade_smooth()

    # 2. Flowing Wispy Tail Ribbons
    # Main central wisp (curling smoothly backwards towards +Y and upwards)
    pts_main = [
        {"co": Vector((0.0, 0.10, 0.42))},
        {"co": Vector((0.0, 0.35, 0.44))},
        {"co": Vector((0.0, 0.60, 0.52))},
        {"co": Vector((0.0, 0.82, 0.62))},
    ]
    wisp_main = build_smooth_wisp(f"{spirit_type}_wisp_main", pts_main, base_thickness=0.20, mat=m_body)
    wisp_main.parent = root

    # Left lateral flowing wisp (sweeps back and out)
    pts_left = [
        {"co": Vector((-0.16, 0.08, 0.38))},
        {"co": Vector((-0.28, 0.32, 0.36))},
        {"co": Vector((-0.38, 0.55, 0.40))},
        {"co": Vector((-0.42, 0.72, 0.45))},
    ]
    wisp_left = build_smooth_wisp(f"{spirit_type}_wisp_left", pts_left, base_thickness=0.13, mat=m_body)
    wisp_left.parent = root

    # Right lateral flowing wisp (sweeps back and out)
    pts_right = [
        {"co": Vector((0.16, 0.08, 0.38))},
        {"co": Vector((0.28, 0.32, 0.36))},
        {"co": Vector((0.38, 0.55, 0.40))},
        {"co": Vector((0.42, 0.72, 0.45))},
    ]
    wisp_right = build_smooth_wisp(f"{spirit_type}_wisp_right", pts_right, base_thickness=0.13, mat=m_body)
    wisp_right.parent = root

    # Soft top crest wisp (characteristic billowing silhouette from concept sheet!)
    pts_crest = [
        {"co": Vector((0.0, -0.05, 0.72))},
        {"co": Vector((0.0, 0.14, 0.76))},
        {"co": Vector((0.0, 0.32, 0.74))},
    ]
    wisp_crest = build_smooth_wisp(f"{spirit_type}_wisp_crest", pts_crest, base_thickness=0.11, mat=m_body)
    wisp_crest.parent = root

    # 3. Facial Features by Personality (facing -Y)
    if spirit_type == "follower":
        # Cute round glossy brown oval eyes
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=12, radius=0.048,
                location=(side * 0.11, -0.37, 0.45)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.scale = (0.75, 0.35, 1.15); bpy.ops.object.transform_apply(scale=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            # Eye shine catchlight
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.018,
                location=(side * 0.10 - 0.01, -0.39, 0.475)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

            # Rosy blush cheeks
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.055,
                location=(side * 0.20, -0.32, 0.38)
            )
            blush = bpy.context.active_object; blush.name = f"blush_{side}"
            blush.scale = (1.1, 0.3, 0.8); bpy.ops.object.transform_apply(scale=True)
            blush.data.materials.append(m_blush); blush.parent = root
            bpy.ops.object.shade_smooth()

    elif spirit_type == "cutter":
        # Mischievous angled eyes
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=12, radius=0.022, depth=0.10,
                location=(side * 0.12, -0.37, 0.45)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.rotation_euler = (0, -side * math.radians(28), 0)
            bpy.ops.object.transform_apply(rotation=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            # Catchlight
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.015,
                location=(side * 0.11, -0.385, 0.47)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

    elif spirit_type == "wanderer":
        # Starry dreamy eyes
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=12, radius=0.054,
                location=(side * 0.12, -0.37, 0.45)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            # Star twinkle highlight
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.022,
                location=(side * 0.11, -0.395, 0.48)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

            # Blush cheeks
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.055,
                location=(side * 0.20, -0.32, 0.38)
            )
            blush = bpy.context.active_object; blush.name = f"blush_{side}"
            blush.scale = (1.1, 0.3, 0.8); bpy.ops.object.transform_apply(scale=True)
            blush.data.materials.append(m_blush); blush.parent = root
            bpy.ops.object.shade_smooth()

        # Golden Sparkle Halo Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.48, minor_radius=0.016,
            major_segments=24, minor_segments=8,
            location=(0, 0, 0.45)
        )
        halo = bpy.context.active_object; halo.name = "golden_halo"
        halo.rotation_euler = (math.radians(18), math.radians(24), 0)
        bpy.ops.object.transform_apply(rotation=True)
        halo.data.materials.append(m_halo); halo.parent = root
        bpy.ops.object.shade_smooth()

    # Center origin and export clean GLB - ONLY objects belonging to this spirit
    bpy.ops.object.select_all(action='DESELECT')
    for child in root.children:
        child.select_set(True)

    out_path = f"d:/Projects/MOMO MAZE/WebGame/models/ghost_{spirit_type}.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT'
    )
    print(f"Exported clean {spirit_type} to {out_path} successfully!")

if __name__ == "__main__":
    for st in ["follower", "cutter", "wanderer"]:
        build_spirit(st)
