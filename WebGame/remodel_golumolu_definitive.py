"""
Definitive Golumolu 3D Model Generator - Hero Scale
Faithfully matches Reference Concept Sheet: 02_Golumolu_Character_Concept.png
- Chubby, fluffy creature who loves momos!
- Increased Hero Size (~1.15m wide) to prominently fill spacious 2.0m garden corridors
- Soft cream fur body (#FCEEDD), white belly patch (#FFFBF2)
- Peach round ears, tiny peach paws, tiny peach feet (#FFC189)
- Rounded cute peach nub tail at back
- Prominent rosy blush cheeks (#FFB3B0)
- Glossy dark brown happy eyes (#6B4226) and open smiling mouth (#E27567)
- 100% clean export with ZERO stray cubes
"""
import bpy
import math

def reset():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve)

def create_golumolu_materials():
    # 1. Warm Golden Apricot / Honey Dino Fur Body (Vibrant & Distinct from white ghosts!)
    m_body = bpy.data.materials.new("M_Golu_Cream_Fur")
    b_b = m_body.node_tree.nodes.get("Principled BSDF")
    b_b.inputs["Base Color"].default_value = (1.0, 0.65, 0.28, 1.0)
    b_b.inputs["Roughness"].default_value = 0.82
    if "Subsurface Weight" in b_b.inputs:
        b_b.inputs["Subsurface Weight"].default_value = 0.35

    # 2. Warm Custard Belly Patch
    m_belly = bpy.data.materials.new("M_Golu_Belly")
    b_be = m_belly.node_tree.nodes.get("Principled BSDF")
    b_be.inputs["Base Color"].default_value = (1.0, 0.90, 0.75, 1.0)
    b_be.inputs["Roughness"].default_value = 0.85

    # 3. Rich Peach Accent (Ears, Paws, Tail)
    m_peach = bpy.data.materials.new("M_Golu_Peach_Accent")
    b_p = m_peach.node_tree.nodes.get("Principled BSDF")
    b_p.inputs["Base Color"].default_value = (1.0, 0.48, 0.20, 1.0)
    b_p.inputs["Roughness"].default_value = 0.75

    # 4. Rosy Cheeks
    m_blush = bpy.data.materials.new("M_Golu_Rosy_Blush")
    b_bl = m_blush.node_tree.nodes.get("Principled BSDF")
    b_bl.inputs["Base Color"].default_value = (1.0, 0.28, 0.38, 1.0)
    b_bl.inputs["Roughness"].default_value = 0.75

    # 5. Dark Brown Eyes (#6B4226)
    m_eye = bpy.data.materials.new("M_Golu_Eyes")
    b_e = m_eye.node_tree.nodes.get("Principled BSDF")
    b_e.inputs["Base Color"].default_value = (0.08, 0.045, 0.025, 1.0)
    b_e.inputs["Roughness"].default_value = 0.15

    # 6. Eye Shine (#FFFFFF)
    m_shine = bpy.data.materials.new("M_Golu_Eye_Shine")
    b_s = m_shine.node_tree.nodes.get("Principled BSDF")
    b_s.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    if "Emission Color" in b_s.inputs:
        b_s.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        b_s.inputs["Emission Strength"].default_value = 2.0

    # 7. Mouth Inner (#E27567)
    m_mouth = bpy.data.materials.new("M_Golu_Mouth")
    b_m = m_mouth.node_tree.nodes.get("Principled BSDF")
    b_m.inputs["Base Color"].default_value = (0.886, 0.459, 0.404, 1.0)
    b_m.inputs["Roughness"].default_value = 0.45

    return m_body, m_belly, m_peach, m_blush, m_eye, m_shine, m_mouth

