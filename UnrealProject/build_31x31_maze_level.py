import unreal
import json
import os
import traceback

LOG_FILE = "D:/Projects/MOMO MAZE/UnrealProject/ue_level_build_log.txt"
JSON_PATH = "D:/Projects/MOMO MAZE/UnrealProject/Content/MazeData_31x31.json"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def build_maze_level():
    with open(LOG_FILE, "w") as f:
        f.write("Starting 31x31 Maze Level Generation in UE 5.8...\n")
    
    try:
        log("Loading 31x31 Maze JSON Data...")
        with open(JSON_PATH, "r") as f:
            maze_data = json.load(f)

        grid = maze_data["grid"]
        grid_size = maze_data["grid_size"]
        cell_size = 180.0 # 1.8 meters in Unreal units (cm)

        # 1. Create a new World / Level
        map_package_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
        world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
        log("Created Blank Map for M_Maze_31x31")

        # Load Static Meshes
        sm_hedge = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Environment/SM_Hedge_Straight")
        sm_floor = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Environment/SM_Path_Tile")
        sm_momo = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Environment/SM_Momo_Collectible")
        sm_gate = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Environment/SM_Leaf_Gate")
        sm_golumolu = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Characters/golumolu_validated")
        sm_follower = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Characters/ghost_follower_validated")
        sm_cutter = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Characters/ghost_cutter_validated")
        sm_wanderer = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Characters/ghost_wanderer_validated")

        # Load Materials
        m_hedge = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Hedge_Foliage")
        m_grass = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Grass_Path")
        m_momo_mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Momo_Dough")

        log("Loaded assets and materials successfully.")

        # Spawn actors in World
        spawned_walls = 0
        spawned_floors = 0
        spawned_momos = 0
        spawned_gates = 0

        # Center offset so maze is centered around (0, 0, 0)
        half_extent = (grid_size * cell_size) / 2.0

        for y in range(grid_size):
            for x in range(grid_size):
                world_x = (x * cell_size) - half_extent + (cell_size / 2.0)
                world_y = (y * cell_size) - half_extent + (cell_size / 2.0)
                val = grid[y][x]

                loc = unreal.Vector(world_x, world_y, 0.0)

                # Floor for all walkable corridors and items
                if val in (0, 2, 3, 4, 5, 6):
                    floor_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_floor, loc)
                    if floor_actor:
                        floor_actor.set_actor_label(f"Floor_{x}_{y}")
                        if m_grass:
                            floor_actor.static_mesh_component.set_material(0, m_grass)
                        spawned_floors += 1

                # Solid Hedge Wall
                if val == 1:
                    wall_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_hedge, loc)
                    if wall_actor:
                        wall_actor.set_actor_label(f"HedgeWall_{x}_{y}")
                        # Scale to match 180cm cell size
                        wall_actor.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
                        if m_hedge:
                            wall_actor.static_mesh_component.set_material(0, m_hedge)
                        spawned_walls += 1

                # Moving Hedge Gate A
                elif val == 2:
                    gate_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_hedge, loc)
                    if gate_actor:
                        gate_actor.set_actor_label(f"MovingGate_A_{x}_{y}")
                        gate_actor.tags = ["MovingGate", "PhaseA"]
                        if m_hedge:
                            gate_actor.static_mesh_component.set_material(0, m_hedge)
                        spawned_gates += 1

                # Moving Hedge Gate B
                elif val == 3:
                    gate_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_hedge, loc)
                    if gate_actor:
                        gate_actor.set_actor_label(f"MovingGate_B_{x}_{y}")
                        gate_actor.tags = ["MovingGate", "PhaseB"]
                        if m_hedge:
                            gate_actor.static_mesh_component.set_material(0, m_hedge)
                        spawned_gates += 1

                # Momo Collectible
                elif val == 5:
                    momo_loc = unreal.Vector(world_x, world_y, 25.0)
                    momo_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_momo, momo_loc)
                    if momo_actor:
                        momo_actor.set_actor_label(f"MomoCollectible_{x}_{y}")
                        momo_actor.tags = ["MomoCollectible"]
                        if m_momo_mat:
                            momo_actor.static_mesh_component.set_material(0, m_momo_mat)
                        spawned_momos += 1

                # Exit Leaf Gate
                elif val == 6:
                    gate_loc = unreal.Vector(world_x, world_y, 0.0)
                    leaf_gate = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_gate, gate_loc)
                    if leaf_gate:
                        leaf_gate.set_actor_label("Exit_Leaf_Gate")
                        leaf_gate.tags = ["ExitGate"]

                # Player Start
                elif val == 4:
                    start_loc = unreal.Vector(world_x, world_y, 50.0)
                    p_start = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, start_loc)
                    if p_start:
                        p_start.set_actor_label("Momo_PlayerStart")

        log(f"Spawned Level Elements: {spawned_walls} Hedge Walls, {spawned_floors} Path Tiles, {spawned_gates} Moving Gates, {spawned_momos} Momos.")

        # 2. Spawn Characters
        start_x = (maze_data["player_start"]["x"] * cell_size) - half_extent + (cell_size / 2.0)
        start_y = (maze_data["player_start"]["y"] * cell_size) - half_extent + (cell_size / 2.0)
        
        golu_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_golumolu, unreal.Vector(start_x, start_y, 20.0))
        if golu_actor:
            golu_actor.set_actor_label("BP_Golumolu_PlayerPreview")
            golu_actor.set_actor_scale3d(unreal.Vector(0.5, 0.5, 0.5))

        # Spawn 3 Ghosts at Patrol Chokepoints
        ghost_spawns = [
            {"mesh": sm_follower, "label": "BP_Ghost_Follower", "x": 11, "y": 15},
            {"mesh": sm_cutter, "label": "BP_Ghost_Cutter", "x": 19, "y": 15},
            {"mesh": sm_wanderer, "label": "BP_Ghost_Wanderer", "x": 15, "y": 25},
        ]
        for gs in ghost_spawns:
            gx = (gs["x"] * cell_size) - half_extent + (cell_size / 2.0)
            gy = (gs["y"] * cell_size) - half_extent + (cell_size / 2.0)
            g_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(gs["mesh"], unreal.Vector(gx, gy, 80.0))
            if g_actor:
                g_actor.set_actor_label(gs["label"])
                g_actor.set_actor_scale3d(unreal.Vector(0.45, 0.45, 0.45))
                g_actor.tags = ["GhostAI", gs["label"]]

        log("Spawned Golumolu & 3 Spirit Ghosts into 31x31 Maze.")

        # 3. Setup Directional Sunlight & Sky Atmosphere
        sun_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000.0))
        if sun_actor:
            sun_actor.set_actor_label("Sun_Golden_Key")
            sun_actor.set_actor_rotation(unreal.Rotator(-45.0, 35.0, 0.0), False)
            light_comp = sun_actor.get_component_by_class(unreal.DirectionalLightComponent)
            if light_comp:
                light_comp.set_intensity(6.0)
                light_comp.set_light_color(unreal.LinearColor(1.0, 0.94, 0.82))

        sky_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 800.0))
        if sky_actor:
            sky_actor.set_actor_label("Sky_Ambient_Fill")
            sky_comp = sky_actor.get_component_by_class(unreal.SkyLightComponent)
            if sky_comp:
                sky_comp.set_intensity(1.2)
                sky_comp.set_light_color(unreal.LinearColor(0.85, 0.92, 1.0))

        # NavMeshBoundsVolume for AI Pathfinding
        nav_bounds = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(0, 0, 100.0))
        if nav_bounds:
            nav_bounds.set_actor_label("NavMeshBounds_31x31")
            nav_bounds.set_actor_scale3d(unreal.Vector(grid_size * 2.0, grid_size * 2.0, 5.0))

        # Save Level Package
        unreal.EditorLoadingAndSavingUtils.save_current_level()
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log("  ✓ Level M_Maze_31x31 built and saved successfully in Unreal Engine!")

    except Exception as e:
        log(f"EXCEPTION in level generation: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    build_maze_level()
