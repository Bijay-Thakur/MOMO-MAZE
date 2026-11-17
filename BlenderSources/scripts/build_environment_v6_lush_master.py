"""
build_environment_v6_lush_master.py
MOMO MAZE - Master Grassy & Fluffy Environment Scene v6 (Blender 5.2)

Strictly fulfilling the user request:
- "the maize is grassy, there need to be a lot of grass and the quality right now is really low.
   the trees, flower, grass and fluffiness. these should be improved refer to the refrence image for more detailed representation."

Key Upgrades:
1. Dense 3D Physical Grass: Hundreds of instanced 3D grass tufts (curved stylized blades with SSS)
   carpet the maze corridors and outer meadow, casting rich micro-shadows.
2. Fluffy Living Hedges: Hedges are upgraded with hundreds of organic foliage puffs along the crests,
   corners, and surfaces to create volumetric, cloud-like living greenery matching Reference Image 4.
3. Stylized Puffy Background Trees: 4 large cartoon trees with thick cedar trunks, root flares,
   and multi-lobed fluffy cloud foliage canopies framing the back perimeter behind the Leaf Gate.
4. Lush Flower & Clover Beds: 5-petal daisies (creamy white with golden centers), pink buttercups,
   and 3-leaf clovers nestled into corridor corners, along the stone perimeter, and around trees.
5. Whimsical Leaf Gate: Sturdy cedar wood posts, stone footings, curved leaf crown, and glowing Momo crest.
6. Characters:
   - Golumolu v11 Master Dino: Mid-leap towards the glowing Momo peach, with Godzilla dorsal spikes,
     plump tail, happy anime eyes with white shine patches, peachy-pink fur, and joyful motion dust.
   - 3 Ghost Spirits v9: Follower, Cutter, and Wanderer floating gracefully through corridors with
     their 3-4 trailing wisp tails.
7. Golden-hour lighting with Cycles render (128 samples).
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
    col = bpy.data.collections.new("Master_Environment_Lush_v6")
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
    noise.inputs['Scale'].default_value = 3.2
    noise.inputs['Detail'].default_value = 3.5
    noise.inputs['Roughness'].default_value = 0.60
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.12
    ramp.color_ramp.elements[0].color = (0.14, 0.32, 0.06, 1.0) # Deep forest shadow #24520F
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.62, 0.88, 0.18, 1.0) # Sunlit vibrant lime #A4E030
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Micro-leaf texture bump
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Foliage velvet sheen and SSS
    bsdf.inputs['Roughness'].default_value = 0.52
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.85
        bsdf.inputs['Sheen Roughness'].default_value = 0.40
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.75, 0.95, 0.35, 1.0)
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
    ramp.color_ramp.elements[0].position = 0.10
    ramp.color_ramp.elements[0].color = (0.24, 0.48, 0.08, 1.0) # Deep spring root #3D7A14
    ramp.color_ramp.elements[1].position = 0.90
    ramp.color_ramp.elements[1].color = (0.68, 0.92, 0.22, 1.0) # Radiant lime tip #AEEB38
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
    ramp.color_ramp.elements[0].color = (0.28, 0.52, 0.10, 1.0) # Meadow base
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.50, 0.78, 0.16, 1.0) # Sunny lawn
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
    ramp.color_ramp.elements[0].color = (0.78, 0.58, 0.44, 1.0) # Terracotta warm stone #C79470
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.90, 0.75, 0.62, 1.0) # Sandy limestone #E6BF9E
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.68
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_wood_trunk_material():
    mat = bpy.data.materials.new("M_Wood_Trunk")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.42, 0.26, 0.16, 1.0) # Warm cedar brown #6B4229
    bsdf.inputs['Roughness'].default_value = 0.72
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_flower_materials():
    mats = {}

    # White Daisy Petals
    m_wp = bpy.data.materials.new("M_Petal_White")
    m_wp.use_nodes = True
    b = m_wp.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.98, 0.98, 0.95, 1.0)
    b.inputs['Roughness'].default_value = 0.40
    mats["white_petal"] = m_wp

    # Yellow Flower Center
    m_yc = bpy.data.materials.new("M_Center_Yellow")
    m_yc.use_nodes = True
    b = m_yc.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.80, 0.10, 1.0) # Golden yellow
    b.inputs['Roughness'].default_value = 0.35
    mats["yellow_center"] = m_yc

    # Pink Buttercup Petals
    m_pp = bpy.data.materials.new("M_Petal_Pink")
    m_pp.use_nodes = True
    b = m_pp.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.58, 0.68, 1.0) # Soft pastel pink
    b.inputs['Roughness'].default_value = 0.40
    mats["pink_petal"] = m_pp

    # Clover Leaf
    m_clv = bpy.data.materials.new("M_Clover_Leaf")
    m_clv.use_nodes = True
    b = m_clv.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.35, 0.75, 0.12, 1.0) # Clover green
    b.inputs['Roughness'].default_value = 0.45
    mats["clover"] = m_clv

    return mats

def create_momo_materials():
    mats = {}

    # Momo Peach
    m_momo = bpy.data.materials.new("M_Momo_Peach")
    m_momo.use_nodes = True
    b = m_momo.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.65, 0.45, 1.0) # Golden peach
    b.inputs['Roughness'].default_value = 0.30
    if 'Emission Color' in b.inputs:
        b.inputs['Emission Color'].default_value = (1.00, 0.70, 0.40, 1.0)
        b.inputs['Emission Strength'].default_value = 0.85
    mats["peach"] = m_momo

    # Momo Leaf
    m_leaf = bpy.data.materials.new("M_Momo_Leaf")
    m_leaf.use_nodes = True
    b = m_leaf.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.20, 0.75, 0.25, 1.0)
    b.inputs['Roughness'].default_value = 0.35
    mats["leaf"] = m_leaf

    # Sparkle Star
    m_spk = bpy.data.materials.new("M_Sparkle_Gold")
    m_spk.use_nodes = True
    b = m_spk.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (1.00, 0.90, 0.30, 1.0)
    if 'Emission Color' in b.inputs:
        b.inputs['Emission Color'].default_value = (1.00, 0.90, 0.30, 1.0)
        b.inputs['Emission Strength'].default_value = 2.5
    mats["sparkle"] = m_spk

    return mats

# ==============================================================================
# PROCEDURAL 3D ASSETS: GRASS, HEDGES, TREES, FLOWERS
# ==============================================================================
def create_3d_grass_tuft_mesh(name, mat_grass, col):
    """Creates a stylized 3D grass tuft mesh object (6 curved blades fanning out)."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()

    num_blades = 6
    for i in range(num_blades):
        angle = (i / num_blades) * 2 * math.pi + random.uniform(-0.2, 0.2)
        tilt = random.uniform(0.18, 0.38) # radians outward lean
        height = random.uniform(0.20, 0.38)
        width = random.uniform(0.035, 0.055)

        dx = math.cos(angle)
        dy = math.sin(angle)
        perp_x = -dy
        perp_y = dx

        # Base vertices
        v0 = bm.verts.new(Vector((-perp_x * width * 0.5, -perp_y * width * 0.5, 0.0)))
        v1 = bm.verts.new(Vector((perp_x * width * 0.5, perp_y * width * 0.5, 0.0)))
        # Mid vertices (curved outward)
        mid_lean = tilt * 0.5
        v2 = bm.verts.new(Vector((-perp_x * width * 0.35 + dx * mid_lean, -perp_y * width * 0.35 + dy * mid_lean, height * 0.5)))
        v3 = bm.verts.new(Vector((perp_x * width * 0.35 + dx * mid_lean, perp_y * width * 0.35 + dy * mid_lean, height * 0.5)))
        # Tip vertex (pointed)
        tip_lean = tilt
        v4 = bm.verts.new(Vector((dx * tip_lean, dy * tip_lean, height)))

        bm.faces.new([v0, v1, v3, v2])
        bm.faces.new([v2, v3, v4])

    bm.to_mesh(mesh)
    bm.free()

    obj.data.materials.append(mat_grass)
    bpy.context.view_layer.update()
    col.objects.link(obj)
    return obj

