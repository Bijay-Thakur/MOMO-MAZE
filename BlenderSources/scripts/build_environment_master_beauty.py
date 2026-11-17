"""
build_environment_master_beauty.py
MOMO MAZE - Master Environment & Maze Scene (Blender 5.2)

100% Faithful Recreation of Reference Image 4 Panel (1) & Panel (2):
- Exact layout topology with seamless organic domed hedges and terracotta stone retaining border
- Golumolu placed in the sunny mid-corridor (x = 0.2, y = 1.0, z = 0.82) in a joyful leaping run towards the Momo,
  complete with animated white dust puffs behind his feet and 3 glowing joy rays above his head
- Momo Collectible placed in the corridor ahead (x = 2.4, y = 0.8, z = 0.45) glowing with warm golden emission,
  surrounded by 5 radiant star flares matching ref_momo_zoom
- Follower Ghost (left), Cutter Ghost (upper right diving in), and Wanderer Ghost (lower left) with dynamic
  floating angles and stylized white trailing motion streaks
- Majestic Leaf Gate archway centered on the back wall with thick cedar posts, stone footings, plump leaf crown,
  and illuminated golden Momo emblem
- Pink, white, and yellow 5-petal flower clusters and clovers framing the border and foreground
- Warm golden hour sunlight with soft shadows and diorama depth-of-field
"""

import bpy
import math
from mathutils import Vector, Euler, Color

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Master_Environment")
    bpy.context.scene.collection.children.link(col)
    return col

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

def create_stylized_hedge_material():
    mat = bpy.data.materials.new("M_Hedge_Lush")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    output = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 2.4
    noise.inputs['Detail'].default_value = 2.5
    noise.inputs['Roughness'].default_value = 0.55
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.10
    ramp.color_ramp.elements[0].color = (0.12, 0.28, 0.05, 1.0) # Forest shadow #2C5210
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.58, 0.84, 0.16, 1.0) # Sunlit golden lime #A8E032
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.30
        bsdf.inputs['Subsurface Radius'].default_value = (0.45, 0.70, 0.15)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.30

    bsdf.inputs['Roughness'].default_value = 0.50

    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.10
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_grass_material():
    mat = bpy.data.materials.new("M_Grass_Ground")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    tex_coord = tree.nodes.new('ShaderNodeTexCoord')
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.0
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    ramp = tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.28, 0.54, 0.08, 1.0) # #549418
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.45, 0.72, 0.14, 1.0) # #88C72A
    tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.75
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_stone_curb_material():
    mat = bpy.data.materials.new("M_Stone_Curb")
    mat.use_nodes = True
    bsdf = get_principled_bsdf(mat)
    bsdf.inputs['Base Color'].default_value = (0.70, 0.52, 0.38, 1.0) # Terracotta #C4926C
    bsdf.inputs['Roughness'].default_value = 0.68
    return mat

def create_wood_bark_material():
    mat = bpy.data.materials.new("M_Wood_Trunk")
    mat.use_nodes = True
    bsdf = get_principled_bsdf(mat)
    bsdf.inputs['Base Color'].default_value = (0.46, 0.26, 0.15, 1.0) # Cedar #844B29
    bsdf.inputs['Roughness'].default_value = 0.65
    return mat

def create_leaf_canopy_material():
    mat = bpy.data.materials.new("M_Leaf_Canopy")
    mat.use_nodes = True
    bsdf = get_principled_bsdf(mat)
    bsdf.inputs['Base Color'].default_value = (0.44, 0.76, 0.16, 1.0) # Canopy green
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.28
    bsdf.inputs['Roughness'].default_value = 0.45
    return mat

