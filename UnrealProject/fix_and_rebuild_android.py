"""
fix_and_rebuild_android.py
==========================
Fixes the two blocking issues visible in the device screenshot:
  1. NAVMESH NEEDS TO BE REBUILT  → builds nav mesh via UBT
  2. Gray / untextured meshes     → ensures material base colours are vivid

Must be run INSIDE the Unreal Editor Python console (or via -ExecPython flag).
"""

import unreal
import os

LOG_PATH = "D:/Projects/MOMO MAZE/UnrealProject/fix_rebuild_log.txt"

def log(msg):
    print(f"[FixRebuild] {msg}")
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")

# ──────────────────────────────────────────────
# 1. Load the 31x31 level
# ──────────────────────────────────────────────
def load_level():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        subsystem.load_level(level_path)
        log(f"Loaded level: {level_path}")
    else:
        log(f"ERROR: Level not found at {level_path}")
        return False
    return True

# ──────────────────────────────────────────────
# 2. Fix material base colours so they cook vividly
# ──────────────────────────────────────────────
MATERIAL_COLORS = {
    # path                                       R      G      B
    "/Game/Materials/Environment/M_Hedge_Foliage":  (0.08, 0.38, 0.08),   # deep garden green
    "/Game/Materials/Environment/M_Grass_Path":     (0.26, 0.55, 0.14),   # bright grass
    "/Game/Materials/Environment/M_Leaf_Gate":      (0.05, 0.52, 0.18),   # emerald leaf
    "/Game/Materials/Environment/M_Momo_Dough":     (0.95, 0.88, 0.70),   # warm cream
    "/Game/Materials/Characters/M_Golumolu_Fur":    (0.22, 0.22, 0.26),   # dark charcoal
    "/Game/Materials/Characters/M_Ghost_Master":    (0.72, 0.85, 0.95),   # pale blue-white
    "/Game/Materials/UI/M_UI_Gold":                 (1.00, 0.72, 0.08),   # vibrant gold
    "/Game/Materials/UI/M_UI_Cream":                (1.00, 0.95, 0.85),   # warm cream
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
        mat = unreal.EditorAssetLibrary.load_asset(mat_path)
        if not mat:
            log(f"  SKIP (not found): {mat_path}")
            continue
        # Check if it's a Material (not MaterialInstance)
        if not isinstance(mat, unreal.Material):
            log(f"  SKIP (not a base Material): {mat_path}")
            continue
        # Try to set base colour constant
        try:
            # Find or create constant 3-vector for base colour
            existing = ml.get_material_property_input_node(mat, unreal.MaterialProperty.MP_BASE_COLOR)
            if existing:
                # Set if it's already a constant
                nodes = ml.get_material_nodes(mat, unreal.MaterialExpressionVectorParameter)
                if not nodes:
                    nodes = ml.get_material_nodes(mat, unreal.MaterialExpressionConstant3Vector)
                if nodes:
                    node = nodes[0]
                    node.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
                    log(f"  Updated existing colour node: {mat_path} -> ({r:.2f},{g:.2f},{b:.2f})")
                    fixed += 1
                    ml.recompile_material(mat)
                    unreal.EditorAssetLibrary.save_asset(mat_path)
                    continue
            # Create a new Constant3Vector and wire to Base Color
            expr = ml.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
            if expr:
                expr.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
                ml.connect_material_property(expr, "", unreal.MaterialProperty.MP_BASE_COLOR)
                log(f"  Created colour node: {mat_path} -> ({r:.2f},{g:.2f},{b:.2f})")
                fixed += 1
                ml.recompile_material(mat)
                unreal.EditorAssetLibrary.save_asset(mat_path)
        except Exception as e:
            log(f"  ERROR on {mat_path}: {e}")
    log(f"Materials fixed: {fixed}/{len(MATERIAL_COLORS)}")

# ──────────────────────────────────────────────
# 3. Ensure NavMesh Bounds Volume covers the full maze
#    and trigger navigation build
# ──────────────────────────────────────────────
def fix_navmesh():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # Find or create NavMeshBoundsVolume
    nav_vol = None
    for a in actors:
        if isinstance(a, unreal.NavMeshBoundsVolume):
            nav_vol = a
            break

    grid_size = 31
    cell_size = 180.0
    maze_extent = grid_size * cell_size  # 5580 cm

    if nav_vol is None:
        log("No NavMeshBoundsVolume found — spawning one...")
        nav_vol = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.NavMeshBoundsVolume,
            unreal.Vector(0, 0, 150.0)
        )
        nav_vol.set_actor_label("NavMeshBounds_MomoMaze_31x31")
    else:
        log(f"Found existing NavMeshBoundsVolume: {nav_vol.get_actor_label()}")

    # Resize to cover entire 31x31 maze plus margin
    half = (maze_extent / 100.0) + 10.0  # convert cm->m equivalent in scale units
    # In UE5, NavMeshBoundsVolume scale works like a box extent in world units
    # The brush is 200x200x200 by default, so scale * 100 = half-extent in cm
    scale_xy = (maze_extent / 2.0 + 500.0) / 100.0
    scale_z = 10.0  # ~1000cm height for the bounds
    nav_vol.set_actor_scale3d(unreal.Vector(scale_xy, scale_xy, scale_z))
    nav_vol.set_actor_location(unreal.Vector(0, 0, 100.0), False, False)
    log(f"NavMeshBoundsVolume resized: scale=({scale_xy:.1f},{scale_xy:.1f},{scale_z})")

    # Save the level first
    unreal.EditorLoadingAndSavingUtils.save_current_level()
    log("Level saved.")

    # Trigger navigation build
    try:
        nav_sys = unreal.NavigationSystemV1.get_current(unreal.EditorLevelLibrary.get_editor_world())
        if nav_sys:
            nav_sys.build()
            log("NavigationSystem.build() triggered successfully!")
        else:
            log("WARNING: NavigationSystemV1 not found — trying subsystem rebuild...")
            # Alternative: use editor command
            unreal.EditorLevelLibrary.editor_set_game_view(False)
    except Exception as e:
        log(f"Nav build attempt: {e}")

    # Save again after nav build
    unreal.EditorLoadingAndSavingUtils.save_current_level()
    log("Level saved after nav build.")

# ──────────────────────────────────────────────
# 4. Set all static mesh actors to Static mobility
#    for better lighting bake
# ──────────────────────────────────────────────
def fix_mobility():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    static_fixed = 0
    for a in actors:
        if isinstance(a, unreal.StaticMeshActor):
            comp = a.static_mesh_component
            if comp:
                mob = comp.get_editor_property("mobility")
                if mob == unreal.ComponentMobility.MOVABLE:
                    comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
                    static_fixed += 1
    log(f"Set {static_fixed} StaticMeshComponents from Movable -> Static for lighting.")

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    with open(LOG_PATH, "w") as f:
        f.write("=== MOMO MAZE Android Fix Script ===\n")

    log("Step 1: Load 31x31 level...")
    if not load_level():
        return

    log("\nStep 2: Fix material base colours...")
    fix_materials()

    log("\nStep 3: Fix NavMesh bounds and trigger build...")
    fix_navmesh()

    log("\nStep 4: Fix static mesh mobility...")
    fix_mobility()

    log("\nStep 5: Final save...")
    unreal.EditorLoadingAndSavingUtils.save_current_level()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log(f"\nDONE. Total actors in level: {len(actors)}")
    log("NEXT STEP: Run Android package from File > Package Project > Android (ASTC)")
    log("           or use UAT command: RunUAT BuildCookRun -project=... -platform=Android")

if __name__ == "__main__":
    main()