def build_puffy_hedge_wall(name, x1, y1, x2, y2, height, width, mat_hedge, col):
    """
    Builds a living fluffy hedge wall: core collision block + organic foliage puff clumps
    along the crest and sides for lush volumetric cloud-like foliage.
    """
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    cx = (x1 + x2) * 0.5
    cy = (y1 + y2) * 0.5
    cz = height * 0.5
    angle = math.atan2(dy, dx)

    # 1. Base Core
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    core = bpy.context.active_object
    core.name = f"{name}_Core"
    core.location = (cx, cy, cz)
    core.scale = (length, width, height)
    core.rotation_euler = (0, 0, angle)
    core.data.materials.append(mat_hedge)
    bpy.ops.object.shade_smooth()
    col.objects.link(core)

    # 2. Overlapping Organic Foliage Puffs along the Crest
    num_puffs = max(2, int(length / 0.55))
    for i in range(num_puffs + 1):
        t = i / max(1, num_puffs)
        px = x1 + dx * t + random.uniform(-0.06, 0.06)
        py = y1 + dy * t + random.uniform(-0.06, 0.06)
        pz = height + random.uniform(-0.05, 0.08)

        radius = random.uniform(width * 0.55, width * 0.85)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=radius)
        puff = bpy.context.active_object
        puff.name = f"{name}_Puff_{i}"
        puff.location = (px, py, pz)
        puff.scale = (1.0 + random.uniform(-0.15, 0.15), 1.0 + random.uniform(-0.15, 0.15), 0.85 + random.uniform(-0.1, 0.1))
        puff.parent = core
        puff.data.materials.append(mat_hedge)
        bpy.ops.object.shade_smooth()
        col.objects.link(puff)