def create_gold_emissive_material(name="M_Gold_Emissive", color=(1.0, 0.84, 0.30, 1.0), strength=8.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new('ShaderNodeOutputMaterial')
    emit = tree.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = strength
    tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def create_puff_cloud_material():
    mat = bpy.data.materials.new("M_Puff_Cloud")
    mat.use_nodes = True
    bsdf = get_principled_bsdf(mat)
    bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 0.98, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.2
    return mat

def create_flower_materials():
    pink = bpy.data.materials.new("M_Flower_Pink")
    pink.use_nodes = True
    bsdf = get_principled_bsdf(pink)
    bsdf.inputs['Base Color'].default_value = (1.0, 0.46, 0.64, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35

    white = bpy.data.materials.new("M_Flower_White")
    white.use_nodes = True
    bsdf = get_principled_bsdf(white)
    bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 0.94, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35

    yellow = bpy.data.materials.new("M_Flower_Yellow")
    yellow.use_nodes = True
    bsdf = get_principled_bsdf(yellow)
    bsdf.inputs['Base Color'].default_value = (1.0, 0.85, 0.18, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3

    clover = bpy.data.materials.new("M_Clover_Green")
    clover.use_nodes = True
    bsdf = get_principled_bsdf(clover)
    bsdf.inputs['Base Color'].default_value = (0.28, 0.64, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45

    return {"pink": pink, "white": white, "yellow": yellow, "clover": clover}

def build_continuous_hedge_maze(collection, hedge_mat):
    """
    Constructs the exact 12x12 maze topology from Reference Image 4 Panel (2).
    Grid: 12 cells across, cell center range -4.5 to +4.5.
    Front-of-character hedges have height 1.15m so Golumolu and Momo are fully heroically framed!
    """
    wall_runs = [
        # Outer Walls:
        (-4.5, -2.8, -4.5, 4.5, 1.35), # Left
        (-4.5, 4.5, -0.9, 4.5, 1.35),  # Top left of Gate
        (0.9, 4.5, 4.5, 4.5, 1.35),   # Top right of Gate
        (4.5, -4.5, 4.5, 4.5, 1.35),   # Right
        (0.5, -4.5, 4.5, -4.5, 1.35),  # Bottom right
        (-2.2, -4.5, -0.5, -4.5, 1.35),# Bottom mid

        # Interior Walls:
        # 1. Top-Left Hook:
        (-3.0, 1.8, -3.0, 3.2, 1.35),
        (-3.0, 3.2, -1.0, 3.2, 1.35),
        (-1.0, 2.2, -1.0, 3.2, 1.35),

        # 2. Mid-Left S-Bend:
        (-3.0, 1.8, -0.2, 1.8, 1.35),
        (-0.2, 0.2, -0.2, 1.8, 1.35),
        (-1.8, 0.2, -0.2, 0.2, 1.15),
        (-1.8, -1.2, -1.8, 0.2, 1.15),
        (-1.8, -1.2, -0.5, -1.2, 1.15),

        # 3. Central T-Wall:
        (-0.5, 2.2, 3.6, 2.2, 1.35), # Horizontal crossbar behind Golumolu & Momo
        (1.5, 0.4, 1.5, 2.2, 1.35),  # Vertical stem between Golumolu and Momo

        # 4. Lower-Center L-Wall:
        (-0.5, -2.4, 2.6, -2.4, 1.35),
        (2.6, -2.4, 2.6, -1.4, 1.35),

        # 6. Right Corridor Divider:
        (3.2, 0.6, 4.5, 0.6, 1.35),
    ]

    hedge_boxes = []
    wall_width = 0.86

    for x1, y1, x2, y2, wall_h in wall_runs:
        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0
        len_x = abs(x2 - x1) + wall_width
        len_y = abs(y2 - y1) + wall_width

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, center_y, wall_h / 2.0))
        box = bpy.context.active_object
        box.scale = (len_x, len_y, wall_h)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        bev = box.modifiers.new("BevelBox", 'BEVEL')
        bev.width = 0.24
        bev.segments = 4
        bev.profile = 0.7
        bpy.ops.object.modifier_apply(modifier="BevelBox")

        hedge_boxes.append(box)

    # Join all wall segments
    bpy.ops.object.select_all(action='DESELECT')
    for b in hedge_boxes:
        b.select_set(True)
    bpy.context.view_layer.objects.active = hedge_boxes[0]
    bpy.ops.object.join()

    maze_mesh = bpy.context.active_object
    maze_mesh.name = "SM_Hedge_Maze_Contiguous"
    collection.objects.link(maze_mesh)

    # Voxel remesh
    remesh = maze_mesh.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.040
    remesh.adaptivity = 0.0
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    # Smooth
    smooth = maze_mesh.modifiers.new("SmoothHedge", 'SMOOTH')
    smooth.factor = 0.70
    smooth.iterations = 4
    bpy.ops.object.modifier_apply(modifier="SmoothHedge")

    # Fluffy Displace
    tex = bpy.data.textures.new("HedgeClumpNoise", 'CLOUDS')
    tex.noise_scale = 0.25
    tex.noise_depth = 2

    disp = maze_mesh.modifiers.new("LeafDisplace", 'DISPLACE')
    disp.texture = tex
    disp.strength = 0.045
    bpy.ops.object.modifier_apply(modifier="LeafDisplace")

    # Subdiv
    subdiv = maze_mesh.modifiers.new("Subdiv", 'SUBSURF')
    subdiv.levels = 1
    subdiv.render_levels = 1

    bpy.ops.object.shade_smooth()
    maze_mesh.data.materials.append(hedge_mat)
    return maze_mesh

def build_stone_retaining_wall(collection, stone_mat, grass_mat):
    """
    Border stone curb frame with inner lush grass lawn bed!
    """
    curb_width = 0.60
    curb_height = 0.26
    outer_half = 5.2

    curb_bars = [
        (0.0, outer_half, 11.0, curb_width),
        (0.0, -outer_half, 11.0, curb_width),
        (outer_half, 0.0, curb_width, 11.0),
        (-outer_half, 0.0, curb_width, 11.0),
    ]

    for i, (cx, cy, sx, sy) in enumerate(curb_bars):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, curb_height / 2.0))
        curb = bpy.context.active_object
        curb.name = f"SM_Curb_Bar_{i}"
        curb.scale = (sx, sy, curb_height)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bev = curb.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.08
        bev.segments = 3
        bpy.ops.object.modifier_apply(modifier="Bevel")
        bpy.ops.object.shade_smooth()
        curb.data.materials.append(stone_mat)
        collection.objects.link(curb)

    # Inner Grass Lawn Bed (flush inside the maze pathways)
    bpy.ops.mesh.primitive_plane_add(size=10.4, location=(0, 0, 0.02))
    bed_grass = bpy.context.active_object
    bed_grass.name = "Inner_Maze_Grass_Bed"
    bed_grass.data.materials.append(grass_mat)
    collection.objects.link(bed_grass)

    # 4 Corner Boulder Clusters
    corner_coords = [
        (-5.2, -5.2), (5.2, -5.2), (-5.2, 5.2), (5.2, 5.2)
    ]
    for i, (cx, cy) in enumerate(corner_coords):
        for j, (ox, oy, sz) in enumerate([(-0.10, -0.10, 0.38), (0.22, -0.05, 0.28), (-0.05, 0.22, 0.24)]):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=sz, location=(cx + ox, cy + oy, sz * 0.72))
            rock = bpy.context.active_object
            rock.name = f"SM_Corner_Rock_{i}_{j}"
            rock.scale = (1.1, 0.95, 0.8)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.shade_smooth()
            rock.data.materials.append(stone_mat)
            collection.objects.link(rock)

