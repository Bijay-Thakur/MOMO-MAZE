"""
build_golumolu_v9_dino_master.py
MOMO MAZE - Master Refined Golumolu (Furry Dino Edition)

Refinements:
- Plump, cute dinosaur tail curving gently upward with rounded peach tip
- 3 rounded Godzilla-style dorsal plates/spikes running down the spine (warm peach)
- Big glossy black/dark chocolate eyes with prominent upper white catchlight shine patches (happy sparkling vibe)
- Open joyful D-smile mouth (:D) with cute tongue
- Warm peachy-pink cream fur body (#FFF0E2 to #FFD4C0) with velvety sheen and micro-fur hair texture
- Rosy blush cheeks (#FFA8A2) and peach ears/limbs
- High-quality studio lighting (warm key, cool fill, warm rim, soft studio environment)
- 4 Orthographic validation renders + master blend + FBX export
"""

import bpy
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Golumolu_Master")
    bpy.context.scene.collection.children.link(col)
    return col

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

def create_fluffy_fur_shader(name, base_color_rgb, sheen_tint_rgb=(1.0, 0.85, 0.78, 1.0), sss_weight=0.32):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    # Object-space micro-fur noise texture
    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 45.0
    noise.inputs['Detail'].default_value = 3.5
    noise.inputs['Roughness'].default_value = 0.6
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    # Color ramp for subtle fur strand tone variation
    ramp = tree.nodes.new('ShaderNodeValToRGB')
    r, g, b = base_color_rgb
    c_dark = (r * 0.94, g * 0.90, b * 0.86, 1.0)
    c_light = (min(1.0, r * 1.04), min(1.0, g * 1.02), min(1.0, b * 1.01), 1.0)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = c_dark
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = c_light
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # SSS for soft warm living creature glow
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = sss_weight
        bsdf.inputs['Subsurface Radius'].default_value = (0.55, 0.40, 0.30)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = sss_weight

    # Sheen for velvety peach-fuzz / hair rim
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.90
        bsdf.inputs['Sheen Roughness'].default_value = 0.40
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.90

    bsdf.inputs['Roughness'].default_value = 0.60

    # Micro bump for fuzzy hair texture
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.07
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_materials():
    # Warm cream body with subtle orange/pink blush undertone (#FFF2E4)
    mat_body = create_fluffy_fur_shader("M_Golumolu_CreamFur", (1.0, 0.94, 0.88), sss_weight=0.35)

    # Vibrant warm peach for ears, limbs, tail, and dorsal plates (#FFAE78)
    mat_peach = create_fluffy_fur_shader("M_Golumolu_PeachAccent", (1.0, 0.72, 0.52), sss_weight=0.40)

    # Rosy pink blush cheeks (#FFA8A2)
    mat_blush = create_fluffy_fur_shader("M_Golumolu_Blush", (1.0, 0.66, 0.64), sss_weight=0.45)

    # Glossy deep black/dark chocolate eyes (#1A1008)
    mat_eyes = bpy.data.materials.new("M_Golumolu_Eyes")
    mat_eyes.use_nodes = True
    bsdf_eyes = get_principled_bsdf(mat_eyes)
    bsdf_eyes.inputs['Base Color'].default_value = (0.10, 0.06, 0.03, 1.0)
    bsdf_eyes.inputs['Roughness'].default_value = 0.05
    if 'Specular IOR Level' in bsdf_eyes.inputs:
        bsdf_eyes.inputs['Specular IOR Level'].default_value = 0.9

    # Bright white catchlight shine patch for eyes (gives sparkling happy vibe)
    mat_shine = bpy.data.materials.new("M_Golumolu_EyeCatchlight")
    mat_shine.use_nodes = True
    bsdf_shine = get_principled_bsdf(mat_shine)
    bsdf_shine.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_shine.inputs['Roughness'].default_value = 0.02
    if 'Emission Color' in bsdf_shine.inputs:
        bsdf_shine.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf_shine.inputs['Emission Strength'].default_value = 1.5
    elif 'Emission' in bsdf_shine.inputs:
        bsdf_shine.inputs['Emission'].default_value = (1.0, 1.0, 1.0, 1.0)

    # Mouth cavity (#88251E)
    mat_mouth_dark = bpy.data.materials.new("M_Golumolu_MouthDark")
    mat_mouth_dark.use_nodes = True
    bsdf_md = get_principled_bsdf(mat_mouth_dark)
    bsdf_md.inputs['Base Color'].default_value = (0.55, 0.15, 0.12, 1.0)
    bsdf_md.inputs['Roughness'].default_value = 0.35

    # Mouth tongue coral pink (#FF7068)
    mat_tongue = bpy.data.materials.new("M_Golumolu_Tongue")
    mat_tongue.use_nodes = True
    bsdf_tg = get_principled_bsdf(mat_tongue)
    bsdf_tg.inputs['Base Color'].default_value = (1.0, 0.44, 0.41, 1.0)
    bsdf_tg.inputs['Roughness'].default_value = 0.3

    return {
        "body": mat_body,
        "peach": mat_peach,
        "blush": mat_blush,
        "eyes": mat_eyes,
        "shine": mat_shine,
        "mouth_dark": mat_mouth_dark,
        "tongue": mat_tongue
    }

