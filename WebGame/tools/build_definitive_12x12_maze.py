import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Color

def run():
    print("[MOMO MAZE] Building Definitive 12x12 Living Garden Maze...")

    # Clear existing objects in scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve, do_unlink=True)

    col = bpy.data.collections.get("Collection")
    if not col:
        col = bpy.data.collections.new("Master_Living_Garden_Maze")
        bpy.context.scene.collection.children.link(col)

    # 12x12 Grid Layout matching Reference 4 Top-Down Plan
    # 0 = Open Walkable Path, 1 = Living Hedge Wall, 2 = Leaf Gate Exit, 3 = Golden Momo Sanctuary
    grid = [
        [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # Row 0: North border with Leaf Gate at cols 5,6
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # Row 1: North traverse avenue
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],  # Row 2
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],  # Row 3
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],  # Row 4
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],  # Row 5: Central East-West crossway
        [1, 1, 1, 0, 1, 3, 3, 1, 0, 1, 0, 1],  # Row 6: Golden Momo Sanctuary
        [1, 0, 0, 0, 1, 3, 3, 1, 0, 0, 0, 1],  # Row 7: Approach to Golden Momo
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],  # Row 8
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],  # Row 9: South traverse avenue
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1],  # Row 10: Golumolu Start at (1, 10)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Row 11: South border
    ]

    size = 12
    cell_size = 1.6
    offset = (size - 1) / 2.0  # 5.5

    def get_blender_coords(gx, gy):
        bx = (gx - offset) * cell_size
        by = (offset - gy) * cell_size
        return bx, by

    # -------------------------------------------------------------------------
    # Materials Setup
    # -------------------------------------------------------------------------
    def create_pbr(name, base_color, roughness=0.6, metalness=0.0, emissive=None, emissive_strength=1.0):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metalness
        if emissive and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emissive
            bsdf.inputs["Emission Strength"].default_value = emissive_strength
        return mat

    mat_hedge_main = create_pbr("M_Hedge_Living", (0.26, 0.62, 0.14, 1.0), roughness=0.62)
    mat_hedge_top  = create_pbr("M_Hedge_Crown",  (0.34, 0.74, 0.18, 1.0), roughness=0.55)
    mat_ground     = create_pbr("M_Garden_Ground", (0.35, 0.62, 0.18, 1.0), roughness=0.88)
    mat_outer_lawn = create_pbr("M_Outer_Lawn",   (0.38, 0.68, 0.20, 1.0), roughness=0.90)
    mat_paver      = create_pbr("M_Cobble_Paver",  (0.88, 0.82, 0.72, 1.0), roughness=0.72)
    mat_curb       = create_pbr("M_Terracotta_Curb", (0.75, 0.48, 0.32, 1.0), roughness=0.68)
    mat_stone      = create_pbr("M_Ancient_Stone", (0.78, 0.75, 0.68, 1.0), roughness=0.75)
    mat_flower_pink = create_pbr("M_Flower_Pink",  (1.0, 0.52, 0.66, 1.0), roughness=0.35)
    mat_flower_white = create_pbr("M_Flower_White", (0.98, 0.98, 0.94, 1.0), roughness=0.35)
    mat_flower_yellow = create_pbr("M_Flower_Yellow", (1.0, 0.85, 0.20, 1.0), roughness=0.30)
    mat_leaf_gate  = create_pbr("M_Gate_Canopy",   (0.20, 0.58, 0.12, 1.0), roughness=0.50)
    mat_gold_momo  = create_pbr("M_Golden_Momo",   (1.0, 0.88, 0.48, 1.0), roughness=0.25, emissive=(1.0, 0.82, 0.30, 1.0), emissive_strength=2.5)

    # -------------------------------------------------------------------------
    # 1. Base Meadow Lawn & Terracotta Retaining Border
    # -------------------------------------------------------------------------
    # Surrounding meadow (36m x 36m)
    bpy.ops.mesh.primitive_plane_add(size=38.0)
    meadow = bpy.context.active_object
    meadow.name = "SM_Surrounding_Meadow"
    meadow.location = (0, 0, -0.25)
    meadow.data.materials.append(mat_outer_lawn)

    # Raised Terracotta Curb Wall around the 12x12 garden island
    garden_span = size * cell_size  # 19.2m
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    curb = bpy.context.active_object
    curb.name = "SM_Terracotta_Curb"
    curb.scale = (garden_span + 1.2, garden_span + 1.2, 0.40)
    curb.location = (0, 0, -0.15)
    bpy.ops.object.transform_apply(scale=True, location=True)
    curb.data.materials.append(mat_curb)
    bev = curb.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.22
    bev.segments = 3
    bpy.ops.object.shade_smooth()

    # Garden lawn bed
    bpy.ops.mesh.primitive_plane_add(size=garden_span + 0.8)
    lawn = bpy.context.active_object
    lawn.name = "SM_Garden_Lawn"
    lawn.location = (0, 0, 0.0)
    lawn.data.materials.append(mat_ground)

    # -------------------------------------------------------------------------
    # 2. Walkable Path Cobblestone Pavers
    # -------------------------------------------------------------------------
    for gy in range(size):
        for gx in range(size):
            cell_type = grid[gy][gx]
            if cell_type in (0, 2, 3):
                bx, by = get_blender_coords(gx, gy)
                # Create a rounded cobblestone tile
                bpy.ops.mesh.primitive_cube_add(size=1.0)
                tile = bpy.context.active_object
                tile.name = f"Path_Tile_{gx}_{gy}"
                tile.scale = (cell_size * 0.92, cell_size * 0.92, 0.04)
                tile.location = (bx, by, 0.02)
                bpy.ops.object.transform_apply(scale=True, location=True)
                tile.data.materials.append(mat_paver)
                t_bev = tile.modifiers.new("Bevel", 'BEVEL')
                t_bev.width = 0.08
                t_bev.segments = 2
                bpy.ops.object.shade_smooth()

    # -------------------------------------------------------------------------
    # 3. Fluffy Living Hedge Walls with Overlapping Foliage Crowns & Flowers
    # -------------------------------------------------------------------------
    random.seed(42)

    hedge_height = 1.35
    wall_width = cell_size * 0.96  # 1.54m, overlaps seamlessly with adjacent walls

    for gy in range(size):
        for gx in range(size):
            if grid[gy][gx] == 1:
                bx, by = get_blender_coords(gx, gy)

                # Base hedge body
                bpy.ops.mesh.primitive_cube_add(size=1.0)
                h_body = bpy.context.active_object
                h_body.name = f"Hedge_Block_{gx}_{gy}"
                h_body.scale = (wall_width, wall_width, hedge_height)
                h_body.location = (bx, by, hedge_height / 2.0)
                bpy.ops.object.transform_apply(scale=True, location=True)
                h_body.data.materials.append(mat_hedge_main)
                h_bev = h_body.modifiers.new("Bevel", 'BEVEL')
                h_bev.width = 0.28
                h_bev.segments = 3
                bpy.ops.object.shade_smooth()

                # Add 2 fluffy rounded crown domes on top to create the lush, cloud-like living hedge
                for crown_idx in range(2):
                    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.48)
                    crown = bpy.context.active_object
                    crown.name = f"Hedge_Crown_{gx}_{gy}_{crown_idx}"
                    cx_off = (crown_idx - 0.5) * 0.45 + (random.random() - 0.5) * 0.15
                    cy_off = (random.random() - 0.5) * 0.35
                    crown.scale = (1.1, 1.1, 0.75)
                    crown.location = (bx + cx_off, by + cy_off, hedge_height + 0.18)
                    bpy.ops.object.transform_apply(scale=True, location=True)
                    crown.data.materials.append(mat_hedge_top)
                    bpy.ops.object.shade_smooth()

                # Random daisy flowers sprouting on top edges (matching Ref 1, Ref 4)
                if random.random() < 0.65:
                    num_flowers = random.randint(1, 3)
                    for f_idx in range(num_flowers):
                        fx = bx + (random.random() - 0.5) * 0.8
                        fy = by + (random.random() - 0.5) * 0.8
                        fz = hedge_height + 0.35

                        # Flower petal disc
                        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=0.03)
                        flower = bpy.context.active_object
                        flower.name = f"Flower_{gx}_{gy}_{f_idx}"
                        flower.location = (fx, fy, fz)
                        flower.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), random.uniform(0, math.pi))
                        bpy.ops.object.transform_apply(location=True, rotation=True)
                        flower.data.materials.append(mat_flower_pink if random.random() > 0.4 else mat_flower_white)

                        # Flower yellow center pistil
                        bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=6, radius=0.04)
                        center = bpy.context.active_object
                        center.name = f"Flower_Center_{gx}_{gy}_{f_idx}"
                        center.location = (fx, fy, fz + 0.02)
                        bpy.ops.object.transform_apply(location=True)
                        center.data.materials.append(mat_flower_yellow)

    # -------------------------------------------------------------------------
    # 4. North Leaf Gate Archway (Exit Portal)
    # -------------------------------------------------------------------------
    # Located at Row 0, cols 5 & 6 (center North)
    gate_bx = 0.0
    gate_by = (offset - 0.0) * cell_size  # +8.8m in Blender Y

    # Left Stone Pillar
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    pillar_l = bpy.context.active_object
    pillar_l.name = "LeafGate_Pillar_L"
    pillar_l.scale = (0.55, 0.70, 1.85)
    pillar_l.location = (gate_bx - 1.25, gate_by, 1.85 / 2.0)
    bpy.ops.object.transform_apply(scale=True, location=True)
    pillar_l.data.materials.append(mat_stone)
    p_bev = pillar_l.modifiers.new("Bevel", 'BEVEL')
    p_bev.width = 0.12
    bpy.ops.object.shade_smooth()

    # Right Stone Pillar
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    pillar_r = bpy.context.active_object
    pillar_r.name = "LeafGate_Pillar_R"
    pillar_r.scale = (0.55, 0.70, 1.85)
    pillar_r.location = (gate_bx + 1.25, gate_by, 1.85 / 2.0)
    bpy.ops.object.transform_apply(scale=True, location=True)
    pillar_r.data.materials.append(mat_stone)
    p_bev2 = pillar_r.modifiers.new("Bevel", 'BEVEL')
    p_bev2.width = 0.12
    bpy.ops.object.shade_smooth()

    # Arching Living Leaf Canopy over the top
    bpy.ops.mesh.primitive_torus_add(major_radius=1.25, minor_radius=0.42, major_segments=16, minor_segments=12)
    arch = bpy.context.active_object
    arch.name = "LeafGate_Arch_Canopy"
    arch.scale = (1.0, 0.85, 1.0)
    arch.rotation_euler = (math.pi / 2.0, 0, 0)
    arch.location = (gate_bx, gate_by, 1.85)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
    arch.data.materials.append(mat_leaf_gate)
    bpy.ops.object.shade_smooth()

    # Golden Momo exit beacon suspended in the arch
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=10, radius=0.35)
    gate_momo = bpy.context.active_object
    gate_momo.name = "LeafGate_Beacon_Momo"
    gate_momo.scale = (1.1, 1.1, 0.85)
    gate_momo.location = (gate_bx, gate_by, 1.70)
    bpy.ops.object.transform_apply(scale=True, location=True)
    gate_momo.data.materials.append(mat_gold_momo)
    bpy.ops.object.shade_smooth()

    # -------------------------------------------------------------------------
    # 5. Central Sanctuary of the Golden Momo
    # -------------------------------------------------------------------------
    # Located at gx=5.5, gy=6.5 -> bx = 0.0, by = (5.5 - 6.5) * 1.6 = -1.6m
    sanc_bx = 0.0
    sanc_by = (offset - 6.5) * cell_size  # -1.6m

    # Stepped circular stone pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.35, depth=0.18)
    ped1 = bpy.context.active_object
    ped1.name = "Sanctuary_Pedestal_Base"
    ped1.location = (sanc_bx, sanc_by, 0.09)
    bpy.ops.object.transform_apply(location=True)
    ped1.data.materials.append(mat_stone)
    ped_bev = ped1.modifiers.new("Bevel", 'BEVEL')
    ped_bev.width = 0.04
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.95, depth=0.15)
    ped2 = bpy.context.active_object
    ped2.name = "Sanctuary_Pedestal_Top"
    ped2.location = (sanc_bx, sanc_by, 0.25)
    bpy.ops.object.transform_apply(location=True)
    ped2.data.materials.append(mat_stone)
    bpy.ops.object.shade_smooth()

    # Bamboo steamer basket base
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55, depth=0.12)
    steamer = bpy.context.active_object
    steamer.name = "Sanctuary_Steamer_Basket"
    steamer.location = (sanc_bx, sanc_by, 0.38)
    bpy.ops.object.transform_apply(location=True)
    steamer.data.materials.append(mat_curb)
    bpy.ops.object.shade_smooth()

    # The Golden Momo dumpling itself
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.38)
    gold_momo = bpy.context.active_object
    gold_momo.name = "Sanctuary_Golden_Momo_Mesh"
    gold_momo.scale = (1.15, 1.15, 0.90)
    gold_momo.location = (sanc_bx, sanc_by, 0.62)
    bpy.ops.object.transform_apply(scale=True, location=True)
    gold_momo.data.materials.append(mat_gold_momo)
    bpy.ops.object.shade_smooth()

    # Golden halo aura ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.75, minor_radius=0.03, major_segments=24, minor_segments=8)
    halo = bpy.context.active_object
    halo.name = "Sanctuary_Golden_Halo"
    halo.location = (sanc_bx, sanc_by, 0.68)
    bpy.ops.object.transform_apply(location=True)
    halo.data.materials.append(mat_gold_momo)

    # -------------------------------------------------------------------------
    # 6. Lighting and Camera for Render Verification
    # -------------------------------------------------------------------------
    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(18, -25, 30))
    sun = bpy.context.active_object
    sun.name = "Sun_Warm_Peach"
    sun.data.energy = 4.5
    sun.data.color = (1.0, 0.88, 0.72)
    sun.rotation_euler = (math.radians(48), math.radians(18), math.radians(-38))

    # Cozy isometric camera matching Ref 8-A Gameplay HUD
    bpy.ops.object.camera_add(location=(0, -18.5, 19.5))
    cam = bpy.context.active_object
    cam.name = "Hero_Game_Camera"
    cam.rotation_euler = (math.radians(46), 0, 0)
    cam.data.lens = 45.0
    cam.data.clip_start = 0.5
    cam.data.clip_end = 200.0
    bpy.context.scene.camera = cam

    # Set render resolution
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.film_transparent = False

    # Render verification image
    render_path = "D:/Projects/MOMO MAZE/WebGame/renders/definitive_12x12_maze.png"
    bpy.context.scene.render.filepath = render_path
    print(f"[MOMO MAZE] Rendering preview to {render_path}...")
    bpy.ops.render.render(write_still=True)
    print("[MOMO MAZE] Render complete!")

    # -------------------------------------------------------------------------
    # 7. Export definitive GLB for WebGame & Unreal
    # -------------------------------------------------------------------------
    export_glb_path = "D:/Projects/MOMO MAZE/WebGame/models/beauty_maze.glb"
    print(f"[MOMO MAZE] Exporting master GLB to {export_glb_path}...")
    bpy.ops.export_scene.gltf(
        filepath=export_glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    print("[MOMO MAZE] Export beauty_maze.glb completed successfully!")

if __name__ == "__main__":
    run()