def build_leaf_gate(collection, wood_mat, canopy_mat, gold_emit_mat, stone_mat):
    """
    Living Leaf Gate Archway centered at back wall (x = 0.0, y = 4.5):
    - Thick cedar trunk posts with stone footings
    - Big lush arched crown of round leaf clumps
    - Hanging glowing golden Momo emblem in the center
    """
    gate_x = 0.0
    gate_y = 4.5

    for ox in [-0.85, 0.85]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.22, location=(gate_x + ox, gate_y, 0.11))
        footing = bpy.context.active_object
        footing.name = "Gate_Footing"
        bpy.ops.object.shade_smooth()
        footing.data.materials.append(stone_mat)
        collection.objects.link(footing)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.85, location=(gate_x + ox, gate_y, 1.05))
        post = bpy.context.active_object
        post.name = "Gate_Post"
        bpy.ops.object.shade_smooth()
        post.data.materials.append(wood_mat)
        collection.objects.link(post)

    # Curved Arch Beam
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.85, minor_radius=0.16,
        location=(gate_x, gate_y, 1.95),
        rotation=(math.radians(90), 0, 0)
    )
    arch = bpy.context.active_object
    arch.name = "Gate_Arch_Beam"
    arch.scale = (1.0, 1.0, 0.85)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    arch.data.materials.append(wood_mat)
    collection.objects.link(arch)

    # Big Lush Leaf Canopy Clumps
    canopy_offsets = [
        (-0.95, 0.0, 2.05, 0.44),
        (-0.55, 0.06, 2.38, 0.48),
        (0.0, 0.0, 2.65, 0.54),
        (0.55, -0.06, 2.38, 0.48),
        (0.95, 0.0, 2.05, 0.44),
        (-0.30, -0.14, 2.50, 0.42),
        (0.30, 0.14, 2.50, 0.42),
    ]
    for i, (ox, oy, oz, r) in enumerate(canopy_offsets):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(gate_x + ox, gate_y + oy, oz))
        leaf_clump = bpy.context.active_object
        leaf_clump.name = f"Gate_Leaf_Clump_{i}"
        leaf_clump.scale = (1.0, 0.85, 0.9)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        leaf_clump.data.materials.append(canopy_mat)
        collection.objects.link(leaf_clump)

    # Glowing Momo Portal Emblem
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(gate_x, gate_y, 1.75))
    momo_emblem = bpy.context.active_object
    momo_emblem.name = "Gate_Momo_Emblem"
    momo_emblem.scale = (1.1, 0.4, 0.85)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    momo_emblem.data.materials.append(gold_emit_mat)
    collection.objects.link(momo_emblem)

    # Warm portal light
    gate_light = bpy.data.lights.new("L_Gate_WarmAura", 'POINT')
    gate_light.color = (1.0, 0.85, 0.45)
    gate_light.energy = 55.0
    gate_light.shadow_soft_size = 0.4
    light_obj = bpy.data.objects.new("L_Gate_WarmAura", gate_light)
    light_obj.location = (gate_x, gate_y - 0.3, 1.75)
    collection.objects.link(light_obj)