def build_golumolu_model(collection, mats):
    """
    Builds the complete refined Golumolu character model:
    - Chubby cream body with peachy-pink blush
    - Dinosaur tail curving gently upward with rounded peach tip
    - 3 rounded Godzilla-style dorsal plates running along spine
    - Big glossy black eyes with prominent upper white catchlight shine patches
    - Cheerful open D-mouth (:D) with pink tongue
    - Peach ears, rosy blush cheeks, tiny rounded paws and feet
    """
    # 1. Main Chubby Body (Plump rounded creature volume)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "Golumolu_Body"
    body.scale = (1.08, 1.02, 0.98)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    body.data.materials.append(mats["body"])
    bpy.ops.object.shade_smooth()
    collection.objects.link(body)

    # 2. Dinosaur Tail (Plump, curved upwards gently, extending along +Y)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.34, depth=0.60,
        location=(0, 0.95, -0.12),
        rotation=(math.radians(-65), 0, 0)
    )
    tail = bpy.context.active_object
    tail.name = "Golumolu_Dino_Tail"
    tail.scale = (0.95, 0.85, 1.15)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Add rounded sphere cap at tip of tail
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.20,
        location=(0, 1.25, 0.05)
    )
    tip = bpy.context.active_object
    tip.name = "Golumolu_Tail_Tip"

    # Join tail cylinder and tip
    bpy.ops.object.select_all(action='DESELECT')
    tail.select_set(True)
    tip.select_set(True)
    bpy.context.view_layer.objects.active = tail
    bpy.ops.object.join()

    sub_tail = tail.modifiers.new("SubdivTail", 'SUBSURF')
    sub_tail.levels = 1
    bpy.ops.object.modifier_apply(modifier="SubdivTail")
    bpy.ops.object.shade_smooth()
    tail.data.materials.append(mats["peach"])
    tail.parent = body
    collection.objects.link(tail)

    # 3. Godzilla-Style Rounded Dorsal Plates (3 along the spine)
    plate_configs = [
        # (y, z, scale_x, scale_y, scale_z, tilt_angle)
        (0.35, 0.92, 0.12, 0.18, 0.22, math.radians(18)),   # Upper back (behind ears)
        (0.68, 0.68, 0.15, 0.22, 0.25, math.radians(35)),   # Mid-back (largest hero plate)
        (0.92, 0.30, 0.12, 0.17, 0.20, math.radians(52)),   # Lower back (near tail base)
    ]
    for idx, (py, pz, scx, scy, scz, tilt) in enumerate(plate_configs):
        # Create rounded dorsal fin / plate
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1.0,
            location=(0, py, pz),
            rotation=(tilt, 0, 0)
        )
        plate = bpy.context.active_object
        plate.name = f"Golumolu_Dorsal_Plate_{idx}"
        plate.scale = (scx, scy, scz)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        plate.data.materials.append(mats["peach"])
        plate.parent = body
        collection.objects.link(plate)

    # 4. Tiny Round Ears (Peach)
    ear_x = 0.52
    ear_y = -0.15
    ear_z = 0.88
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(sign * ear_x, ear_y, ear_z))
        ear = bpy.context.active_object
        ear.name = f"Golumolu_Ear_{side}"
        ear.scale = (1.0, 0.85, 0.95)
        ear.rotation_euler = (math.radians(-10), sign * math.radians(15), sign * math.radians(10))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        ear.data.materials.append(mats["peach"])
        ear.parent = body
        collection.objects.link(ear)

    # 5. Big Sparkling Black Eyes with Upper White Catchlight Shine Patch
    # Face is along -Y
    eye_x = 0.32
    eye_y = -0.92
    eye_z = 0.22
    for side, sign in [("L", -1), ("R", 1)]:
        # Base glossy dark eyeball
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(sign * eye_x, eye_y, eye_z))
        eye = bpy.context.active_object
        eye.name = f"Golumolu_Eye_{side}"
        eye.scale = (0.92, 0.42, 1.12) # Big, friendly chibi oval
        eye.rotation_euler = (math.radians(15), sign * math.radians(-5), 0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eyes"])
        eye.parent = body
        collection.objects.link(eye)

        # Upper White Catchlight Shine Patch (happy sparkling expression!)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.075,
            location=(sign * (eye_x - 0.035 * sign), eye_y - 0.055, eye_z + 0.065)
        )
        shine = bpy.context.active_object
        shine.name = f"Golumolu_Eye_Shine_{side}"
        shine.scale = (1.0, 0.25, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mats["shine"])
        shine.parent = body
        collection.objects.link(shine)

        # Secondary tiny lower twinkle
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.035,
            location=(sign * (eye_x + 0.045 * sign), eye_y - 0.045, eye_z - 0.045)
        )
        twinkle = bpy.context.active_object
        twinkle.name = f"Golumolu_Eye_Twinkle_{side}"
        twinkle.scale = (1.0, 0.25, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        twinkle.data.materials.append(mats["shine"])
        twinkle.parent = body
        collection.objects.link(twinkle)

    # 6. Rosy Pink Blush Cheeks (Soft Ovals under eyes)
    cheek_x = 0.58
    cheek_y = -0.84
    cheek_z = 0.04
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(sign * cheek_x, cheek_y, cheek_z))
        cheek = bpy.context.active_object
        cheek.name = f"Golumolu_Cheek_{side}"
        cheek.scale = (1.15, 0.35, 0.75) # Wide soft oval
        cheek.rotation_euler = (math.radians(20), sign * math.radians(-10), sign * math.radians(12))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        cheek.data.materials.append(mats["blush"])
        cheek.parent = body
        collection.objects.link(cheek)

    # 7. Joyful Open D-Smile Mouth (:D) with Tongue
    # Outer mouth opening
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.18, depth=0.15,
        location=(0, -0.96, 0.05),
        rotation=(math.radians(90), 0, 0)
    )
    mouth = bpy.context.active_object
    mouth.name = "Golumolu_Mouth_Cavity"
    mouth.scale = (1.15, 0.30, 0.95)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mats["mouth_dark"])
    mouth.parent = body
    collection.objects.link(mouth)

    # Cute pink tongue inside mouth
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.10,
        location=(0, -0.97, -0.01)
    )
    tongue = bpy.context.active_object
    tongue.name = "Golumolu_Tongue"
    tongue.scale = (1.2, 0.4, 0.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    tongue.data.materials.append(mats["tongue"])
    tongue.parent = body
    collection.objects.link(tongue)

    # 8. Tiny Rounded Limbs (Peach)
    # Hands (front sides, ready to grab Momos!)
    hand_x = 0.88
    hand_y = -0.25
    hand_z = -0.05
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(sign * hand_x, hand_y, hand_z))
        hand = bpy.context.active_object
        hand.name = f"Golumolu_Hand_{side}"
        hand.scale = (0.85, 1.25, 0.85)
        hand.rotation_euler = (math.radians(-15), sign * math.radians(25), sign * math.radians(-20))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        hand.data.materials.append(mats["peach"])
        hand.parent = body
        collection.objects.link(hand)

    # Feet (bottom support)
    foot_x = 0.44
    foot_y = 0.05
    foot_z = -0.88
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(sign * foot_x, foot_y, foot_z))
        foot = bpy.context.active_object
        foot.name = f"Golumolu_Foot_{side}"
        foot.scale = (0.9, 1.3, 0.75)
        foot.rotation_euler = (math.radians(10), sign * math.radians(-5), sign * math.radians(10))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        foot.data.materials.append(mats["peach"])
        foot.parent = body
        collection.objects.link(foot)

    return body

