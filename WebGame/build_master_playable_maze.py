"""
build_master_playable_maze.py
Builds the 100% faithful, playable 12x12 Master Maze for MOMO MAZE.
Matches Ref 4 Panel (1) & Panel (2) cell-for-cell at cellSize = 2.0m.
"""

import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Color

def run():
    # 1. Reset scene cleanly
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras, bpy.data.images):
        for item in b:
            b.remove(item)

    scene = bpy.context.scene
    col = bpy.data.collections.new("Playable_Master_Maze")
    scene.collection.children.link(col)

    # 12x12 Master Grid matching Ref 4 Panel 2:
    # 1 = Hedge Wall, 0 = Open Walkable Path, 2 = Leaf Gate Exit
    grid = [
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1],  # Row 0 (North, Leaf Gate at 8,9)
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # Row 1 (Top open corridor under gate)
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],  # Row 2
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1],  # Row 3 (Loop around hook)
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],  # Row 4 (Cross connection)
        [1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1],  # Row 5 (Mid divider)
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],  # Row 6 (Golden Momo Chamber at 8,6)
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],  # Row 7
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1],  # Row 8
        [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],  # Row 9
        [1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1],  # Row 10 (Player start at 1,10)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]   # Row 11 (South perimeter)
    ]

    size = 12
    cell_size = 2.0
    offset = (size - 1) / 2.0 # 5.5

    def get_world(gx, gy):
        return (gx - offset) * cell_size, (gy - offset) * cell_size

    # =========================================================================
    # Materials
    # =========================================================================
    def make_mat(name, color, roughness=0.6, metalness=0.0, emissive=(0,0,0,1), emissive_strength=0.0):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metalness
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emissive
            bsdf.inputs["Emission Strength"].default_value = emissive_strength
        return mat

    # Stylized living hedge: vibrant garden green with warm lime highlights
    mat_hedge = make_mat("M_Living_Hedge", (0.35, 0.72, 0.20, 1.0), roughness=0.65)
    mat_hedge_dark = make_mat("M_Hedge_Base", (0.22, 0.50, 0.12, 1.0), roughness=0.75)
    mat_ground = make_mat("M_Garden_Ground", (0.42, 0.68, 0.22, 1.0), roughness=0.85)
    mat_cobble = make_mat("M_Cobble_Path", (0.85, 0.80, 0.70, 1.0), roughness=0.70)
    mat_curb = make_mat("M_Terracotta_Curb", (0.76, 0.52, 0.38, 1.0), roughness=0.70)
    mat_wood = make_mat("M_Cedar_Wood", (0.55, 0.38, 0.24, 1.0), roughness=0.65)
    mat_gate_leaf = make_mat("M_Gate_Canopy", (0.28, 0.65, 0.18, 1.0), roughness=0.60)
    mat_flower_pink = make_mat("M_Flower_Pink", (1.0, 0.55, 0.68, 1.0), roughness=0.40)
    mat_flower_white = make_mat("M_Flower_White", (0.98, 0.98, 0.95, 1.0), roughness=0.40)
    mat_flower_yellow = make_mat("M_Flower_Yellow", (1.0, 0.85, 0.18, 1.0), roughness=0.35)
    mat_momo_gold = make_mat("M_Golden_Momo", (1.0, 0.88, 0.45, 1.0), roughness=0.30, emissive=(1.0, 0.82, 0.30, 1.0), emissive_strength=1.8)
    mat_sparkle = make_mat("M_Gold_Sparkle", (1.0, 0.95, 0.50, 1.0), roughness=0.20, emissive=(1.0, 0.95, 0.50, 1.0), emissive_strength=5.0)

    # =========================================================================
    # 1. Base Garden Bed & Cobblestone Path Floor
    # =========================================================================
    # Raised Terracotta Curb (outer retaining wall)
    total_span = size * cell_size # 24m
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    curb = bpy.context.active_object
    curb.name = "SM_Garden_Retaining_Border"
    curb.scale = (total_span + 1.6, total_span + 1.6, 0.45)
    curb.location = (0, 0, -0.225)
    bpy.ops.object.transform_apply(scale=True, location=True)
    curb.data.materials.append(mat_curb)
    bev = curb.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.28
    bev.segments = 3
    bpy.ops.object.shade_smooth()
    col.objects.link(curb)

    # Base Lawn Ground
    bpy.ops.mesh.primitive_plane_add(size=total_span + 1.2)
    lawn = bpy.context.active_object
    lawn.name = "SM_Meadow_Lawn"
    lawn.location = (0, 0, 0.0)
    lawn.data.materials.append(mat_ground)
    col.objects.link(lawn)

    # Paved Stepping Stone / Cobblestone Path Tiles for walkable cells
    for gy in range(size):
        for gx in range(size):
            if grid[gy][gx] in (0, 2):
                wx, wz = get_world(gx, gy)
                # Create a rounded square paver tile
                bpy.ops.mesh.primitive_cube_add(size=1.0)
                tile = bpy.context.active_object
                tile.name = f"Path_Tile_{gx}_{gy}"
                tile.scale = (cell_size * 0.94, cell_size * 0.94, 0.04)
                tile.location = (wx, wz, 0.02)
                bpy.ops.object.transform_apply(scale=True, location=True)
                tile.data.materials.append(mat_cobble)
                t_bev = tile.modifiers.new("Bevel", 'BEVEL')
                t_bev.width = 0.08
                bpy.ops.object.shade_smooth()
                col.objects.link(tile)

    # =========================================================================
    # 2. Living Hedge Walls (1:1 with Grid, Seamless Merged Blocks)
    # =========================================================================
    # Wall dimensions:
    # Each wall cell has width = 1.05m (or spans 2.0m when adjacent).
    # To make corridors 100% open and spacious:
    # A single wall cell has width = 1.15m, height = 1.45m.
    # When adjacent to another wall cell, it seamlessly connects to form contiguous runs.
    hedge_height = 1.45
    wall_thickness = 1.15

    hedge_boxes = []

    # Find maximal horizontal and vertical wall runs to create clean seamless geometry
    # First, mark which cells are walls
    wall_cells = set()
    for gy in range(size):
        for gx in range(size):
            if grid[gy][gx] == 1:
                wall_cells.add((gx, gy))

    # Build individual rounded hedge cubes for every wall cell, slightly overlapping so they fuse seamlessly
    for (gx, gy) in wall_cells:
        wx, wz = get_world(gx, gy)

        # Check adjacent neighbors
        has_n = (gx, gy - 1) in wall_cells
        has_s = (gx, gy + 1) in wall_cells
        has_w = (gx - 1, gy) in wall_cells
        has_e = (gx + 1, gy) in wall_cells

        # Compute dimension to bridge seamlessly with neighbors
        sx = cell_size if (has_w or has_e) else wall_thickness
        sy = cell_size if (has_n or has_s) else wall_thickness

        # If it has only one neighbor, extend half-way to meet it
        offset_x = 0.0
        offset_y = 0.0
        if has_w and not has_e:
            sx = (cell_size + wall_thickness) / 2.0
            offset_x = - (cell_size - wall_thickness) / 4.0
        elif has_e and not has_w:
            sx = (cell_size + wall_thickness) / 2.0
            offset_x = + (cell_size - wall_thickness) / 4.0

        if has_n and not has_s:
            sy = (cell_size + wall_thickness) / 2.0
            offset_y = - (cell_size - wall_thickness) / 4.0
        elif has_s and not has_n:
            sy = (cell_size + wall_thickness) / 2.0
            offset_y = + (cell_size - wall_thickness) / 4.0

        bpy.ops.mesh.primitive_cube_add(size=1.0)
        h = bpy.context.active_object
        h.name = f"Hedge_{gx}_{gy}"
        h.scale = (sx, sy, hedge_height)
        h.location = (wx + offset_x, wz + offset_y, hedge_height / 2.0)
        bpy.ops.object.transform_apply(scale=True, location=True)
        h.data.materials.append(mat_hedge)

        # Soft bevel for rounded living hedge aesthetic
        h_bev = h.modifiers.new("Bevel", 'BEVEL')
        h_bev.width = 0.22
        h_bev.segments = 3
        h_bev.limit_method = 'NONE'
        bpy.ops.object.shade_smooth()
        col.objects.link(h)
        hedge_boxes.append(h)

    # =========================================================================
    # 3. Daisies & Flowers on Hedge Tops (Pink, White, Yellow)
    # =========================================================================
    random.seed(1337)
    flower_count = 0
    # Place flower clusters on top of hedge walls
    for (gx, gy) in sorted(wall_cells):
        if random.random() < 0.45:
            wx, wz = get_world(gx, gy)
            num_flowers = random.randint(1, 3)
            for _ in range(num_flowers):
                fx = wx + random.uniform(-0.35, 0.35)
                fz = wz + random.uniform(-0.35, 0.35)
                fy = hedge_height + 0.02

                is_pink = (random.random() < 0.5)
                p_mat = mat_flower_pink if is_pink else mat_flower_white

                # 5 Petals
                for i in range(5):
                    ang = i * (2.0 * math.pi / 5.0)
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=10, ring_count=6)
                    pet = bpy.context.active_object
                    pet.name = f"Flower_Petal_{flower_count}"
                    pet.scale = (0.7, 1.4, 0.4)
                    rad = 0.08
                    pet.location = (fx + rad * math.cos(ang), fz + rad * math.sin(ang), fy)
                    pet.rotation_euler = (0, 0, ang)
                    pet.data.materials.append(p_mat)
                    bpy.ops.object.shade_smooth()
                    col.objects.link(pet)

                # Center golden pistil
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, segments=10, ring_count=6)
                pis = bpy.context.active_object
                pis.name = f"Flower_Pistil_{flower_count}"
                pis.location = (fx, fz, fy + 0.02)
                pis.scale = (1.0, 1.0, 0.6)
                pis.data.materials.append(mat_flower_yellow)
                bpy.ops.object.shade_smooth()
                col.objects.link(pis)
                flower_count += 1

    # =========================================================================
    # 4. The Grand Leaf Gate Archway (at North exit: Cols 8 & 9, Row 0)
    # =========================================================================
    gate_x, gate_z = get_world(8.5, 0.0) # Center of cols 8 & 9
    gate_root = bpy.data.objects.new("SM_Leaf_Gate_Exit", None)
    gate_root.location = (gate_x, gate_z, 0.0)
    col.objects.link(gate_root)

    # 2 Cedar wood pillars
    for side, px in [("Left", -1.4), ("Right", 1.4)]:
        # Wood pillar
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=2.7, vertices=16)
        pillar = bpy.context.active_object
        pillar.name = f"Gate_Pillar_{side}"
        pillar.location = (gate_x + px, gate_z, 1.35)
        pillar.data.materials.append(mat_wood)
        pillar.parent = gate_root
        bpy.ops.object.shade_smooth()
        col.objects.link(pillar)

        # Stone footing base
        bpy.ops.mesh.primitive_cube_add(size=0.65)
        plinth = bpy.context.active_object
        plinth.name = f"Gate_Plinth_{side}"
        plinth.location = (gate_x + px, gate_z, 0.25)
        plinth.scale = (1.0, 1.0, 0.75)
        plinth.data.materials.append(mat_curb)
        plinth.parent = gate_root
        p_bev = plinth.modifiers.new("Bevel", 'BEVEL')
        p_bev.width = 0.08
        bpy.ops.object.shade_smooth()
        col.objects.link(plinth)

    # Arch Lintel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=3.2, vertices=16)
    lintel = bpy.context.active_object
    lintel.name = "Gate_Lintel"
    lintel.location = (gate_x, gate_z, 2.7)
    lintel.rotation_euler = (0, math.radians(90), 0)
    lintel.data.materials.append(mat_wood)
    lintel.parent = gate_root
    bpy.ops.object.shade_smooth()
    col.objects.link(lintel)

    # Glowing Golden Momo Emblem in center of Arch
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.36, segments=20, ring_count=16)
    crest = bpy.context.active_object
    crest.name = "Gate_Momo_Crest"
    crest.location = (gate_x, gate_z, 2.7)
    crest.scale = (1.1, 0.8, 0.95)
    crest.data.materials.append(mat_momo_gold)
    crest.parent = gate_root
    bpy.ops.object.shade_smooth()
    col.objects.link(crest)

    # Plump Tiered Leaf Canopy Lobes
    canopy_lobes = [
        {"loc": (0, 0, 3.25), "scale": (1.1, 0.8, 0.55)},
        {"loc": (-0.6, 0, 3.10), "scale": (0.9, 0.7, 0.50)},
        {"loc": (0.6, 0, 3.10), "scale": (0.9, 0.7, 0.50)},
        {"loc": (-1.2, 0, 2.85), "scale": (0.8, 0.6, 0.45)},
        {"loc": (1.2, 0, 2.85), "scale": (0.8, 0.6, 0.45)},
        {"loc": (-1.65, 0, 2.50), "scale": (0.7, 0.55, 0.40)},
        {"loc": (1.65, 0, 2.50), "scale": (0.7, 0.55, 0.40)},
    ]
    for idx, cl in enumerate(canopy_lobes):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, segments=16, ring_count=12)
        lobe = bpy.context.active_object
        lobe.name = f"Canopy_Lobe_{idx+1}"
        lobe.location = (gate_x + cl["loc"][0], gate_z + cl["loc"][1], cl["loc"][2])
        lobe.scale = cl["scale"]
        lobe.data.materials.append(mat_gate_leaf)
        lobe.parent = gate_root
        bpy.ops.object.shade_smooth()
        col.objects.link(lobe)

    # =========================================================================
    # 5. Sanctuary of the Golden Momo (at gx = 8, gy = 6)
    # =========================================================================
    shrine_x, shrine_z = get_world(8, 6)
    shrine_root = bpy.data.objects.new("SM_Golden_Momo_Sanctuary", None)
    shrine_root.location = (shrine_x, shrine_z, 0.0)
    col.objects.link(shrine_root)

    # Raised Bamboo Leaf Pedestal
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=0.18, vertices=24)
    ped = bpy.context.active_object
    ped.name = "Shrine_Pedestal"
    ped.location = (shrine_x, shrine_z, 0.09)
    ped.data.materials.append(mat_curb)
    ped.parent = shrine_root
    bpy.ops.object.shade_smooth()
    col.objects.link(ped)

    # 8 Radial Bamboo Steamer Leaves
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, segments=12, ring_count=8)
        lf = bpy.context.active_object
        lf.name = f"Shrine_Leaf_{i+1}"
        lf.scale = (0.7, 1.4, 0.22)
        r_dist = 0.42
        lf.location = (shrine_x + r_dist * math.cos(ang), shrine_z + r_dist * math.sin(ang), 0.16)
        lf.rotation_euler = (0, 0, ang + math.pi/2)
        lf.data.materials.append(mat_gate_leaf)
        lf.parent = shrine_root
        bpy.ops.object.shade_smooth()
        col.objects.link(lf)

    # Plump Glowing Golden Momo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, segments=24, ring_count=18)
    dumpling = bpy.context.active_object
    dumpling.name = "Shrine_Golden_Dumpling"
    dumpling.location = (shrine_x, shrine_z, 0.48)
    dumpling.scale = (1.18, 1.18, 0.88)
    dumpling.data.materials.append(mat_momo_gold)
    dumpling.parent = shrine_root
    bpy.ops.object.shade_smooth()
    col.objects.link(dumpling)

    # Golden swirl top knot
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.14, radius2=0.02, depth=0.22)
    knot = bpy.context.active_object
    knot.name = "Shrine_Golden_Knot"
    knot.location = (shrine_x, shrine_z, 0.84)
    knot.data.materials.append(mat_momo_gold)
    knot.parent = shrine_root
    bpy.ops.object.shade_smooth()
    col.objects.link(knot)

    # 6 Radiant Floating Star Flares
    sparkle_offsets = [
        (-0.55, -0.30, 0.95),
        (0.55, -0.25, 1.05),
        (0.0, 0.55, 1.15),
        (-0.45, 0.40, 0.75),
        (0.48, 0.38, 0.85),
        (0.0, -0.58, 0.90)
    ]
    for idx, sc in enumerate(sparkle_offsets):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, segments=10, ring_count=8)
        spk = bpy.context.active_object
        spk.name = f"Shrine_Sparkle_{idx+1}"
        spk.location = (shrine_x + sc[0], shrine_z + sc[1], sc[2])
        spk.data.materials.append(mat_sparkle)
        spk.parent = shrine_root
        col.objects.link(spk)

    # Inner warm golden point light
    glow_light = bpy.data.lights.new("Shrine_Golden_Light", 'POINT')
    glow_light.energy = 80.0
    glow_light.color = (1.0, 0.82, 0.40)
    glow_obj = bpy.data.objects.new("Shrine_Golden_Light", glow_light)
    glow_obj.location = (shrine_x, shrine_z, 0.65)
    col.objects.link(glow_obj)
    glow_obj.parent = shrine_root

    # =========================================================================
    # 6. Corner Framing Cedar Trees
    # =========================================================================
    corner_coords = [
        (-total_span/2 - 1.2, -total_span/2 - 1.2),
        (total_span/2 + 1.2, -total_span/2 - 1.2),
        (-total_span/2 - 1.2, total_span/2 + 1.2),
        (total_span/2 + 1.2, total_span/2 + 1.2),
    ]
    for idx, (tx, tz) in enumerate(corner_coords):
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=3.2, vertices=16)
        trunk = bpy.context.active_object
        trunk.name = f"Tree_Trunk_{idx+1}"
        trunk.location = (tx, tz, 1.6)
        trunk.data.materials.append(mat_wood)
        bpy.ops.object.shade_smooth()
        col.objects.link(trunk)

        # 3 Puffy Canopy Lobes
        for l_idx, (lx, lz, ly, rad) in enumerate([(0, 0, 3.4, 1.5), (-0.4, 0.3, 4.2, 1.2), (0.4, -0.2, 4.0, 1.3)]):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=16, ring_count=12)
            t_lobe = bpy.context.active_object
            t_lobe.name = f"Tree_Lobe_{idx+1}_{l_idx+1}"
            t_lobe.location = (tx + lx, tz + lz, ly)
            t_lobe.scale = (1.0, 1.0, 0.75)
            t_lobe.data.materials.append(mat_gate_leaf)
            bpy.ops.object.shade_smooth()
            col.objects.link(t_lobe)

    # =========================================================================
    # 7. Lighting & Camera (Matching Ref 4 Warm Golden Hour Sunlight)
    # =========================================================================
    # Sun Light
    sun = bpy.data.lights.new("Sun_Beauty", 'SUN')
    sun.energy = 4.5
    sun.color = (1.0, 0.94, 0.85)
    sun_obj = bpy.data.objects.new("Sun_Beauty", sun)
    sun_obj.location = (15, -20, 25)
    sun_obj.rotation_euler = (math.radians(55), math.radians(15), math.radians(-35))
    col.objects.link(sun_obj)

    # Warm sky fill
    hemi = bpy.data.lights.new("Sky_Fill", 'SUN')
    hemi.energy = 1.2
    hemi.color = (0.75, 0.90, 1.0)
    hemi_obj = bpy.data.objects.new("Sky_Fill", hemi)
    hemi_obj.rotation_euler = (math.radians(180), 0, 0)
    col.objects.link(hemi_obj)

    # Diorama Camera
    cam = bpy.data.cameras.new("Camera_Beauty")
    cam.lens = 42
    cam_obj = bpy.data.objects.new("Camera_Beauty", cam)
    cam_obj.location = (0, 24, 25)
    cam_obj.rotation_euler = (math.radians(48), 0, math.radians(180))
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    # Render settings
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.image_settings.file_format = 'PNG'

    render_path = r"D:\Projects\MOMO MAZE\WebGame\renders\test_maze_playable.png"
    os.makedirs(os.path.dirname(render_path), exist_ok=True)
    scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)
    print("Rendered test beauty image to:", render_path)

    # Export GLTF
    export_glb = r"D:\Projects\MOMO MAZE\WebGame\models\beauty_maze_env.glb"
    os.makedirs(os.path.dirname(export_glb), exist_ok=True)

    # Select all objects in collection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=export_glb,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT',
        export_lights=True,
        export_yup=True
    )
    print("Exported Playable GLB to:", export_glb)

if __name__ == "__main__":
    run()
