import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for item in b:
            b.remove(item)

# ==============================================================================
# 1. SHADERS & MATERIALS (Strictly Matching Ref 4 Palette & Style)
# ==============================================================================

def create_environment_materials():
    # 1. Lush Grassy Living Hedge Material (Deep Emerald to Sunlit Lime)
    m_hedge = bpy.data.materials.new("M_Living_Hedge_Master")
    m_hedge.use_nodes = True
    nodes = m_hedge.node_tree.nodes
    links = m_hedge.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    tex_coord = nodes.new("ShaderNodeTexCoord")
    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.feature = 'F1'
    voronoi.inputs["Scale"].default_value = 8.0
    
    ramp = nodes.new("ShaderNodeValToRGB")
    # Base Moss Green (#2A6020)
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (0.165, 0.376, 0.125, 1.0)
    # Mid Living Green (#3E822A)
    ramp.color_ramp.elements.new(0.55)
    ramp.color_ramp.elements[1].color = (0.243, 0.510, 0.165, 1.0)
    # Sunlit Yellow-Lime Highlights (#88C236)
    ramp.color_ramp.elements[2].position = 0.90
    ramp.color_ramp.elements[2].color = (0.533, 0.761, 0.212, 1.0)
    
    links.new(tex_coord.outputs["Object"], voronoi.inputs["Vector"])
    links.new(voronoi.outputs["Distance"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.58
    bsdf.inputs["Subsurface Weight"].default_value = 0.28
    bsdf.inputs["Subsurface Radius"].default_value = (0.5, 0.8, 0.2)
    bsdf.inputs["Subsurface Scale"].default_value = 0.08
    bsdf.inputs["Sheen Weight"].default_value = 0.65
    bsdf.inputs["Sheen Tint"].default_value = (0.7, 0.9, 0.4, 1.0)

    # Procedural leaf-clumping bump
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 45.0
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.65
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.04
    
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # 2. Rich Lawn Grass Blade Material
    m_grass = bpy.data.materials.new("M_Lawn_Grass_Master")
    m_grass.use_nodes = True
    n_g = m_grass.node_tree.nodes
    l_g = m_grass.node_tree.links
    n_g.clear()
    out_g = n_g.new("ShaderNodeOutputMaterial")
    b_g = n_g.new("ShaderNodeBsdfPrincipled")
    
    tc_g = n_g.new("ShaderNodeTexCoord")
    sep_g = n_g.new("ShaderNodeSeparateXYZ")
    ramp_g = n_g.new("ShaderNodeValToRGB")
    # Base: Deep forest green (#234818)
    ramp_g.color_ramp.elements[0].position = 0.0
    ramp_g.color_ramp.elements[0].color = (0.137, 0.282, 0.094, 1.0)
    # Tip: Vibrant lime gold (#7DB82E)
    ramp_g.color_ramp.elements[1].position = 1.0
    ramp_g.color_ramp.elements[1].color = (0.490, 0.722, 0.180, 1.0)
    
    l_g.new(tc_g.outputs["Generated"], sep_g.inputs["Vector"])
    l_g.new(sep_g.outputs["Z"], ramp_g.inputs["Fac"])
    l_g.new(ramp_g.outputs["Color"], b_g.inputs["Base Color"])
    b_g.inputs["Roughness"].default_value = 0.40
    b_g.inputs["Subsurface Weight"].default_value = 0.45
    b_g.inputs["Subsurface Radius"].default_value = (0.4, 0.8, 0.2)
    b_g.inputs["Sheen Weight"].default_value = 0.8
    l_g.new(b_g.outputs["BSDF"], out_g.inputs["Surface"])

    # 3. Ground Earth & Lawn Substrate
    m_ground = bpy.data.materials.new("M_Ground_Lawn")
    m_ground.use_nodes = True
    b_gr = m_ground.node_tree.nodes.get("Principled BSDF")
    b_gr.inputs["Base Color"].default_value = (0.22, 0.38, 0.14, 1.0)
    b_gr.inputs["Roughness"].default_value = 0.85

    # 4. Terracotta / Sandstone Curb Material
    m_curb = bpy.data.materials.new("M_Raised_Curb")
    m_curb.use_nodes = True
    b_c = m_curb.node_tree.nodes.get("Principled BSDF")
    b_c.inputs["Base Color"].default_value = (0.75, 0.52, 0.38, 1.0)
    b_c.inputs["Roughness"].default_value = 0.75

    # 5. Flower Petal Materials (Pink, White, Yellow Center)
    m_pink = bpy.data.materials.new("M_Flower_Pink")
    m_pink.use_nodes = True
    b_pk = m_pink.node_tree.nodes.get("Principled BSDF")
    b_pk.inputs["Base Color"].default_value = (1.0, 0.65, 0.72, 1.0)
    b_pk.inputs["Subsurface Weight"].default_value = 0.5
    b_pk.inputs["Roughness"].default_value = 0.4

    m_white = bpy.data.materials.new("M_Flower_White")
    m_white.use_nodes = True
    b_wh = m_white.node_tree.nodes.get("Principled BSDF")
    b_wh.inputs["Base Color"].default_value = (0.98, 0.98, 0.96, 1.0)
    b_wh.inputs["Subsurface Weight"].default_value = 0.4
    b_wh.inputs["Roughness"].default_value = 0.4

    m_yellow = bpy.data.materials.new("M_Flower_Center")
    m_yellow.use_nodes = True
    b_yl = m_yellow.node_tree.nodes.get("Principled BSDF")
    b_yl.inputs["Base Color"].default_value = (1.0, 0.78, 0.15, 1.0)
    b_yl.inputs["Roughness"].default_value = 0.35

    # 6. Leaf & Clover Material
    m_clover = bpy.data.materials.new("M_Clover_Leaf")
    m_clover.use_nodes = True
    b_cl = m_clover.node_tree.nodes.get("Principled BSDF")
    b_cl.inputs["Base Color"].default_value = (0.28, 0.62, 0.18, 1.0)
    b_cl.inputs["Subsurface Weight"].default_value = 0.45
    b_cl.inputs["Roughness"].default_value = 0.35

    # 7. Wooden Posts (Leaf Gate & Trees)
    m_wood = bpy.data.materials.new("M_Cozy_Wood")
    m_wood.use_nodes = True
    b_wd = m_wood.node_tree.nodes.get("Principled BSDF")
    b_wd.inputs["Base Color"].default_value = (0.55, 0.36, 0.22, 1.0)
    b_wd.inputs["Roughness"].default_value = 0.65

    # 8. Golden Momo Dumpling Collectible
    m_momo = bpy.data.materials.new("M_Momo_Golden_Master")
    m_momo.use_nodes = True
    b_mo = m_momo.node_tree.nodes.get("Principled BSDF")
    b_mo.inputs["Base Color"].default_value = (1.0, 0.91, 0.65, 1.0)
    b_mo.inputs["Subsurface Weight"].default_value = 0.60
    b_mo.inputs["Subsurface Radius"].default_value = (1.0, 0.7, 0.4)
    b_mo.inputs["Emission Color"].default_value = (1.0, 0.85, 0.45, 1.0)
    b_mo.inputs["Emission Strength"].default_value = 1.4
    b_mo.inputs["Roughness"].default_value = 0.30

    # 9. Golden Sparkles
    m_sparkle = bpy.data.materials.new("M_Gold_Sparkle")
    m_sparkle.use_nodes = True
    b_sp = m_sparkle.node_tree.nodes.get("Principled BSDF")
    b_sp.inputs["Base Color"].default_value = (1.0, 0.9, 0.4, 1.0)
    b_sp.inputs["Emission Color"].default_value = (1.0, 0.9, 0.4, 1.0)
    b_sp.inputs["Emission Strength"].default_value = 6.0

    return {
        "hedge": m_hedge,
        "grass": m_grass,
        "ground": m_ground,
        "curb": m_curb,
        "pink": m_pink,
        "white": m_white,
        "yellow": m_yellow,
        "clover": m_clover,
        "wood": m_wood,
        "momo": m_momo,
        "sparkle": m_sparkle
    }

# ==============================================================================
# 2. MODULAR MESH GENERATORS (Clean, High Quality Stylized PBR)
# ==============================================================================

def build_straight_hedge_block(name, length=1.8, width=0.55, height=1.35, mats=None):
    """Creates a clean, solid, rounded rectangular hedge block with organic beveled edges."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (length, width, height)
    bpy.ops.object.transform_apply(scale=True)
    obj.location.z = height / 2.0
    bpy.ops.object.transform_apply(location=True)
    
    # Bevel modifier for rich rounded cushion corners
    bevel = obj.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.16
    bevel.segments = 3
    bevel.limit_method = 'NONE'
    
    # Subdivision surface for organic softness
    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    
    bpy.ops.object.shade_smooth()
    if mats:
        obj.data.materials.append(mats["hedge"])
    return obj

def create_flower_sprig(name, petal_color='pink', mats=None):
    """Creates a cute 5-petal stylized daisy with golden pistil center and green leaf."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)

    # 5 Petals
    p_mat = mats["pink"] if petal_color == 'pink' else mats["white"]
    for i in range(5):
        angle = i * (2.0 * math.pi / 5.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, segments=12, ring_count=8)
        pet = bpy.context.active_object
        pet.scale = (0.7, 1.25, 0.35)
        rad = 0.085
        pet.location = (rad * math.cos(angle), rad * math.sin(angle), 0.02)
        pet.rotation_euler = (0, 0, angle + math.pi/2)
        pet.data.materials.append(p_mat)
        pet.parent = root
        bpy.ops.object.shade_smooth()

    # Center Pistil
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, segments=12, ring_count=8)
    pistil = bpy.context.active_object
    pistil.scale = (1.0, 1.0, 0.6)
    pistil.location = (0, 0, 0.04)
    pistil.data.materials.append(mats["yellow"])
    pistil.parent = root
    bpy.ops.object.shade_smooth()

    # Green Leaf
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=12, ring_count=8)
    leaf = bpy.context.active_object
    leaf.scale = (0.6, 1.3, 0.25)
    leaf.location = (0.12, -0.06, -0.01)
    leaf.rotation_euler = (math.radians(10), math.radians(-15), math.radians(45))
    leaf.data.materials.append(mats["clover"])
    leaf.parent = root
    bpy.ops.object.shade_smooth()

    return root

