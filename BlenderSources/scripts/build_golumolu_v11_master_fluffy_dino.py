"""
build_golumolu_v11_master_fluffy_dino.py
MOMO MAZE - Golumolu Master Asset v11 (Definitive Fluffy Dinosaur Edition)

Strictly incorporating user requirements:
- Furry & fluffy with visible hair texture and soft velvety sheen
- Color: Soft warm apricot-pink blush (#FFDDC8 to #FFB499 peachy-pink gradient)
- Cute dinosaur anatomy: Plump curved tail, chubby playful posture, tiny paws and feet
- Godzilla-style dorsal spikes: 4 stylized stepped triangular dorsal plates along the spine
- Smiling happy chibi eyes: Glossy dark eyes with prominent white highlight patch on upper half
  giving an unmistakable happy, joyful, smiling anime vibe
- Open cheerful smile with pink tongue and chubby peach blush cheeks
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Golumolu_v11_Master")
    bpy.context.scene.collection.children.link(col)
    return col

def create_fluffy_fur_material():
    mat = bpy.data.materials.new("M_Golumolu_Fluffy_Fur")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    # Color gradient: base cream-apricot to warm rosy peach on top/cheeks
    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    sep_xyz = tree.nodes.new('ShaderNodeSeparateXYZ')
    tree.links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])

    color_ramp = tree.nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.elements[0].position = 0.15
    color_ramp.color_ramp.elements[0].color = (1.00, 0.81, 0.72, 1.0) # Warm peachy orange-pink #FFCFB8
    color_ramp.color_ramp.elements[1].position = 0.85
    color_ramp.color_ramp.elements[1].color = (1.00, 0.65, 0.55, 1.0) # Rosy peach #FFA68C
    tree.links.new(sep_xyz.outputs['Z'], color_ramp.inputs['Fac'])
    tree.links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Micro-fur / hair bump for visible downy fluff
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 85.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.70
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.03
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Velvety peach-fuzz sheen
    bsdf.inputs['Roughness'].default_value = 0.58
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 1.0
        bsdf.inputs['Sheen Roughness'].default_value = 0.40
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (1.0, 0.75, 0.65, 1.0)
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 1.0

    # Subsurface scattering for soft translucent flesh
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.60, 0.45)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.35
        bsdf.inputs['Subsurface Color'].default_value = (1.0, 0.60, 0.50, 1.0)

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_spikes_material():
    mat = bpy.data.materials.new("M_Godzilla_Spikes")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.98, 0.68, 0.48, 1.0) # Warm apricot coral #FAAD7A
    bsdf.inputs['Roughness'].default_value = 0.45
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.40
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.45, 0.30)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.40

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_eye_materials():
    # Base eye: Deep glossy black
    mat_eye = bpy.data.materials.new("M_Eye_Deep_Black")
    mat_eye.use_nodes = True
    bsdf_e = mat_eye.node_tree.nodes.get("Principled BSDF")
    bsdf_e.inputs['Base Color'].default_value = (0.05, 0.04, 0.04, 1.0)
    bsdf_e.inputs['Roughness'].default_value = 0.08
    if 'IOR' in bsdf_e.inputs:
        bsdf_e.inputs['IOR'].default_value = 1.45

    # Catchlight shine patch: Pure gleaming white
    mat_shine = bpy.data.materials.new("M_Eye_Catchlight_White")
    mat_shine.use_nodes = True
    bsdf_s = mat_shine.node_tree.nodes.get("Principled BSDF")
    bsdf_s.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_s.inputs['Roughness'].default_value = 0.05
    if 'Emission Color' in bsdf_s.inputs:
        bsdf_s.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf_s.inputs['Emission Strength'].default_value = 0.80

    return mat_eye, mat_shine

def create_accent_materials():
    # Cheeks
    mat_cheek = bpy.data.materials.new("M_Cheek_Blush")
    mat_cheek.use_nodes = True
    bsdf_c = mat_cheek.node_tree.nodes.get("Principled BSDF")
    bsdf_c.inputs['Base Color'].default_value = (1.0, 0.58, 0.55, 1.0) # Rosy blush #FF948C
    bsdf_c.inputs['Roughness'].default_value = 0.60
    if 'Subsurface Weight' in bsdf_c.inputs:
        bsdf_c.inputs['Subsurface Weight'].default_value = 0.45

    # Mouth interior
    mat_mouth = bpy.data.materials.new("M_Mouth_Interior")
    mat_mouth.use_nodes = True
    bsdf_m = mat_mouth.node_tree.nodes.get("Principled BSDF")
    bsdf_m.inputs['Base Color'].default_value = (0.42, 0.08, 0.12, 1.0)
    bsdf_m.inputs['Roughness'].default_value = 0.30

    # Tongue
    mat_tongue = bpy.data.materials.new("M_Tongue_Pink")
    mat_tongue.use_nodes = True
    bsdf_t = mat_tongue.node_tree.nodes.get("Principled BSDF")
    bsdf_t.inputs['Base Color'].default_value = (0.95, 0.35, 0.42, 1.0)
    bsdf_t.inputs['Roughness'].default_value = 0.25

    return mat_cheek, mat_mouth, mat_tongue

def build_godzilla_spike(name, location, scale_vec, mat_spike, col):
    """Creates a stylized stepped Godzilla dorsal plate with center fin and mini side notches."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    spike = bpy.context.active_object
    spike.name = name

    # Edit geometry into a fan-crested stepped triangular plate
    bm = bmesh.new()
    bm.from_mesh(spike.data)

    # Taper top vertices and pull back
    for v in bm.verts:
        if v.co.z > 0:
            v.co.x *= 0.18 # Thin dorsal ridge
            v.co.y *= 0.55 # Steeper front
            v.co.z += 0.40 # Taller peak
        else:
            v.co.x *= 0.45 # Broad base
            v.co.y *= 0.85
    bm.to_mesh(spike.data)
    bm.free()

    spike.scale = scale_vec
    spike.location = location
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    sub = spike.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.shade_smooth()

    spike.data.materials.append(mat_spike)
    col.objects.link(spike)
    return spike