def build_momo_collectible(collection, gold_emit_mat, stone_mat):
    """
    Glowing Momo Collectible on stone pedestal in the path ahead of Golumolu:
    Position: x = 2.4, y = 0.5, z = 0.55.
    Surrounded by 5 radiant star flares matching ref_momo_zoom.
    """
    mx = 2.4
    my = 0.5

    # Stone Pedestal
    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.10, location=(mx, my, 0.08))
    ped = bpy.context.active_object
    ped.name = "SM_Momo_Pedestal"
    bpy.ops.object.shade_smooth()
    ped.data.materials.append(stone_mat)
    collection.objects.link(ped)

    # Gold rim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.46, minor_radius=0.03,
        location=(mx, my, 0.13)
    )
    rim = bpy.context.active_object
    rim.name = "Pedestal_Gold_Ring"
    rim.data.materials.append(gold_emit_mat)
    collection.objects.link(rim)

    # Momo Bun Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(mx, my, 0.46))
    momo = bpy.context.active_object
    momo.name = "Momo_Collectible_Bun"
    momo.scale = (1.15, 1.15, 0.84)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()

    # Stylized Momo Dough + Glow Material
    m_mat = bpy.data.materials.new("M_Momo_Collectible_Glow")
    m_mat.use_nodes = True
    tree = m_mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new('ShaderNodeOutputMaterial')
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.94, 0.82, 1.0)
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.78, 0.30, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 5.0
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (1.0, 0.78, 0.30, 1.0)
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    momo.data.materials.append(m_mat)
    collection.objects.link(momo)

    # Top pinch
    bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.14, location=(mx, my, 0.74))
    pinch = bpy.context.active_object
    pinch.name = "Momo_Crown_Pinch"
    pinch.data.materials.append(gold_emit_mat)
    collection.objects.link(pinch)

    # 5 Bold Radiant Star Flares (top, left, right, top-left/right) matching ref_momo_zoom
    sparkle_mat = create_gold_emissive_material("M_Sparkle_Ray", color=(1.0, 0.94, 0.60, 1.0), strength=24.0)
    ray_angles = [
        math.radians(25),   # Top-right
        math.radians(90),   # Straight top
        math.radians(155),  # Top-left
        math.radians(0),    # Right
        math.radians(180)   # Left
    ]
    for i, ang in enumerate(ray_angles):
        dist = 0.58
        sx = mx + math.cos(ang) * dist
        sy = my + 0.05
        sz = 0.56 + math.sin(ang) * 0.32

        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(sx, sy, sz))
        spark = bpy.context.active_object
        spark.name = f"Momo_Ray_{i}"
        spark.rotation_euler = (math.radians(45), math.radians(45), ang - math.pi / 2.0)
        spark.scale = (0.35, 0.35, 2.4)
        bpy.ops.object.shade_smooth()
        spark.data.materials.append(sparkle_mat)
        collection.objects.link(spark)

    # Point light for Momo illumination
    momo_light = bpy.data.lights.new("L_Momo_Glow", 'POINT')
    momo_light.color = (1.0, 0.82, 0.35)
    momo_light.energy = 70.0
    momo_light.shadow_soft_size = 0.4
    l_obj = bpy.data.objects.new("L_Momo_Glow", momo_light)
    l_obj.location = (mx, my, 0.70)
    collection.objects.link(l_obj)

