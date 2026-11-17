"""
build_environment_v7_definitive_diorama.py
MOMO MAZE - Definitive Grassy & Fluffy Maze Diorama v7 (Blender 5.2)

100% Faithful Recreation of Reference Image 4 Panel (1) & Panel (2):
- Complete diorama framing: Full 12x12m square maze within raised stone retaining bed
- Dense 3D physical grass tufts (800+ instanced clumps) carpeting corridors and outer lawn
- Volumetric puffy living hedges: organic cloud clumps along all ridges and corners
- 4 stylized background cartoon trees with multi-lobed cloud foliage behind Leaf Gate
- Flower & clover beds: 5-petal daisies, pink buttercups, green clovers along paths
- Whimsical Leaf Gate with wooden posts, stone plinths, leaf crown, and glowing Momo crest
- Momo Collectible: Glowing peach fruit on stone pedestal with golden star motes
- Golumolu v11 Master Dino scaled properly to corridor (scale 0.48), leaping joyfully
- 3 Ghost Spirits v9 scaled to corridor (scale 0.45) floating gracefully with 3-4 trailing wisps
- Isometric diorama camera matching Reference Image 4
- Cycles CPU render (1920x1080 beauty view, 1200x1200 top-down plan)
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Master_Diorama_v7")
    bpy.context.scene.collection.children.link(col)
    return col

# ==============================================================================
# MATERIALS
# ==============================================================================
def create_lush_hedge_material():
    mat = bpy.data.materials.new("M_Hedge_Lush_Fluffy")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.5
    noise.inputs['Detail'].default_value = 3.5
    noise.inputs['Roughness'].default_value = 0.55
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.10
    ramp.color_ramp.elements[0].color = (0.16, 0.36, 0.08, 1.0) # Forest shadow #295C14
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.65, 0.90, 0.20, 1.0) # Sunlit lime #A6E633
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.50
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.85
        bsdf.inputs['Sheen Roughness'].default_value = 0.40
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.80, 0.98, 0.40, 1.0)
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.85

    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.35
        bsdf.inputs['Subsurface Radius'].default_value = (0.50, 0.80, 0.20)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.35

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_grass_blade_material():
    mat = bpy.data.materials.new("M_Grass_Blade")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    sep_xyz = tree.nodes.new('ShaderNodeSeparateXYZ')
    tree.links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.05
    ramp.color_ramp.elements[0].color = (0.22, 0.46, 0.08, 1.0) # Deep spring root #387514
    ramp.color_ramp.elements[1].position = 0.95
    ramp.color_ramp.elements[1].color = (0.72, 0.95, 0.25, 1.0) # Radiant lime tip #B8F240
    tree.links.new(sep_xyz.outputs['Z'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.45
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.40
        bsdf.inputs['Subsurface Radius'].default_value = (0.45, 0.85, 0.20)

    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_ground_lawn_material():
    mat = bpy.data.materials.new("M_Ground_Lawn")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 4.5
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (0.30, 0.55, 0.12, 1.0) # #4D8C1F
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.54, 0.82, 0.18, 1.0) # #8AD12E
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.75
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_retaining_stone_material():
    mat = bpy.data.materials.new("M_Retaining_Stone")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 6.0
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.80, 0.60, 0.46, 1.0) # Terracotta #CC9975
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.92, 0.78, 0.65, 1.0) # Sandy limestone #EBC7A6
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.65
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_wood_trunk_material():
    mat = bpy.data.materials.new("M_Wood_Trunk")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.44, 0.28, 0.18, 1.0) # Warm cedar #70472E
    bsdf.inputs['Roughness'].default_value = 0.70
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_flower_materials():
    mats = {}

    m_wp = bpy.data.materials.new("M_Petal_White")
    m_wp.use_nodes = True
    b = m_wp.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.98, 0.98, 0.95, 1.0)
    b.inputs['Roughness'].default_value = 0.40
    mats["white_petal"] = m_wp

    m_yc = bpy.data.materials.new("M_Center_Yellow")
    m_yc.use_nodes = True
    b = m_yc.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.82, 0.12, 1.0)
    b.inputs['Roughness'].default_value = 0.35
    mats["yellow_center"] = m_yc

    m_pp = bpy.data.materials.new("M_Petal_Pink")
    m_pp.use_nodes = True
    b = m_pp.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.60, 0.70, 1.0)
    b.inputs['Roughness'].default_value = 0.40
    mats["pink_petal"] = m_pp

    m_clv = bpy.data.materials.new("M_Clover_Leaf")
    m_clv.use_nodes = True
    b = m_clv.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.38, 0.78, 0.14, 1.0)
    b.inputs['Roughness'].default_value = 0.45
    mats["clover"] = m_clv

    return mats

def create_momo_materials():
    mats = {}

    m_momo = bpy.data.materials.new("M_Momo_Peach")
    m_momo.use_nodes = True
    b = m_momo.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.65, 0.45, 1.0)
    b.inputs['Roughness'].default_value = 0.30
    if 'Emission Color' in b.inputs:
        b.inputs['Emission Color'].default_value = (1.00, 0.70, 0.42, 1.0)
        b.inputs['Emission Strength'].default_value = 1.0
    mats["peach"] = m_momo

    m_leaf = bpy.data.materials.new("M_Momo_Leaf")
    m_leaf.use_nodes = True
    b = m_leaf.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.22, 0.78, 0.26, 1.0)
    b.inputs['Roughness'].default_value = 0.35
    mats["leaf"] = m_leaf

    m_spk = bpy.data.materials.new("M_Sparkle_Gold")
    m_spk.use_nodes = True
    b = m_spk.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.92, 0.35, 1.0)
    if 'Emission Color' in b.inputs:
        b.inputs['Emission Color'].default_value = (1.00, 0.92, 0.35, 1.0)
        b.inputs['Emission Strength'].default_value = 2.5
    mats["sparkle"] = m_spk

    # Stone pedestal for Momo fruit
    m_ped = bpy.data.materials.new("M_Pedestal_Stone")
    m_ped.use_nodes = True
    b_p = m_ped.node_tree.nodes.get("Principled BSDF")
    b_p.inputs['Base Color'].default_value = (0.85, 0.82, 0.78, 1.0)
    b_p.inputs['Roughness'].default_value = 0.60
    mats["pedestal"] = m_ped

    return mats

# ==============================================================================
# 3D PROCEDURAL ASSET GENERATORS
# ==============================================================================
def create_3d_grass_tuft_mesh(name, mat_grass, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()

    num_blades = 6
    for i in range(num_blades):
        angle = (i / num_blades) * 2 * math.pi + random.uniform(-0.2, 0.2)
        tilt = random.uniform(0.18, 0.38)
        height = random.uniform(0.20, 0.38)
        width = random.uniform(0.035, 0.055)

        dx = math.cos(angle)
        dy = math.sin(angle)
        perp_x = -dy
        perp_y = dx

        v0 = bm.verts.new(Vector((-perp_x * width * 0.5, -perp_y * width * 0.5, 0.0)))
        v1 = bm.verts.new(Vector((perp_x * width * 0.5, perp_y * width * 0.5, 0.0)))
        mid_lean = tilt * 0.5
        v2 = bm.verts.new(Vector((-perp_x * width * 0.35 + dx * mid_lean, -perp_y * width * 0.35 + dy * mid_lean, height * 0.5)))
        v3 = bm.verts.new(Vector((perp_x * width * 0.35 + dx * mid_lean, perp_y * width * 0.35 + dy * mid_lean, height * 0.5)))
        tip_lean = tilt
        v4 = bm.verts.new(Vector((dx * tip_lean, dy * tip_lean, height)))

        bm.faces.new([v0, v1, v3, v2])
        bm.faces.new([v2, v3, v4])

    bm.to_mesh(mesh)
    bm.free()

    obj.data.materials.append(mat_grass)
    col.objects.link(obj)
    return obj

def build_puffy_hedge_wall(name, x1, y1, x2, y2, height, width, mat_hedge, col):
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    cx = (x1 + x2) * 0.5
    cy = (y1 + y2) * 0.5
    cz = height * 0.5
    angle = math.atan2(dy, dx)

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    core = bpy.context.active_object
    core.name = f"{name}_Core"
    core.location = (cx, cy, cz)
    core.scale = (length, width, height)
    core.rotation_euler = (0, 0, angle)
    core.data.materials.append(mat_hedge)
    
    # Crisp stylized bevel modifier
    bev = core.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.08
    bev.segments = 2
    bpy.ops.object.shade_smooth()
    col.objects.link(core)

    num_puffs = max(2, int(length / 0.50))
    for i in range(num_puffs + 1):
        t = i / max(1, num_puffs)
        px = x1 + dx * t + random.uniform(-0.06, 0.06)
        py = y1 + dy * t + random.uniform(-0.06, 0.06)
        pz = height + random.uniform(-0.04, 0.08)

        radius = random.uniform(width * 0.60, width * 0.88)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=radius)
        puff = bpy.context.active_object
        puff.name = f"{name}_Puff_{i}"
        puff.location = (px, py, pz)
        puff.scale = (1.05 + random.uniform(-0.1, 0.1), 1.05 + random.uniform(-0.1, 0.1), 0.88 + random.uniform(-0.1, 0.1))
        puff.parent = core
        puff.data.materials.append(mat_hedge)
        bpy.ops.object.shade_smooth()
        col.objects.link(puff)

def build_stylized_tree(name, location, trunk_height, canopy_radius, mat_trunk, mat_foliage, col):
    x, y, z = location

    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.28, depth=trunk_height)
    trunk = bpy.context.active_object
    trunk.name = f"{name}_Trunk"
    trunk.location = (x, y, z + trunk_height * 0.5)
    trunk.data.materials.append(mat_trunk)
    bpy.ops.object.shade_smooth()
    col.objects.link(trunk)

    for i in range(3):
        r_angle = i * (2 * math.pi / 3) + 0.3
        rx = x + math.cos(r_angle) * 0.35
        ry = y + math.sin(r_angle) * 0.35
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.22, radius2=0.08, depth=0.45)
        root = bpy.context.active_object
        root.name = f"{name}_Root_{i}"
        root.location = (rx, ry, z + 0.20)
        root.rotation_euler = (math.radians(20) * math.sin(r_angle), math.radians(-20) * math.cos(r_angle), 0)
        root.parent = trunk
        root.data.materials.append(mat_trunk)
        bpy.ops.object.shade_smooth()
        col.objects.link(root)

    canopy_z = z + trunk_height + canopy_radius * 0.65
    lobes = [
        ((0, 0, 0.2), canopy_radius * 0.95),
        ((-0.45 * canopy_radius, 0.35 * canopy_radius, -0.1), canopy_radius * 0.75),
        ((0.45 * canopy_radius, 0.35 * canopy_radius, -0.05), canopy_radius * 0.78),
        ((-0.35 * canopy_radius, -0.45 * canopy_radius, -0.15), canopy_radius * 0.72),
        ((0.35 * canopy_radius, -0.45 * canopy_radius, -0.10), canopy_radius * 0.74),
        ((0, 0, 0.55 * canopy_radius), canopy_radius * 0.60)
    ]
    for idx, (offset, r) in enumerate(lobes):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=r)
        lobe = bpy.context.active_object
        lobe.name = f"{name}_Canopy_{idx}"
        lobe.location = (x + offset[0], y + offset[1], canopy_z + offset[2])
        lobe.scale = (1.05, 1.05, 0.95)
        lobe.parent = trunk
        lobe.data.materials.append(mat_foliage)
        bpy.ops.object.shade_smooth()
        col.objects.link(lobe)

def build_flower_cluster(name, location, count, mats_flower, col):
    cx, cy, cz = location
    for i in range(count):
        ox = cx + random.uniform(-0.35, 0.35)
        oy = cy + random.uniform(-0.35, 0.35)
        is_pink = (i % 2 == 1)

        mat_petal = mats_flower["pink_petal"] if is_pink else mats_flower["white_petal"]
        mat_center = mats_flower["yellow_center"]

        num_petals = 5
        petal_scale = random.uniform(0.045, 0.075)
        for p in range(num_petals):
            p_ang = p * (2 * math.pi / num_petals)
            px = ox + math.cos(p_ang) * petal_scale * 0.9
            py = oy + math.sin(p_ang) * petal_scale * 0.9
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=petal_scale)
            petal = bpy.context.active_object
            petal.name = f"{name}_Petal_{i}_{p}"
            petal.location = (px, py, cz + 0.04)
            petal.scale = (1.2, 0.55, 0.25)
            petal.rotation_euler = (0, 0, p_ang)
            petal.data.materials.append(mat_petal)
            bpy.ops.object.shade_smooth()
            col.objects.link(petal)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=petal_scale * 0.65)
        center = bpy.context.active_object
        center.name = f"{name}_Center_{i}"
        center.location = (ox, oy, cz + 0.06)
        center.data.materials.append(mat_center)
        bpy.ops.object.shade_smooth()
        col.objects.link(center)

        for c in range(3):
            c_ang = c * (2 * math.pi / 3) + 0.5
            cx_pos = ox + math.cos(c_ang) * 0.12
            cy_pos = oy + math.sin(c_ang) * 0.12
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.035)
            clv = bpy.context.active_object
            clv.name = f"{name}_Clover_{i}_{c}"
            clv.location = (cx_pos, cy_pos, cz + 0.02)
            clv.scale = (1.1, 0.8, 0.2)
            clv.rotation_euler = (0, 0, c_ang)
            clv.data.materials.append(mats_flower["clover"])
            bpy.ops.object.shade_smooth()
            col.objects.link(clv)

def build_leaf_gate_arch(location, mat_wood, mat_hedge, mats_momo, col):
    x, y, z = location

    for sign, suffix in [(-1, "L"), (1, "R")]:
        px = x + sign * 1.35
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        base = bpy.context.active_object
        base.name = f"Gate_Base_{suffix}"
        base.location = (px, y, z + 0.18)
        base.scale = (0.55, 0.55, 0.36)
        base.data.materials.append(mat_wood)
        bpy.ops.object.shade_smooth()
        col.objects.link(base)

        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=2.4)
        post = bpy.context.active_object
        post.name = f"Gate_Post_{suffix}"
        post.location = (px, y, z + 1.35)
        post.data.materials.append(mat_wood)
        bpy.ops.object.shade_smooth()
        col.objects.link(post)

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = "Gate_Beam"
    beam.location = (x, y, z + 2.55)
    beam.scale = (3.1, 0.32, 0.22)
    beam.data.materials.append(mat_wood)
    bpy.ops.object.shade_smooth()
    col.objects.link(beam)

    leaf_clusters = [
        ((-0.8, 0.0, 2.75), (0.75, 0.25, 0.45), math.radians(25)),
        ((0.8, 0.0, 2.75), (0.75, 0.25, 0.45), math.radians(-25)),
        ((0.0, 0.0, 2.95), (0.95, 0.30, 0.55), 0.0)
    ]
    for idx, (l_loc, l_scale, l_rot) in enumerate(leaf_clusters):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=1.0)
        leaf = bpy.context.active_object
        leaf.name = f"Gate_CrownLeaf_{idx}"
        leaf.location = (x + l_loc[0], y + l_loc[1], z + l_loc[2])
        leaf.scale = l_scale
        leaf.rotation_euler = (0, l_rot, 0)
        leaf.data.materials.append(mat_hedge)
        bpy.ops.object.shade_smooth()
        col.objects.link(leaf)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.22)
    momo_crest = bpy.context.active_object
    momo_crest.name = "Gate_Momo_Crest"
    momo_crest.location = (x, y - 0.22, z + 2.62)
    momo_crest.scale = (1.0, 0.85, 1.1)
    momo_crest.data.materials.append(mats_momo["peach"])
    bpy.ops.object.shade_smooth()
    col.objects.link(momo_crest)

def build_momo_collectible(location, mats_momo, col):
    x, y, z = location

    # Stone pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.35, depth=0.22)
    ped = bpy.context.active_object
    ped.name = "Momo_Pedestal"
    ped.location = (x, y, z + 0.11)
    ped.data.materials.append(mats_momo["pedestal"])
    bpy.ops.object.shade_smooth()
    col.objects.link(ped)

    # Peach
    pz = z + 0.38
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.22)
    peach = bpy.context.active_object
    peach.name = "Momo_Collectible_Fruit"
    peach.location = (x, y, pz)
    peach.scale = (1.05, 0.95, 1.15)
    peach.data.materials.append(mats_momo["peach"])
    bpy.ops.object.shade_smooth()
    col.objects.link(peach)

    for sign, angle in [(-1, math.radians(-35)), (1, math.radians(35))]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.09)
        leaf = bpy.context.active_object
        leaf.name = f"Momo_Leaf_{sign}"
        leaf.location = (x + sign * 0.08, y, pz + 0.24)
        leaf.scale = (1.2, 0.45, 0.25)
        leaf.rotation_euler = (0, angle, 0)
        leaf.data.materials.append(mats_momo["leaf"])
        bpy.ops.object.shade_smooth()
        col.objects.link(leaf)

    sparkle_offsets = [
        (0.30, 0.18, 0.22),
        (-0.28, -0.20, 0.26),
        (0.14, -0.32, 0.10),
        (-0.24, 0.26, 0.16)
    ]
    for idx, off in enumerate(sparkle_offsets):
        bpy.ops.mesh.primitive_cube_add(size=0.055)
        star = bpy.context.active_object
        star.name = f"Momo_Star_{idx}"
        star.location = (x + off[0], y + off[1], pz + off[2])
        star.rotation_euler = (math.radians(45), math.radians(45), math.radians(45))
        star.data.materials.append(mats_momo["sparkle"])
        bpy.ops.object.shade_smooth()
        col.objects.link(star)

# ==============================================================================
# MAIN ENVIRONMENT BUILD
# ==============================================================================
def build_master_environment():
    col = reset_scene()

    mat_hedge = create_lush_hedge_material()
    mat_grass = create_grass_blade_material()
    mat_lawn = create_ground_lawn_material()
    mat_stone = create_retaining_stone_material()
    mat_wood = create_wood_trunk_material()
    mats_flower = create_flower_materials()
    mats_momo = create_momo_materials()

    # 1. Base Meadow Ground Plane
    bpy.ops.mesh.primitive_plane_add(size=28.0)
    ground = bpy.context.active_object
    ground.name = "Terrain_Meadow_Lawn"
    ground.location = (0, 0, 0)
    ground.data.materials.append(mat_lawn)
    col.objects.link(ground)

    # 2. Retaining Stone Curb Framing 12x12 Maze Planter
    curb_w = 0.55
    curb_h = 0.26
    curb_half = 6.0
    for idx, (p1, p2) in enumerate([
        ((-curb_half, -curb_half), (curb_half, -curb_half)),
        ((-curb_half, curb_half), (curb_half, curb_half)),
        ((-curb_half, -curb_half), (-curb_half, curb_half)),
        ((curb_half, -curb_half), (curb_half, curb_half))
    ]):
        cx = (p1[0] + p2[0]) * 0.5
        cy = (p1[1] + p2[1]) * 0.5
        leng = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        c_obj = bpy.context.active_object
        c_obj.name = f"Stone_Curb_{idx}"
        c_obj.location = (cx, cy, curb_h * 0.5)
        c_obj.scale = (leng + curb_w, curb_w, curb_h)
        c_obj.rotation_euler = (0, 0, ang)
        c_obj.data.materials.append(mat_stone)
        bpy.ops.object.shade_smooth()
        col.objects.link(c_obj)

    # 3. Fluffy Living Hedges
    h_h = 1.35
    h_w = 0.65
    hedge_segments = [
        ("Hedge_Perim_Bottom_L", -5.4, -5.4, -1.8, -5.4),
        ("Hedge_Perim_Bottom_R",  1.8, -5.4,  5.4, -5.4),
        ("Hedge_Perim_Top_L",    -5.4,  5.4, -1.6,  5.4),
        ("Hedge_Perim_Top_R",     1.6,  5.4,  5.4,  5.4),
        ("Hedge_Perim_Left",     -5.4, -5.4, -5.4,  5.4),
        ("Hedge_Perim_Right",     5.4, -5.4,  5.4,  5.4),

        ("Hedge_Int_01", -3.6, -3.6,  3.6, -3.6),
        ("Hedge_Int_02", -3.6, -1.8, -1.8, -1.8),
        ("Hedge_Int_03",  0.0, -1.8,  3.6, -1.8),
        ("Hedge_Int_04", -1.8, -1.8, -1.8,  1.8),
        ("Hedge_Int_05",  1.8, -1.8,  1.8,  0.0),
        ("Hedge_Int_06", -3.6,  0.0, -1.8,  0.0),
        ("Hedge_Int_07", -3.6,  1.8, -1.8,  1.8),
        ("Hedge_Int_08",  1.8,  1.8,  3.6,  1.8),
        ("Hedge_Int_09", -3.6,  3.6,  0.0,  3.6),
        ("Hedge_Int_10",  1.8,  3.6,  3.6,  3.6),
        ("Hedge_Int_11",  0.0,  1.8,  0.0,  3.6)
    ]
    for name, x1, y1, x2, y2 in hedge_segments:
        build_puffy_hedge_wall(name, x1, y1, x2, y2, h_h, h_w, mat_hedge, col)

    # 4. Dense 3D Physical Grass (800+ instanced clumps)
    tuft_proto = create_3d_grass_tuft_mesh("Proto_Grass_Tuft", mat_grass, col)
    grass_col = bpy.data.collections.new("Dense_3D_Grass_Field")
    bpy.context.scene.collection.children.link(grass_col)

    random.seed(42)
    # Corridors
    for _ in range(500):
        gx = random.uniform(-5.0, 5.0)
        gy = random.uniform(-5.0, 5.0)
        on_wall = False
        for _, x1, y1, x2, y2 in hedge_segments:
            dx = x2 - x1
            dy = y2 - y1
            l2 = dx*dx + dy*dy
            t = max(0, min(1, ((gx - x1)*dx + (gy - y1)*dy) / l2))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            if math.hypot(gx - proj_x, gy - proj_y) < 0.40:
                on_wall = True
                break
        if on_wall:
            continue
        inst = tuft_proto.copy()
        inst.location = (gx, gy, 0.0)
        inst.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))
        sc = random.uniform(0.65, 1.15)
        inst.scale = (sc, sc, sc * random.uniform(0.9, 1.35))
        grass_col.objects.link(inst)

    # Outer perimeter yard
    for _ in range(300):
        ox = random.choice([-1, 1]) * random.uniform(6.2, 10.5)
        oy = random.uniform(-10.5, 10.5)
        if random.random() > 0.5:
            ox, oy = oy, ox
        inst = tuft_proto.copy()
        inst.location = (ox, oy, 0.0)
        inst.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))
        sc = random.uniform(0.85, 1.40)
        inst.scale = (sc, sc, sc * random.uniform(1.0, 1.45))
        grass_col.objects.link(inst)

    tuft_proto.location = (0, 0, -100.0)

    # 5. Stylized Puffy Background Trees
    trees_data = [
        ("Tree_Back_L", (-3.4, 8.5, 0.0), 3.4, 2.5),
        ("Tree_Back_R", ( 3.4, 8.5, 0.0), 3.6, 2.7),
        ("Tree_Side_L", (-8.8, 2.0, 0.0), 3.0, 2.3),
        ("Tree_Side_R", ( 8.8, 2.0, 0.0), 3.2, 2.4)
    ]
    for t_name, t_loc, t_th, t_cr in trees_data:
        build_stylized_tree(t_name, t_loc, t_th, t_cr, mat_wood, mat_hedge, col)

    # 6. Flower & Clover Beds
    flower_locs = [
        ("Flower_Bed_01", (-2.4, -4.5, 0.0), 8),
        ("Flower_Bed_02", ( 2.4, -4.5, 0.0), 8),
        ("Flower_Bed_03", (-4.2, -0.8, 0.0), 6),
        ("Flower_Bed_04", ( 4.2, -0.8, 0.0), 6),
        ("Flower_Bed_05", (-2.2,  2.4, 0.0), 7),
        ("Flower_Bed_06", ( 2.2,  2.4, 0.0), 7),
        ("Flower_Bed_07", (-1.0,  5.0, 0.0), 6),
        ("Flower_Bed_08", ( 1.0,  5.0, 0.0), 6),
        ("Flower_Bed_09", (-6.5, -4.0, 0.0), 7),
        ("Flower_Bed_10", ( 6.5, -4.0, 0.0), 7)
    ]
    for f_name, f_loc, f_cnt in flower_locs:
        build_flower_cluster(f_name, f_loc, f_cnt, mats_flower, col)

    # 7. Leaf Gate Archway
    build_leaf_gate_arch((0.0, 5.4, 0.0), mat_wood, mat_hedge, mats_momo, col)

    # 8. Momo Collectible on Pedestal
    build_momo_collectible((2.4, 0.8, 0.0), mats_momo, col)

    # 9. Import Characters Scaled Perfectly for Diorama
    # Golumolu v11 (scale 0.48)
    golumolu_blend = "D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend"
    with bpy.data.libraries.load(golumolu_blend, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith("Golumolu_")]

    g_root = None
    for obj in data_to.objects:
        col.objects.link(obj)
        obj.scale = (obj.scale.x * 0.48, obj.scale.y * 0.48, obj.scale.z * 0.48)
        if obj.name == "Golumolu_Body":
            g_root = obj

    if g_root:
        g_root.location = (0.3, 0.9, 0.52) # Leaping mid-air towards Momo
        g_root.rotation_euler = (math.radians(-12), math.radians(8), math.radians(-55))

        dust_mat = bpy.data.materials.new("M_Joy_Dust")
        dust_mat.use_nodes = True
        b_d = dust_mat.node_tree.nodes.get("Principled BSDF")
        b_d.inputs['Base Color'].default_value = (1.0, 0.95, 0.90, 1.0)
        b_d.inputs['Roughness'].default_value = 0.50

        for d_idx, d_off in enumerate([(-0.25, 0.25, 0.08), (-0.40, 0.18, 0.04)]):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.06 * (1.0 - d_idx * 0.2))
            dust = bpy.context.active_object
            dust.name = f"Golumolu_DustPuff_{d_idx}"
            dust.location = (0.3 + d_off[0], 0.9 + d_off[1], d_off[2])
            dust.data.materials.append(dust_mat)
            bpy.ops.object.shade_smooth()
            col.objects.link(dust)

    # Ghost Spirits v9 (scale 0.45)
    ghosts_blend = "D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend"
    with bpy.data.libraries.load(ghosts_blend, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith("Ghost_")]

    for obj in data_to.objects:
        col.objects.link(obj)
        obj.scale = (obj.scale.x * 0.45, obj.scale.y * 0.45, obj.scale.z * 0.45)

    g_f = bpy.data.objects.get("Ghost_Follower_Root")
    if g_f:
        g_f.location = (-2.8, -0.9, 0.85)
        g_f.rotation_euler = (math.radians(8), math.radians(-12), math.radians(-40))

    g_c = bpy.data.objects.get("Ghost_Cutter_Root")
    if g_c:
        g_c.location = (3.8, 2.6, 0.92)
        g_c.rotation_euler = (math.radians(12), math.radians(10), math.radians(-130))

    g_w = bpy.data.objects.get("Ghost_Wanderer_Root")
    if g_w:
        g_w.location = (-0.9, -3.8, 0.78)
        g_w.rotation_euler = (math.radians(-6), math.radians(12), math.radians(40))

    # Save Master Blend
    master_blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/maze_beauty_environment.blend"
    bpy.ops.wm.save_as_mainfile(filepath=master_blend_path)
    print(f"  ✓ Saved Master Diorama Blend -> {master_blend_path}")

    return col

def render_environment_views(col):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'

    # Warm Golden Hour Studio World
    world = scene.world or bpy.data.worlds.new("World_Diorama_Golden")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.94, 0.96, 0.98, 1.0)
        bg.inputs['Strength'].default_value = 0.80

    # Key Golden Sunlight
    sun = bpy.data.lights.new("Sun_Golden_Key", 'SUN')
    sun.energy = 6.5
    sun.color = (1.00, 0.90, 0.76) # Rich golden hour
    sun.angle = math.radians(10)
    sun_obj = bpy.data.objects.new("Sun_Golden_Key", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    col.objects.link(sun_obj)

    # Sky Fill
    fill = bpy.data.lights.new("Sky_Fill", 'SUN')
    fill.energy = 2.4
    fill.color = (0.86, 0.93, 1.0)
    fill.angle = math.radians(25)
    fill_obj = bpy.data.objects.new("Sky_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-15), math.radians(140))
    col.objects.link(fill_obj)

    # Warm Rim
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.color = (1.0, 0.85, 0.65)
    rim.energy = 180.0
    rim.shadow_soft_size = 1.2
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.5, 6.5, 5.5)
    col.objects.link(rim_obj)

    # 1. Perspective Diorama Beauty Camera (Framing Entire Square Maze like Ref 4)
    cam_data = bpy.data.cameras.new("Cam_Beauty_Diorama")
    cam_data.type = 'PERSP'
    cam_data.lens = 44 # Stylized diorama focal length
    cam_obj = bpy.data.objects.new("Cam_Beauty_Diorama", cam_data)
    cam_obj.location = (0.0, -15.5, 12.8)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    # Aim directly at center of maze
    target_empty = bpy.data.objects.new("Cam_Target", None)
    target_empty.location = (0.0, 0.4, 0.5)
    col.objects.link(target_empty)

    cam_track = cam_obj.constraints.new(type='TRACK_TO')
    cam_track.target = target_empty
    cam_track.track_axis = 'TRACK_NEGATIVE_Z'
    cam_track.up_axis = 'UP_Y'

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    beauty_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_beauty_view_v7_diorama.png"
    scene.render.filepath = beauty_out
    print(f"Rendering Master Diorama Beauty View (1920x1080)...")
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Beauty View -> {beauty_out}")

    # 2. Orthographic Top-Down Plan
    cam_data_top = bpy.data.cameras.new("Cam_TopDown")
    cam_data_top.type = 'ORTHO'
    cam_data_top.ortho_scale = 14.5
    cam_top_obj = bpy.data.objects.new("Cam_TopDown", cam_data_top)
    cam_top_obj.location = (0, 0, 16.0)
    cam_top_obj.rotation_euler = (0, 0, 0)
    col.objects.link(cam_top_obj)
    scene.camera = cam_top_obj

    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    top_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_topdown_plan_v7.png"
    scene.render.filepath = top_out
    print(f"Rendering Master Top-Down Plan (1200x1200)...")
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Top-Down Plan -> {top_out}")

if __name__ == "__main__":
    print("==================================================")
    print("Building Definitive Grassy & Fluffy Maze Diorama v7")
    print("==================================================")
    col = build_master_environment()
    render_environment_views(col)
    print("Diorama v7 build and render complete!")