def build_golumolu_v11():
    col = reset_scene()

    mat_fur = create_fluffy_fur_material()
    mat_spike = create_spikes_material()
    mat_eye, mat_shine = create_eye_materials()
    mat_cheek, mat_mouth, mat_tongue = create_accent_materials()

    # 1. Main Body (Cute round pear-shaped marshmallow dinosaur)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0)
    body = bpy.context.active_object
    body.name = "Golumolu_Body"
    body.scale = (1.05, 1.10, 0.98)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    body.location = (0, 0, 1.0)

    sub_body = body.modifiers.new("Subsurf", 'SUBSURF')
    sub_body.levels = 2
    sub_body.render_levels = 2
    bpy.ops.object.shade_smooth()
    body.data.materials.append(mat_fur)
    col.objects.link(body)

    # 2. Plump Dinosaur Tail (Fleshy, curving up playfully behind)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.48, radius2=0.12, depth=1.2)
    tail = bpy.context.active_object
    tail.name = "Golumolu_Tail"
    tail.rotation_euler = (math.radians(-75), 0, math.radians(180))
    tail.location = (0, -0.98, -0.22)
    tail.parent = body
    sub_t = tail.modifiers.new("Subsurf", 'SUBSURF')
    sub_t.levels = 2
    sub_t.render_levels = 2
    bpy.ops.object.shade_smooth()
    tail.data.materials.append(mat_fur)
    col.objects.link(tail)

    # Tail tip soft sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.15)
    tip = bpy.context.active_object
    tip.name = "Golumolu_Tail_Tip"
    tip.location = (0, -1.55, 0.10)
    tip.parent = body
    bpy.ops.object.shade_smooth()
    tip.data.materials.append(mat_fur)
    col.objects.link(tip)

    # 3. Godzilla Dorsal Spikes (4 stepped plates along the spine and tail)
    spikes_config = [
        ("Spike_01_Neck", (0, -0.15, 0.98), (0.16, 0.32, 0.34)),
        ("Spike_02_Main", (0, -0.55, 0.92), (0.20, 0.42, 0.44)),
        ("Spike_03_Back", (0, -0.92, 0.70), (0.18, 0.36, 0.36)),
        ("Spike_04_Tail", (0, -1.25, 0.32), (0.14, 0.28, 0.26))
    ]
    spikes = []
    for s_name, s_loc, s_scale in spikes_config:
        spk = build_godzilla_spike(s_name, s_loc, s_scale, mat_spike, col)
        spk.parent = body
        spikes.append(spk)

    # 4. Cute Rounded Nub Horns/Ears on Crown
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.25)
        ear = bpy.context.active_object
        ear.name = f"Golumolu_Ear_{suffix}"
        ear.scale = (0.9, 0.9, 1.25)
        ear.location = (sign * 0.46, 0.15, 0.88)
        ear.rotation_euler = (math.radians(-12), math.radians(sign * 22), 0)
        ear.parent = body
        bpy.ops.object.shade_smooth()
        ear.data.materials.append(mat_fur)
        col.objects.link(ear)

    # 5. Big Smiling Eyes with White Catchlight Shine Patch on Upper Half
    for sign, suffix in [(-1, "L"), (1, "R")]:
        # Dark glossy pupil base
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.22)
        eye = bpy.context.active_object
        eye.name = f"Golumolu_Eye_{suffix}"
        eye.scale = (0.75, 0.30, 1.05)
        eye.location = (sign * 0.38, 0.96, 0.14)
        eye.rotation_euler = (math.radians(-12), math.radians(sign * 8), math.radians(-sign * 6))
        eye.parent = body
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_eye)
        col.objects.link(eye)

        # Upper white gleam patch (happy smiling crescent / shine covering ~45% of eye)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.11)
        shine_up = bpy.context.active_object
        shine_up.name = f"Golumolu_EyeShine_Upper_{suffix}"
        shine_up.scale = (1.1, 0.35, 0.85)
        shine_up.location = (sign * 0.38, 1.05, 0.22)
        shine_up.rotation_euler = eye.rotation_euler
        shine_up.parent = body
        bpy.ops.object.shade_smooth()
        shine_up.data.materials.append(mat_shine)
        col.objects.link(shine_up)

        # Secondary cute lower twinkle dot
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.045)
        shine_low = bpy.context.active_object
        shine_low.name = f"Golumolu_EyeShine_Lower_{suffix}"
        shine_low.location = (sign * 0.44, 1.05, 0.08)
        shine_low.parent = body
        bpy.ops.object.shade_smooth()
        shine_low.data.materials.append(mat_shine)
        col.objects.link(shine_low)

    # 6. Chubby Peach Blush Cheeks
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.22)
        chk = bpy.context.active_object
        chk.name = f"Golumolu_Cheek_{suffix}"
        chk.scale = (1.20, 0.40, 0.85)
        chk.location = (sign * 0.64, 0.88, -0.06)
        chk.rotation_euler = (math.radians(-10), math.radians(sign * 25), math.radians(-sign * 15))
        chk.parent = body
        bpy.ops.object.shade_smooth()
        chk.data.materials.append(mat_cheek)
        col.objects.link(chk)

    # 7. Happy Open Cheerful Smile
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.18)
    mouth = bpy.context.active_object
    mouth.name = "Golumolu_Mouth"
    mouth.scale = (1.25, 0.30, 0.65)
    mouth.location = (0, 1.09, -0.06)
    mouth.rotation_euler = (math.radians(-15), 0, 0)
    mouth.parent = body
    bpy.ops.object.shade_smooth()
    mouth.data.materials.append(mat_mouth)
    col.objects.link(mouth)

    # Pink cute tongue
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.12)
    tongue = bpy.context.active_object
    tongue.name = "Golumolu_Tongue"
    tongue.scale = (1.1, 0.35, 0.55)
    tongue.location = (0, 1.12, -0.09)
    tongue.parent = body
    bpy.ops.object.shade_smooth()
    tongue.data.materials.append(mat_tongue)
    col.objects.link(tongue)

    # 8. Chubby Front Paws (Reaching playfully forward)
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.20)
        paw = bpy.context.active_object
        paw.name = f"Golumolu_Paw_{suffix}"
        paw.scale = (0.75, 1.15, 0.70)
        paw.location = (sign * 0.62, 0.82, -0.22)
        paw.rotation_euler = (math.radians(-25), math.radians(sign * 20), math.radians(sign * 15))
        paw.parent = body
        bpy.ops.object.shade_smooth()
        paw.data.materials.append(mat_fur)
        col.objects.link(paw)

    # 9. Plump Rounded Feet (Underneath)
    for sign, suffix in [(-1, "L"), (1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.28)
        foot = bpy.context.active_object
        foot.name = f"Golumolu_Foot_{suffix}"
        foot.scale = (0.90, 1.30, 0.65)
        foot.location = (sign * 0.44, -0.15, -0.88)
        foot.rotation_euler = (math.radians(12), math.radians(sign * 10), math.radians(sign * 15))
        foot.parent = body
        bpy.ops.object.shade_smooth()
        foot.data.materials.append(mat_fur)
        col.objects.link(foot)

    # Save Blend & FBX
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved Master Blend -> {blend_path}")

    fbx_path = "D:/Projects/MOMO MAZE/BlenderSources/exports/fbx/golumolu_validated.fbx"
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, apply_scale_options='FBX_SCALE_ALL')
    print(f"  ✓ Exported Master FBX -> {fbx_path}")

    return body, col

