"""
build_golumolu_v8_furry_dino.py
MOMO MAZE - Refined Golumolu Master Model (Blender 5.2)

Refinements based on user feedback & concept sheet:
- Dinosaur tail: Plump, cute creature tail extending from the lower back
- Godzilla-like soft rounded dorsal spikes (3-4 peach spikes along the spine)
- Eyes: Glossy dark eyes with distinct white catchlight patches on the upper part for a happy, sparkling expression
- Fur & Hair: Procedural micro-fur texture with velvety sheen and SSS for that soft, fluffy sensation
- Color: Warm cream with slight orange/pink blush undertone and vibrant peach accents
- 4 Orthographic validation renders (Front, 3/4 View, Side, Back)
- Export game-ready FBX and update golumolu_validated.blend
"""

import bpy
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Golumolu_Refined")
    bpy.context.scene.collection.children.link(col)
    return col

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

def create_fluffy_fur_material(name, base_rgb, sheen_rgb=(1.0, 0.85, 0.78, 1.0), sss_weight=0.35):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    # Object-space micro-fur noise
    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.6
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    # Color ramp for subtle fur strand tone variation
    ramp = tree.nodes.new('ShaderNodeValToRGB')
    c_base = Color((base_rgb[0], base_rgb[1], base_rgb[2]))
    c_dark = Color((base_rgb[0] * 0.92, base_rgb[1] * 0.90, base_rgb[2] * 0.88))
    c_light = Color((min(1.0, base_rgb[0] * 1.05), min(1.0, base_rgb[1] * 1.04), min(1.0, base_rgb[2] * 1.02)))
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (c_dark.r, c_dark.g, c_dark.b, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (c_light.r, c_light.g, c_light.b, 1.0)
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # SSS for soft fleshy glow
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = sss_weight
        bsdf.inputs['Subsurface Radius'].default_value = (0.55, 0.40, 0.30)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = sss_weight

    # Sheen for velvety peach-fuzz / hair rim
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.85
        bsdf.inputs['Sheen Roughness'].default_value = 0.45
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.85

    bsdf.inputs['Roughness'].default_value = 0.65

    # Micro bump for fuzzy hair texture
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_materials():
    # Warm cream body with subtle orange-pink undertone (#FFEADA)
    mat_body = create_fluffy_fur_material("M_Golumolu_CreamFur", (1.0, 0.92, 0.85), sss_weight=0.35)

    # Vibrant peach accents for ears, tail tip, limbs & dorsal spikes (#FFAE78)
    mat_peach = create_fluffy_fur_material("M_Golumolu_PeachAccent", (1.0, 0.70, 0.50), sss_weight=0.40)

    # Rosy pink blush cheeks (#FFA4A0)
    mat_blush = create_fluffy_fur_material("M_Golumolu_Blush", (1.0, 0.64, 0.62), sss_weight=0.45)

    # Dark glossy eyes (#20120A)
    mat_eyes = bpy.data.materials.new("M_Golumolu_Eyes")
    mat_eyes.use_nodes = True
    bsdf_eyes = get_principled_bsdf(mat_eyes)
    bsdf_eyes.inputs['Base Color'].default_value = (0.12, 0.07, 0.04, 1.0)
    bsdf_eyes.inputs['Roughness'].default_value = 0.08
    if 'Specular IOR Level' in bsdf_eyes.inputs:
        bsdf_eyes.inputs['Specular IOR Level'].default_value = 0.8

    # White catchlight shine patch for eyes
    mat_shine = bpy.data.materials.new("M_Golumolu_EyeCatchlight")
    mat_shine.use_nodes = True
    bsdf_shine = get_principled_bsdf(mat_shine)
    bsdf_shine.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_shine.inputs['Roughness'].default_value = 0.05
    if 'Emission Color' in bsdf_shine.inputs:
        bsdf_shine.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf_shine.inputs['Emission Strength'].default_value = 1.2
    elif 'Emission' in bsdf_shine.inputs:
        bsdf_shine.inputs['Emission'].default_value = (1.0, 1.0, 1.0, 1.0)

    # Mouth inner coral red (#E25B50)
    mat_mouth = bpy.data.materials.new("M_Golumolu_Mouth")
    mat_mouth.use_nodes = True
    bsdf_mouth = get_principled_bsdf(mat_mouth)
    bsdf_mouth.inputs['Base Color'].default_value = (0.88, 0.36, 0.32, 1.0)
    bsdf_mouth.inputs['Roughness'].default_value = 0.35

    return {
        "body": mat_body,
        "peach": mat_peach,
        "blush": mat_blush,
        "eyes": mat_eyes,
        "shine": mat_shine,
        "mouth": mat_mouth
    }

def build_golumolu_model(collection, mats):
    """
    Builds the complete refined Golumolu character model:
    - Chubby cream-peach body
    - Dinosaur tail extending backwards with peach tip
    - Row of 3 soft rounded dorsal spikes along spine (Godzilla style)
    - Big dark glossy eyes with upper white catchlight shine patches
    - Peach ears, pink blush ovals, happy D-mouth
    - Tiny rounded hands and feet
    """
    # 1. Main Chubby Body (Slightly teardrop/pear shape)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "Golumolu_Body"
    body.scale = (1.08, 1.02, 0.96)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    body.data.materials.append(mats["body"])
    bpy.ops.object.shade_smooth()
    collection.objects.link(body)

    # 2. Dinosaur Tail (Extending backwards along +Y)
    bpy.ops.mesh.primitive_cone_add(
        vertices=32, radius1=0.32, depth=0.65,
        location=(0, 0.95, -0.15),
        rotation=(math.radians(-75), 0, 0)
    )
    tail = bpy.context.active_object
    tail.name = "Golumolu_Dino_Tail"
    tail.scale = (1.0, 0.9, 1.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Subdiv + Smooth on tail for soft plump curvature
    sub_tail = tail.modifiers.new("SubdivTail", 'SUBSURF')
    sub_tail.levels = 1
    bpy.ops.object.modifier_apply(modifier="SubdivTail")
    bpy.ops.object.shade_smooth()
    tail.data.materials.append(mats["peach"])
    tail.parent = body
    collection.objects.link(tail)

    # 3. Soft Rounded Dorsal Spikes (Godzilla / Dinosaur Ridges along spine)
    # 3 peach spikes running down the back from between the ears to base of tail
    spike_configs = [
        # (y, z, scale_x, scale_y, scale_z, tilt_angle)
        (0.35, 0.90, 0.12, 0.16, 0.18, math.radians(20)),   # Top spike (behind head)
        (0.65, 0.65, 0.14, 0.18, 0.20, math.radians(35)),   # Mid-back spike (largest)
        (0.90, 0.28, 0.11, 0.15, 0.16, math.radians(50)),   # Lower back spike (near tail)
    ]
    for idx, (sy, sz, scx, scy, scz, tilt) in enumerate(spike_configs):
        bpy.ops.mesh.primitive_cone_add(
            vertices=24, radius1=1.0, depth=1.0,
            location=(0, sy, sz),
            rotation=(tilt, 0, 0)
        )
        spike = bpy.context.active_object
        spike.name = f"Golumolu_Dorsal_Spike_{idx}"
        spike.scale = (scx, scy, scz)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        bev_spk = spike.modifiers.new("BevelSpike", 'BEVEL')
        bev_spk.width = 0.05
        bev_spk.segments = 3
        bpy.ops.object.modifier_apply(modifier="BevelSpike")

        sub_spk = spike.modifiers.new("SubdivSpike", 'SUBSURF')
        sub_spk.levels = 1
        bpy.ops.object.modifier_apply(modifier="SubdivSpike")

        bpy.ops.object.shade_smooth()
        spike.data.materials.append(mats["peach"])
        spike.parent = body
        collection.objects.link(spike)

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

    # 5. Big Sparkling Eyes (Dark with upper white catchlight shine patch)
    # Face is along -Y
    eye_x = 0.32
    eye_y = -0.92
    eye_z = 0.22
    for side, sign in [("L", -1), ("R", 1)]:
        # Base glossy dark eyeball
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(sign * eye_x, eye_y, eye_z))
        eye = bpy.context.active_object
        eye.name = f"Golumolu_Eye_{side}"
        eye.scale = (0.9, 0.45, 1.1) # Happy rounded oval
        eye.rotation_euler = (math.radians(15), sign * math.radians(-5), 0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mats["eyes"])
        eye.parent = body
        collection.objects.link(eye)

        # Upper White Catchlight Shine Patch (Gives sparkling happy smiling vibe!)
        # Placed on the upper-outer quadrant of each eye
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.065,
            location=(sign * (eye_x - 0.03 * sign), eye_y - 0.05, eye_z + 0.06)
        )
        shine = bpy.context.active_object
        shine.name = f"Golumolu_Eye_Shine_{side}"
        shine.scale = (1.0, 0.3, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        shine.data.materials.append(mats["shine"])
        shine.parent = body
        collection.objects.link(shine)

        # Secondary tiny twinkle catchlight
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.03,
            location=(sign * (eye_x + 0.04 * sign), eye_y - 0.04, eye_z - 0.04)
        )
        twinkle = bpy.context.active_object
        twinkle.name = f"Golumolu_Eye_Twinkle_{side}"
        twinkle.scale = (1.0, 0.3, 1.0)
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
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(sign * cheek_x, cheek_y, cheek_z))
        cheek = bpy.context.active_object
        cheek.name = f"Golumolu_Cheek_{side}"
        cheek.scale = (1.1, 0.35, 0.75) # Wide soft oval
        cheek.rotation_euler = (math.radians(20), sign * math.radians(-10), sign * math.radians(12))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        cheek.data.materials.append(mats["blush"])
        cheek.parent = body
        collection.objects.link(cheek)

    # 7. Open Joyful D-Smile Mouth
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.18, depth=0.12,
        location=(0, -0.96, 0.05),
        rotation=(math.radians(90), 0, 0)
    )
    mouth = bpy.context.active_object
    mouth.name = "Golumolu_Mouth"
    mouth.scale = (1.1, 0.3, 0.9)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mats["mouth"])
    mouth.parent = body
    collection.objects.link(mouth)

    # 8. Tiny Rounded Limbs (Peach)
    # Hands (front sides)
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