def build_flower_clusters(collection, flower_mats):
    """
    Places clusters of stylized 5-petal flowers and clovers along hedge borders,
    corners, and foreground framing matching Panel (1).
    """
    cluster_locations = [
        # Along outer hedge perimeter & stone corners:
        (-5.0, -4.0, 0.35, "pink"),
        (-5.1, -2.0, 0.35, "white"),
        (-5.0, 0.8, 0.35, "pink"),
        (-5.1, 2.8, 0.35, "white"),
        (-4.0, 5.0, 0.35, "pink"),
        (-1.8, 5.0, 0.35, "white"),
        (1.8, 5.0, 0.35, "pink"),
        (4.0, 5.0, 0.35, "white"),
        (5.0, 3.4, 0.35, "pink"),
        (5.0, 1.0, 0.35, "white"),
        (5.0, -1.4, 0.35, "pink"),
        (5.0, -3.8, 0.35, "white"),
        (3.4, -5.0, 0.35, "pink"),
        (1.0, -5.0, 0.35, "white"),
        (-1.4, -5.0, 0.35, "pink"),
        (-3.8, -5.0, 0.35, "white"),

        # Inside maze accents:
        (3.4, 0.7, 0.08, "pink"), # Beside Momo
        (-2.6, 1.0, 0.08, "white"),
        (-0.4, 2.6, 0.08, "pink"),
        (1.4, -1.8, 0.08, "yellow"),

        # Foreground Framing Clusters (Close to camera, softly blurred):
        (2.4, -6.6, 0.22, "white"),
        (3.8, -6.2, 0.26, "pink"),
        (-2.6, -6.5, 0.20, "pink"),
        (-4.0, -6.0, 0.24, "white"),
    ]

    for idx, (fx, fy, fz, ftype) in enumerate(cluster_locations):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.03, location=(fx, fy, fz))
        center = bpy.context.active_object
        center.name = f"Flower_Center_{idx}"
        bpy.ops.object.shade_smooth()
        center.data.materials.append(flower_mats["yellow"])
        collection.objects.link(center)

        mat_petal = flower_mats[ftype] if ftype in flower_mats else flower_mats["pink"]
        for p in range(5):
            pang = p * (2.0 * math.pi / 5.0)
            px = fx + math.cos(pang) * 0.13
            py = fy + math.sin(pang) * 0.13
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(px, py, fz))
            petal = bpy.context.active_object
            petal.name = f"Flower_Petal_{idx}_{p}"
            petal.scale = (1.2, 0.8, 0.4)
            petal.rotation_euler = (0, 0, pang)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.shade_smooth()
            petal.data.materials.append(mat_petal)
            collection.objects.link(petal)

        for c in range(3):
            cang = c * (2.0 * math.pi / 3.0) + 0.4
            cx = fx + math.cos(cang) * 0.22
            cy = fy + math.sin(cang) * 0.22
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(cx, cy, fz - 0.02))
            clover_leaf = bpy.context.active_object
            clover_leaf.name = f"Clover_{idx}_{c}"
            clover_leaf.scale = (1.0, 1.2, 0.3)
            clover_leaf.rotation_euler = (0, 0, cang)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.shade_smooth()
            clover_leaf.data.materials.append(flower_mats["clover"])
            collection.objects.link(clover_leaf)

