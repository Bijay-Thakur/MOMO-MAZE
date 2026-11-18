import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

def create_pbr(name, base_color, roughness=0.5, metalness=0.0, emissive=None, emissive_strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metalness
    if emissive and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emissive
        bsdf.inputs["Emission Strength"].default_value = emissive_strength
    return mat

def build_spirit(ghost_type):
    # Clear scene objects
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)

    # Materials
    mat_body = create_pbr(f"M_Spirit_{ghost_type}", (0.99, 0.98, 0.95, 1.0), roughness=0.52)
    mat_eye = create_pbr("M_Spirit_Eye", (0.04, 0.03, 0.02, 1.0), roughness=0.10)
    mat_glint = create_pbr("M_Eye_Glint", (1.0, 1.0, 1.0, 1.0), roughness=0.10, emissive=(1.0, 1.0, 1.0, 1.0), emissive_strength=2.0)
    mat_mouth = create_pbr("M_Spirit_Mouth", (0.22, 0.10, 0.10, 1.0), roughness=0.30)
    mat_sparkle = create_pbr("M_Gold_Aura", (1.0, 0.92, 0.45, 1.0), roughness=0.20, emissive=(1.0, 0.88, 0.35, 1.0), emissive_strength=4.0)

    # Orientation:
    # Front of face points towards -Y in Blender (Forward in glTF)
    # Tail extends backwards towards +Y in Blender

    # 1. Fluffy Pear/Egg Head & Body
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=16, radius=0.55)
    body = bpy.context.active_object
    body.name = f"Ghost_{ghost_type}_Body"
    body.scale = (0.92, 1.05, 0.95)
    body.location = (0, 0, 0.55)
    bpy.ops.object.transform_apply(scale=True, location=True)
    body.data.materials.append(mat_body)
    bpy.ops.object.shade_smooth()

    # 2. Horizontal Wispy Comet Tails flowing backwards (+Y)
    # Main central wisp tail
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.38, radius2=0.03, depth=1.15)
    tail_main = bpy.context.active_object
    tail_main.name = f"Ghost_{ghost_type}_TailMain"
    tail_main.rotation_euler = (math.pi / 2.0, 0, 0)
    tail_main.scale = (0.85, 0.70, 1.0)
    tail_main.location = (0, 0.65, 0.52)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
    tail_main.data.materials.append(mat_body)
    bpy.ops.object.shade_smooth()

    # Left wisp tail curving gently
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.22, radius2=0.02, depth=0.85)
    tail_l = bpy.context.active_object
    tail_l.name = f"Ghost_{ghost_type}_TailL"
    tail_l.rotation_euler = (math.radians(82), math.radians(-14), math.radians(18))
    tail_l.scale = (0.75, 0.65, 1.0)
    tail_l.location = (-0.28, 0.52, 0.46)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
    tail_l.data.materials.append(mat_body)
    bpy.ops.object.shade_smooth()

    # Right wisp tail curving gently
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.22, radius2=0.02, depth=0.85)
    tail_r = bpy.context.active_object
    tail_r.name = f"Ghost_{ghost_type}_TailR"
    tail_r.rotation_euler = (math.radians(82), math.radians(14), math.radians(-18))
    tail_r.scale = (0.75, 0.65, 1.0)
    tail_r.location = (0.28, 0.52, 0.46)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
    tail_r.data.materials.append(mat_body)
    bpy.ops.object.shade_smooth()

    # 3. Expressive Personality Faces (Front facing -Y)
    if ghost_type == "follower":
        # Curious, loyal, friendly: 2 shiny black bead eyes with glints
        for eye_side in (-1, 1):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=10, radius=0.08)
            eye = bpy.context.active_object
            eye.name = f"Eye_{'L' if eye_side < 0 else 'R'}"
            eye.scale = (0.80, 0.50, 1.15)
            eye.location = (eye_side * 0.20, -0.48, 0.58)
            bpy.ops.object.transform_apply(scale=True, location=True)
            eye.data.materials.append(mat_eye)
            bpy.ops.object.shade_smooth()

            # Specular twinkle glint
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.025)
            glint = bpy.context.active_object
            glint.name = f"Glint_{'L' if eye_side < 0 else 'R'}"
            glint.location = (eye_side * 0.18, -0.52, 0.62)
            bpy.ops.object.transform_apply(location=True)
            glint.data.materials.append(mat_glint)

        # Sweet curved smile mouth
        bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.018, major_segments=16, minor_segments=8)
        mouth = bpy.context.active_object
        mouth.name = "Smile_Mouth"
        mouth.rotation_euler = (math.pi / 2.0, 0, 0)
        mouth.scale = (1.0, 0.6, 0.8)
        mouth.location = (0, -0.50, 0.46)
        bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
        mouth.data.materials.append(mat_mouth)

    elif ghost_type == "cutter":
        # Clever, sneaky: angled eyebrows, narrowed cunning eyes, smirk
        for eye_side in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1.0)
            eye = bpy.context.active_object
            eye.name = f"Eye_{'L' if eye_side < 0 else 'R'}"
            eye.scale = (0.12, 0.04, 0.07)
            # Tilted angled eyebrows/eyes
            tilt = math.radians(22) * (-eye_side)
            eye.rotation_euler = (0, tilt, 0)
            eye.location = (eye_side * 0.20, -0.48, 0.58)
            bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
            eye.data.materials.append(mat_eye)
            bpy.ops.object.shade_smooth()

        # Sneaky sly smirk
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.03)
        mouth = bpy.context.active_object
        mouth.name = "Smirk_Mouth"
        mouth.rotation_euler = (math.pi / 2.0, math.radians(15), 0)
        mouth.location = (0.05, -0.50, 0.45)
        bpy.ops.object.transform_apply(rotation=True, location=True)
        mouth.data.materials.append(mat_mouth)

    elif ghost_type == "wanderer":
        # Dreamy, cheerful, joyful: arching laughing eyes (^ ^), open happy mouth (:D), golden aura ring
        for eye_side in (-1, 1):
            # Arching laughing eye (torus slice)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.02, major_segments=16, minor_segments=8)
            eye = bpy.context.active_object
            eye.name = f"Eye_Arch_{'L' if eye_side < 0 else 'R'}"
            eye.rotation_euler = (math.pi / 2.0, 0, 0)
            eye.scale = (1.0, 0.4, 0.9)
            eye.location = (eye_side * 0.20, -0.49, 0.60)
            bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
            eye.data.materials.append(mat_eye)

        # Cheerful open smiling mouth (:D)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.09)
        mouth = bpy.context.active_object
        mouth.name = "Open_Mouth"
        mouth.scale = (1.1, 0.5, 1.2)
        mouth.location = (0, -0.50, 0.44)
        bpy.ops.object.transform_apply(scale=True, location=True)
        mouth.data.materials.append(mat_mouth)

        # Swirling golden aura particle ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.72, minor_radius=0.025, major_segments=24, minor_segments=8)
        aura = bpy.context.active_object
        aura.name = "Wanderer_Aura_Ring"
        aura.rotation_euler = (math.radians(25), math.radians(15), 0)
        aura.location = (0, 0, 0.55)
        bpy.ops.object.transform_apply(rotation=True, location=True)
        aura.data.materials.append(mat_sparkle)

    # Export GLB
    export_path = f"D:/Projects/MOMO MAZE/WebGame/models/ghost_{ghost_type}.glb"
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    print(f"[MOMO MAZE] Exported ghost_{ghost_type}.glb successfully!")

def run():
    for gtype in ["follower", "cutter", "wanderer"]:
        build_spirit(gtype)
    print("[MOMO MAZE] All 3 ghosts remodeled and exported!")

if __name__ == "__main__":
    run()
