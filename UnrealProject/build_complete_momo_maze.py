import unreal
import json
import math
import os

MAP_PATH = "/Game/Maps/LVL_MomoMaze_Game"

def log(msg):
    print(f"[MomoBuild] {msg}")

def spawn_mesh(world, mesh_path, location, rotation=unreal.Rotator(0,0,0), scale=unreal.Vector(1,1,1), name="SM_Actor", mat_path=None, tags=[]):
    mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
    if not mesh:
        log(f"Warning: Mesh missing {mesh_path}")
        return None
        
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    if not actor:
        return None
        
    actor.set_actor_label(name)
    comp = actor.static_mesh_component
    comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(scale)
    
    if mat_path:
        mat = unreal.EditorAssetLibrary.load_asset(mat_path)
        if mat:
            comp.set_material(0, mat)
            
    if tags:
        actor.tags = tags
    return actor

def spawn_text(text_str, location, rotation=unreal.Rotator(0,90,0), size=24.0, color=unreal.Color(255, 244, 222, 255), name="Text_Actor"):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, location, rotation)
    if not actor:
        return None
    actor.set_actor_label(name)
    comp = actor.text_render
    comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    comp.set_text(unreal.Text(text_str))
    comp.set_world_size(size)
    comp.set_text_render_color(color)
    comp.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    comp.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    return actor