def create_grass_tuft_prototype(name, mats=None):
    """Creates a stylized curved 3D grass blade cluster for instancing."""
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 4
    curve_data.bevel_depth = 0.035
    curve_data.bevel_resolution = 3
    curve_data.use_fill_caps = True

    # 6 curved blades radiating outwards
    angles = [0, 60, 120, 180, 240, 300]
    heights = [0.42, 0.48, 0.38, 0.45, 0.36, 0.44]
    bends = [0.18, 0.22, 0.16, 0.20, 0.15, 0.21]

    for a_deg, h, b in zip(angles, heights, bends):
        rad = math.radians(a_deg)
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        # Root
        spline.bezier_points[0].co = Vector((0.02 * math.cos(rad), 0.02 * math.sin(rad), 0.0))
        spline.bezier_points[0].radius = 1.0
        # Mid
        spline.bezier_points[1].co = Vector((0.08 * math.cos(rad), 0.08 * math.sin(rad), h * 0.55))
        spline.bezier_points[1].radius = 0.65
        # Tip
        spline.bezier_points[2].co = Vector(((0.08 + b) * math.cos(rad), ((0.08 + b)) * math.sin(rad), h))
        spline.bezier_points[2].radius = 0.08
        for bp in spline.bezier_points:
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

    c_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(c_obj)
    bpy.context.view_layer.objects.active = c_obj
    c_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    m_obj = bpy.context.active_object
    if mats:
        m_obj.data.materials.append(mats["grass"])
    bpy.ops.object.shade_smooth()
    return m_obj