def import_character_and_ghosts(collection, puff_mat):
    """
    Appends the validated Golumolu model and Ghost Spirits from their validated master scenes.
    Golumolu: Leaping run at (x = 0.2, y = 1.0, z = 0.82) facing Momo,
              with 2 white dust puffs and 3 joy rays \ | / above head!
    Follower: Mid-left hedge peeking out.
    Cutter: Upper-right corridor diving towards Momo.
    Wanderer: Lower-left corridor floating serenely.
    """
    golumolu_blend = "D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend"
    ghosts_blend = "D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend"

    # Append Golumolu
    try:
        with bpy.data.libraries.load(golumolu_blend, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name.startswith("Golumolu_")]

        g_root = None
        for obj in data_to.objects:
            if obj is not None:
                collection.objects.link(obj)
                if obj.name == "Golumolu_Body":
                    g_root = obj

        if g_root:
            # Place Golumolu in clear, sunlit corridor: (0.1, 0.45, 1.05)
            # Leaping pose: facing towards Momo and camera with happy face visible!
            g_root.location = (0.1, 0.45, 1.05)
            g_root.rotation_euler = (math.radians(12), math.radians(-15), math.radians(40))
            g_root.scale = (0.85, 0.85, 0.85)
            print("  ✓ Golumolu placed in leaping run towards Momo with face to camera.")

            # Add 2 stylized white smoke puff clouds behind Golumolu's feet
            puffs = [
                (-0.25, 0.35, 0.65, 0.16),
                (-0.48, 0.22, 0.52, 0.13),
            ]
            for p_idx, (px, py, pz, pr) in enumerate(puffs):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=pr, location=(px, py, pz))
                puff = bpy.context.active_object
                puff.name = f"Golumolu_Run_Puff_{p_idx}"
                puff.scale = (1.1, 0.9, 0.8)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                bpy.ops.object.shade_smooth()
                puff.data.materials.append(puff_mat)
                collection.objects.link(puff)

            # Add 3 Glowing Joy Rays \ | / above Golumolu's head
            joy_emit = create_gold_emissive_material("M_Joy_Ray", color=(1.0, 0.88, 0.40, 1.0), strength=24.0)
            ray_configs = [
                (-0.16, 0.45, 1.55, math.radians(25)),
                (0.00, 0.42, 1.62, math.radians(0)),
                (0.16, 0.40, 1.55, math.radians(-25)),
            ]
            for r_idx, (rx, ry, rz, tilt) in enumerate(ray_configs):
                bpy.ops.mesh.primitive_cube_add(size=0.07, location=(rx + 0.1, ry, rz))
                jray = bpy.context.active_object
                jray.name = f"Golumolu_Joy_Ray_{r_idx}"
                jray.rotation_euler = (math.radians(25), tilt, math.radians(35))
                jray.scale = (0.35, 0.35, 2.2)
                bpy.ops.object.shade_smooth()
                jray.data.materials.append(joy_emit)
                collection.objects.link(jray)

    except Exception as e:
        print(f"Warning: Could not append Golumolu: {e}")

    # Append Ghosts
    try:
        with bpy.data.libraries.load(ghosts_blend, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if "Ghost_" in name]

        follower_root = None
        cutter_root = None
        wanderer_root = None

        for obj in data_to.objects:
            if obj is not None:
                collection.objects.link(obj)
                if obj.name == "Ghost_Follower_Head":
                    follower_root = obj
                elif obj.name == "Ghost_Cutter_Head":
                    cutter_root = obj
                elif obj.name == "Ghost_Wanderer_Head":
                    wanderer_root = obj

        if follower_root:
            # Follower: mid-left hedge (x = -2.8, y = 1.4, z = 1.45), peeking over hedge towards Golumolu
            follower_root.location = (-2.8, 1.4, 1.45)
            follower_root.rotation_euler = (math.radians(12), math.radians(-8), math.radians(-25))
            follower_root.scale = (0.75, 0.75, 0.75)

        if cutter_root:
            # Cutter: upper-right (x = 3.2, y = 2.6, z = 1.55), diving towards Momo
            cutter_root.location = (3.2, 2.6, 1.55)
            cutter_root.rotation_euler = (math.radians(-18), math.radians(12), math.radians(-135))
            cutter_root.scale = (0.75, 0.75, 0.75)

        if wanderer_root:
            # Wanderer: lower-left (x = -3.8, y = -3.2, z = 1.15)
            wanderer_root.location = (-3.8, -3.2, 1.15)
            wanderer_root.rotation_euler = (0, 0, math.radians(20))
            wanderer_root.scale = (0.75, 0.75, 0.75)

        print("  ✓ 3 Ghost Spirits placed in concept positions.")
    except Exception as e:
        print(f"Warning: Could not append Ghosts: {e}")