def setup_lighting(collection):
    # Warm golden 3-point portrait lighting for character validation
    sun_data = bpy.data.lights.new("Sun_Key", 'SUN')
    sun_data.color = (1.0, 0.95, 0.85)
    sun_data.energy = 4.0
    sun_data.angle = math.radians(10)
    sun_obj = bpy.data.objects.new("Sun_Key", sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill_data.color = (0.88, 0.94, 1.0)
    fill_data.energy = 1.5
    fill_data.angle = math.radians(25)
    fill_obj = bpy.data.objects.new("Sun_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("Rim_Light", 'POINT')
    rim_data.color = (1.0, 0.85, 0.70)
    rim_data.energy = 30.0
    rim_data.shadow_soft_size = 0.3
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (0, 2.2, 1.2)
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
        ("golumolu_v008_front", (0, -4.0, 0), (math.radians(90), 0, 0)),
        ("golumolu_v008_34view", (2.8, -2.8, 1.2), (math.radians(75), 0, math.radians(45))),
        ("golumolu_v008_side", (4.0, 0, 0), (math.radians(90), 0, math.radians(90))),
        ("golumolu_v008_back", (0, 4.0, 0), (math.radians(90), 0, math.radians(180))),
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
    print("=== Building Refined Golumolu (Furry Dino Edition) ===")
    col = reset_scene()
    mats = create_materials()
    build_golumolu_model(col, mats)
    setup_lighting(col)
    export_assets()
    render_orthographic_views(col)
    print("=== Golumolu Refinement Complete ===")

if __name__ == "__main__":
    main()