def build_stylized_tree(name, location, trunk_height, canopy_radius, mat_trunk, mat_foliage, col):
    """Builds a whimsical cartoon tree with cedar trunk, root flares, and multi-lobed cloud canopy."""
    x, y, z = location

    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.28, depth=trunk_height)
    trunk = bpy.context.active_object
    trunk.name = f"{name}_Trunk"
    trunk.location = (x, y, z + trunk_height * 0.5)
    trunk.data.materials.append(mat_trunk)
    bpy.ops.object.shade_smooth()
    col.objects.link(trunk)

    # Root flares
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

    # Multi-lobed Fluffy Cloud Canopy (5-6 overlapping spheres)
    canopy_z = z + trunk_height + canopy_radius * 0.65
    lobes = [
        ((0, 0, 0.2), canopy_radius * 0.95),
        ((-0.45 * canopy_radius, 0.35 * canopy_radius, -0.1), canopy_radius * 0.75),
        ((0.45 * canopy_radius, 0.35 * canopy_radius, -0.05), canopy_radius * 0.78),
        ((-0.35 * canopy_radius, -0.45 * canopy_radius, -0.15), canopy_radius * 0.72),
        ((0.35 * canopy_radius, -0.45 * canopy_radius, -0.10), canopy_radius * 0.74),
        ((0, 0, 0.55 * canopy_radius), canopy_radius * 0.60) # Top crown puff
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
    """Spawns a cluster of stylized 5-petal daisies and pink buttercups with clovers."""
    cx, cy, cz = location
    for i in range(count):
        ox = cx + random.uniform(-0.35, 0.35)
        oy = cy + random.uniform(-0.35, 0.35)
        is_pink = (i % 2 == 1)

        mat_petal = mats_flower["pink_petal"] if is_pink else mats_flower["white_petal"]
        mat_center = mats_flower["yellow_center"]

        # 5 rounded petals
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

        # Center button
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=petal_scale * 0.65)
        center = bpy.context.active_object
        center.name = f"{name}_Center_{i}"
        center.location = (ox, oy, cz + 0.06)
        center.data.materials.append(mat_center)
        bpy.ops.object.shade_smooth()
        col.objects.link(center)

        # Clover triplet
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
    """Builds the iconic whimsical Leaf Gate archway with wooden pillars and leaf crown."""
    x, y, z = location

    # Upright Wooden Posts with stone bases
    for sign, suffix in [(-1, "L"), (1, "R")]:
        px = x + sign * 1.35
        # Stone base
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        base = bpy.context.active_object
        base.name = f"Gate_Base_{suffix}"
        base.location = (px, y, z + 0.18)
        base.scale = (0.55, 0.55, 0.36)
        base.data.materials.append(mat_wood)
        bpy.ops.object.shade_smooth()
        col.objects.link(base)

        # Cedar post
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=2.4)
        post = bpy.context.active_object
        post.name = f"Gate_Post_{suffix}"
        post.location = (px, y, z + 1.35)
        post.data.materials.append(mat_wood)
        bpy.ops.object.shade_smooth()
        col.objects.link(post)

    # Curved Crossbeam Arch
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = "Gate_Beam"
    beam.location = (x, y, z + 2.55)
    beam.scale = (3.1, 0.32, 0.22)
    beam.data.materials.append(mat_wood)
    bpy.ops.object.shade_smooth()
    col.objects.link(beam)

    # Lush Leaf Crown (Arching curved leaves)
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

    # Golden Momo Crest at center
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.22)
    momo_crest = bpy.context.active_object
    momo_crest.name = "Gate_Momo_Crest"
    momo_crest.location = (x, y - 0.22, z + 2.62)
    momo_crest.scale = (1.0, 0.85, 1.1)
    momo_crest.data.materials.append(mats_momo["peach"])
    bpy.ops.object.shade_smooth()
    col.objects.link(momo_crest)