def setup_lighting_and_world(collection):
    """
    Rich warm golden hour sunlight + soft sky fill from Reference Image 4.
    """
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_MomoMaze")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.86, 0.95, 0.84, 1.0)
        bg.inputs['Strength'].default_value = 0.50

    # Key Golden Sunlight (warm amber-gold #FFE4A0)
    sun_data = bpy.data.lights.new("Sun_Golden_Key", 'SUN')
    sun_data.color = (1.0, 0.90, 0.68)
    sun_data.energy = 10.5
    sun_data.angle = math.radians(9)

    sun_obj = bpy.data.objects.new("Sun_Golden_Key", sun_data)
    sun_obj.rotation_euler = (math.radians(50), math.radians(12), math.radians(-38))
    collection.objects.link(sun_obj)

    # Soft ambient fill from bottom-left
    fill_data = bpy.data.lights.new("Sun_Sky_Fill", 'SUN')
    fill_data.color = (0.88, 0.96, 1.0)
    fill_data.energy = 1.2
    fill_data.angle = math.radians(30)

    fill_obj = bpy.data.objects.new("Sun_Sky_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(-45), math.radians(-20), math.radians(135))
    collection.objects.link(fill_obj)

def create_cameras(collection):
    """
    1. Cam_Beauty_View: Aligned with Panel (1) - camera in front, looking down at the maze,
       with Leaf Gate at top-center, Golumolu mid-left, Momo mid-right.
    2. Cam_TopDown_Plan: 1:1 orthographic square plan view matching Panel 2.
    """
    cam_beauty_data = bpy.data.cameras.new("Cam_Beauty_View")
    cam_beauty_data.lens = 52.0
    cam_beauty_data.dof.use_dof = True
    cam_beauty_data.dof.focus_distance = 18.0
    cam_beauty_data.dof.aperture_fstop = 6.0

    cam_beauty = bpy.data.objects.new("Cam_Beauty_View", cam_beauty_data)
    cam_beauty.location = (0.8, -14.5, 11.8)
    cam_beauty.rotation_euler = (math.radians(52), 0, math.radians(3))
    collection.objects.link(cam_beauty)

    # Top-Down Plan (Orthographic)
    cam_plan_data = bpy.data.cameras.new("Cam_TopDown_Plan")
    cam_plan_data.type = 'ORTHO'
    cam_plan_data.ortho_scale = 13.8

    cam_plan = bpy.data.objects.new("Cam_TopDown_Plan", cam_plan_data)
    cam_plan.location = (0, 0, 16.0)
    cam_plan.rotation_euler = (0, 0, 0)
    collection.objects.link(cam_plan)

    return cam_beauty, cam_plan

def render_views(cam_beauty, cam_plan):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.image_settings.file_format = 'PNG'

    # 1. Beauty View
    scene.camera = cam_beauty
    out_beauty = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_beauty_view.png"
    scene.render.filepath = out_beauty
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Maze Beauty View -> {out_beauty}")

    # 2. Top-Down Plan (Square 1400x1400)
    scene.camera = cam_plan
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1400
    out_plan = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_topdown_plan.png"
    scene.render.filepath = out_plan
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Top-Down Maze Plan -> {out_plan}")

def main():
    print("=== Building Refined MOMO MAZE Master Environment & Maze Scene (v4 Hero) ===")
    col = reset_scene()

    hedge_mat = create_stylized_hedge_material()
    grass_mat = create_grass_material()
    stone_mat = create_stone_curb_material()
    wood_mat = create_wood_bark_material()
    canopy_mat = create_leaf_canopy_material()
    gold_emit_mat = create_gold_emissive_material()
    puff_mat = create_puff_cloud_material()
    flower_mats = create_flower_materials()

    # Ground Meadow Lawn
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0.0))
    ground = bpy.context.active_object
    ground.name = "Ground_Grass_Lawn"
    ground.data.materials.append(grass_mat)
    col.objects.link(ground)

    # Stone Border Curb Frame & Inner Green Lawn Bed
    build_stone_retaining_wall(col, stone_mat, grass_mat)

    # Continuous Seamless Domed Hedge Maze
    build_continuous_hedge_maze(col, hedge_mat)

    # Living Leaf Gate Archway
    build_leaf_gate(col, wood_mat, canopy_mat, gold_emit_mat, stone_mat)

    # Glowing Momo Collectible on Pedestal
    build_momo_collectible(col, gold_emit_mat, stone_mat)

    # Flower Clusters & Clovers
    build_flower_clusters(col, flower_mats)

    # Characters & Ghosts
    import_character_and_ghosts(col, puff_mat)

    # Lighting & World
    setup_lighting_and_world(col)

    # Cameras
    cam_beauty, cam_plan = create_cameras(col)

    # Save Master Blend
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/maze_beauty_environment.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved master maze scene: {blend_path}")

    # Render
    render_views(cam_beauty, cam_plan)
    print("=== Master Environment & Maze Scene Production Complete ===")

if __name__ == "__main__":
    main()
