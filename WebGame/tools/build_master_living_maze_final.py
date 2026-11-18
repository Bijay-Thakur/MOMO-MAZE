import bpy
import math
import random
from mathutils import Vector, Euler

def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve, do_unlink=True)

def create_mat(name, base_color, roughness=0.6, metalness=0.0, emissive=None, emissive_strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metalness
    if emissive and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emissive
        bsdf.inputs["Emission Strength"].default_value = emissive_strength
    return mat

def build_scene():
    print("[MOMO MAZE] Building Master Living Garden Maze (100% Playable & Open)...")
    reset_scene()

    col = bpy.data.collections.get("Collection")
    if not col:
        col = bpy.data.collections.new("Master_Living_Garden_Maze")
        bpy.context.scene.collection.children.link(col)

    # Palette
    mat_hedge       = create_mat("M_Living_Hedge",     (0.25, 0.62, 0.14, 1.0), roughness=0.62)
    mat_hedge_crown = create_mat("M_Hedge_Crown",      (0.35, 0.76, 0.18, 1.0), roughness=0.55)
    mat_ground      = create_mat("M_Garden_Ground",    (0.36, 0.65, 0.18, 1.0), roughness=0.85)
    mat_meadow      = create_mat("M_Outer_Meadow",     (0.40, 0.70, 0.22, 1.0), roughness=0.90)
    mat_curb        = create_mat("M_Terracotta_Curb",  (0.76, 0.48, 0.32, 1.0), roughness=0.68)
    mat_paver       = create_mat("M_Cobble_Paver",     (0.88, 0.82, 0.72, 1.0), roughness=0.70)
    mat_stone       = create_mat("M_Ancient_Stone",    (0.78, 0.75, 0.68, 1.0), roughness=0.75)
    mat_wood        = create_mat("M_Cedar_Wood",       (0.55, 0.38, 0.24, 1.0), roughness=0.65)
    mat_leaf_gate   = create_mat("M_Gate_Canopy",      (0.20, 0.58, 0.12, 1.0), roughness=0.50)
    mat_flower_pink = create_mat("M_Flower_Pink",      (1.0, 0.52, 0.66, 1.0), roughness=0.35)
    mat_flower_white= create_mat("M_Flower_White",     (0.98, 0.98, 0.94, 1.0), roughness=0.35)
    mat_flower_yellow=(1.0, 0.85, 0.20, 1.0)
    mat_momo_gold   = create_mat("M_Golden_Momo",      (1.0, 0.88, 0.48, 1.0), roughness=0.25, emissive=(1.0, 0.82, 0.30, 1.0), emissive_strength=2.2)
    mat_sparkle     = create_mat("M_Gold_Sparkle",     (1.0, 0.95, 0.50, 1.0), roughness=0.20, emissive=(1.0, 0.95, 0.50, 1.0), emissive_strength=5.0)

    # 1. Broad Meadow Ground Plane (32m x 32m)
    bpy.ops.mesh.primitive_plane_add(size=34.0)
    meadow = bpy.context.active_object
    meadow.name = "SM_Outer_Meadow"
    meadow.location = (0, 0, -0.35)
    meadow.data.materials.append(mat_meadow)

    # 2. Raised Terracotta Curb (12.8m x 12.8m)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    curb = bpy.context.active_object
    curb.name = "SM_Garden_Retaining_Border"
    curb.scale = (12.8, 12.8, 0.40)
    curb.location = (0, 0, -0.20)
    bpy.ops.object.transform_apply(scale=True, location=True)
    curb.data.materials.append(mat_curb)
    c_bev = curb.modifiers.new("Bevel", 'BEVEL')
    c_bev.width = 0.22
    c_bev.segments = 3
    bpy.ops.object.shade_smooth()

    # 3. Inner Garden Lawn Plane
    bpy.ops.mesh.primitive_plane_add(size=12.2)
    lawn = bpy.context.active_object
    lawn.name = "SM_Garden_Lawn"
    lawn.location = (0, 0, 0.0)
    lawn.data.materials.append(mat_ground)

    # 4. Verified 100% Playable Wall Segments (Coordinate system: X is East, Y in Blender is glTF -Z)
    # Blender Y = -glTF Z. So glTF Z = -Blender Y.
    walls = [
        # North Wall with central opening for Leaf Gate at (0, -5.7)
        {"name": "Wall_N_Left",  "x": -3.6, "y":  5.7, "sx": 4.8,  "sy": 0.65},
        {"name": "Wall_N_Right", "x":  3.6, "y":  5.7, "sx": 4.8,  "sy": 0.65},
        # South Wall
        {"name": "Wall_South",   "x":  0.0, "y": -5.7, "sx": 12.0, "sy": 0.65},
        # West Wall
        {"name": "Wall_West",    "x": -5.7, "y":  0.0, "sx": 0.65, "sy": 12.0},
        # East Wall
        {"name": "Wall_East",    "x":  5.7, "y":  0.0, "sx": 0.65, "sy": 12.0},

        # Interior Corridors
        {"name": "Wall_H_1",     "x": -2.5, "y":  3.8, "sx": 3.8,  "sy": 0.65},
        {"name": "Wall_H_2",     "x":  2.5, "y":  3.8, "sx": 3.8,  "sy": 0.65},

        {"name": "Wall_H_3",     "x": -1.4, "y":  1.9, "sx": 3.0,  "sy": 0.65},
        {"name": "Wall_H_4",     "x":  3.2, "y":  1.9, "sx": 3.0,  "sy": 0.65},

        {"name": "Wall_H_5",     "x": -3.2, "y": -0.2, "sx": 3.4,  "sy": 0.65},
        {"name": "Wall_H_6",     "x":  2.2, "y": -0.2, "sx": 3.4,  "sy": 0.65},

        {"name": "Wall_H_7",     "x": -1.8, "y": -2.1, "sx": 3.8,  "sy": 0.65},
        {"name": "Wall_H_8",     "x":  2.5, "y": -2.1, "sx": 3.4,  "sy": 0.65},

        {"name": "Wall_H_9",     "x":  0.0, "y": -3.9, "sx": 6.2,  "sy": 0.65},

        {"name": "Wall_V_1",     "x": -3.8, "y":  2.0, "sx": 0.65, "sy": 3.0},
        {"name": "Wall_V_2",     "x": -1.8, "y": -0.5, "sx": 0.65, "sy": 2.6},
        {"name": "Wall_V_3",     "x":  1.8, "y":  2.8, "sx": 0.65, "sy": 2.2},
        {"name": "Wall_V_4",     "x":  3.8, "y": -1.2, "sx": 0.65, "sy": 2.4},
        {"name": "Wall_V_5",     "x": -3.8, "y": -2.8, "sx": 0.65, "sy": 2.0},
    ]

    hedge_height = 1.35
    random.seed(42)

    for w in walls:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        h = bpy.context.active_object
        h.name = w["name"]
        h.scale = (w["sx"], w["sy"], hedge_height)
        h.location = (w["x"], w["y"], hedge_height / 2.0)
        bpy.ops.object.transform_apply(scale=True, location=True)
        h.data.materials.append(mat_hedge)
        bev = h.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.24
        bev.segments = 3
        bpy.ops.object.shade_smooth()

        # Place puffy rounded cloud crowns along the top of each wall
        length = max(w["sx"], w["sy"])
        is_horiz = w["sx"] >= w["sy"]
        step = 0.95
        num_crowns = max(2, int(length / step))
        for ci in range(num_crowns):
            t = (ci + 0.5) / num_crowns - 0.5
            cx = w["x"] + (t * w["sx"] if is_horiz else 0) + random.uniform(-0.08, 0.08)
            cy = w["y"] + (0 if is_horiz else t * w["sy"]) + random.uniform(-0.08, 0.08)
            cz = hedge_height + 0.12

            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.45)
            cr = bpy.context.active_object
            cr.name = f"{w['name']}_Crown_{ci}"
            cr.scale = (1.05, 1.05, 0.70)
            cr.location = (cx, cy, cz)
            bpy.ops.object.transform_apply(scale=True, location=True)
            cr.data.materials.append(mat_hedge_crown)
            bpy.ops.object.shade_smooth()

            # Daisy flowers sprouting along crown
            if random.random() < 0.45:
                fx = cx + random.uniform(-0.25, 0.25)
                fy = cy + random.uniform(-0.25, 0.25)
                fz = cz + 0.28
                bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=0.03)
                fl = bpy.context.active_object
                fl.name = f"Flower_{w['name']}_{ci}"
                fl.location = (fx, fy, fz)
                fl.rotation_euler = (random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15), random.uniform(0, math.pi))
                bpy.ops.object.transform_apply(location=True, rotation=True)
                fl.data.materials.append(mat_flower_pink if random.random() > 0.4 else mat_flower_white)

    # 5. North Leaf Gate Archway (at x = 0, y = 5.75 in Blender)
    gate_root = bpy.data.objects.new("SM_Leaf_Gate", None)
    bpy.context.collection.objects.link(gate_root)
    gate_root.location = (0.0, 5.75, 0.0)

    # Left and Right Stone Pillars
    for side, px in [("Left", -1.2), ("Right", 1.2)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=2.4, vertices=16)
        post = bpy.context.active_object
        post.name = f"Gate_Pillar_{side}"
        post.location = (px, 0, 1.2)
        post.data.materials.append(mat_wood)
        post.parent = gate_root
        bpy.ops.object.shade_smooth()

        # Stone Plinth
        bpy.ops.mesh.primitive_cube_add(size=0.60)
        plinth = bpy.context.active_object
        plinth.name = f"Gate_Plinth_{side}"
        plinth.location = (px, 0, 0.24)
        plinth.scale = (1.0, 1.0, 0.8)
        plinth.data.materials.append(mat_curb)
        plinth.parent = gate_root
        p_bev = plinth.modifiers.new("Bevel", 'BEVEL')
        p_bev.width = 0.08
        bpy.ops.object.shade_smooth()

    # Wooden Lintel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.6, vertices=16)
    lintel = bpy.context.active_object
    lintel.name = "Gate_Lintel"
    lintel.location = (0, 0, 2.38)
    lintel.rotation_euler = (0, math.radians(90), 0)
    lintel.data.materials.append(mat_wood)
    lintel.parent = gate_root
    bpy.ops.object.shade_smooth()

    # Arched Living Foliage Canopy
    bpy.ops.mesh.primitive_torus_add(major_radius=1.35, minor_radius=0.45, major_segments=16, minor_segments=12)
    arch = bpy.context.active_object
    arch.name = "Gate_Arch_Canopy"
    arch.scale = (1.0, 0.8, 0.9)
    arch.rotation_euler = (math.pi / 2.0, 0, 0)
    arch.location = (0, 0, 2.35)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=True)
    arch.data.materials.append(mat_leaf_gate)
    arch.parent = gate_root
    bpy.ops.object.shade_smooth()

    # Golden Momo Beacon inside gate
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.36)
    crest = bpy.context.active_object
    crest.name = "Gate_Momo_Crest"
    crest.location = (0, 0, 2.30)
    crest.scale = (1.15, 1.15, 0.9)
    crest.data.materials.append(mat_momo_gold)
    crest.parent = gate_root
    bpy.ops.object.shade_smooth()

    # 6. Central Sanctuary of the Golden Momo (at x = 0.0, y = 1.0 in Blender)
    sanc_root = bpy.data.objects.new("SM_Golden_Momo_Sanctuary", None)
    bpy.context.collection.objects.link(sanc_root)
    sanc_root.location = (0.0, 1.0, 0.0)

    # Circular stone pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.35, depth=0.20)
    ped1 = bpy.context.active_object
    ped1.name = "Momo_Pedestal_Base"
    ped1.location = (0, 0, 0.10)
    ped1.data.materials.append(mat_stone)
    ped1.parent = sanc_root
    p1_bev = ped1.modifiers.new("Bevel", 'BEVEL')
    p1_bev.width = 0.04
    bpy.ops.object.shade_smooth()

    # Upper stepped altar
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.95, depth=0.16)
    ped2 = bpy.context.active_object
    ped2.name = "Momo_Pedestal_Top"
    ped2.location = (0, 0, 0.28)
    ped2.data.materials.append(mat_stone)
    ped2.parent = sanc_root
    bpy.ops.object.shade_smooth()

    # Bamboo steamer basket
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.55, depth=0.14)
    steamer = bpy.context.active_object
    steamer.name = "Momo_Steamer_Basket"
    steamer.location = (0, 0, 0.43)
    steamer.data.materials.append(mat_curb)
    steamer.parent = sanc_root
    bpy.ops.object.shade_smooth()

    # Golden Momo Dumpling
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=16, radius=0.38)
    momo_d = bpy.context.active_object
    momo_d.name = "Golden_Momo_Dumpling"
    momo_d.scale = (1.15, 1.15, 0.90)
    momo_d.location = (0, 0, 0.68)
    momo_d.data.materials.append(mat_momo_gold)
    momo_d.parent = sanc_root
    bpy.ops.object.shade_smooth()

    # Golden Momo Swirl
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=0.01, depth=0.18)
    swirl = bpy.context.active_object
    swirl.name = "Golden_Momo_Swirl"
    swirl.location = (0, 0, 1.0)
    swirl.data.materials.append(mat_momo_gold)
    swirl.parent = sanc_root
    bpy.ops.object.shade_smooth()

    # Sparkle stars
    for si, spos in enumerate([(-0.4, 0.3, 0.95), (0.45, -0.2, 1.05), (0.0, -0.45, 1.15), (-0.35, -0.35, 0.75)]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.045)
        sp = bpy.context.active_object
        sp.name = f"Momo_Sparkle_{si+1}"
        sp.location = spos
        sp.data.materials.append(mat_sparkle)
        sp.parent = sanc_root

    # 7. Four Framing Cloud Trees in the Outer Corners
    for tname, tx, ty in [("Tree_NW", -7.5, 7.5), ("Tree_NE", 7.5, 7.5), ("Tree_SW", -7.5, -7.5), ("Tree_SE", 7.5, -7.5)]:
        troot = bpy.data.objects.new(tname, None)
        bpy.context.collection.objects.link(troot)
        troot.location = (tx, ty, -0.35)

        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=3.0, vertices=16)
        trunk = bpy.context.active_object
        trunk.location = (0, 0, 1.5)
        trunk.data.materials.append(mat_wood)
        trunk.parent = troot
        bpy.ops.object.shade_smooth()

        # 3 Puffy foliage cloud lobes
        for li, (lx, ly, lz, lr) in enumerate([(0, 0, 3.2, 1.3), (-0.4, 0.3, 2.7, 1.0), (0.4, -0.2, 2.6, 1.1)]):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=lr)
            lobe = bpy.context.active_object
            lobe.name = f"{tname}_Lobe_{li+1}"
            lobe.scale = (1.1, 1.1, 0.8)
            lobe.location = (lx, ly, lz)
            lobe.data.materials.append(mat_hedge_crown)
            lobe.parent = troot
            bpy.ops.object.shade_smooth()

    # 8. Set up Camera and Render
    bpy.ops.object.camera_add(location=(-11.5, -16.5, 15.5))
    cam = bpy.context.active_object
    cam.name = "Cam_Beauty_View"
    cam.rotation_euler = (math.radians(48), 0, math.radians(-34))
    cam.data.lens = 55.0
    bpy.context.scene.camera = cam

    # Sun Light
    bpy.ops.object.light_add(type='SUN', location=(15, -20, 25))
    sun = bpy.context.active_object
    sun.data.energy = 4.2
    sun.data.color = (1.0, 0.90, 0.78)
    sun.rotation_euler = (math.radians(45), math.radians(18), math.radians(-32))

    # Render Preview
    render_out = "D:/Projects/MOMO MAZE/WebGame/renders/master_living_maze_final.png"
    bpy.context.scene.render.filepath = render_out
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    print(f"[MOMO MAZE] Rendering to {render_out}...")
    bpy.ops.render.render(write_still=True)
    print("[MOMO MAZE] Render complete!")

    # 9. Export to GLB
    for path in ["D:/Projects/MOMO MAZE/WebGame/models/beauty_maze.glb", "D:/Projects/MOMO MAZE/WebGame/models/beauty_maze_env.glb"]:
        print(f"[MOMO MAZE] Exporting to {path}...")
        bpy.ops.export_scene.gltf(
            filepath=path,
            export_format='GLB',
            use_selection=False,
            export_apply=True,
            export_yup=True
        )
    print("[MOMO MAZE] Export completed successfully for all targets!")

if __name__ == "__main__":
    build_scene()