def build_game_level():
    log("=== Building Complete MOMO MAZE Game Level ===")
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    # 1. Load or Create Map
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        world = subsystem.load_level(MAP_PATH)
    else:
        world = subsystem.new_level(MAP_PATH)
        
    # Clean previous actors
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        unreal.EditorLevelLibrary.destroy_actor(a)
    log("Cleared previous actors from world.")
    
    # 2. Lighting & Atmosphere (Peach sunlit magical garden)
    dir_light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, -3000, 800), unreal.Rotator(-48, 45, 0))
    dir_light = dir_light_actor.root_component
    dir_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    dir_light.set_editor_property("intensity", 6.5)
    dir_light_actor.set_actor_label("Peach_Sun_DirectionalLight")
    
    sky_light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, -2500, 600), unreal.Rotator(0, 0, 0))
    sky_light = sky_light_actor.root_component
    sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sky_light.set_editor_property("intensity", 2.2)
    sky_light_actor.set_actor_label("Sky_Ambient_Light")
    
    pp_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    pp_actor.set_editor_property("unbound", True)
    pp_settings = pp_actor.settings
    pp_settings.bloom_intensity = 0.45
    pp_settings.bloom_threshold = 0.85
    pp_settings.auto_exposure_min_brightness = 1.0
    pp_settings.auto_exposure_max_brightness = 1.0
    pp_actor.settings = pp_settings
    pp_actor.set_actor_label("PostProcess_CozyGarden")
    
    # 3. 3D Menu Stage Diorama (Station at Y = -2500)
    stage_center = unreal.Vector(0, -2500, 40)
    
    # Ground & Hedges for Menu Stage
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Path_Tile", unreal.Vector(0, -2500, -180), scale=unreal.Vector(18, 12, 1), name="MenuStage_Ground", mat_path="/Game/Materials/Environment/M_Grass_Path")
    for x_off in range(-700, 800, 200):
        spawn_mesh(world, "/Game/Meshes/Environment/SM_Hedge_Straight", unreal.Vector(x_off, -2380, -100), scale=unreal.Vector(1.8, 1.8, 2.5), name=f"MenuHedge_Back_{x_off}", mat_path="/Game/Materials/Environment/M_Hedge_Foliage")
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Hedge_Corner", unreal.Vector(-800, -2400, -100), rotation=unreal.Rotator(0, 0, 0), scale=unreal.Vector(2, 2, 2.5), name="MenuHedge_CornerL", mat_path="/Game/Materials/Environment/M_Hedge_Foliage")
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Hedge_Corner", unreal.Vector(800, -2400, -100), rotation=unreal.Rotator(0, 90, 0), scale=unreal.Vector(2, 2, 2.5), name="MenuHedge_CornerR", mat_path="/Game/Materials/Environment/M_Hedge_Foliage")
    
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Flower_Cluster", unreal.Vector(-420, -2460, -150), scale=unreal.Vector(1.6, 1.6, 1.6), name="MenuFlowers_L")
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Flower_Cluster", unreal.Vector(420, -2460, -150), scale=unreal.Vector(1.6, 1.6, 1.6), name="MenuFlowers_R")
    
    # Cameo Characters framing the card
    spawn_mesh(world, "/Game/Meshes/Characters/SK_Golumolu", unreal.Vector(-360, -2520, -110), rotation=unreal.Rotator(0, 75, 0), scale=unreal.Vector(1.35, 1.35, 1.35), name="Cameo_Golumolu", mat_path="/Game/Materials/Characters/M_Golumolu_Fur")
    spawn_mesh(world, "/Game/Meshes/Characters/SK_Ghost_Follower", unreal.Vector(360, -2510, 50), rotation=unreal.Rotator(0, 105, 0), scale=unreal.Vector(1.15, 1.15, 1.15), name="Cameo_Ghost", mat_path="/Game/Materials/Characters/M_Ghost_Master")
    
    # 4. Central 3D Card Frame & Header Ribbon
    # In Blender, Card thickness is along Z, Face is in XY plane
    # To face camera at (0, -3100, 40) looking +Y:
    # Rotate Pitch=90, Yaw=0, Roll=0
    card_actor = spawn_mesh(world, "/Game/Meshes/UI/SM_UI_CardFrame", stage_center, rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(0.70, 0.76, 1.0), name="UI_CardFrame", mat_path="/Game/Materials/UI/M_UI_Cream_Master")
    
    # Header Ribbon atop card
    ribbon_loc = unreal.Vector(0, -2508, 205)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_HeaderRibbon", ribbon_loc, rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(0.55, 0.45, 1.0), name="UI_HeaderRibbon", mat_path="/Game/Materials/UI/M_UI_ToastBrown")
    spawn_text("MOMO MAZE", unreal.Vector(0, -2516, 205), size=26.0, color=unreal.Color(255, 244, 222, 255), name="Text_HeaderTitle")
    
    # Corner Leaf Pairs & Flower
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_LeafPair", unreal.Vector(-220, -2512, 190), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(0.35, 0.35, 1.0), name="Leaf_TopL", mat_path="/Game/Materials/UI/M_UI_LeafGreen")
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_LeafPair", unreal.Vector(220, -2512, 190), rotation=unreal.Rotator(90, 180, 0), scale=unreal.Vector(0.35, 0.35, 1.0), name="Leaf_TopR", mat_path="/Game/Materials/UI/M_UI_LeafGreen")
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_FlowerCorner", unreal.Vector(220, -2514, 190), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(0.30, 0.30, 1.0), name="Flower_TopR", mat_path="/Game/Materials/UI/M_UI_SpiritWhite")
    
    # 5. Interactive 3D Buttons (Main Menu Screen 02 default)
    # Primary "Play" Gold Button
    play_btn_loc = unreal.Vector(0, -2515, 30)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", play_btn_loc, rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(0.48, 0.42, 1.0), name="Btn_3D_Play", mat_path="/Game/Materials/UI/M_UI_Gold", tags=["Button3D", "Play"])
    spawn_text("▶  Play", unreal.Vector(0, -2522, 30), size=24.0, color=unreal.Color(95, 51, 31, 255), name="Text_PlayBtn")
    
    # Secondary Nav Buttons (Levels, Golumolu, Spirits, Settings)
    sec_btns = [
        (-180, "Btn_3D_Levels", "Levels", "Levels"),
        (-60, "Btn_3D_Closet", "Closet", "Golumolu"),
        (60, "Btn_3D_Spirits", "Spirits", "Spirits"),
        (180, "Btn_3D_Settings", "Settings", "Settings")
    ]
    for x_pos, bname, label, tag in sec_btns:
        b_loc = unreal.Vector(x_pos, -2514, -80)
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", b_loc, rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(0.24, 0.30, 1.0), name=bname, mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=["Button3D", tag])
        spawn_text(label, unreal.Vector(x_pos, -2520, -80), size=14.0, color=unreal.Color(95, 51, 31, 255), name=f"Text_{label}")
    
    # Menu Stage Camera
    cam_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0, -3100, 40), unreal.Rotator(0, 90, 0))
    cam = cam_actor.camera_component
    cam.set_editor_property("field_of_view", 48.0)
    cam.set_editor_property("aspect_ratio", 1.777778)
    cam_actor.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
    cam_actor.set_actor_label("MenuStage_Camera")
    
    # 6. Build Gameplay Maze (Level 1 from LEVEL_CONFIG_25.json)
    # Maze placed at (0, 1500, 0)
    grid_size = 15
    cell_size = 180.0
    half_ext = (grid_size * cell_size) / 2.0
    maze_origin_y = 1500.0
    
    # Load LEVEL_CONFIG_25
    with open("D:/Projects/MOMO MAZE/LEVEL_CONFIG_25.json", "r") as f:
        cfg = json.load(f)
    lvl1 = cfg["campaign"][0]
    log(f"Configuring Level 1: '{lvl1['name']}', grid {lvl1['grid_size']}x{lvl1['grid_size']}")
    
    # Seeded maze generator for Level 1 (guaranteed solvable)
    import random
    random.seed(101) # Level 1 seed
    grid = [[1 for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Carve paths with DFS
    def carve(cx, cy):
        grid[cy][cx] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < grid_size - 1 and 1 <= ny < grid_size - 1:
                if grid[ny][nx] == 1:
                    grid[cy + dy//2][cx + dx//2] = 0
                    carve(nx, ny)
    carve(1, 1)
    # Ensure start (1,1) and exit (grid_size-2, grid_size-2) open
    grid[1][1] = 0
    grid[grid_size-2][grid_size-2] = 0
    
    # Add loop shortcuts for cozy exploration
    for y in range(2, grid_size - 2, 3):
        for x in range(2, grid_size - 2, 3):
            if random.random() < 0.45:
                grid[y][x] = 0
                
    # Place actors for Level 1 maze
    path_cells = []
    walls_count = 0
    momos_count = 0
    
    for y in range(grid_size):
        for x in range(grid_size):
            wx = (x * cell_size) - half_ext + (cell_size / 2.0)
            wy = maze_origin_y + (y * cell_size) - half_ext + (cell_size / 2.0)
            loc = unreal.Vector(wx, wy, 0.0)
            
            # Floor tile under every cell
            spawn_mesh(world, "/Game/Meshes/Environment/SM_Path_Tile", unreal.Vector(wx, wy, -10.0), scale=unreal.Vector(1.8, 1.8, 1.0), name=f"Path_{x}_{y}", mat_path="/Game/Materials/Environment/M_Grass_Path", tags=["PathFloor"])
            
            if grid[y][x] == 1:
                # Hedge Wall
                spawn_mesh(world, "/Game/Meshes/Environment/SM_Hedge_Straight", loc, scale=unreal.Vector(1.8, 1.8, 2.4), name=f"Hedge_{x}_{y}", mat_path="/Game/Materials/Environment/M_Hedge_Foliage", tags=["HedgeWall"])
                walls_count += 1
            else:
                path_cells.append((x, y, wx, wy))
                
    log(f"Spawned {walls_count} hedge walls and {len(path_cells)} path tiles.")
    
    # Spawn PlayerStart at (1, 1)
    p_wx = (1 * cell_size) - half_ext + (cell_size / 2.0)
    p_wy = maze_origin_y + (1 * cell_size) - half_ext + (cell_size / 2.0)
    pstart = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(p_wx, p_wy, 80.0), unreal.Rotator(0, 0, 0))
    pstart.set_actor_label("PlayerStart_Level1")
    
    # Spawn Exit Leaf Gate & Golden Momo at (grid_size-2, grid_size-2)
    e_wx = ((grid_size - 2) * cell_size) - half_ext + (cell_size / 2.0)
    e_wy = maze_origin_y + ((grid_size - 2) * cell_size) - half_ext + (cell_size / 2.0)
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Leaf_Gate", unreal.Vector(e_wx, e_wy, 0.0), scale=unreal.Vector(1.8, 1.8, 2.2), name="Exit_Leaf_Gate", mat_path="/Game/Materials/Environment/M_Leaf_Gate", tags=["ExitLeafGate"])
    spawn_mesh(world, "/Game/Meshes/Environment/SM_Momo_Collectible", unreal.Vector(e_wx, e_wy, 45.0), scale=unreal.Vector(2.0, 2.0, 2.0), name="Golden_Momo_Grand", mat_path="/Game/Materials/UI/M_UI_Gold", tags=["GoldenMomo"])
    
    # Scatter 6 Target Momos on path junctions
    eligible = [c for c in path_cells if (c[0], c[1]) not in [(1,1), (grid_size-2, grid_size-2)]]
    step = len(eligible) // 6
    for i in range(6):
        c = eligible[i * step]
        spawn_mesh(world, "/Game/Meshes/Environment/SM_Momo_Collectible", unreal.Vector(c[2], c[3], 35.0), scale=unreal.Vector(1.2, 1.2, 1.2), name=f"Momo_Dumpling_{i+1}", mat_path="/Game/Materials/Environment/M_Momo_Dough", tags=["MomoCollectible"])
        momos_count += 1
    log(f"Spawned {momos_count} Momo dumplings across Level 1 paths.")
    
    # Spawn Level 1 Ghost (Follower)
    mid_c = eligible[len(eligible) // 2]
    spawn_mesh(world, "/Game/Meshes/Characters/SK_Ghost_Follower", unreal.Vector(mid_c[2], mid_c[3], 50.0), scale=unreal.Vector(1.0, 1.0, 1.0), name="Ghost_Follower_Lvl1", mat_path="/Game/Materials/Characters/M_Ghost_Master", tags=["GhostAI", "Ghost_Follower"])
    
    # 7. Save Map
    unreal.EditorLevelLibrary.save_current_level()
    log(f"Level {MAP_PATH} successfully built and saved!")

if __name__ == "__main__":
    build_game_level()
