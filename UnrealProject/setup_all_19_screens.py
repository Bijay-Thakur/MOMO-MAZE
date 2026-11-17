import unreal
import json

MAP_PATH = "/Game/Maps/LVL_MomoMaze_Game"

def log(msg):
    print(f"[UIBuilder] {msg}")

def spawn_mesh(world, mesh_path, location, rotation=unreal.Rotator(90,0,0), scale=unreal.Vector(1,1,1), name="SM_Actor", mat_path=None, tags=[]):
    mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
    if not mesh:
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

def spawn_text(text_str, location, rotation=unreal.Rotator(0,90,0), size=20.0, color=unreal.Color(255, 244, 222, 255), name="Text_Actor", tags=[]):
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
    if tags:
        actor.tags = tags
    return actor

def build_all_screens():
    log("Building all 19 approved screens into LVL_MomoMaze_Game...")
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem.load_level(MAP_PATH)
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Clean previous screen-specific actors (keep stage diorama, lighting, maze)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        t = [str(x) for x in a.tags]
        if any(x.startswith("Screen_") or x.startswith("Btn_") for x in t):
            unreal.EditorLevelLibrary.destroy_actor(a)
            
    # Base coordinates for 3D card surface
    # Card is at (0, -2500, 40). Surface is at Y = -2514
    Y_SURF = -2514.0
    Y_TXT = -2520.0
    
    COL_BROWN = unreal.Color(95, 51, 31, 255)
    COL_WHITE = unreal.Color(255, 245, 235, 255)
    COL_GOLD = unreal.Color(255, 205, 75, 255)
    
    # -------------------------------------------------------------
    # SCREEN 01: Splash
    # -------------------------------------------------------------
    t1 = ["Screen_01"]
    spawn_text("MOMO MAZE", unreal.Vector(0, Y_TXT, 120), size=36.0, color=COL_BROWN, name="S01_Logo", tags=t1)
    spawn_text("A Cozy Garden Adventure", unreal.Vector(0, Y_TXT, 75), size=18.0, color=COL_BROWN, name="S01_Sub", tags=t1)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, Y_SURF, -30), scale=unreal.Vector(0.55, 0.45, 1.0), name="S01_Btn_Start", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t1 + ["Btn_Splash_Start"])
    spawn_text("Tap Anywhere to Begin", unreal.Vector(0, Y_TXT, -30), size=20.0, color=COL_BROWN, name="S01_Txt_Start", tags=t1)
    
    # -------------------------------------------------------------
    # SCREEN 02: Main Menu (Active by default)
    # -------------------------------------------------------------
    t2 = ["Screen_02"]
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, Y_SURF, 35), scale=unreal.Vector(0.50, 0.45, 1.0), name="S02_Btn_Play", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t2 + ["Btn_Main_Play"])
    spawn_text("▶  Play", unreal.Vector(0, Y_TXT, 35), size=26.0, color=COL_BROWN, name="S02_Txt_Play", tags=t2)
    
    nav_btns = [
        (-195, "Levels", "Btn_Main_Levels"),
        (-65, "Closet", "Btn_Main_Closet"),
        (65, "Spirits", "Btn_Main_Spirits"),
        (195, "Settings", "Btn_Main_Settings")
    ]
    for x_pos, label, btn_tag in nav_btns:
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(x_pos, Y_SURF, -75), scale=unreal.Vector(0.24, 0.32, 1.0), name=f"S02_{btn_tag}", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t2 + [btn_tag])
        spawn_text(label, unreal.Vector(x_pos, Y_TXT, -75), size=14.0, color=COL_BROWN, name=f"S02_Txt_{label}", tags=t2)
        
    # -------------------------------------------------------------
    # SCREEN 03: Play Menu
    # -------------------------------------------------------------
    t3 = ["Screen_03"]
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, Y_SURF, 85), scale=unreal.Vector(0.65, 0.36, 1.0), name="S03_Btn_Continue", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t3 + ["Btn_Play_Continue"])
    spawn_text("▶  Continue Adventure (Level 1)", unreal.Vector(0, Y_TXT, 85), size=18.0, color=COL_BROWN, name="S03_Txt_Continue", tags=t3)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, 25), scale=unreal.Vector(0.65, 0.36, 1.0), name="S03_Btn_New", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t3 + ["Btn_Play_New"])
    spawn_text("✦  New Adventure (Level 1)", unreal.Vector(0, Y_TXT, 25), size=18.0, color=COL_BROWN, name="S03_Txt_New", tags=t3)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -35), scale=unreal.Vector(0.65, 0.36, 1.0), name="S03_Btn_Custom", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t3 + ["Btn_Play_Custom"])
    spawn_text("⚙  Custom Play", unreal.Vector(0, Y_TXT, -35), size=18.0, color=COL_BROWN, name="S03_Txt_Custom", tags=t3)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -95), scale=unreal.Vector(0.32, 0.28, 1.0), name="S03_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t3 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(0, Y_TXT, -95), size=15.0, color=COL_BROWN, name="S03_Txt_Back", tags=t3)

    # -------------------------------------------------------------
    # SCREEN 04: Garden Level Map (25 Nodes across 5 Chapters)
    # -------------------------------------------------------------
    t4 = ["Screen_04"]
    # 5 rows x 5 columns of level nodes
    for i in range(25):
        lvl_num = i + 1
        col = i % 5
        row = i // 5
        nx = -200.0 + col * 100.0
        nz = 110.0 - row * 45.0
        is_unlocked = (lvl_num == 1)
        mat = "/Game/Materials/UI/M_UI_Gold" if is_unlocked else "/Game/Materials/UI/M_UI_Cream_Master"
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_LevelNode", unreal.Vector(nx, Y_SURF, nz), scale=unreal.Vector(0.18, 0.18, 1.0), name=f"S04_Node_{lvl_num}", mat_path=mat, tags=t4 + [f"Btn_LevelNode_{lvl_num}"])
        spawn_text(str(lvl_num), unreal.Vector(nx, Y_TXT, nz), size=14.0, color=COL_BROWN, name=f"S04_TxtNode_{lvl_num}", tags=t4)
        
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -115), scale=unreal.Vector(0.30, 0.26, 1.0), name="S04_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t4 + ["Btn_Back"])
    spawn_text("Back to Menu", unreal.Vector(0, Y_TXT, -115), size=14.0, color=COL_BROWN, name="S04_Txt_Back", tags=t4)

    # -------------------------------------------------------------
    # SCREEN 05: Level Preview
    # -------------------------------------------------------------
    t5 = ["Screen_05"]
    spawn_text("Level 1: First Bite", unreal.Vector(0, Y_TXT, 125), size=24.0, color=COL_BROWN, name="S05_Title", tags=t5)
    spawn_text("Chapter 1: The Little Meadow", unreal.Vector(0, Y_TXT, 95), size=15.0, color=COL_BROWN, name="S05_ChTitle", tags=t5)
    
    # Objectives card
    spawn_text("Objectives:", unreal.Vector(-120, Y_TXT, 55), size=16.0, color=COL_BROWN, name="S05_ObjHdr", tags=t5)
    spawn_text("• Reach the Golden Momo Gate\n• Collect 6 delicious Momos\n• Finish with 2+ Hearts", unreal.Vector(0, Y_TXT, 15), size=14.0, color=COL_BROWN, name="S05_ObjList", tags=t5)
    spawn_text("Grid: 15x15  |  Spirits: 1 Follower  |  Gates: None", unreal.Vector(0, Y_TXT, -35), size=13.0, color=COL_BROWN, name="S05_Info", tags=t5)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(80, Y_SURF, -90), scale=unreal.Vector(0.38, 0.35, 1.0), name="S05_Btn_Start", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t5 + ["Btn_Preview_Start"])
    spawn_text("▶  Start", unreal.Vector(80, Y_TXT, -90), size=20.0, color=COL_BROWN, name="S05_Txt_Start", tags=t5)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(-80, Y_SURF, -90), scale=unreal.Vector(0.32, 0.35, 1.0), name="S05_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t5 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(-80, Y_TXT, -90), size=16.0, color=COL_BROWN, name="S05_Txt_Back", tags=t5)

    # -------------------------------------------------------------
    # SCREEN 06: Loading
    # -------------------------------------------------------------
    t6 = ["Screen_06"]
    spawn_text("Loading Garden...", unreal.Vector(0, Y_TXT, 60), size=26.0, color=COL_BROWN, name="S06_Title", tags=t6)
    # Dumpling spinner icon
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_MomoIcon", unreal.Vector(0, Y_SURF, 0), scale=unreal.Vector(0.40, 0.40, 1.0), name="S06_MomoIcon", mat_path="/Game/Materials/Environment/M_Momo_Dough", tags=t6)
    # Progress slider track & knob
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_SliderTrack", unreal.Vector(0, Y_SURF, -50), scale=unreal.Vector(0.65, 0.25, 1.0), name="S06_Track", mat_path="/Game/Materials/UI/M_UI_ToastBrown", tags=t6)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_SliderKnob", unreal.Vector(60, Y_SURF - 2, -50), scale=unreal.Vector(0.25, 0.25, 1.0), name="S06_Knob", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t6)
    spawn_text("Cozy Tip: Eat a momo to temporarily banish nearby spirits!", unreal.Vector(0, Y_TXT, -95), size=13.0, color=COL_BROWN, name="S06_Tip", tags=t6)

    # -------------------------------------------------------------
    # SCREEN 07: Tutorial
    # -------------------------------------------------------------
    t7 = ["Screen_07"]
    spawn_text("How to Play", unreal.Vector(0, Y_TXT, 125), size=26.0, color=COL_BROWN, name="S07_Title", tags=t7)
    spawn_text("1. Move Golumolu with WASD or Virtual Joystick\n\n2. Collect Momos for points, speed, and spirit banishment\n\n3. Reach the Golden Momo Exit Gate to Win!\n\n4. Avoid the 3 mischievous Spirits (Follower, Cutter, Wanderer)", unreal.Vector(0, Y_TXT, 15), size=14.0, color=COL_BROWN, name="S07_Body", tags=t7)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, Y_SURF, -85), scale=unreal.Vector(0.45, 0.38, 1.0), name="S07_Btn_Next", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t7 + ["Btn_Tutorial_Next"])
    spawn_text("Got it! ▶", unreal.Vector(0, Y_TXT, -85), size=20.0, color=COL_BROWN, name="S07_Txt_Next", tags=t7)

    # -------------------------------------------------------------
    # SCREEN 08: Gameplay HUD (3D Bevelled Readouts & Controls)
    # -------------------------------------------------------------
    t8 = ["Screen_08"]
    # 3 Coral Hearts (Top-Left)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Heart", unreal.Vector(-240, Y_SURF, 120), scale=unreal.Vector(0.25, 0.25, 1.0), name="S08_Heart1", mat_path="/Game/Materials/UI/M_UI_CoralHeart", tags=t8)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Heart", unreal.Vector(-200, Y_SURF, 120), scale=unreal.Vector(0.25, 0.25, 1.0), name="S08_Heart2", mat_path="/Game/Materials/UI/M_UI_CoralHeart", tags=t8)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Heart", unreal.Vector(-160, Y_SURF, 120), scale=unreal.Vector(0.25, 0.25, 1.0), name="S08_Heart3", mat_path="/Game/Materials/UI/M_UI_CoralHeart", tags=t8)
    
    # Momo Counter (Top-Center)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_MomoIcon", unreal.Vector(-30, Y_SURF, 120), scale=unreal.Vector(0.28, 0.28, 1.0), name="S08_MomoIcon", mat_path="/Game/Materials/Environment/M_Momo_Dough", tags=t8)
    spawn_text("0 / 6", unreal.Vector(25, Y_TXT, 120), size=18.0, color=COL_BROWN, name="S08_Txt_MomoCount", tags=t8)
    
    # Timer (Top-Right)
    spawn_text("00:00", unreal.Vector(130, Y_TXT, 120), size=18.0, color=COL_BROWN, name="S08_Txt_Timer", tags=t8)
    
    # Map Icon Button & Pause Icon Button (Top-Right)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonIcon", unreal.Vector(200, Y_SURF, 120), scale=unreal.Vector(0.22, 0.22, 1.0), name="S08_Btn_Map", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t8 + ["Btn_HUD_Map"])
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_MapIcon", unreal.Vector(200, Y_SURF - 2, 120), scale=unreal.Vector(0.18, 0.18, 1.0), name="S08_MapIconMesh", mat_path="/Game/Materials/UI/M_UI_ToastBrown", tags=t8)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonIcon", unreal.Vector(245, Y_SURF, 120), scale=unreal.Vector(0.22, 0.22, 1.0), name="S08_Btn_Pause", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t8 + ["Btn_HUD_Pause"])
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_PauseIcon", unreal.Vector(245, Y_SURF - 2, 120), scale=unreal.Vector(0.18, 0.18, 1.0), name="S08_PauseIconMesh", mat_path="/Game/Materials/UI/M_UI_ToastBrown", tags=t8)
    
    # Touch Controls (Bottom-Left Joystick base & Knob, Bottom-Right Puff Dash)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonIcon", unreal.Vector(-210, Y_SURF, -80), scale=unreal.Vector(0.45, 0.45, 1.0), name="S08_JoyBase", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t8)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonIcon", unreal.Vector(-210, Y_SURF - 2, -80), scale=unreal.Vector(0.25, 0.25, 1.0), name="S08_JoyKnob", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t8)
    spawn_text("Move", unreal.Vector(-210, Y_TXT, -125), size=12.0, color=COL_BROWN, name="S08_Txt_Move", tags=t8)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(210, Y_SURF, -80), scale=unreal.Vector(0.35, 0.35, 1.0), name="S08_Btn_Dash", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t8 + ["Btn_HUD_Dash"])
    spawn_text("💨 Puff Dash", unreal.Vector(210, Y_TXT, -80), size=15.0, color=COL_BROWN, name="S08_Txt_Dash", tags=t8)

    # -------------------------------------------------------------
    # SCREEN 09: Map Overlay
    # -------------------------------------------------------------
    t9 = ["Screen_09"]
    spawn_text("Garden Maze Map", unreal.Vector(0, Y_TXT, 125), size=24.0, color=COL_BROWN, name="S09_Title", tags=t9)
    # Minimap frame
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_CardFrame", unreal.Vector(0, Y_SURF, 20), scale=unreal.Vector(0.50, 0.50, 1.0), name="S09_MiniMapCard", mat_path="/Game/Materials/Environment/M_Grass_Path", tags=t9)
    # Legend pins
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_MomoIcon", unreal.Vector(-180, Y_SURF, 50), scale=unreal.Vector(0.20, 0.20, 1.0), name="S09_Leg_Momo", mat_path="/Game/Materials/Environment/M_Momo_Dough", tags=t9)
    spawn_text("Momo Collectible", unreal.Vector(-100, Y_TXT, 50), size=12.0, color=COL_BROWN, name="S09_Txt_LegMomo", tags=t9)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_LeafPair", unreal.Vector(-180, Y_SURF, 10), scale=unreal.Vector(0.20, 0.20, 1.0), name="S09_Leg_Gate", mat_path="/Game/Materials/UI/M_UI_LeafGreen", tags=t9)
    spawn_text("Golden Exit Gate", unreal.Vector(-100, Y_TXT, 10), size=12.0, color=COL_BROWN, name="S09_Txt_LegGate", tags=t9)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_SpiritIcon", unreal.Vector(-180, Y_SURF, -30), scale=unreal.Vector(0.20, 0.20, 1.0), name="S09_Leg_Spirit", mat_path="/Game/Materials/UI/M_UI_SpiritWhite", tags=t9)
    spawn_text("Spirits (Spooky!)", unreal.Vector(-100, Y_TXT, -30), size=12.0, color=COL_BROWN, name="S09_Txt_LegSpirit", tags=t9)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -95), scale=unreal.Vector(0.32, 0.30, 1.0), name="S09_Btn_Close", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t9 + ["Btn_Back"])
    spawn_text("Close Map (X)", unreal.Vector(0, Y_TXT, -95), size=16.0, color=COL_BROWN, name="S09_Txt_Close", tags=t9)

    # -------------------------------------------------------------
    # SCREEN 10: Pause
    # -------------------------------------------------------------
    t10 = ["Screen_10"]
    pause_btns = [
        (80, "Btn_Pause_Resume", "▶  Resume", "/Game/Materials/UI/M_UI_Gold"),
        (25, "Btn_Pause_Restart", "↻  Restart Level", "/Game/Materials/UI/M_UI_Cream_Master"),
        (-30, "Btn_Pause_Settings", "⚙  Settings", "/Game/Materials/UI/M_UI_Cream_Master"),
        (-85, "Btn_Pause_Exit", "⌂  Exit to Menu", "/Game/Materials/UI/M_UI_Cream_Master")
    ]
    for z_pos, btn_tag, label, mat in pause_btns:
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill" if "Gold" in mat else "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, z_pos), scale=unreal.Vector(0.55, 0.32, 1.0), name=f"S10_{btn_tag}", mat_path=mat, tags=t10 + [btn_tag])
        spawn_text(label, unreal.Vector(0, Y_TXT, z_pos), size=18.0, color=COL_BROWN, name=f"S10_Txt_{btn_tag}", tags=t10)

    # -------------------------------------------------------------
    # SCREEN 11: Victory
    # -------------------------------------------------------------
    t11 = ["Screen_11"]
    spawn_text("Level Complete! 🏆", unreal.Vector(0, Y_TXT, 125), size=26.0, color=COL_BROWN, name="S11_Title", tags=t11)
    # 3 Gold Stars
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Star", unreal.Vector(-70, Y_SURF, 75), scale=unreal.Vector(0.35, 0.35, 1.0), name="S11_Star1", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t11)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Star", unreal.Vector(0, Y_SURF, 85), scale=unreal.Vector(0.42, 0.42, 1.0), name="S11_Star2", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t11)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Star", unreal.Vector(70, Y_SURF, 75), scale=unreal.Vector(0.35, 0.35, 1.0), name="S11_Star3", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t11)
    
    spawn_text("Time: 01:18  |  Momos: 6/6  |  Hearts: 3/3", unreal.Vector(0, Y_TXT, 15), size=16.0, color=COL_BROWN, name="S11_Stats", tags=t11)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(90, Y_SURF, -70), scale=unreal.Vector(0.38, 0.35, 1.0), name="S11_Btn_Next", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t11 + ["Btn_Victory_Next"])
    spawn_text("Next Level ▶", unreal.Vector(90, Y_TXT, -70), size=17.0, color=COL_BROWN, name="S11_Txt_Next", tags=t11)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(-90, Y_SURF, -70), scale=unreal.Vector(0.35, 0.35, 1.0), name="S11_Btn_Replay", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t11 + ["Btn_Victory_Replay"])
    spawn_text("↻ Replay", unreal.Vector(-90, Y_TXT, -70), size=17.0, color=COL_BROWN, name="S11_Txt_Replay", tags=t11)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -120), scale=unreal.Vector(0.30, 0.25, 1.0), name="S11_Btn_Map", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t11 + ["Btn_Back"])
    spawn_text("Level Map", unreal.Vector(0, Y_TXT, -120), size=14.0, color=COL_BROWN, name="S11_Txt_Map", tags=t11)

    # -------------------------------------------------------------
    # SCREEN 12: Defeat
    # -------------------------------------------------------------
    t12 = ["Screen_12"]
    spawn_text("Oh, Crumbs!", unreal.Vector(0, Y_TXT, 125), size=28.0, color=COL_BROWN, name="S12_Title", tags=t12)
    spawn_text("The spirits caught you!\nEat momos to temporarily banish them next time.", unreal.Vector(0, Y_TXT, 45), size=15.0, color=COL_BROWN, name="S12_Body", tags=t12)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, Y_SURF, -30), scale=unreal.Vector(0.48, 0.38, 1.0), name="S12_Btn_Retry", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t12 + ["Btn_Defeat_Retry"])
    spawn_text("↻  Retry Level", unreal.Vector(0, Y_TXT, -30), size=20.0, color=COL_BROWN, name="S12_Txt_Retry", tags=t12)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -90), scale=unreal.Vector(0.36, 0.30, 1.0), name="S12_Btn_Menu", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t12 + ["Btn_Back"])
    spawn_text("⌂  Main Menu", unreal.Vector(0, Y_TXT, -90), size=16.0, color=COL_BROWN, name="S12_Txt_Menu", tags=t12)

    # -------------------------------------------------------------
    # SCREEN 13: Chapter Complete
    # -------------------------------------------------------------
    t13 = ["Screen_13"]
    spawn_text("Chapter Cleared! 🌸", unreal.Vector(0, Y_TXT, 120), size=26.0, color=COL_BROWN, name="S13_Title", tags=t13)
    spawn_text("You conquered the Little Meadow!\n\nNew Reward Unlocked: Garden Cap", unreal.Vector(0, Y_TXT, 35), size=16.0, color=COL_BROWN, name="S13_Body", tags=t13)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, Y_SURF, -70), scale=unreal.Vector(0.48, 0.38, 1.0), name="S13_Btn_Continue", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t13 + ["Btn_Chapter_Continue"])
    spawn_text("▶  Continue Adventure", unreal.Vector(0, Y_TXT, -70), size=18.0, color=COL_BROWN, name="S13_Txt_Continue", tags=t13)

    # -------------------------------------------------------------
    # SCREEN 14: Golumolu Closet
    # -------------------------------------------------------------
    t14 = ["Screen_14"]
    closet_tabs = [(-140, "Outfits"), (0, "Hats"), (140, "Accessories")]
    for x_pos, tab_name in closet_tabs:
        mat = "/Game/Materials/UI/M_UI_Gold" if tab_name == "Hats" else "/Game/Materials/UI/M_UI_Cream_Master"
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_Tab_Pill", unreal.Vector(x_pos, Y_SURF, 115), scale=unreal.Vector(0.25, 0.25, 1.0), name=f"S14_Tab_{tab_name}", mat_path=mat, tags=t14)
        spawn_text(tab_name, unreal.Vector(x_pos, Y_TXT, 115), size=14.0, color=COL_BROWN, name=f"S14_Txt_{tab_name}", tags=t14)
        
    closet_items = [
        (-140, "Garden Cap", True),
        (0, "Leaf Scarf", True),
        (140, "Golden Crown", False)
    ]
    for x_pos, iname, unlocked in closet_items:
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ChoiceChip", unreal.Vector(x_pos, Y_SURF, 20), scale=unreal.Vector(0.24, 0.35, 1.0), name=f"S14_Item_{iname}", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t14)
        status = "Equipped" if iname == "Garden Cap" else ("Unlocked" if unlocked else "Locked")
        spawn_text(f"{iname}\n[{status}]", unreal.Vector(x_pos, Y_TXT, 20), size=12.0, color=COL_BROWN, name=f"S14_Txt_{iname}", tags=t14)
        
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -95), scale=unreal.Vector(0.30, 0.30, 1.0), name="S14_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t14 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(0, Y_TXT, -95), size=16.0, color=COL_BROWN, name="S14_Txt_Back", tags=t14)

    # -------------------------------------------------------------
    # SCREEN 15: Spirit Book
    # -------------------------------------------------------------
    t15 = ["Screen_15"]
    spirits = [
        (-150, "Follower", "Chases directly\nSpeed: 320\nTrait: Persistent"),
        (0, "Cutter", "Cuts off paths\nSpeed: 350\nTrait: Cunning"),
        (150, "Wanderer", "Patrols junctions\nSpeed: 300\nTrait: Unpredictable")
    ]
    for x_pos, sname, desc in spirits:
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ChoiceChip", unreal.Vector(x_pos, Y_SURF, 40), scale=unreal.Vector(0.26, 0.42, 1.0), name=f"S15_Card_{sname}", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t15)
        spawn_text(f"✦ {sname} ✦\n\n{desc}", unreal.Vector(x_pos, Y_TXT, 40), size=11.0, color=COL_BROWN, name=f"S15_Txt_{sname}", tags=t15)
        
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -95), scale=unreal.Vector(0.30, 0.30, 1.0), name="S15_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t15 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(0, Y_TXT, -95), size=16.0, color=COL_BROWN, name="S15_Txt_Back", tags=t15)

    # -------------------------------------------------------------
    # SCREEN 16: Sticker Collection (12 Stickers)
    # -------------------------------------------------------------
    t16 = ["Screen_16"]
    stickers = ["Golden Momo", "Happy Golu", "Follower", "Cutter", "Wanderer", "Daisy", "Clover", "Mushroom", "Garden Gate", "Magic Leaf", "Star Dumpling", "Grand Crown"]
    for i, sname in enumerate(stickers):
        col = i % 4
        row = i // 4
        sx = -180.0 + col * 120.0
        sz = 80.0 - row * 50.0
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ChoiceChip", unreal.Vector(sx, Y_SURF, sz), scale=unreal.Vector(0.20, 0.20, 1.0), name=f"S16_Sticker_{i+1}", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t16)
        spawn_text(sname, unreal.Vector(sx, Y_TXT, sz), size=10.0, color=COL_BROWN, name=f"S16_Txt_{i+1}", tags=t16)
        
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -105), scale=unreal.Vector(0.30, 0.28, 1.0), name="S16_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t16 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(0, Y_TXT, -105), size=15.0, color=COL_BROWN, name="S16_Txt_Back", tags=t16)

    # -------------------------------------------------------------
    # SCREEN 17: Custom Play
    # -------------------------------------------------------------
    t17 = ["Screen_17"]
    spawn_text("Custom Challenge", unreal.Vector(0, Y_TXT, 125), size=24.0, color=COL_BROWN, name="S17_Title", tags=t17)
    opts = [
        ("Spirits: [ 1 ]  2   3   4", 65),
        ("Maze Size: [ Small ]  Medium  Large", 20),
        ("Ghost Speed: Slow  [ Normal ]  Fast", -25)
    ]
    for opt_txt, z_pos in opts:
        spawn_text(opt_txt, unreal.Vector(0, Y_TXT, z_pos), size=16.0, color=COL_BROWN, name=f"S17_Opt_{z_pos}", tags=t17)
        
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(80, Y_SURF, -85), scale=unreal.Vector(0.38, 0.35, 1.0), name="S17_Btn_Start", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t17 + ["Btn_Custom_Start"])
    spawn_text("▶  Start", unreal.Vector(80, Y_TXT, -85), size=18.0, color=COL_BROWN, name="S17_Txt_Start", tags=t17)
    
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(-80, Y_SURF, -85), scale=unreal.Vector(0.30, 0.35, 1.0), name="S17_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t17 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(-80, Y_TXT, -85), size=16.0, color=COL_BROWN, name="S17_Txt_Back", tags=t17)

    # -------------------------------------------------------------
    # SCREEN 18: Settings
    # -------------------------------------------------------------
    t18 = ["Screen_18"]
    spawn_text("Settings", unreal.Vector(0, Y_TXT, 125), size=26.0, color=COL_BROWN, name="S18_Title", tags=t18)
    sliders = [
        ("Master Volume: 100%", 65),
        ("Music Volume: 80%", 20),
        ("Sound Effects: 100%", -25)
    ]
    for sl_label, z_pos in sliders:
        spawn_text(sl_label, unreal.Vector(-90, Y_TXT, z_pos), size=15.0, color=COL_BROWN, name=f"S18_Lbl_{z_pos}", tags=t18)
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_SliderTrack", unreal.Vector(90, Y_SURF, z_pos), scale=unreal.Vector(0.35, 0.20, 1.0), name=f"S18_Trk_{z_pos}", mat_path="/Game/Materials/UI/M_UI_ToastBrown", tags=t18)
        spawn_mesh(world, "/Game/Meshes/UI/SM_UI_SliderKnob", unreal.Vector(110, Y_SURF - 2, z_pos), scale=unreal.Vector(0.20, 0.20, 1.0), name=f"S18_Knb_{z_pos}", mat_path="/Game/Materials/UI/M_UI_Gold", tags=t18)
        
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -85), scale=unreal.Vector(0.30, 0.30, 1.0), name="S18_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t18 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(0, Y_TXT, -85), size=16.0, color=COL_BROWN, name="S18_Txt_Back", tags=t18)

    # -------------------------------------------------------------
    # SCREEN 19: Credits
    # -------------------------------------------------------------
    t19 = ["Screen_19"]
    spawn_text("MOMO MAZE", unreal.Vector(0, Y_TXT, 120), size=28.0, color=COL_BROWN, name="S19_Title", tags=t19)
    spawn_text("A Cozy Garden Adventure\n\nCrafted with Unreal Engine 5.8 & Blender 5.2\nDeveloped for Mobile & Desktop\nAntigravity Game Studios", unreal.Vector(0, Y_TXT, 30), size=15.0, color=COL_BROWN, name="S19_Body", tags=t19)
    spawn_mesh(world, "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, Y_SURF, -85), scale=unreal.Vector(0.30, 0.30, 1.0), name="S19_Btn_Back", mat_path="/Game/Materials/UI/M_UI_Cream_Master", tags=t19 + ["Btn_Back"])
    spawn_text("Back", unreal.Vector(0, Y_TXT, -85), size=16.0, color=COL_BROWN, name="S19_Txt_Back", tags=t19)

    # By default, hide all screens except Screen_02 (Main Menu)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        t = [str(x) for x in a.tags]
        for s_idx in range(1, 20):
            s_tag = f"Screen_{s_idx:02d}"
            if s_tag in t:
                # Keep Screen 02 visible, hide all other screens
                should_hide = (s_idx != 2)
                a.set_actor_hidden_in_game(should_hide)
                
    unreal.EditorLevelLibrary.save_current_level()
    log("All 19 screens successfully created, styled with 3D bevels, and saved!")

if __name__ == "__main__":
    build_all_screens()