def build_golumolu():
    reset()
    m_body, m_belly, m_peach, m_blush, m_eye, m_shine, m_mouth = create_golumolu_materials()

    root = bpy.data.objects.new("Golumolu_Hero", None)
    bpy.context.collection.objects.link(root)

    # Hero scale: radius 0.54 (total width ~1.12m, height ~1.18m)
    # Character faces -Y in Blender (maps to +Z in Three.js forward)

    # 1. Chubby Fluffy Body Sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.54, location=(0, 0, 0.55))
    body = bpy.context.active_object; body.name = "golumolu_body"
    body.scale = (1.04, 0.96, 0.94); bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_body); body.parent = root
    bpy.ops.object.shade_smooth()

    # 2. Fluffy White Tummy Patch (-Y front)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.38, location=(0, -0.24, 0.45))
    belly = bpy.context.active_object; belly.name = "golumolu_belly"
    belly.scale = (0.95, 0.50, 0.95); bpy.ops.object.transform_apply(scale=True)
    belly.data.materials.append(m_belly); belly.parent = root
    bpy.ops.object.shade_smooth()

    # 3. Soft Peach Ears (Tiny rounded peach nubs on top)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.15,
            location=(side * 0.34, 0.0, 1.04)
        )
        ear = bpy.context.active_object; ear.name = f"ear_{side}"
        ear.scale = (0.85, 0.70, 0.95); bpy.ops.object.transform_apply(scale=True)
        ear.data.materials.append(m_peach); ear.parent = root
        bpy.ops.object.shade_smooth()

    # 4. Big Rosy Blush Cheeks (front -Y)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=14, ring_count=10, radius=0.13,
            location=(side * 0.36, -0.38, 0.53)
        )
        blush = bpy.context.active_object; blush.name = f"blush_{side}"
        blush.scale = (1.10, 0.30, 0.85); bpy.ops.object.transform_apply(scale=True)
        blush.data.materials.append(m_blush); blush.parent = root
        bpy.ops.object.shade_smooth()

    # 5. Happy Expressive Eyes & Catchlights (front -Y)
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.08,
            location=(side * 0.20, -0.48, 0.64)
        )
        eye = bpy.context.active_object; eye.name = f"eye_{side}"
        eye.scale = (0.85, 0.35, 1.15); bpy.ops.object.transform_apply(scale=True)
        eye.data.materials.append(m_eye); eye.parent = root
        bpy.ops.object.shade_smooth()

        # Catchlight
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8, ring_count=8, radius=0.03,
            location=(side * 0.18 - 0.015, -0.52, 0.68)
        )
        glint = bpy.context.active_object; glint.name = f"glint_{side}"
        glint.data.materials.append(m_shine); glint.parent = root

    # 6. Tiny Cute Nose & Open Smiling Mouth
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.033, location=(0, -0.53, 0.58)
    )
    nose = bpy.context.active_object; nose.name = "nose"
    nose.scale = (1.0, 0.6, 0.8); bpy.ops.object.transform_apply(scale=True)
    nose.data.materials.append(m_eye); nose.parent = root

    # Open smile
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=12, radius=0.085, location=(0, -0.51, 0.48)
    )
    mouth = bpy.context.active_object; mouth.name = "mouth"
    mouth.scale = (1.2, 0.4, 0.9); bpy.ops.object.transform_apply(scale=True)
    mouth.data.materials.append(m_mouth); mouth.parent = root
    bpy.ops.object.shade_smooth()

    # 7. Tiny Rounded Peach Paws
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=14, ring_count=10, radius=0.12,
            location=(side * 0.42, -0.27, 0.36)
        )
        hand = bpy.context.active_object; hand.name = f"hand_{side}"
        hand.scale = (0.85, 1.10, 0.75); bpy.ops.object.transform_apply(scale=True)
        hand.data.materials.append(m_peach); hand.parent = root
        bpy.ops.object.shade_smooth()

    # 8. Tiny Rounded Peach Feet
    for side in (-1.0, 1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.14,
            location=(side * 0.24, -0.04, 0.12)
        )
        foot = bpy.context.active_object; foot.name = f"foot_{side}"
        foot.scale = (0.90, 1.35, 0.65); bpy.ops.object.transform_apply(scale=True)
        foot.data.materials.append(m_peach); foot.parent = root
        bpy.ops.object.shade_smooth()

    # 9. Cute Rounded Peach Nub Tail at back (+Y)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=12, radius=0.15, location=(0, 0.52, 0.36)
    )
    tail = bpy.context.active_object; tail.name = "tail"
    tail.scale = (0.90, 1.15, 0.85); bpy.ops.object.transform_apply(scale=True)
    tail.data.materials.append(m_peach); tail.parent = root
    bpy.ops.object.shade_smooth()

    # Export clean GLB
    bpy.ops.object.select_all(action='DESELECT')
    for child in root.children:
        child.select_set(True)

    out_path = "d:/Projects/MOMO MAZE/WebGame/models/golumolu.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT'
    )
    print(f"Exported Hero Golumolu (~1.15m) to {out_path} cleanly!")

if __name__ == "__main__":
    build_golumolu()