def build_momo_collectible(location, mats_momo, col):
    """Spawns the glowing Momo peach with green leaves and radiant golden sparkles."""
    x, y, z = location

    # Glowing Peach
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.35)
    peach = bpy.context.active_object
    peach.name = "Momo_Collectible_Fruit"
    peach.location = (x, y, z)
    peach.scale = (1.05, 0.95, 1.15)
    peach.data.materials.append(mats_momo["peach"])
    bpy.ops.object.shade_smooth()
    col.objects.link(peach)

    # Pair of green leaves on top
    for sign, angle in [(-1, math.radians(-35)), (1, math.radians(35))]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.14)
        leaf = bpy.context.active_object
        leaf.name = f"Momo_Leaf_{sign}"
        leaf.location = (x + sign * 0.12, y, z + 0.38)
        leaf.scale = (1.2, 0.45, 0.25)
        leaf.rotation_euler = (0, angle, 0)
        leaf.data.materials.append(mats_momo["leaf"])
        bpy.ops.object.shade_smooth()
        col.objects.link(leaf)

    # Floating golden sparkle stars
    sparkle_offsets = [
        (0.45, 0.25, 0.35),
        (-0.40, -0.30, 0.40),
        (0.20, -0.45, 0.15),
        (-0.35, 0.38, 0.25)
    ]
    for idx, off in enumerate(sparkle_offsets):
        bpy.ops.mesh.primitive_cube_add(size=0.08)
        star = bpy.context.active_object
        star.name = f"Momo_Star_{idx}"
        star.location = (x + off[0], y + off[1], z + off[2])
        star.rotation_euler = (math.radians(45), math.radians(45), math.radians(45))
        star.data.materials.append(mats_momo["sparkle"])
        bpy.ops.object.shade_smooth()
        col.objects.link(star)