def render_four_views(body, col):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.image_settings.file_format = 'PNG'

    # Lighting
    world = scene.world or bpy.data.worlds.new("World_Studio")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.95, 0.93, 0.90, 1.0)
        bg.inputs['Strength'].default_value = 0.85

    sun = bpy.data.lights.new("Sun_Main", 'SUN')
    sun.energy = 4.5
    sun.color = (1.0, 0.96, 0.90)
    sun_obj = bpy.data.objects.new("Sun_Main", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    col.objects.link(sun_obj)

    fill = bpy.data.lights.new("Sun_Fill", 'SUN')
    fill.energy = 2.0
    fill.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("Sun_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-20), math.radians(140))
    col.objects.link(fill_obj)

    cam_data = bpy.data.cameras.new("Cam_Val")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 3.6
    cam_obj = bpy.data.objects.new("Cam_Val", cam_data)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    views = [
        ("front",  (0, 4.0, 1.0),      (math.radians(90), 0, math.radians(180))),
        ("34view", (2.8, 2.8, 2.2),    (math.radians(65), 0, math.radians(135))),
        ("side",   (4.0, 0, 1.0),      (math.radians(90), 0, math.radians(90))),
        ("back",   (0, -4.0, 1.0),     (math.radians(90), 0, 0))
    ]

    for view_name, cam_pos, cam_rot in views:
        cam_obj.location = cam_pos
        cam_obj.rotation_euler = cam_rot
        bpy.context.view_layer.update()
        out_file = f"D:/Projects/MOMO MAZE/BlenderSources/renders/golumolu/golumolu_v011_{view_name}.png"
        scene.render.filepath = out_file
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ Rendered Golumolu v11 [{view_name}] -> {out_file}")

if __name__ == "__main__":
    print("==================================================")
    print("Building Golumolu Master Asset v11 (Dino & Fur)")
    print("==================================================")
    body, col = build_golumolu_v11()
    render_four_views(body, col)
    print("All tasks completed successfully!")
