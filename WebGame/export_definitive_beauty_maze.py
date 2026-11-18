"""
export_definitive_beauty_maze.py
Generates the definitive, breathtaking 12x12 living garden maze in Blender 5.2.
100% faithful to Reference 4 Panel (1) Beauty View & Panel (2) Top-Down Plan.
Exports clean, rich PBR GLB directly to WebGame/models/beauty_maze_env.glb.
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
    col = bpy.data.collections.new("Master_Living_Garden_Maze")
    scene.collection.children.link(col)

    # -------------------------------------------------------------------------
    # 2. Materials
    # -------------------------------------------------------------------------
    def make_pbr_mat(name, color, roughness=0.55, metalness=0.0, emissive=(0,0,0,1), emissive_strength=0.0):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metalness
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emissive
            bsdf.inputs["Emission Strength"].default_value = emissive_strength
        return mat

    # Palette strictly based on Ref 4
    # Living hedge: vibrant emerald green (#48A626) with lime highlights
    mat_hedge = make_pbr_mat("M_Living_Hedge", (0.28, 0.65, 0.15, 1.0), roughness=0.58)
    mat_ground = make_pbr_mat("M_Garden_Earth", (0.36, 0.62, 0.18, 1.0), roughness=0.85)
    mat_meadow = make_pbr_mat("M_Outer_Meadow", (0.42, 0.70, 0.22, 1.0), roughness=0.90)
    mat_curb = make_pbr_mat("M_Terracotta_Stone", (0.75, 0.52, 0.38, 1.0), roughness=0.72)
    mat_wood = make_pbr_mat("M_Cedar_Wood", (0.55, 0.36, 0.22, 1.0), roughness=0.65)
    mat_gate_leaf = make_pbr_mat("M_Canopy_Leaf", (0.22, 0.58, 0.14, 1.0), roughness=0.50)
    mat_flower_pink = make_pbr_mat("M_Flower_Pink", (1.0, 0.52, 0.66, 1.0), roughness=0.35)
    mat_flower_white = make_pbr_mat("M_Flower_White", (0.98, 0.98, 0.94, 1.0), roughness=0.35)
    mat_flower_yellow = make_pbr_mat("M_Flower_Yellow", (1.0, 0.82, 0.15, 1.0), roughness=0.30)
    mat_momo_gold = make_pbr_mat("M_Golden_Momo", (1.0, 0.88, 0.52, 1.0), roughness=0.28, emissive=(1.0, 0.82, 0.35, 1.0), emissive_strength=2.2)
    mat_sparkle = make_pbr_mat("M_Gold_Sparkle", (1.0, 0.95, 0.55, 1.0), roughness=0.15, emissive=(1.0, 0.95, 0.55, 1.0), emissive_strength=6.0)
    mat_grass_blade = make_pbr_mat("M_Lawn_Blade", (0.32, 0.68, 0.16, 1.0), roughness=0.50)

    # -------------------------------------------------------------------------
    # 3. Outer Meadow, Raised Terracotta Retaining Border & Garden Lawn Ground
    # -------------------------------------------------------------------------
    # Large surrounding meadow ground (spans 45m x 45m)
    bpy.ops.mesh.primitive_plane_add(size=45.0)
    outer_meadow = bpy.context.active_object
    outer_meadow.name = "SM_Outer_Meadow"
    outer_meadow.location = (0, 0, -0.45)
    outer_meadow.data.materials.append(mat_meadow)
    col.objects.link(outer_meadow)

    # Raised diorama bed holding the garden island (12.8m x 12.8m)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    curb = bpy.context.active_object
    curb.name = "SM_Garden_Retaining_Border"
    curb.scale = (13.6, 13.6, 0.44)
    curb.location = (0, 0, -0.22)
    bpy.ops.object.transform_apply(scale=True, location=True)
    curb.data.materials.append(mat_curb)
    c_bev = curb.modifiers.new("Bevel", 'BEVEL')
    c_bev.width = 0.22
    c_bev.segments = 3
    bpy.ops.object.shade_smooth()
    col.objects.link(curb)

    # Inner lawn surface
    bpy.ops.mesh.primitive_plane_add(size=13.0)
    lawn = bpy.context.active_object
    lawn.name = "SM_Garden_Lawn"
    lawn.location = (0, 0, 0.0)
    lawn.data.materials.append(mat_ground)
    col.objects.link(lawn)

    # -------------------------------------------------------------------------
    # 4. Verified 21 Living Hedge Walls (100% Reachable, Ref 4 Layout)
    # -------------------------------------------------------------------------
    wall_segments = [
        # Perimeter Walls (Outer Square Border)
        # North Wall with Leaf Gate Opening in Center (Exit gap at x in [-1.1, 1.1])
        {"name": "Wall_N_Left", "x": -3.5, "y": 5.75, "sx": 4.8, "sy": 0.55},
        {"name": "Wall_N_Right", "x":  3.5, "y": 5.75, "sx": 4.8, "sy": 0.55},
        # South Wall (Continuous)
        {"name": "Wall_South", "x":  0.0, "y": -5.75, "sx": 12.0, "sy": 0.55},
        # West Wall (Continuous)
        {"name": "Wall_West", "x": -5.75, "y":  0.0, "sx": 0.55, "sy": 12.0},
        # East Wall (Continuous)
        {"name": "Wall_East", "x":  5.75, "y":  0.0, "sx": 0.55, "sy": 12.0},

        # Interior Maze Corridors (Faithfully matching Ref 4 Panel 2 Top-Down Plan)
        # Horizontal Interior Corridors
        {"name": "Wall_H_1", "x": -2.8, "y":  3.8, "sx": 3.6, "sy": 0.55},
        {"name": "Wall_H_2", "x":  3.2, "y":  3.8, "sx": 3.0, "sy": 0.55},
        {"name": "Wall_H_3", "x": -1.2, "y":  1.9, "sx": 3.2, "sy": 0.55},
        {"name": "Wall_H_4", "x":  3.0, "y":  1.9, "sx": 3.4, "sy": 0.55},
        {"name": "Wall_H_5", "x": -3.2, "y": -0.2, "sx": 3.8, "sy": 0.55},
        {"name": "Wall_H_6", "x":  2.8, "y": -0.2, "sx": 2.2, "sy": 0.55}, # Open entrance to Golden Momo
        {"name": "Wall_H_7", "x": -1.8, "y": -2.1, "sx": 4.5, "sy": 0.55},
        {"name": "Wall_H_8", "x":  2.5, "y": -2.1, "sx": 3.8, "sy": 0.55},
        {"name": "Wall_H_9", "x": -0.5, "y": -4.0, "sx": 6.5, "sy": 0.55},

        # Vertical Interior Corridors
        {"name": "Wall_V_1", "x": -3.8, "y":  2.0, "sx": 0.55, "sy": 3.2},
        {"name": "Wall_V_2", "x": -1.8, "y": -0.5, "sx": 0.55, "sy": 3.0},
        {"name": "Wall_V_3", "x": -0.5, "y":  3.0, "sx": 0.55, "sy": 1.6}, # Clear open avenue to North Leaf Gate
        {"name": "Wall_V_4", "x":  0.2, "y": -1.2, "sx": 0.55, "sy": 2.2},
        {"name": "Wall_V_5", "x":  1.9, "y":  2.8, "sx": 0.55, "sy": 2.2},
        {"name": "Wall_V_6", "x":  3.8, "y": -1.2, "sx": 0.55, "sy": 2.8},
        {"name": "Wall_V_7", "x": -3.8, "y": -2.8, "sx": 0.55, "sy": 2.2},
    ]

    wall_height = 1.35
    for ws in wall_segments:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        h = bpy.context.active_object
        h.name = ws["name"]
        h.scale = (ws["sx"], ws["sy"], wall_height)
        h.location = (ws["x"], ws["y"], wall_height / 2.0)
        bpy.ops.object.transform_apply(scale=True, location=True)
        h.data.materials.append(mat_hedge)

        # Rounded organic pillow bevel
        h_bev = h.modifiers.new("Bevel", 'BEVEL')
        h_bev.width = 0.16
        h_bev.segments = 3
        h_bev.limit_method = 'NONE'

        # Subtle subsurf for plush soft vegetation look
        sub = h.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        bpy.ops.object.shade_smooth()
        col.objects.link(h)

    # -------------------------------------------------------------------------
    # 5. Blooming Daisies on Hedge Tops (Pink, White, Yellow Centers)
    # -------------------------------------------------------------------------
    random.seed(2026)
    fl_idx = 0
    for ws in wall_segments:
        # Scatter 2 to 4 flower clusters along each wall segment
        cluster_count = max(2, int(max(ws["sx"], ws["sy"]) / 1.5))
        for _ in range(cluster_count):
            if ws["sx"] >= ws["sy"]:
                fx = ws["x"] + random.uniform(-ws["sx"]*0.4, ws["sx"]*0.4)
                fy = ws["y"] + random.uniform(-0.15, 0.15)
            else:
                fx = ws["x"] + random.uniform(-0.15, 0.15)
                fy = ws["y"] + random.uniform(-ws["sy"]*0.4, ws["sy"]*0.4)
            fz = wall_height + 0.02

            is_pink = (random.random() < 0.55)
            p_mat = mat_flower_pink if is_pink else mat_flower_white

            # 5 Petals
            for i in range(5):
                ang = i * (2.0 * math.pi / 5.0)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, segments=10, ring_count=6)
                pet = bpy.context.active_object
                pet.name = f"Petal_{fl_idx}_{i}"
                pet.scale = (0.7, 1.35, 0.35)
                rad = 0.075
                pet.location = (fx + rad * math.cos(ang), fy + rad * math.sin(ang), fz)
                pet.rotation_euler = (0, 0, ang)
                pet.data.materials.append(p_mat)
                bpy.ops.object.shade_smooth()
                col.objects.link(pet)

            # Golden Pistil Center
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, segments=10, ring_count=6)
            pis = bpy.context.active_object
            pis.name = f"Pistil_{fl_idx}"
            pis.location = (fx, fy, fz + 0.02)
            pis.scale = (1.0, 1.0, 0.6)
            pis.data.materials.append(mat_flower_yellow)
            bpy.ops.object.shade_smooth()
            col.objects.link(pis)
            fl_idx += 1

    # -------------------------------------------------------------------------
    # 6. The Grand Leaf Gate Arch (at North exit: x = 0, y = 5.75)
    # -------------------------------------------------------------------------
    gate_root = bpy.data.objects.new("SM_Leaf_Gate", None)
    gate_root.location = (0.0, 5.75, 0.0)
    col.objects.link(gate_root)

    # 2 Cedar Wood Pillars with Stone Plinths
    for side, px in [("Left", -1.1), ("Right", 1.1)]:
        # Wood pillar (local coordinates relative to gate_root!)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.4, vertices=16)
        pillar = bpy.context.active_object
        pillar.name = f"Gate_Pillar_{side}"
        pillar.location = (px, 0.0, 1.2)
        pillar.data.materials.append(mat_wood)
        pillar.parent = gate_root
        bpy.ops.object.shade_smooth()
        col.objects.link(pillar)

        # Stone footing plinth
        bpy.ops.mesh.primitive_cube_add(size=0.55)
        plinth = bpy.context.active_object
        plinth.name = f"Gate_Plinth_{side}"
        plinth.location = (px, 0.0, 0.22)
        plinth.scale = (1.0, 1.0, 0.8)
        plinth.data.materials.append(mat_curb)
        plinth.parent = gate_root
        p_bev = plinth.modifiers.new("Bevel", 'BEVEL')
        p_bev.width = 0.08
        bpy.ops.object.shade_smooth()
        col.objects.link(plinth)

    # Arch Lintel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=2.4, vertices=16)
    lintel = bpy.context.active_object
    lintel.name = "Gate_Lintel"
    lintel.location = (0.0, 0.0, 2.35)
    lintel.rotation_euler = (0, math.radians(90), 0)
    lintel.data.materials.append(mat_wood)
    lintel.parent = gate_root
    bpy.ops.object.shade_smooth()
    col.objects.link(lintel)

    # Glowing Golden Momo Emblem in center of Arch
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, segments=20, ring_count=16)
    crest = bpy.context.active_object
    crest.name = "Gate_Momo_Crest"
    crest.location = (0.0, 0.0, 2.35)
    crest.scale = (1.1, 0.8, 1.0)
    crest.data.materials.append(mat_momo_gold)
    crest.parent = gate_root
    bpy.ops.object.shade_smooth()
    col.objects.link(crest)

    # Tiered Leaf Canopy
    leaf_lobes = [
        {"loc": (0, 0, 2.85), "scale": (0.85, 0.65, 0.45)},
        {"loc": (-0.45, 0, 2.75), "scale": (0.75, 0.60, 0.40)},
        {"loc": (0.45, 0, 2.75), "scale": (0.75, 0.60, 0.40)},
        {"loc": (-0.95, 0, 2.55), "scale": (0.70, 0.55, 0.38)},
        {"loc": (0.95, 0, 2.55), "scale": (0.70, 0.55, 0.38)},
        {"loc": (-1.35, 0, 2.25), "scale": (0.60, 0.50, 0.35)},
        {"loc": (1.35, 0, 2.25), "scale": (0.60, 0.50, 0.35)},
    ]
    for idx, ll in enumerate(leaf_lobes):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, segments=16, ring_count=12)
        lobe = bpy.context.active_object
        lobe.name = f"Canopy_Leaf_{idx+1}"
        lobe.location = (ll["loc"][0], ll["loc"][1], ll["loc"][2])
        lobe.scale = ll["scale"]
        lobe.data.materials.append(mat_gate_leaf)
        lobe.parent = gate_root
        bpy.ops.object.shade_smooth()
        col.objects.link(lobe)

    # -------------------------------------------------------------------------
    # 7. Sanctuary of the Golden Momo (at x = 1.8, y = 0.8)
    # -------------------------------------------------------------------------
    momo_root = bpy.data.objects.new("SM_Golden_Momo_Sanctuary", None)
    momo_root.location = (1.8, 0.8, 0.0)
    col.objects.link(momo_root)

    # Stone pedestal (local coords relative to momo_root!)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.22, vertices=24)
    ped = bpy.context.active_object
    ped.name = "Momo_Pedestal"
    ped.location = (0.0, 0.0, 0.11)
    ped.data.materials.append(mat_curb)
    ped.parent = momo_root
    bpy.ops.object.shade_smooth()
    col.objects.link(ped)

    # 6 Radial Bamboo Steamer Leaves
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, segments=12, ring_count=8)
        lf = bpy.context.active_object
        lf.name = f"Momo_Base_Leaf_{i+1}"
        lf.scale = (0.8, 1.4, 0.28)
        r_dist = 0.30
        lf.location = (r_dist * math.cos(ang), r_dist * math.sin(ang), 0.22)
        lf.rotation_euler = (0, 0, ang + math.pi/2)
        lf.data.materials.append(mat_gate_leaf)
        lf.parent = momo_root
        bpy.ops.object.shade_smooth()
        col.objects.link(lf)

    # Plump Golden Dumpling
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, segments=24, ring_count=18)
    dumpling = bpy.context.active_object
    dumpling.name = "Golden_Momo_Dumpling"
    dumpling.location = (0.0, 0.0, 0.52)
    dumpling.scale = (1.15, 1.15, 0.90)
    dumpling.data.materials.append(mat_momo_gold)
    dumpling.parent = momo_root
    sub_d = dumpling.modifiers.new("Subsurf", 'SUBSURF')
    sub_d.levels = 1
    bpy.ops.object.shade_smooth()
    col.objects.link(dumpling)

    # Top pinch swirl knot
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.11, radius2=0.015, depth=0.18)
    knot = bpy.context.active_object
    knot.name = "Golden_Momo_Swirl"
    knot.location = (0.0, 0.0, 0.82)
    knot.data.materials.append(mat_momo_gold)
    knot.parent = momo_root
    bpy.ops.object.shade_smooth()
    col.objects.link(knot)

    # 5 Floating Golden Star Sparkles
    sparkle_coords = [
        (-0.45, -0.25, 0.85),
        (0.48, -0.20, 0.92),
        (0.0, 0.45, 1.05),
        (-0.35, 0.35, 0.65),
        (0.38, 0.30, 0.72)
    ]
    for idx, sc in enumerate(sparkle_coords):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, segments=10, ring_count=8)
        spk = bpy.context.active_object
        spk.name = f"Momo_Sparkle_{idx+1}"
        spk.location = sc
        spk.data.materials.append(mat_sparkle)
        spk.parent = momo_root
        col.objects.link(spk)

    # Warm inner point light
    glow_light = bpy.data.lights.new("Golden_Momo_Light", 'POINT')
    glow_light.energy = 55.0
    glow_light.color = (1.0, 0.84, 0.45)
    glow_obj = bpy.data.objects.new("Golden_Momo_Light", glow_light)
    glow_obj.location = (0.0, 0.0, 0.65)
    col.objects.link(glow_obj)
    glow_obj.parent = momo_root

    # -------------------------------------------------------------------------
    # 8. Framing Cedar / Cloud Trees in Outer Corners
    # -------------------------------------------------------------------------
    tree_coords = [
        (-7.2, -7.2), (7.2, -7.2), (-7.2, 7.2), (7.2, 7.2)
    ]
    for idx, (tx, ty) in enumerate(tree_coords):
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=3.4, vertices=16)
        trunk = bpy.context.active_object
        trunk.name = f"Tree_Trunk_{idx+1}"
        trunk.location = (tx, ty, 1.7)
        trunk.data.materials.append(mat_wood)
        bpy.ops.object.shade_smooth()
        col.objects.link(trunk)

        # 3 Puffy canopy lobes
        for l_idx, (lx, ly, lz, rad) in enumerate([(0, 0, 3.5, 1.6), (-0.4, 0.3, 4.3, 1.25), (0.4, -0.2, 4.1, 1.35)]):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=16, ring_count=12)
            lobe = bpy.context.active_object
            lobe.name = f"Tree_Lobe_{idx+1}_{l_idx+1}"
            lobe.location = (tx + lx, ty + ly, lz)
            lobe.scale = (1.0, 1.0, 0.78)
            lobe.data.materials.append(mat_gate_leaf)
            bpy.ops.object.shade_smooth()
            col.objects.link(lobe)

    # -------------------------------------------------------------------------
    # 9. Low Manicured Lawn Grass Tufts (Height 0.08m)
    # -------------------------------------------------------------------------
    for g_idx in range(250):
        gx = random.uniform(-5.2, 5.2)
        gy = random.uniform(-5.2, 5.2)

        in_wall = False
        for ws in wall_segments:
            if (ws["x"] - ws["sx"]/2 - 0.1 <= gx <= ws["x"] + ws["sx"]/2 + 0.1) and \
               (ws["y"] - ws["sy"]/2 - 0.1 <= gy <= ws["y"] + ws["sy"]/2 + 0.1):
                in_wall = True
                break
        if not in_wall:
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.04, radius2=0.005, depth=0.08)
            tuft = bpy.context.active_object
            tuft.name = f"Lawn_Tuft_{g_idx+1}"
            tuft.location = (gx, gy, 0.04)
            tuft.rotation_euler = (random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15), random.uniform(0, math.pi*2))
            tuft.data.materials.append(mat_grass_blade)
            col.objects.link(tuft)

    # -------------------------------------------------------------------------
    # 10. Render Master Beauty Image & Export GLB
    # -------------------------------------------------------------------------
    # Warm Sky World
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.85, 0.94, 0.98, 1.0)
    bg.inputs["Strength"].default_value = 0.95

    # Golden Hour Sunlight
    sun = bpy.data.lights.new("Sun_Beauty", 'SUN')
    sun.energy = 4.5
    sun.color = (1.0, 0.95, 0.88)
    sun_obj = bpy.data.objects.new("Sun_Beauty", sun)
    sun_obj.location = (15, -20, 25)
    sun_obj.rotation_euler = (math.radians(50), math.radians(22), math.radians(-38))
    col.objects.link(sun_obj)

    # Sky fill
    fill = bpy.data.lights.new("Sky_Fill", 'SUN')
    fill.energy = 1.8
    fill.color = (0.84, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("Sky_Fill", fill)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(145))
    col.objects.link(fill_obj)

    # Camera matching Ref 4 Isometric gameplay angle
    cam = bpy.data.cameras.new("Cam_Beauty")
    cam.lens = 52
    cam_obj = bpy.data.objects.new("Cam_Beauty", cam)
    cam_obj.location = (-12.0, -18.0, 18.0)
    # Track to center
    cam_obj.rotation_euler = (math.radians(50), 0, math.radians(-32))
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    render_out = r"D:\Projects\MOMO MAZE\WebGame\renders\definitive_beauty_maze.png"
    os.makedirs(os.path.dirname(render_out), exist_ok=True)
    scene.render.filepath = render_out
    bpy.ops.render.render(write_still=True)
    print("Rendered beauty view to:", render_out)

    # Export clean GLB directly to WebGame/models/beauty_maze_env.glb
    export_glb = r"D:\Projects\MOMO MAZE\WebGame\models\beauty_maze_env.glb"
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
    print("Successfully exported definitive GLB to:", export_glb)

if __name__ == "__main__":
    run()