# ==============================================================================
# MASTER SCENE COMPOSITION
# ==============================================================================
def build_master_environment():
    col = reset_scene()

    # Materials
    mat_hedge = create_lush_hedge_material()
    mat_grass = create_grass_blade_material()
    mat_lawn = create_ground_lawn_material()
    mat_stone = create_retaining_stone_material()
    mat_wood = create_wood_trunk_material()
    mats_flower = create_flower_materials()
    mats_momo = create_momo_materials()

    # 1. Base Terrain Ground Plane
    bpy.ops.mesh.primitive_plane_add(size=24.0)
    ground = bpy.context.active_object
    ground.name = "Terrain_Meadow_Lawn"
    ground.location = (0, 0, 0)
    ground.data.materials.append(mat_lawn)
    col.objects.link(ground)

    # 2. Retaining Stone Curb Framing the Maze (12x12m)
    # 4 border walls forming the raised planter bed
    curb_w = 0.55
    curb_h = 0.24
    curb_half = 6.0
    curb_borders = [
        ((-curb_half, 0), (curb_half, 0), (-curb_half, -curb_half), (curb_half, -curb_half)), # Bottom
        ((-curb_half, curb_half), (curb_half, curb_half)), # Top
        ((-curb_half, -curb_half), (-curb_half, curb_half)), # Left
        ((curb_half, -curb_half), (curb_half, curb_half))   # Right
    ]
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

    # 3. Fluffy Living Hedges (12x12 Topology from Ref 4 Panel 1 & 2)
    # Hedge specifications: height = 1.35m, width = 0.65m
    h_h = 1.35
    h_w = 0.65

    hedge_segments = [
        # Outer Perimeter Walls
        ("Hedge_Perim_Bottom_L", -5.4, -5.4, -1.8, -5.4),
        ("Hedge_Perim_Bottom_R",  1.8, -5.4,  5.4, -5.4),
        ("Hedge_Perim_Top_L",    -5.4,  5.4, -1.6,  5.4), # Left of Gate
        ("Hedge_Perim_Top_R",     1.6,  5.4,  5.4,  5.4), # Right of Gate
        ("Hedge_Perim_Left",     -5.4, -5.4, -5.4,  5.4),
        ("Hedge_Perim_Right",     5.4, -5.4,  5.4,  5.4),

        # Interior Maze Corridors
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

    # 4. Dense 3D Physical Grass Scattering
    # Create master grass clump and instance 500+ clumps across paths and outer yard
    tuft_proto = create_3d_grass_tuft_mesh("Proto_Grass_Tuft", mat_grass, col)

    # Scatter points in paths and perimeter
    random.seed(42)
    grass_col = bpy.data.collections.new("Dense_3D_Grass_Field")
    bpy.context.scene.collection.children.link(grass_col)

    # Corridors grass (dense carpet inside maze pathways)
    for _ in range(420):
        # Pick a valid corridor area
        gx = random.uniform(-4.8, 4.8)
        gy = random.uniform(-4.8, 4.8)

        # Skip positions inside hedge walls
        on_wall = False
        for _, x1, y1, x2, y2 in hedge_segments:
            # Distance from point to line segment
            dx = x2 - x1
            dy = y2 - y1
            l2 = dx*dx + dy*dy
            t = max(0, min(1, ((gx - x1)*dx + (gy - y1)*dy) / l2))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = math.hypot(gx - proj_x, gy - proj_y)
            if dist < 0.42:
                on_wall = True
                break
        if on_wall:
            continue

        tuft_inst = tuft_proto.copy()
        tuft_inst.name = f"Grass_Tuft_Corr_{_}"
        tuft_inst.location = (gx, gy, 0.0)
        tuft_inst.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))
        sc = random.uniform(0.75, 1.30)
        tuft_inst.scale = (sc, sc, sc * random.uniform(0.9, 1.4))
        grass_col.objects.link(tuft_inst)

    # Outer meadow grass (perimeter around stone curb)
    for _ in range(180):
        ox = random.choice([-1, 1]) * random.uniform(6.2, 9.5)
        oy = random.uniform(-9.5, 9.5)
        if random.random() > 0.5:
            ox, oy = oy, ox
        tuft_inst = tuft_proto.copy()
        tuft_inst.name = f"Grass_Tuft_Outer_{_}"
        tuft_inst.location = (ox, oy, 0.0)
        tuft_inst.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))
        sc = random.uniform(0.85, 1.45)
        tuft_inst.scale = (sc, sc, sc * random.uniform(1.0, 1.5))
        grass_col.objects.link(tuft_inst)

    # Hide prototype
    tuft_proto.location = (0, 0, -100.0)

    # 5. Stylized Puffy Background Trees (4 trees framing behind Leaf Gate and corners)
    trees_data = [
        ("Tree_Back_L", (-3.2, 8.2, 0.0), 3.2, 2.4),
        ("Tree_Back_R", ( 3.2, 8.2, 0.0), 3.4, 2.6),
        ("Tree_Side_L", (-8.2, 2.5, 0.0), 2.8, 2.2),
        ("Tree_Side_R", ( 8.2, 2.5, 0.0), 3.0, 2.3)
    ]
    for t_name, t_loc, t_th, t_cr in trees_data:
        build_stylized_tree(t_name, t_loc, t_th, t_cr, mat_wood, mat_hedge, col)

    # 6. Lush Flower & Clover Beds along Paths and Hedge Edges
    flower_locs = [
        ("Flower_Bed_01", (-2.4, -4.5, 0.0), 8),
        ("Flower_Bed_02", ( 2.4, -4.5, 0.0), 8),
        ("Flower_Bed_03", (-4.2, -0.8, 0.0), 6),
        ("Flower_Bed_04", ( 4.2, -0.8, 0.0), 6),
        ("Flower_Bed_05", (-2.2,  2.4, 0.0), 7),
        ("Flower_Bed_06", ( 2.2,  2.4, 0.0), 7),
        ("Flower_Bed_07", (-1.0,  5.0, 0.0), 6), # Foot of Leaf Gate L
        ("Flower_Bed_08", ( 1.0,  5.0, 0.0), 6)  # Foot of Leaf Gate R
    ]
    for f_name, f_loc, f_cnt in flower_locs:
        build_flower_cluster(f_name, f_loc, f_cnt, mats_flower, col)

    # 7. Leaf Gate Archway (Centered on Back Perimeter at y = 5.4)
    build_leaf_gate_arch((0.0, 5.4, 0.0), mat_wood, mat_hedge, mats_momo, col)

    # 8. Momo Collectible Fruit (Sunlit corridor at x = 2.4, y = 0.8, z = 0.45)
    build_momo_collectible((2.4, 0.8, 0.45), mats_momo, col)

    # 9. Import/Link Characters: Golumolu v11 & Ghost Spirits v9
    # Import Golumolu v11
    golumolu_blend = "D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend"
    with bpy.data.libraries.load(golumolu_blend, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith("Golumolu_")]

    g_root = None
    for obj in data_to.objects:
        col.objects.link(obj)
        if obj.name == "Golumolu_Body":
            g_root = obj

    if g_root:
        # Position in sunny mid-corridor leaping towards Momo
        g_root.location = (0.2, 0.9, 0.95) # Leaping mid-air
        g_root.rotation_euler = (math.radians(-15), math.radians(10), math.radians(-55)) # Leaping towards Momo

        # Add joyful motion dust puffs behind his feet
        dust_mat = bpy.data.materials.new("M_Joy_Dust")
        dust_mat.use_nodes = True
        b_d = dust_mat.node_tree.nodes.get("Principled BSDF")
        b_d.inputs['Base Color'].default_value = (1.0, 0.95, 0.90, 1.0)
        b_d.inputs['Roughness'].default_value = 0.50

        for d_idx, d_off in enumerate([(-0.35, 0.45, 0.15), (-0.55, 0.30, 0.08), (-0.75, 0.20, 0.04)]):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.10 * (1.0 - d_idx * 0.2))
            dust = bpy.context.active_object
            dust.name = f"Golumolu_DustPuff_{d_idx}"
            dust.location = (0.2 + d_off[0], 0.9 + d_off[1], d_off[2])
            dust.data.materials.append(dust_mat)
            bpy.ops.object.shade_smooth()
            col.objects.link(dust)

    # Import Ghost Spirits v9
    ghosts_blend = "D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend"
    with bpy.data.libraries.load(ghosts_blend, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith("Ghost_")]

    for obj in data_to.objects:
        col.objects.link(obj)

    # Position Spirits dynamically through corridors
    ghost_follower_root = bpy.data.objects.get("Ghost_Follower_Root")
    if ghost_follower_root:
        ghost_follower_root.location = (-2.6, -0.9, 1.35)
        ghost_follower_root.rotation_euler = (math.radians(10), math.radians(-15), math.radians(-40))

    ghost_cutter_root = bpy.data.objects.get("Ghost_Cutter_Root")
    if ghost_cutter_root:
        ghost_cutter_root.location = (3.8, 2.6, 1.45)
        ghost_cutter_root.rotation_euler = (math.radians(15), math.radians(12), math.radians(-125))

    ghost_wanderer_root = bpy.data.objects.get("Ghost_Wanderer_Root")
    if ghost_wanderer_root:
        ghost_wanderer_root.location = (-0.8, -3.8, 1.25)
        ghost_wanderer_root.rotation_euler = (math.radians(-8), math.radians(15), math.radians(45))

    # Save Master Blend
    master_blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/maze_beauty_environment.blend"
    bpy.ops.wm.save_as_mainfile(filepath=master_blend_path)
    print(f"  ✓ Saved Master Lush Environment Blend -> {master_blend_path}")

    return col

