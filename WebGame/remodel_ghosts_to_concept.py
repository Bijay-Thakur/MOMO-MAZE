"""
Remodel Ghost Spirits to EXACTLY match Reference Concept Sheet: 03_Ghosts_Spirits_Concept.png
- Round fluffy head/body
- Curled, waving, flowing misty ribbons/wisps tail (curving up and out, NO cones, NO spikes)
- Individual personalities: Follower, Cutter, Wanderer
- Export clean GLB files without default cubes or camera artifacts
"""
import bpy
import bmesh
import math
from mathutils import Vector, Euler

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_spirit_materials():
    # 1. Warm Fluffy White Body (translucent look, soft emission)
    m_body = bpy.data.materials.new("M_Spirit_Fluffy_Master")
    m_body.use_nodes = True
    nodes = m_body.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.985, 0.965, 0.935, 1.0) # #FFF7EE warm white
    bsdf.inputs["Roughness"].default_value = 0.45
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.50
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.97, 0.92, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.25

    # 2. Dark Eyes
    m_eye = bpy.data.materials.new("M_Spirit_Eyes")
    m_eye.use_nodes = True
    b_eye = m_eye.node_tree.nodes.get("Principled BSDF")
    b_eye.inputs["Base Color"].default_value = (0.04, 0.035, 0.035, 1.0)
    b_eye.inputs["Roughness"].default_value = 0.10

    # 3. Eye Glint Catchlight
    m_glint = bpy.data.materials.new("M_Spirit_Catchlight")
    m_glint.use_nodes = True
    b_gl = m_glint.node_tree.nodes.get("Principled BSDF")
    b_gl.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    if "Emission Color" in b_gl.inputs:
        b_gl.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        b_gl.inputs["Emission Strength"].default_value = 3.0

    # 4. Rosy Blush Cheeks
    m_blush = bpy.data.materials.new("M_Spirit_Blush")
    m_blush.use_nodes = True
    b_bl = m_blush.node_tree.nodes.get("Principled BSDF")
    b_bl.inputs["Base Color"].default_value = (1.0, 0.65, 0.65, 1.0)
    b_bl.inputs["Roughness"].default_value = 0.70

    # 5. Golden Halo
    m_halo = bpy.data.materials.new("M_Spirit_Golden_Halo")
    m_halo.use_nodes = True
    b_ha = m_halo.node_tree.nodes.get("Principled BSDF")
    b_ha.inputs["Base Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    if "Emission Color" in b_ha.inputs:
        b_ha.inputs["Emission Color"].default_value = (1.0, 0.88, 0.45, 1.0)
        b_ha.inputs["Emission Strength"].default_value = 4.0

    return m_body, m_eye, m_glint, m_blush, m_halo

def build_wisp_curve(name, points, base_thickness=0.35, mat=None):
    """Creates a smooth lofted Bezier wisp with rounded taper along control points."""
    curve = bpy.data.curves.new(name=f"{name}_curve", type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = base_thickness
    curve.bevel_resolution = 6
    curve.use_fill_caps = True

    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)

    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = pt["co"]
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        t = i / float(len(points) - 1)
        # Soft graceful taper to a rounded tip
        bp.radius = max(0.08, (1.0 - t)**1.2)

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

    # 1. Round Fluffy Head/Body (radius 0.65)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=20, radius=0.65, location=(0, 0, 0.45))
    body = bpy.context.active_object
    body.name = f"{spirit_type}_head"
    body.scale = (0.96, 1.04, 0.98)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_body)
    body.parent = root
    bpy.ops.object.shade_smooth()

    # 2. Flowing Wispy Tail Ribbons (curling softly upwards & outwards like flowing mist)
    # Main central wisp (curling gently upwards)
    pts_main = [
        {"co": Vector((0.0, -0.35, 0.45))},
        {"co": Vector((0.0, -0.80, 0.48))},
        {"co": Vector((0.0, -1.25, 0.58))},
        {"co": Vector((0.0, -1.65, 0.72))},
    ]
    wisp_main = build_wisp_curve(f"{spirit_type}_wisp_main", pts_main, base_thickness=0.32, mat=m_body)
    wisp_main.parent = root

    # Left lateral wisp
    pts_left = [
        {"co": Vector((-0.28, -0.32, 0.38))},
        {"co": Vector((-0.52, -0.75, 0.36))},
        {"co": Vector((-0.68, -1.15, 0.40))},
        {"co": Vector((-0.78, -1.48, 0.46))},
    ]
    wisp_left = build_wisp_curve(f"{spirit_type}_wisp_left", pts_left, base_thickness=0.20, mat=m_body)
    wisp_left.parent = root

    # Right lateral wisp
    pts_right = [
        {"co": Vector((0.28, -0.32, 0.38))},
        {"co": Vector((0.52, -0.75, 0.36))},
        {"co": Vector((0.68, -1.15, 0.40))},
        {"co": Vector((0.78, -1.48, 0.46))},
    ]
    wisp_right = build_wisp_curve(f"{spirit_type}_wisp_right", pts_right, base_thickness=0.20, mat=m_body)
    wisp_right.parent = root

    # Soft top crest wisp (characteristic silhouette from concept sheet!)
    pts_crest = [
        {"co": Vector((0.0, 0.12, 0.98))},
        {"co": Vector((0.0, -0.22, 1.05))},
        {"co": Vector((0.0, -0.58, 1.02))},
    ]
    wisp_crest = build_wisp_curve(f"{spirit_type}_wisp_crest", pts_crest, base_thickness=0.18, mat=m_body)
    wisp_crest.parent = root

    # 3. Facial Features by Personality
    if spirit_type == "follower":
        # Cute round glossy brown oval eyes
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=12, radius=0.08,
                location=(side * 0.18, 0.58, 0.52)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.scale = (0.75, 0.35, 1.15); bpy.ops.object.transform_apply(scale=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            # Eye shine catchlight
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.03,
                location=(side * 0.16 + 0.02, 0.605, 0.56)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

            # Rosy cheeks
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.09,
                location=(side * 0.34, 0.48, 0.38)
            )
            blush = bpy.context.active_object; blush.name = f"blush_{side}"
            blush.scale = (1.1, 0.3, 0.8); bpy.ops.object.transform_apply(scale=True)
            blush.data.materials.append(m_blush); blush.parent = root
            bpy.ops.object.shade_smooth()

    elif spirit_type == "cutter":
        # Mischievous angled eyes (slanted inward ~30 degrees)
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=12, radius=0.085,
                location=(side * 0.19, 0.58, 0.52)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.scale = (1.2, 0.35, 0.65)
            eye.rotation_euler = (0, 0, math.radians(side * -28))
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

    elif spirit_type == "wanderer":
        # Happy smiling crescent eyes (^ ^)
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.07, minor_radius=0.022,
                major_segments=16, minor_segments=8,
                location=(side * 0.18, 0.58, 0.52)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.rotation_euler = (math.radians(90), 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            # Rosy cheeks
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.09,
                location=(side * 0.34, 0.48, 0.38)
            )
            blush = bpy.context.active_object; blush.name = f"blush_{side}"
            blush.scale = (1.1, 0.3, 0.8); bpy.ops.object.transform_apply(scale=True)
            blush.data.materials.append(m_blush); blush.parent = root
            bpy.ops.object.shade_smooth()

        # Golden Sparkle Halo Ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.85, minor_radius=0.025,
            major_segments=24, minor_segments=8,
            location=(0, 0, 0.45)
        )
        halo = bpy.context.active_object; halo.name = "golden_halo"
        halo.rotation_euler = (math.radians(18), math.radians(24), 0)
        bpy.ops.object.transform_apply(rotation=True)
        halo.data.materials.append(m_halo); halo.parent = root
        bpy.ops.object.shade_smooth()

    # Center origin and export GLB
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.select_set(True)

    out_path = f"d:/Projects/MOMO MAZE/WebGame/models/ghost_{spirit_type}.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT'
    )
    print(f"Exported {spirit_type} to {out_path} cleanly!")

if __name__ == "__main__":
    for st in ["follower", "cutter", "wanderer"]:
        build_spirit(st)