def build_leaf_gate(mats):
    """Builds the living Leaf Gate at exit matching Reference 4."""
    root = bpy.data.objects.new("Leaf_Gate_Master", None)
    bpy.context.collection.objects.link(root)
    root.location = (0.0, 5.75, 0.0)

    # 1. Two Wooden Uprights
    for side, x in [("L", -1.1), ("R", 1.1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.4, vertices=16)
        post = bpy.context.active_object
        post.name = f"gate_post_{side}"
        post.location = (x, 0, 1.2)
        post.data.materials.append(mats["wood"])
        post.parent = root
        bpy.ops.object.shade_smooth()

        # Stone Plinth Base
        bpy.ops.mesh.primitive_cube_add(size=0.55)
        plinth = bpy.context.active_object
        plinth.name = f"gate_plinth_{side}"
        plinth.location = (x, 0, 0.22)
        plinth.scale = (1.0, 1.0, 0.8)
        plinth.data.materials.append(mats["curb"])
        plinth.parent = root
        bevel = plinth.modifiers.new("Bevel", 'BEVEL')
        bevel.width = 0.08
        bpy.ops.object.shade_smooth()

    # 2. Wooden Arch Lintel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=2.4, vertices=16)
    lintel = bpy.context.active_object
    lintel.name = "gate_lintel"
    lintel.location = (0, 0, 2.35)
    lintel.rotation_euler = (0, math.radians(90), 0)
    lintel.data.materials.append(mats["wood"])
    lintel.parent = root
    bpy.ops.object.shade_smooth()

    # 3. Glowing Golden Momo Crest in Center of Arch
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, segments=20, ring_count=16)
    crest = bpy.context.active_object
    crest.name = "gate_momo_crest"
    crest.location = (0, 0, 2.35)
    crest.scale = (1.1, 0.8, 1.0)
    crest.data.materials.append(mats["momo"])
    crest.parent = root
    bpy.ops.object.shade_smooth()

    # 4. Glorious Tiered Leaf Canopy
    leaf_clusters = [
        # Top crest
        {"loc": (0, 0, 2.85), "scale": (0.85, 0.65, 0.45)},
        {"loc": (-0.45, 0, 2.75), "scale": (0.75, 0.60, 0.40)},
        {"loc": (0.45, 0, 2.75), "scale": (0.75, 0.60, 0.40)},
        {"loc": (-0.95, 0, 2.55), "scale": (0.70, 0.55, 0.38)},
        {"loc": (0.95, 0, 2.55), "scale": (0.70, 0.55, 0.38)},
        {"loc": (-1.35, 0, 2.25), "scale": (0.60, 0.50, 0.35)},
        {"loc": (1.35, 0, 2.25), "scale": (0.60, 0.50, 0.35)},
    ]
    for i, lc in enumerate(leaf_clusters):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, segments=16, ring_count=12)
        lobe = bpy.context.active_object
        lobe.name = f"canopy_leaf_{i+1}"
        lobe.location = lc["loc"]
        lobe.scale = lc["scale"]
        lobe.data.materials.append(mats["clover"])
        lobe.parent = root
        bpy.ops.object.shade_smooth()

    # Blooming Gate Flowers
    f1 = create_flower_sprig("gate_fl_1", petal_color='pink', mats=mats)
    f1.location = (-0.75, -0.25, 2.65)
    f1.parent = root
    f2 = create_flower_sprig("gate_fl_2", petal_color='white', mats=mats)
    f2.location = (0.75, -0.25, 2.65)
    f2.parent = root

    return root