def setup_studio_lighting(collection):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Studio")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Soft warm studio environment
        bg.inputs['Color'].default_value = (0.96, 0.94, 0.92, 1.0)
        bg.inputs['Strength'].default_value = 0.85

    # Key Warm Golden Sun
    sun_data = bpy.data.lights.new("Sun_Key", 'SUN')
    sun_data.color = (1.0, 0.96, 0.88)
    sun_data.energy = 5.0
    sun_data.angle = math.radians(10)
    sun_obj = bpy.data.objects.new("Sun_Key", sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    collection.objects.link(sun_obj)

    # Soft Fill Light
    fill_data = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill_data.color = (0.90, 0.95, 1.0)
    fill_data.energy = 2.0
    fill_data.angle = math.radians(25)
    fill_obj = bpy.data.objects.new("Sun_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    collection.objects.link(fill_obj)

    # Rim Light (creates that lovely edge fuzz glow)
    rim_data = bpy.data.lights.new("Rim_Light", 'POINT')
    rim_data.color = (1.0, 0.85, 0.70)
    rim_data.energy = 45.0
    rim_data.shadow_soft_size = 0.4
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (0, 2.4, 1.4)
    collection.objects.link(rim_obj)

def render_orthographic_views(col):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.image_settings.file_format = 'PNG'

    cam_data = bpy.data.cameras.new("Cam_Ortho")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 3.2
    cam_obj = bpy.data.objects.new("Cam_Ortho", cam_data)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    views = [
        ("golumolu_v009_front", (0, -4.0, 0), (math.radians(90), 0, 0)),
        ("golumolu_v009_34view", (2.8, -2.8, 1.2), (math.radians(75), 0, math.radians(45))),
        ("golumolu_v009_side", (4.0, 0, 0), (math.radians(90), 0, math.radians(90))),
        ("golumolu_v009_back", (0, 4.0, 0), (math.radians(90), 0, math.radians(180))),
    ]

    for name, loc, rot in views:
        cam_obj.location = loc
        cam_obj.rotation_euler = rot
        out_path = f"D:/Projects/MOMO MAZE/BlenderSources/renders/golumolu/{name}.png"
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ Rendered {name} -> {out_path}")

def export_assets():
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved master Golumolu scene: {blend_path}")

    fbx_path = "D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/golumolu_validated.fbx"
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=False,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=True,
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"  ✓ Exported game-ready FBX: {fbx_path}")

def main():
    print("=== Building Master Refined Golumolu (v9 Dino Edition) ===")
    col = reset_scene()
    mats = create_materials()
    build_golumolu_model(col, mats)
    setup_studio_lighting(col)
    export_assets()
    render_orthographic_views(col)
    print("=== Master Refined Golumolu Complete ===")

if __name__ == "__main__":
    main()