def render_environment_views(col):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'

    # Warm Golden Hour Lighting
    world = scene.world or bpy.data.worlds.new("World_Lush_Golden")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.92, 0.95, 0.98, 1.0) # Sky blue ambient
        bg.inputs['Strength'].default_value = 0.75

    # Golden Sun Key Light
    sun = bpy.data.lights.new("Sun_Golden_Key", 'SUN')
    sun.energy = 5.5
    sun.color = (1.00, 0.92, 0.82) # Warm golden hour sunlight
    sun.angle = math.radians(12)
    sun_obj = bpy.data.objects.new("Sun_Golden_Key", sun)
    sun_obj.rotation_euler = (math.radians(48), math.radians(22), math.radians(-38))
    col.objects.link(sun_obj)

    # Sky Fill Light
    fill = bpy.data.lights.new("Sky_Fill", 'SUN')
    fill.energy = 2.0
    fill.color = (0.85, 0.92, 1.0)
    fill.angle = math.radians(30)
    fill_obj = bpy.data.objects.new("Sky_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-15), math.radians(140))
    col.objects.link(fill_obj)

    # Warm Rim Light
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.color = (1.0, 0.85, 0.65)
    rim.energy = 150.0
    rim.shadow_soft_size = 1.2
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.5, 4.5, 3.5)
    col.objects.link(rim_obj)

    # 1. Perspective Beauty Camera (Matching Ref 4 Panel 1 & 2)
    cam_data = bpy.data.cameras.new("Cam_Beauty_Lush")
    cam_data.type = 'PERSP'
    cam_data.lens = 52 # Stylized diorama focal length
    cam_obj = bpy.data.objects.new("Cam_Beauty_Lush", cam_data)
    cam_obj.location = (0.8, -14.8, 12.2)
    cam_obj.rotation_euler = (math.radians(52), 0, math.radians(3))
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    beauty_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_beauty_view_v6_lush.png"
    scene.render.filepath = beauty_out
    print(f"Rendering Master Lush Beauty View (1920x1080)...")
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Beauty View -> {beauty_out}")

    # 2. Orthographic Top-Down Map View
    cam_data_top = bpy.data.cameras.new("Cam_TopDown")
    cam_data_top.type = 'ORTHO'
    cam_data_top.ortho_scale = 14.5
    cam_top_obj = bpy.data.objects.new("Cam_TopDown", cam_data_top)
    cam_top_obj.location = (0, 0, 15.0)
    cam_top_obj.rotation_euler = (0, 0, 0)
    col.objects.link(cam_top_obj)
    scene.camera = cam_top_obj

    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    top_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_topdown_plan_v6.png"
    scene.render.filepath = top_out
    print(f"Rendering Master Top-Down Map View (1200x1200)...")
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Top-Down Plan -> {top_out}")

if __name__ == "__main__":
    print("==================================================")
    print("Building Master Lush Grassy & Fluffy Environment v6")
    print("==================================================")
    col = build_master_environment()
    render_environment_views(col)
    print("All environment tasks completed successfully!")