def build_momo_collectible(mats):
    """Creates the golden glowing Momo Dumpling on leafy pedestal matching Ref 4."""
    root = bpy.data.objects.new("Momo_Collectible_Master", None)
    bpy.context.collection.objects.link(root)
    root.location = (2.2, 0.0, 0.0)

    # 1. Round Stone Pedestal
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.25, vertices=24)
    ped = bpy.context.active_object
    ped.name = "momo_pedestal"
    ped.location = (0, 0, 0.125)
    ped.data.materials.append(mats["curb"])
    ped.parent = root
    bevel = ped.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.05
    bpy.ops.object.shade_smooth()

    # 2. Leaf Ring Under Dumpling
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, segments=12, ring_count=8)
        lf = bpy.context.active_object
        lf.scale = (0.8, 1.4, 0.3)
        rad = 0.28
        lf.location = (rad * math.cos(ang), rad * math.sin(ang), 0.22)
        lf.rotation_euler = (0, 0, ang + math.pi/2)
        lf.data.materials.append(mats["clover"])
        lf.parent = root
        bpy.ops.object.shade_smooth()

    # 3. Plump Golden Dumpling
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, segments=24, ring_count=18)
    dumpling = bpy.context.active_object
    dumpling.name = "momo_dumpling"
    dumpling.location = (0, 0, 0.52)
    dumpling.scale = (1.15, 1.15, 0.90)
    dumpling.data.materials.append(mats["momo"])
    dumpling.parent = root
    sub = dumpling.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    bpy.ops.object.shade_smooth()

    # Dumpling Top Swirl Pinch
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.10, radius2=0.01, depth=0.18)
    swirl = bpy.context.active_object
    swirl.name = "momo_swirl"
    swirl.location = (0, 0, 0.82)
    swirl.data.materials.append(mats["momo"])
    swirl.parent = root
    bpy.ops.object.shade_smooth()

    # 4. Floating Golden Sparkle Stars
    sparkle_coords = [
        (-0.45, -0.25, 0.85),
        (0.48, -0.20, 0.92),
        (0.0, 0.45, 1.05),
        (-0.35, 0.35, 0.65),
    ]
    for j, sc in enumerate(sparkle_coords):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=10, ring_count=8)
        spk = bpy.context.active_object
        spk.name = f"sparkle_{j+1}"
        spk.location = sc
        spk.data.materials.append(mats["sparkle"])
        spk.parent = root

    # Point light for golden ambient glow
    pt = bpy.data.lights.new("Momo_Inner_Glow", 'POINT')
    pt.energy = 45.0
    pt.color = (1.0, 0.85, 0.45)
    pt.shadow_soft_size = 0.4
    pt_obj = bpy.data.objects.new("Momo_Inner_Glow", pt)
    pt_obj.location = (0, 0, 0.6)
    bpy.context.collection.objects.link(pt_obj)
    pt_obj.parent = root

    return root

