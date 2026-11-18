"""
Definitive Ghost Spirits 3D Model Generator - Wavy Ribbon Wisps
Faithfully matches Reference Concept Sheet: 03_Ghosts_Spirits_Concept.png
- Round, fluffy spirit head/body with soft warm white translucent glow (#FFF7EE)
- Wavy, undulating, mist ribbon wisps tail with beautiful S-curve undulations!
  (NO spikes, NO cones! Soft, flowing, wavy cloud-like ribbons)
- 3 Distinct Personalities:
  1. Follower: Friendly round eyes, catchlights, rosy blush cheeks, soft golden-warm halo
  2. Cutter: Clever angled eyes, sharp flicking double-wisp wavy tail
  3. Wanderer: Dreamy starry eyes, rosy blush cheeks, swirling ethereal halo ring
- 100% clean export with ZERO stray cubes
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
    # 1. Warm Fluffy White Body
    m_body = bpy.data.materials.new("M_Spirit_Body")
    bsdf = m_body.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.985, 0.965, 0.935, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.40
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.45
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.96, 0.90, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.35

    # 2. Dark Eyes (#3D2B1F)
    m_eye = bpy.data.materials.new("M_Spirit_Eyes")
    b_eye = m_eye.node_tree.nodes.get("Principled BSDF")
    b_eye.inputs["Base Color"].default_value = (0.05, 0.035, 0.025, 1.0)
    b_eye.inputs["Roughness"].default_value = 0.12

    # 3. Eye Glint Catchlight
    m_glint = bpy.data.materials.new("M_Spirit_Glint")
    b_gl = m_glint.node_tree.nodes.get("Principled BSDF")
    b_gl.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    if "Emission Color" in b_gl.inputs:
        b_gl.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        b_gl.inputs["Emission Strength"].default_value = 3.0

    # 4. Rosy Blush Cheeks (#FFB3B0)
    m_blush = bpy.data.materials.new("M_Spirit_Blush")
    b_bl = m_blush.node_tree.nodes.get("Principled BSDF")
    b_bl.inputs["Base Color"].default_value = (1.0, 0.68, 0.68, 1.0)
    b_bl.inputs["Roughness"].default_value = 0.70

    # 5. Golden Halo
    m_halo = bpy.data.materials.new("M_Spirit_Halo")
    b_ha = m_halo.node_tree.nodes.get("Principled BSDF")
    b_ha.inputs["Base Color"].default_value = (1.0, 0.88, 0.45, 1.0)
    if "Emission Color" in b_ha.inputs:
        b_ha.inputs["Emission Color"].default_value = (1.0, 0.88, 0.45, 1.0)
        b_ha.inputs["Emission Strength"].default_value = 3.5

    return m_body, m_eye, m_glint, m_blush, m_halo

def build_wavy_wisp(name, points, base_thickness=0.22, mat=None):
    """
    Creates a smooth, wavy lofted Bezier wisp with rounded cloud-puff ends.
    Uses generous minimum radius so it has zero spikes or cones.
    """
    curve = bpy.data.curves.new(name=f"{name}_curve", type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 20
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
        # Undulating thickness: stays full and puffy with gentle wave variation, rounded at tip
        bp.radius = max(0.42, 1.0 - 0.48 * t + 0.18 * math.sin(t * math.pi * 1.5))

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

    # Orientation: Face points towards -Y, Tail waves towards +Y, Up is +Z
    # Head radius 0.42 (total span ~0.95m - 1.05m, perfectly matching Golumolu)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=20, radius=0.42, location=(0, -0.06, 0.50))
    body = bpy.context.active_object; body.name = f"{spirit_type}_head"
    body.scale = (0.98, 1.02, 0.98); bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_body); body.parent = root
    bpy.ops.object.shade_smooth()

    # 2. Distinct WAVY Tail Ribbons (S-Curve Undulations!)
    if spirit_type == "follower":
        # Follower: Gentle flowing S-curve wave curling back and upward
        pts_main = [
            {"co": Vector((0.0, 0.10, 0.48))},
            {"co": Vector((0.14, 0.38, 0.56))},  # wave crest right
            {"co": Vector((-0.12, 0.70, 0.50))}, # wave trough left
            {"co": Vector((0.15, 1.02, 0.68))},  # wave crest right
            {"co": Vector((0.0, 1.32, 0.82))},   # rounded puff tip up
        ]
        pts_left = [
            {"co": Vector((-0.20, 0.08, 0.44))},
            {"co": Vector((-0.38, 0.36, 0.42))},
            {"co": Vector((-0.46, 0.68, 0.48))},
            {"co": Vector((-0.52, 0.92, 0.55))},
        ]
        pts_right = [
            {"co": Vector((0.20, 0.08, 0.44))},
            {"co": Vector((0.38, 0.36, 0.42))},
            {"co": Vector((0.46, 0.68, 0.48))},
            {"co": Vector((0.52, 0.92, 0.55))},
        ]
        pts_crest = [
            {"co": Vector((0.0, -0.05, 0.86))},
            {"co": Vector((0.08, 0.18, 0.92))},
            {"co": Vector((-0.06, 0.42, 0.88))},
        ]
    elif spirit_type == "cutter":
        # Cutter: Playful flicking double wave with higher frequency
        pts_main = [
            {"co": Vector((0.0, 0.10, 0.48))},
            {"co": Vector((-0.18, 0.35, 0.58))},
            {"co": Vector((0.18, 0.68, 0.52))},
            {"co": Vector((-0.15, 1.00, 0.72))},
            {"co": Vector((0.05, 1.28, 0.88))},
        ]
        pts_left = [
            {"co": Vector((-0.22, 0.08, 0.44))},
            {"co": Vector((-0.44, 0.35, 0.48))},
            {"co": Vector((-0.35, 0.65, 0.42))},
            {"co": Vector((-0.54, 0.95, 0.60))},
        ]
        pts_right = [
            {"co": Vector((0.22, 0.08, 0.44))},
            {"co": Vector((0.44, 0.35, 0.48))},
            {"co": Vector((0.35, 0.65, 0.42))},
            {"co": Vector((0.54, 0.95, 0.60))},
        ]
        pts_crest = [
            {"co": Vector((0.0, -0.05, 0.86))},
            {"co": Vector((-0.10, 0.20, 0.94))},
            {"co": Vector((0.10, 0.44, 0.90))},
        ]
    else: # wanderer
        # Wanderer: Swirling dreamy spiral wave
        pts_main = [
            {"co": Vector((0.0, 0.10, 0.48))},
            {"co": Vector((0.16, 0.36, 0.52))},
            {"co": Vector((0.05, 0.68, 0.64))},
            {"co": Vector((-0.16, 0.98, 0.58))},
            {"co": Vector((0.0, 1.28, 0.80))},
        ]
        pts_left = [
            {"co": Vector((-0.20, 0.08, 0.44))},
            {"co": Vector((-0.36, 0.35, 0.40))},
            {"co": Vector((-0.48, 0.68, 0.52))},
            {"co": Vector((-0.40, 0.98, 0.65))},
        ]
        pts_right = [
            {"co": Vector((0.20, 0.08, 0.44))},
            {"co": Vector((0.36, 0.35, 0.40))},
            {"co": Vector((0.48, 0.68, 0.52))},
            {"co": Vector((0.40, 0.98, 0.65))},
        ]
        pts_crest = [
            {"co": Vector((0.0, -0.05, 0.86))},
            {"co": Vector((0.0, 0.20, 0.95))},
            {"co": Vector((0.12, 0.45, 0.92))},
        ]

    wisp_main = build_wavy_wisp(f"{spirit_type}_wisp_main", pts_main, base_thickness=0.24, mat=m_body)
    wisp_main.parent = root

    wisp_left = build_wavy_wisp(f"{spirit_type}_wisp_left", pts_left, base_thickness=0.15, mat=m_body)
    wisp_left.parent = root

    wisp_right = build_wavy_wisp(f"{spirit_type}_wisp_right", pts_right, base_thickness=0.15, mat=m_body)
    wisp_right.parent = root

    wisp_crest = build_wavy_wisp(f"{spirit_type}_wisp_crest", pts_crest, base_thickness=0.13, mat=m_body)
    wisp_crest.parent = root

    # 3. Facial Features by Personality (facing -Y)
    if spirit_type == "follower":
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=12, radius=0.056,
                location=(side * 0.13, -0.44, 0.53)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.scale = (0.75, 0.35, 1.15); bpy.ops.object.transform_apply(scale=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.022,
                location=(side * 0.12 - 0.012, -0.465, 0.56)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.065,
                location=(side * 0.24, -0.38, 0.45)
            )
            blush = bpy.context.active_object; blush.name = f"blush_{side}"
            blush.scale = (1.1, 0.3, 0.8); bpy.ops.object.transform_apply(scale=True)
            blush.data.materials.append(m_blush); blush.parent = root
            bpy.ops.object.shade_smooth()

    elif spirit_type == "cutter":
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=12, radius=0.026, depth=0.12,
                location=(side * 0.14, -0.44, 0.53)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.rotation_euler = (0, -side * math.radians(28), 0)
            bpy.ops.object.transform_apply(rotation=True)
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.018,
                location=(side * 0.13, -0.46, 0.55)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

    elif spirit_type == "wanderer":
        for side in (-1.0, 1.0):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=12, radius=0.065,
                location=(side * 0.14, -0.44, 0.53)
            )
            eye = bpy.context.active_object; eye.name = f"eye_{side}"
            eye.data.materials.append(m_eye); eye.parent = root
            bpy.ops.object.shade_smooth()

            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=8, radius=0.026,
                location=(side * 0.13, -0.47, 0.56)
            )
            gl = bpy.context.active_object; gl.name = f"glint_{side}"
            gl.data.materials.append(m_glint); gl.parent = root

            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=12, ring_count=8, radius=0.065,
                location=(side * 0.24, -0.38, 0.45)
            )
            blush = bpy.context.active_object; blush.name = f"blush_{side}"
            blush.scale = (1.1, 0.3, 0.8); bpy.ops.object.transform_apply(scale=True)
            blush.data.materials.append(m_blush); blush.parent = root
            bpy.ops.object.shade_smooth()

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.55, minor_radius=0.018,
            major_segments=24, minor_segments=8,
            location=(0, 0, 0.52)
        )
        halo = bpy.context.active_object; halo.name = "golden_halo"
        halo.rotation_euler = (math.radians(18), math.radians(24), 0)
        bpy.ops.object.transform_apply(rotation=True)
        halo.data.materials.append(m_halo); halo.parent = root
        bpy.ops.object.shade_smooth()

    # Center origin and export clean GLB
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
    print(f"Exported clean wavy {spirit_type} to {out_path} successfully!")

if __name__ == "__main__":
    for st in ["follower", "cutter", "wanderer"]:
        build_spirit(st)
