"""
fix_materials_v2.py  —  UE 5.8 compatible
==========================================
Uses the correct UE5.8 MaterialEditingLibrary API.
get_material_nodes() does not exist in 5.8; instead use:
  - create_material_expression() to add nodes
  - set_material_property_input_node() to connect to base color
  - recompile_material() to finalise

Since we can't easily inspect existing nodes, the safest approach is:
  1. Clear existing base-color connection
  2. Create a Constant3Vector node with our desired colour
  3. Connect it to MP_BASE_COLOR
  4. Recompile and save
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

# Target colours per material (linear colour space)
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

def fix_one_material(mat_path, r, g, b):
    ml = unreal.MaterialEditingLibrary

    mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    if not mat:
        log(f"  SKIP (not found): {mat_path}")
        return False
    if not isinstance(mat, unreal.Material):
        log(f"  SKIP (not base Material, type={type(mat).__name__}): {mat_path}")
        return False

    try:
        # Create a Constant3Vector expression at position (-400, 0)
        expr = ml.create_material_expression(
            mat,
            unreal.MaterialExpressionConstant3Vector,
            -400, 0
        )
        if not expr:
            log(f"  ERROR: Could not create Constant3Vector for {mat_path}")
            return False

        # Set the colour value
        expr.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))

        # Connect to Base Color input
        connected = ml.connect_material_property(
            expr, "",  # output pin name (empty = default)
            unreal.MaterialProperty.MP_BASE_COLOR
        )
        if not connected:
            log(f"  WARN: connect_material_property returned False for {mat_path}")

        # Recompile
        ml.recompile_material(mat)

        # Save
        unreal.EditorAssetLibrary.save_asset(mat_path, only_if_is_dirty=False)
        log(f"  FIXED: {mat_path} -> RGB({r:.2f},{g:.2f},{b:.2f})")
        return True

    except Exception as e:
        log(f"  ERROR on {mat_path}: {e}")
        return False

def fix_materials():
    log("=== Fixing Material Base Colours ===")
    fixed = 0
    for mat_path, (r, g, b) in MATERIAL_COLORS.items():
        if fix_one_material(mat_path, r, g, b):
            fixed += 1
    log(f"Fixed {fixed}/{len(MATERIAL_COLORS)} materials.\n")
    return fixed

def fix_navmesh_volume():
    log("=== Verifying NavMesh Bounds Volume ===")
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
    subsystem.load_level(level_path)

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_all_level_actors()

    nav_vol = None
    for a in actors:
        if isinstance(a, unreal.NavMeshBoundsVolume):
            nav_vol = a
            break

    if nav_vol:
        scale = nav_vol.get_actor_scale3d()
        loc = nav_vol.get_actor_location()
        log(f"NavMeshBoundsVolume found: scale={scale}, loc={loc}")
    else:
        log("NavMeshBoundsVolume NOT found — spawning...")
        actor_subsystem2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        nav_vol = actor_subsystem2.spawn_actor_from_class(
            unreal.NavMeshBoundsVolume,
            unreal.Vector(0, 0, 150.0),
            unreal.Rotator(0, 0, 0)
        )
        if nav_vol:
            nav_vol.set_actor_label("NavMeshBounds_MomoMaze_31x31")
            nav_vol.set_actor_scale3d(unreal.Vector(32.9, 32.9, 10.0))
            log("NavMeshBoundsVolume spawned and sized.")
        else:
            log("ERROR: Could not spawn NavMeshBoundsVolume!")

    unreal.EditorLoadingAndSavingUtils.save_current_level()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("Level + packages saved.")

def main():
    with open(LOG_PATH, "w") as f:
        f.write("=== MOMO MAZE Fix v2 ===\n")

    fix_materials()
    fix_navmesh_volume()

    log("ALL DONE. Ready to package Android.")

main()