def build_puffy_cloud_tree(name, position=(0,0,0), mats=None):
    """Creates a stylized cedar/cloud tree framing the diorama corners."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = position

    # Wooden Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=3.2, vertices=16)
    trunk = bpy.context.active_object
    trunk.location = (0, 0, 1.6)
    trunk.data.materials.append(mats["wood"])
    trunk.parent = root
    bpy.ops.object.shade_smooth()

    # Fluffy Foliage Lobes (Multi-tiered cloud clusters)
    lobes = [
        {"loc": (0, 0, 3.4), "scale": (1.8, 1.8, 1.2)},
        {"loc": (-0.6, 0.4, 4.1), "scale": (1.5, 1.4, 1.1)},
        {"loc": (0.5, -0.4, 4.3), "scale": (1.5, 1.5, 1.1)},
        {"loc": (0, 0, 5.0), "scale": (1.2, 1.2, 1.0)},
    ]
    for i, lb in enumerate(lobes):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=20, ring_count=16)
        fol = bpy.context.active_object
        fol.name = f"{name}_lobe_{i+1}"
        fol.location = lb["loc"]
        fol.scale = lb["scale"]
        fol.data.materials.append(mats["hedge"])
        fol.parent = root
        sub = fol.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        bpy.ops.object.shade_smooth()

    return root

# ==============================================================================
# 3. MASTER DIORAMA ASSEMBLY (12x12 Maze Plan from Ref 4 Panel 2)
# ==============================================================================

def build_master_environment():
    reset_scene()
    mats = create_environment_materials()

    master_col = bpy.context.collection

    # 1. Base Meadow Floor & Raised Diorama Garden Bed
    # Meadow base
    bpy.ops.mesh.primitive_plane_add(size=32.0)
    meadow = bpy.context.active_object
    meadow.name = "meadow_ground"
    meadow.location.z = -0.40
    meadow.data.materials.append(mats["ground"])

    # Raised Terracotta Curb (Holding the 12x12 maze island)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    curb = bpy.context.active_object
    curb.name = "raised_garden_bed"
    # 12 cells * 1.0m + outer borders = ~13.2m x 13.2m, height 0.42m
    curb.scale = (13.6, 13.6, 0.42)
    curb.location = (0, 0, -0.21)
    bpy.ops.object.transform_apply(scale=True, location=True)
    curb.data.materials.append(mats["curb"])
    c_bev = curb.modifiers.new("Bevel", 'BEVEL')
    c_bev.width = 0.22
    c_bev.segments = 3
    bpy.ops.object.shade_smooth()

    # Maze Lawn Ground Plane (Inside raised bed)
    bpy.ops.mesh.primitive_plane_add(size=13.0)
    lawn = bpy.context.active_object
    lawn.name = "maze_inner_lawn"
    lawn.location.z = 0.005
    lawn.data.materials.append(mats["ground"])

    # 2. Approved 12x12 Maze Walls (Reference 4 Panel 2 Layout)
    # Wall segments defined as (x, y, length_x, length_y)
    # Cell spacing = 1.0m, wall height = 1.35m, wall width = 0.55m
    wall_segments = [
        # Perimeter Walls (Outer Square Border)
        # North Wall with Gate Opening in Center (Exit gap at x in [-1.1, 1.1])
        {"x": -3.5, "y": 5.75, "sx": 4.8, "sy": 0.55},
        {"x":  3.5, "y": 5.75, "sx": 4.8, "sy": 0.55},
        # South Wall (Continuous)
        {"x":  0.0, "y": -5.75, "sx": 12.0, "sy": 0.55},
        # West Wall (Continuous)
        {"x": -5.75, "y":  0.0, "sx": 0.55, "sy": 12.0},
        # East Wall (Continuous)
        {"x":  5.75, "y":  0.0, "sx": 0.55, "sy": 12.0},

        # Interior Maze Corridors (Faithfully matching Ref 4 Panel 2 Top-Down Plan)
        # Horizontal Interior Corridors
        {"x": -2.5, "y":  3.8, "sx": 4.2, "sy": 0.55},
        {"x":  2.8, "y":  3.8, "sx": 3.6, "sy": 0.55},
        {"x": -1.2, "y":  1.9, "sx": 3.2, "sy": 0.55},
        {"x":  3.0, "y":  1.9, "sx": 3.4, "sy": 0.55},
        {"x": -3.2, "y": -0.2, "sx": 3.8, "sy": 0.55},
        {"x":  1.8, "y": -0.2, "sx": 4.2, "sy": 0.55},
        {"x": -1.8, "y": -2.1, "sx": 4.5, "sy": 0.55},
        {"x":  2.5, "y": -2.1, "sx": 3.8, "sy": 0.55},
        {"x": -0.5, "y": -4.0, "sx": 6.5, "sy": 0.55},

        # Vertical Interior Corridors
        {"x": -3.8, "y":  2.0, "sx": 0.55, "sy": 3.2},
        {"x": -1.8, "y": -0.5, "sx": 0.55, "sy": 3.0},
        {"x":  0.2, "y":  3.0, "sx": 0.55, "sy": 2.2},
        {"x":  0.2, "y": -1.2, "sx": 0.55, "sy": 2.2},
        {"x":  1.9, "y":  2.8, "sx": 0.55, "sy": 2.2},
        {"x":  3.8, "y": -1.2, "sx": 0.55, "sy": 2.8},
        {"x": -3.8, "y": -2.8, "sx": 0.55, "sy": 2.2},
    ]

    for idx, ws in enumerate(wall_segments):
        build_straight_hedge_block(
            name=f"Hedge_Wall_{idx+1}",
            length=ws["sx"],
            width=ws["sy"],
            height=1.35,
            mats=mats
        ).location = (ws["x"], ws["y"], 0.0)

    # 3. Instanced 3D Grass Carpet
    # Create grass prototype
    grass_proto = create_grass_tuft_prototype("Grass_Blade_Proto", mats=mats)
    grass_proto.location = (0, 0, -20.0) # Hide prototype below scene

    # Scatter 1,400 instanced grass tufts inside pathways and around meadow
    random.seed(42)
    grass_count = 0
    # Pathways bounds: x in [-5.2, 5.2], y in [-5.2, 5.2]
    for _ in range(1200):
        gx = random.uniform(-5.2, 5.2)
        gy = random.uniform(-5.2, 5.2)
        # Avoid putting grass inside solid hedge walls
        in_wall = False
        for ws in wall_segments:
            hwx = ws["sx"] / 2.0 + 0.15
            hwy = ws["sy"] / 2.0 + 0.15
            if (ws["x"] - hwx <= gx <= ws["x"] + hwx) and (ws["y"] - hwy <= gy <= ws["y"] + hwy):
                in_wall = True
                break
        if not in_wall:
            g_inst = grass_proto.copy()
            g_inst.name = f"Grass_Tuft_{grass_count+1}"
            g_inst.location = (gx, gy, 0.0)
            g_inst.scale = (random.uniform(0.65, 1.1), random.uniform(0.65, 1.1), random.uniform(0.7, 1.25))
            g_inst.rotation_euler.z = random.uniform(0, 2.0 * math.pi)
            master_col.objects.link(g_inst)
            grass_count += 1

    # Outer meadow grass
    for _ in range(400):
        gx = random.uniform(-8.5, 8.5)
        gy = random.uniform(-8.5, 8.5)
        if abs(gx) > 6.0 or abs(gy) > 6.0:
            g_inst = grass_proto.copy()
            g_inst.name = f"Meadow_Grass_{grass_count+1}"
            g_inst.location = (gx, gy, -0.40)
            g_inst.scale = (random.uniform(0.8, 1.4), random.uniform(0.8, 1.4), random.uniform(0.8, 1.5))
            g_inst.rotation_euler.z = random.uniform(0, 2.0 * math.pi)
            master_col.objects.link(g_inst)
            grass_count += 1

    # 4. Blooming Flower & Clover Clusters on Hedges and Pathways
    flower_coords = [
        # Along hedge tops and junctions
        {"pos": (-3.8, 5.8, 1.35), "col": "pink"},
        {"pos": ( 3.8, 5.8, 1.35), "col": "white"},
        {"pos": (-5.8, 3.8, 1.35), "col": "pink"},
        {"pos": ( 5.8, 3.8, 1.35), "col": "white"},
        {"pos": (-5.8, -3.8, 1.35), "col": "white"},
        {"pos": ( 5.8, -3.8, 1.35), "col": "pink"},
        {"pos": (-2.5, 3.8, 1.35), "col": "pink"},
        {"pos": ( 2.8, 3.8, 1.35), "col": "white"},
        {"pos": (-1.2, 1.9, 1.35), "col": "white"},
        {"pos": ( 3.0, 1.9, 1.35), "col": "pink"},
        {"pos": (-3.2, -0.2, 1.35), "col": "pink"},
        {"pos": ( 1.8, -0.2, 1.35), "col": "white"},
        {"pos": (-1.8, -2.1, 1.35), "col": "pink"},
        {"pos": ( 2.5, -2.1, 1.35), "col": "white"},
        {"pos": (-0.5, -4.0, 1.35), "col": "pink"},
        # On pathway ground
        {"pos": (-4.5, -4.5, 0.0), "col": "white"},
        {"pos": ( 4.5, -4.5, 0.0), "col": "pink"},
        {"pos": (-4.5,  4.5, 0.0), "col": "pink"},
        {"pos": ( 4.5,  4.5, 0.0), "col": "white"},
        {"pos": ( 0.0, -2.8, 0.0), "col": "pink"},
        {"pos": (-2.0,  0.8, 0.0), "col": "white"},
    ]
    for idx, fc in enumerate(flower_coords):
        fl = create_flower_sprig(f"Flower_Deco_{idx+1}", petal_color=fc["col"], mats=mats)
        fl.location = fc["pos"]
        fl.scale = (random.uniform(0.9, 1.3), random.uniform(0.9, 1.3), random.uniform(0.9, 1.3))
        fl.rotation_euler.z = random.uniform(0, 2 * math.pi)

    # 5. Build Key Landmarks: Leaf Gate, Momo Pedestal, Framing Trees
    gate = build_leaf_gate(mats)
    momo_ped = build_momo_collectible(mats)

    # 4 Framing Cloud Trees in Outer Corners
    tree_positions = [
        {"name": "Tree_NW", "pos": (-7.8,  7.8, -0.4)},
        {"name": "Tree_NE", "pos": ( 7.8,  7.8, -0.4)},
        {"name": "Tree_SW", "pos": (-8.2, -7.5, -0.4)},
        {"name": "Tree_SE", "pos": ( 8.2, -7.5, -0.4)},
    ]
    for tp in tree_positions:
        build_puffy_cloud_tree(tp["name"], position=tp["pos"], mats=mats)

    # 6. Characters in Corridor Action
    # Import or link Golumolu v13 leaping forward towards Momo dumpling
    # Start position: central open corridor at (0.0, -0.8, 0.0)
    # We load Golumolu mesh from validated blend file
    try:
        with bpy.data.libraries.load("D:/Projects/MOMO MAZE/BlenderSources/scenes/golumolu_validated.blend") as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if "Golumolu" in name or "golumolu" in name]
        for obj in data_to.objects:
            if obj:
                master_col.objects.link(obj)
                if obj.name == "Golumolu_v13_Master":
                    obj.location = (0.2, -0.8, 0.25)
                    obj.scale = (0.46, 0.46, 0.46)
                    # Running towards +X/+Y Momo dumpling
                    obj.rotation_euler = (math.radians(12), 0, math.radians(-35))
                    print("  ✓ Golumolu v13 positioned in central maze corridor")
    except Exception as e:
        print(f"Notice loading Golumolu: {e}")

    # Load the 3 Spirits floating in corridors
    try:
        with bpy.data.libraries.load("D:/Projects/MOMO MAZE/BlenderSources/scenes/ghosts_validated.blend") as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if "Spirit_" in name and "Root" in name]
        for s_root in data_to.objects:
            if s_root:
                master_col.objects.link(s_root)
                # Position the 3 spirits in maze corridors
                if "Follower" in s_root.name:
                    s_root.location = (-2.8, 0.8, 0.75)
                    s_root.scale = (0.42, 0.42, 0.42)
                    s_root.rotation_euler = (0, 0, math.radians(-40))
                elif "Cutter" in s_root.name:
                    s_root.location = (3.2, 3.0, 0.85)
                    s_root.scale = (0.42, 0.42, 0.42)
                    s_root.rotation_euler = (0, 0, math.radians(135))
                elif "Wanderer" in s_root.name:
                    s_root.location = (-2.5, -3.2, 0.70)
                    s_root.scale = (0.40, 0.40, 0.40)
                    s_root.rotation_euler = (0, 0, math.radians(25))
        print("  ✓ Spirits positioned gracefully in corridors")
    except Exception as e:
        print(f"Notice loading Spirits: {e}")

    # Save Blend file
    blend_path = "D:/Projects/MOMO MAZE/BlenderSources/scenes/maze_beauty_environment.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  ✓ Saved Master Diorama Blend -> {blend_path}")

    return master_col

# ==============================================================================
# 4. LIGHTING & RENDERING (Faithful to Ref 4 Beauty View & Top-Down Plan)
# ==============================================================================

def render_environment_views(col):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

    # 1. Warm Golden Hour Atmosphere
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    # Soft warm sunny sky
    bg.inputs["Color"].default_value = (0.92, 0.95, 0.98, 1.0)
    bg.inputs["Strength"].default_value = 0.85

    # Golden Sun Key Light (Warm late afternoon sunlight from back-left)
    sun = bpy.data.lights.new("Sun_Golden_Key", 'SUN')
    sun.energy = 4.2
    sun.color = (1.0, 0.93, 0.82)
    sun.angle = math.radians(12)
    sun_obj = bpy.data.objects.new("Sun_Golden_Key", sun)
    sun_obj.rotation_euler = (math.radians(50), math.radians(22), math.radians(-38))
    col.objects.link(sun_obj)

    # Soft Sky Fill Light
    fill = bpy.data.lights.new("Sky_Fill", 'SUN')
    fill.energy = 1.8
    fill.color = (0.84, 0.92, 1.0)
    fill.angle = math.radians(25)
    fill_obj = bpy.data.objects.new("Sky_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    col.objects.link(fill_obj)

    # Warm Golden Rim Light
    rim = bpy.data.lights.new("Rim_Light", 'POINT')
    rim.color = (1.0, 0.85, 0.65)
    rim.energy = 240.0
    rim.shadow_soft_size = 1.2
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (0.5, 7.5, 6.5)
    col.objects.link(rim_obj)

    # --------------------------------------------------------------------------
    # VIEW 1: Beauty View - Gameplay Angle (Faithful to Ref 4 Panel 1)
    # --------------------------------------------------------------------------
    target_empty = bpy.data.objects.new("Cam_Target", None)
    target_empty.location = (0.0, 0.2, 0.3)
    col.objects.link(target_empty)

    cam_data = bpy.data.cameras.new("Cam_Beauty_Diorama")
    cam_data.type = 'PERSP'
    cam_data.lens = 72 # Moderate telephoto for perfect isometric feel without wide-angle distortion
    cam_obj = bpy.data.objects.new("Cam_Beauty_Diorama", cam_data)
    # Distance ~25m, pitch ~46 deg, yaw ~32 deg
    cam_obj.location = (-13.5, -18.5, 17.5)
    col.objects.link(cam_obj)

    cam_track = cam_obj.constraints.new(type='TRACK_TO')
    cam_track.target = target_empty
    cam_track.track_axis = 'TRACK_NEGATIVE_Z'
    cam_track.up_axis = 'UP_Y'

    scene.camera = cam_obj
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    beauty_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_beauty_view_v8_master.png"
    scene.render.filepath = beauty_out
    print(f"Rendering Master Beauty View v8 (1920x1080)...")
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Beauty View -> {beauty_out}")

    # --------------------------------------------------------------------------
    # VIEW 2: Orthographic Top-Down Layout (Faithful to Ref 4 Panel 2)
    # --------------------------------------------------------------------------
    cam_data_top = bpy.data.cameras.new("Cam_TopDown")
    cam_data_top.type = 'ORTHO'
    cam_data_top.ortho_scale = 14.8
    cam_top_obj = bpy.data.objects.new("Cam_TopDown", cam_data_top)
    cam_top_obj.location = (0, 0, 18.0)
    cam_top_obj.rotation_euler = (0, 0, 0)
    col.objects.link(cam_top_obj)

    scene.camera = cam_top_obj
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    top_out = "D:/Projects/MOMO MAZE/BlenderSources/renders/environment/maze_topdown_plan_v8.png"
    scene.render.filepath = top_out
    print(f"Rendering Master Top-Down Plan v8 (1200x1200)...")
    bpy.ops.render.render(write_still=True)
    print(f"  ✓ Rendered Top-Down Plan -> {top_out}")

if __name__ == "__main__":
    print("==================================================")
    print("Building Definitive Grassy & Fluffy Maze Diorama v8")
    print("==================================================")
    col = build_master_environment()
    render_environment_views(col)
    print("Master Diorama v8 build and renders complete!")
