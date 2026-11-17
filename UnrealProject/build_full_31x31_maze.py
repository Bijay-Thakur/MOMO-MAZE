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

def spawn_static_mesh(mesh, location, rotation=unreal.Rotator(0,0,0), scale=unreal.Vector(1,1,1), material=None, label="SM_Actor", tags=[]):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    if not actor:
        return None
    actor.set_actor_label(label)
    comp = actor.static_mesh_component
    if mesh:
        comp.set_static_mesh(mesh)
    if material:
        comp.set_material(0, material)
    actor.set_actor_scale3d(scale)
    if tags:
        actor.tags = tags
    return actor

def build_maze():
    with open(LOG_FILE, "w") as f:
        f.write("=== Building 31x31 MOMO MAZE Level in Unreal Engine 5.8 ===\n")
        
    try:
        level_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
        level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

        # Load or create level
        if unreal.EditorAssetLibrary.does_asset_exist(level_path):
            log(f"Loading existing level: {level_path}")
            level_subsystem.load_level(level_path)
        else:
            log(f"Creating new level: {level_path}")
            level_subsystem.new_level(level_path)

        # Clear existing actors
        existing_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in existing_actors:
            unreal.EditorLevelLibrary.destroy_actor(a)
        log(f"Cleared {len(existing_actors)} previous actors from level.")

        log("Loading Maze JSON...")
        with open(JSON_PATH, "r") as f:
            data = json.load(f)

        grid = data["grid"]
        grid_size = data["grid_size"]
        cell_size = 180.0 # 180cm (1.8m)
        half_extent = (grid_size * cell_size) / 2.0

        # Load Meshes
        mesh_hedge = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Hedge_Straight")
        mesh_corner = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Hedge_Corner")
        mesh_floor = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Path_Tile")
        mesh_flower = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Flower_Cluster")
        mesh_gate = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Leaf_Gate")
        mesh_momo = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Momo_Collectible")

        mesh_golumolu = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
        mesh_follower = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Ghost_Follower")
        mesh_cutter = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Ghost_Cutter")
        mesh_wanderer = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Ghost_Wanderer")

        # Load Materials
        mat_hedge = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Hedge_Foliage")
        mat_grass = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Grass_Path")
        mat_gate = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Leaf_Gate")
        mat_momo = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Environment/M_Momo_Dough")
        mat_golu = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
        mat_ghost = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Ghost_Master")

        log(f"Assets loaded: hedge={bool(mesh_hedge)}, floor={bool(mesh_floor)}, momo={bool(mesh_momo)}, gate={bool(mesh_gate)}")

        wall_count = 0
        floor_count = 0
        gate_count = 0
        momo_count = 0
        flower_count = 0

        # Helper to check if neighbor is wall
        def is_wall(gx, gy):
            if 0 <= gx < grid_size and 0 <= gy < grid_size:
                return grid[gy][gx] == 1
            return True

        for y in range(grid_size):
            for x in range(grid_size):
                wx = (x * cell_size) - half_extent + (cell_size / 2.0)
                wy = (y * cell_size) - half_extent + (cell_size / 2.0)
                val = grid[y][x]
                loc = unreal.Vector(wx, wy, 0.0)

                # Floor for all walkable passages
                if val in (0, 2, 3, 4, 5, 6):
                    f_actor = spawn_static_mesh(mesh_floor, loc, scale=unreal.Vector(1.0, 1.0, 1.0),
                                               material=mat_grass, label=f"Path_Floor_{x}_{y}", tags=["PathFloor"])
                    if f_actor:
                        floor_count += 1

                # 1 = Solid Hedge Wall
                if val == 1:
                    # Check corner orientation
                    n_up = is_wall(x, y - 1)
                    n_down = is_wall(x, y + 1)
                    n_left = is_wall(x - 1, y)
                    n_right = is_wall(x + 1, y)

                    rot = unreal.Rotator(0, 0, 0)
                    mesh_to_use = mesh_hedge
                    # Use corner if it turns
                    if n_down and n_right and not n_up and not n_left:
                        mesh_to_use = mesh_corner if mesh_corner else mesh_hedge
                        rot = unreal.Rotator(0, 0, 0)
                    elif n_down and n_left and not n_up and not n_right:
                        mesh_to_use = mesh_corner if mesh_corner else mesh_hedge
                        rot = unreal.Rotator(0, 90, 0)
                    elif n_up and n_left and not n_down and not n_right:
                        mesh_to_use = mesh_corner if mesh_corner else mesh_hedge
                        rot = unreal.Rotator(0, 180, 0)
                    elif n_up and n_right and not n_down and not n_left:
                        mesh_to_use = mesh_corner if mesh_corner else mesh_hedge
                        rot = unreal.Rotator(0, 270, 0)
                    elif n_up and n_down:
                        rot = unreal.Rotator(0, 90, 0)

                    w_actor = spawn_static_mesh(mesh_to_use, loc, rotation=rot, scale=unreal.Vector(1.0, 1.0, 1.0),
                                                material=mat_hedge, label=f"HedgeWall_{x}_{y}", tags=["HedgeWall"])
                    if w_actor:
                        wall_count += 1

                    # Occasional flower patch on walls
                    if (x * 7 + y * 13) % 29 == 0:
                        fl_loc = unreal.Vector(wx, wy, 15.0)
                        fl_actor = spawn_static_mesh(mesh_flower, fl_loc, rotation=unreal.Rotator(0, (x*35)%360, 0),
                                                     scale=unreal.Vector(0.65, 0.65, 0.65), label=f"Flower_{x}_{y}")
                        if fl_actor:
                            flower_count += 1

                # 2 = Moving Gate A
                elif val == 2:
                    gate_a = spawn_static_mesh(mesh_hedge, loc, scale=unreal.Vector(1.0, 1.0, 1.0),
                                               material=mat_hedge, label=f"MovingGate_A_{x}_{y}",
                                               tags=["MovingGate", "PhaseA"])
                    if gate_a:
                        gate_count += 1

                # 3 = Moving Gate B (Initially Lowered Underground)
                elif val == 3:
                    loc_lowered = unreal.Vector(wx, wy, -250.0)
                    gate_b = spawn_static_mesh(mesh_hedge, loc_lowered, scale=unreal.Vector(1.0, 1.0, 1.0),
                                               material=mat_hedge, label=f"MovingGate_B_{x}_{y}",
                                               tags=["MovingGate", "PhaseB"])
                    if gate_b:
                        gate_count += 1

                # 5 = Momo Collectible
                elif val == 5:
                    momo_loc = unreal.Vector(wx, wy, 45.0)
                    m_actor = spawn_static_mesh(mesh_momo, momo_loc, scale=unreal.Vector(0.75, 0.75, 0.75),
                                               material=mat_momo, label=f"Momo_{x}_{y}",
                                               tags=["MomoCollectible"])
                    if m_actor:
                        momo_count += 1

                # 6 = Exit Leaf Gate
                elif val == 6:
                    gate_loc = unreal.Vector(wx, wy, 0.0)
                    g_actor = spawn_static_mesh(mesh_gate, gate_loc, scale=unreal.Vector(1.0, 1.0, 1.0),
                                               material=mat_gate, label="Exit_Leaf_Gate",
                                               tags=["ExitLeafGate"])

        log(f"Grid placed: {wall_count} Walls, {floor_count} Floors, {gate_count} Moving Gates, {momo_count} Momos, {flower_count} Flower clusters.")

        # Player Start
        p_start_x = (data["player_start"]["x"] * cell_size) - half_extent + (cell_size / 2.0)
        p_start_y = (data["player_start"]["y"] * cell_size) - half_extent + (cell_size / 2.0)
        p_start = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(p_start_x, p_start_y, 80.0))
        if p_start:
            p_start.set_actor_label("Golumolu_PlayerStart")
            p_start.set_actor_rotation(unreal.Rotator(0, -90, 0), False)
            log(f"PlayerStart placed at ({p_start_x}, {p_start_y}, 80)")

        # Golumolu Character Visual Actor
        golu_preview = spawn_static_mesh(mesh_golumolu, unreal.Vector(p_start_x, p_start_y, 20.0),
                                         rotation=unreal.Rotator(0, -90, 0), scale=unreal.Vector(0.55, 0.55, 0.55),
                                         material=mat_golu, label="Preview_Golumolu", tags=["GolumoluPreview"])

        # 3 Ghost Spirits at designated patrol bases
        ghost_configs = [
            {"name": "Ghost_Follower", "mesh": mesh_follower, "x": 11, "y": 15, "tags": ["GhostAI", "Follower"]},
            {"name": "Ghost_Cutter", "mesh": mesh_cutter, "x": 19, "y": 15, "tags": ["GhostAI", "Cutter"]},
            {"name": "Ghost_Wanderer", "mesh": mesh_wanderer, "x": 15, "y": 25, "tags": ["GhostAI", "Wanderer"]},
        ]
        for gc in ghost_configs:
            gx = (gc["x"] * cell_size) - half_extent + (cell_size / 2.0)
            gy = (gc["y"] * cell_size) - half_extent + (cell_size / 2.0)
            spawn_static_mesh(gc["mesh"], unreal.Vector(gx, gy, 85.0), rotation=unreal.Rotator(0, -90, 0),
                              scale=unreal.Vector(0.5, 0.5, 0.5), material=mat_ghost,
                              label=gc["name"], tags=gc["tags"])
            log(f"Placed {gc['name']} at cell ({gc['x']}, {gc['y']})")

        # Lighting & Atmosphere
        # Directional Golden Key Light
        dir_light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1200.0), unreal.Rotator(-50.0, 40.0, 0.0))
        if dir_light:
            dir_light.set_actor_label("Sun_Golden_Key")
            comp = dir_light.get_component_by_class(unreal.DirectionalLightComponent)
            if comp:
                comp.set_intensity(5.5)
                comp.set_light_color(unreal.LinearColor(1.0, 0.94, 0.84, 1.0))
                comp.set_cast_shadows(True)

        # Sky Light for soft ambient fill
        sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1000.0))
        if sky_light:
            sky_light.set_actor_label("Sky_Ambient_Fill")
            scomp = sky_light.get_component_by_class(unreal.SkyLightComponent)
            if scomp:
                scomp.set_intensity(1.2)
                scomp.set_light_color(unreal.LinearColor(0.82, 0.92, 1.0, 1.0))

        # Post Process Volume
        pp_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
        if pp_actor:
            pp_actor.set_actor_label("PP_CozyAtmosphere")
            pp_actor.set_editor_property("unbound", True)
            pps = pp_actor.settings
            pps.bloom_intensity = 0.65
            pps.bloom_threshold = 0.8
            pps.auto_exposure_min_brightness = 1.0
            pps.auto_exposure_max_brightness = 1.0
            pp_actor.settings = pps

        # Top-Down Cozy Camera Actor
        cam_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0, 2400, 3200), unreal.Rotator(-54, -90, 0))
        if cam_actor:
            cam_actor.set_actor_label("Cam_Overview_Diorama")
            cam = cam_actor.camera_component
            cam.set_editor_property("field_of_view", 52.0)

        # NavMeshBoundsVolume for pathfinding across the full 31x31 maze
        nav = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(0, 0, 100.0))
        if nav:
            nav.set_actor_label("NavMeshBounds_MomoMaze_31x31")
            nav.set_actor_scale3d(unreal.Vector(grid_size * 2.8, grid_size * 2.8, 6.0))

        # Save Level Package
        saved = unreal.EditorLoadingAndSavingUtils.save_current_level()
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        
        # Verify count
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        log(f"Level Saved: {saved}. Total actors now in level: {len(all_actors)}")
        log("SUCCESS: M_Maze_31x31 level generated and saved with all assets and lighting!")

    except Exception as e:
        log(f"FATAL ERROR: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    build_maze()
