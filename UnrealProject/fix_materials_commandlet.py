"""
fix_materials_commandlet.py
============================
Fixes material base colours via UE Python commandlet.
Run via:  UnrealEditor-Cmd.exe project.uproject -run=pythonscript -script=this_file.py
Or directly in the UE Editor Python console.
"""

import unreal

LOG_PATH = "D:/Projects/MOMO MAZE/UnrealProject/fix_rebuild_log.txt"

def log(msg):
    print(f"[Fix] {msg}")
    try:
        with open(LOG_PATH, "a") as f:
            f.write(msg + "\n")
    except:
        pass

MATERIAL_COLORS = {
    "/Game/Materials/Environment/M_Hedge_Foliage":  (0.08, 0.38, 0.08),
    "/Game/Materials/Environment/M_Grass_Path":     (0.26, 0.55, 0.14),
    "/Game/Materials/Environment/M_Leaf_Gate":      (0.05, 0.52, 0.18),
    "/Game/Materials/Environment/M_Momo_Dough":     (0.95, 0.88, 0.70),
    "/Game/Materials/Characters/M_Golumolu_Fur":    (0.22, 0.22, 0.26),
    "/Game/Materials/Characters/M_Ghost_Master":    (0.72, 0.85, 0.95),
    "/Game/Materials/UI/M_UI_Gold":                 (1.00, 0.72, 0.08),
    "/Game/Materials/UI/M_UI_Cream":                (1.00, 0.95, 0.85),
    "/Game/Materials/UI/M_UI_Cream_Master":         (1.00, 0.95, 0.85),
    "/Game/Materials/UI/M_UI_LeafGreen":            (0.10, 0.60, 0.20),
    "/Game/Materials/UI/M_UI_SpiritWhite":          (0.95, 0.98, 1.00),
    "/Game/Materials/UI/M_UI_ToastBrown":           (0.42, 0.24, 0.10),
    "/Game/Materials/UI/M_UI_CoralHeart":           (0.90, 0.30, 0.25),
    "/Game/Materials/UI/M_UI_Orange":               (0.95, 0.55, 0.05),
}

def fix_materials():
    ml = unreal.MaterialEditingLibrary
    fixed = 0
    for mat_path, (r, g, b) in MATERIAL_COLORS.items():
        try:
            mat = unreal.EditorAssetLibrary.load_asset(mat_path)
            if not mat:
                log(f"SKIP (not found): {mat_path}")
                continue
            if not isinstance(mat, unreal.Material):
                log(f"SKIP (not a base Material): {mat_path}")
                continue

            # Look for existing Constant3Vector nodes
            c3_nodes = ml.get_material_nodes(mat, unreal.MaterialExpressionConstant3Vector)
            vp_nodes = ml.get_material_nodes(mat, unreal.MaterialExpressionVectorParameter)

            if c3_nodes:
                node = c3_nodes[0]
                node.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
                log(f"  Updated Constant3Vec: {mat_path} -> ({r:.2f},{g:.2f},{b:.2f})")
                fixed += 1
            elif vp_nodes:
                node = vp_nodes[0]
                node.set_editor_property("default_value", unreal.LinearColor(r, g, b, 1.0))
                log(f"  Updated VectorParam: {mat_path} -> ({r:.2f},{g:.2f},{b:.2f})")
                fixed += 1
            else:
                # Create a new one
                expr = ml.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
                if expr:
                    expr.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
                    ml.connect_material_property(expr, "", unreal.MaterialProperty.MP_BASE_COLOR)
                    log(f"  Created colour node: {mat_path} -> ({r:.2f},{g:.2f},{b:.2f})")
                    fixed += 1

            ml.recompile_material(mat)
            unreal.EditorAssetLibrary.save_asset(mat_path)

        except Exception as e:
            log(f"ERROR on {mat_path}: {e}")

    log(f"Materials fixed: {fixed}/{len(MATERIAL_COLORS)}")
    return fixed

def fix_navmesh():
    # Load the 31x31 level
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
    subsystem.load_level(level_path)
    log(f"Loaded level: {level_path}")

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    nav_vol = None
    for a in actors:
        if isinstance(a, unreal.NavMeshBoundsVolume):
            nav_vol = a
            break

    grid_size = 31
    cell_size = 180.0
    maze_extent = grid_size * cell_size

    if nav_vol is None:
        log("No NavMeshBoundsVolume — spawning one...")
        nav_vol = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.NavMeshBoundsVolume,
            unreal.Vector(0, 0, 150.0)
        )
        nav_vol.set_actor_label("NavMeshBounds_MomoMaze_31x31")
    else:
        log(f"Found NavMeshBoundsVolume: {nav_vol.get_actor_label()}")

    scale_xy = (maze_extent / 2.0 + 500.0) / 100.0
    scale_z = 10.0
    nav_vol.set_actor_scale3d(unreal.Vector(scale_xy, scale_xy, scale_z))
    nav_vol.set_actor_location(unreal.Vector(0, 0, 100.0), False, False)
    log(f"NavMeshBoundsVolume set scale=({scale_xy:.1f},{scale_xy:.1f},{scale_z})")

    # Build navigation
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        nav_sys = unreal.NavigationSystemV1.get_current(world)
        if nav_sys:
            nav_sys.build()
            log("Navigation build triggered!")
        else:
            log("Nav system not available in NullRHI mode — will bake at cook time.")
    except Exception as e:
        log(f"Nav build: {e}")

    unreal.EditorLoadingAndSavingUtils.save_current_level()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("Level saved with NavMesh volume.")

def main():
    with open(LOG_PATH, "w") as f:
        f.write("=== MOMO MAZE Fix Script ===\n")

    log("Step 1: Fixing material colours...")
    n = fix_materials()

    log("\nStep 2: Fixing NavMesh...")
    fix_navmesh()

    log("\nDONE.")

main()
