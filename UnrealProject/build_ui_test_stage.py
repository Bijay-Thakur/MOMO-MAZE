import unreal

def build_stage():
    level_path = "/Game/Maps/LVL_UI_TestStage"
    
    # 1. Create Level using LevelEditorSubsystem
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        world = subsystem.load_level(level_path)
    else:
        world = subsystem.new_level(level_path)
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Clean any old actors in world
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        unreal.EditorLevelLibrary.destroy_actor(a)
    
    # 2. Lighting & PostProcess
    dir_light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, -300, 500), unreal.Rotator(-50, 45, 0))
    dir_light = dir_light_actor.root_component
    dir_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    dir_light.set_editor_property("intensity", 7.0)
    dir_light.set_editor_property("light_color", unreal.Color(255, 240, 215, 255))
    
    sky_light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 400), unreal.Rotator(0, 0, 0))
    sky_light = sky_light_actor.root_component
    sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sky_light.set_editor_property("intensity", 2.5)
    sky_light.set_editor_property("light_color", unreal.Color(230, 245, 255, 255))
    
    pp_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    pp_actor.set_editor_property("unbound", True)
    pp_settings = pp_actor.settings
    pp_settings.bloom_intensity = 0.5
    pp_settings.bloom_threshold = 0.8
    pp_settings.auto_exposure_min_brightness = 1.0
    pp_settings.auto_exposure_max_brightness = 1.0
    pp_actor.settings = pp_settings

    # 3. Camera
    cam_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0, -600, 40), unreal.Rotator(0, 90, 0))
    cam = cam_actor.camera_component
    cam.set_editor_property("field_of_view", 48.0)
    cam.set_editor_property("aspect_ratio", 1.777778)
    cam_actor.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)

    # 4. Helper function to spawn static mesh actor
    def spawn_mesh(mesh_path, location, rotation=unreal.Rotator(0,0,0), scale=unreal.Vector(1,1,1), name="MeshActor", mat_override=None):
        mesh_asset = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not mesh_asset:
            print(f"Warning: Could not load mesh {mesh_path}")
            return None
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
        actor.set_actor_label(name)
        comp = actor.static_mesh_component
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        comp.set_static_mesh(mesh_asset)
        actor.set_actor_scale3d(scale)
        if mat_override:
            mat_asset = unreal.EditorAssetLibrary.load_asset(mat_override)
            if mat_asset:
                comp.set_material(0, mat_asset)
        return actor

    def spawn_text(text_str, location, rotation=unreal.Rotator(0,90,0), size=24.0, color=unreal.Color(95, 51, 31, 255)):
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, location, rotation)
        comp = actor.text_render
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        comp.set_text(unreal.Text(text_str))
        comp.set_world_size(size)
        comp.set_text_render_color(color)
        comp.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        comp.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        return actor

    # 5. Garden Diorama Backdrop
    spawn_mesh("/Game/Meshes/Environment/SM_Path_Tile", unreal.Vector(0, 0, -180), scale=unreal.Vector(15, 10, 1), name="GroundPlane")
    for x_offset in range(-600, 700, 200):
        spawn_mesh("/Game/Meshes/Environment/SM_Hedge_Straight", unreal.Vector(x_offset, 120, -100), rotation=unreal.Rotator(0, 0, 0), scale=unreal.Vector(1.8, 1.8, 2.5), name=f"Hedge_Back_{x_offset}")
    spawn_mesh("/Game/Meshes/Environment/SM_Hedge_Corner", unreal.Vector(-700, 100, -100), rotation=unreal.Rotator(0, 0, 0), scale=unreal.Vector(2.0, 2.0, 2.5), name="Hedge_Corner_L")
    spawn_mesh("/Game/Meshes/Environment/SM_Hedge_Corner", unreal.Vector(700, 100, -100), rotation=unreal.Rotator(0, 90, 0), scale=unreal.Vector(2.0, 2.0, 2.5), name="Hedge_Corner_R")
    
    spawn_mesh("/Game/Meshes/Environment/SM_Flower_Cluster", unreal.Vector(-360, 40, -150), scale=unreal.Vector(1.5, 1.5, 1.5), name="Flowers_L")
    spawn_mesh("/Game/Meshes/Environment/SM_Flower_Cluster", unreal.Vector(360, 40, -150), scale=unreal.Vector(1.5, 1.5, 1.5), name="Flowers_R")

    # Cameo Characters
    spawn_mesh("/Game/Meshes/Characters/SK_Golumolu", unreal.Vector(-320, -10, -120), rotation=unreal.Rotator(0, 75, 0), scale=unreal.Vector(1.3, 1.3, 1.3), name="Cameo_Golumolu")
    spawn_mesh("/Game/Meshes/Characters/SK_Ghost_Follower", unreal.Vector(320, 0, 40), rotation=unreal.Rotator(0, 105, 0), scale=unreal.Vector(1.1, 1.1, 1.1), name="Cameo_Ghost")

    # 6. Central 3D Menu Card
    spawn_mesh("/Game/Meshes/UI/SM_UI_CardFrame", unreal.Vector(0, 0, 40), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(68, 1, 75), name="UI_CardFrame", mat_override="/Game/Materials/UI/M_UI_Cream")
    
    # Header Ribbon
    spawn_mesh("/Game/Meshes/UI/SM_UI_HeaderRibbon", unreal.Vector(0, -8, 205), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(55, 1, 45), name="UI_HeaderRibbon", mat_override="/Game/Materials/UI/M_UI_ToastBrown")
    spawn_text("MOMO MAZE 3D UI", unreal.Vector(0, -16, 205), size=24.0, color=unreal.Color(255, 244, 222, 255))
    
    # Corner Leaf Pair and Flower
    spawn_mesh("/Game/Meshes/UI/SM_UI_LeafPair", unreal.Vector(-210, -12, 190), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(35, 1, 35), name="Leaf_TopL", mat_override="/Game/Materials/UI/M_UI_LeafGreen")
    spawn_mesh("/Game/Meshes/UI/SM_UI_LeafPair", unreal.Vector(210, -12, 190), rotation=unreal.Rotator(90, 180, 0), scale=unreal.Vector(35, 1, 35), name="Leaf_TopR", mat_override="/Game/Materials/UI/M_UI_LeafGreen")
    spawn_mesh("/Game/Meshes/UI/SM_UI_FlowerCorner", unreal.Vector(190, -14, 180), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(30, 1, 30), name="Flower_TopR")

    # 7. Interactive 3D Controls
    # Primary 3D Pill Button (Play)
    spawn_mesh("/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill", unreal.Vector(0, -12, 125), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(65, 1, 55), name="Btn_Primary_Play", mat_override="/Game/Materials/UI/M_UI_Gold")
    spawn_text("Play Adventure", unreal.Vector(0, -20, 125), size=26.0, color=unreal.Color(95, 51, 31, 255))
    
    # Secondary 3D Pill Button (Levels)
    spawn_mesh("/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", unreal.Vector(0, -10, 55), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(65, 1, 50), name="Btn_Secondary_Levels", mat_override="/Game/Materials/UI/M_UI_Cream")
    spawn_text("Level Select (25 Levels)", unreal.Vector(0, -18, 55), size=22.0, color=unreal.Color(95, 51, 31, 255))

    # Tabs
    spawn_mesh("/Game/Meshes/UI/SM_UI_Tab_Pill", unreal.Vector(-95, -14, -10), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(50, 1, 45), name="Tab_Spirits_Active", mat_override="/Game/Materials/UI/M_UI_Gold")
    spawn_text("Spirits (3)", unreal.Vector(-95, -20, -10), size=18.0, color=unreal.Color(95, 51, 31, 255))

    spawn_mesh("/Game/Meshes/UI/SM_UI_Tab_Pill", unreal.Vector(95, -8, -10), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(50, 1, 45), name="Tab_Closet_Inactive", mat_override="/Game/Materials/UI/M_UI_Cream")
    spawn_text("Closet", unreal.Vector(95, -14, -10), size=18.0, color=unreal.Color(120, 80, 50, 255))

    # Toggle
    spawn_mesh("/Game/Meshes/UI/SM_UI_ToggleTrack", unreal.Vector(-60, -8, -75), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(55, 1, 50), name="Toggle_Track", mat_override="/Game/Materials/UI/M_UI_ToastBrown")
    spawn_mesh("/Game/Meshes/UI/SM_UI_ToggleKnob", unreal.Vector(-35, -14, -75), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(45, 1, 45), name="Toggle_Knob_ON", mat_override="/Game/Materials/UI/M_UI_Gold")
    spawn_text("Living Gates: ON", unreal.Vector(70, -10, -75), size=18.0, color=unreal.Color(95, 51, 31, 255))

    # Slider
    spawn_mesh("/Game/Meshes/UI/SM_UI_SliderTrack", unreal.Vector(-50, -8, -135), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(50, 1, 45), name="Slider_Track", mat_override="/Game/Materials/UI/M_UI_ToastBrown")
    spawn_mesh("/Game/Meshes/UI/SM_UI_SliderKnob", unreal.Vector(-15, -14, -135), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(45, 1, 45), name="Slider_Knob", mat_override="/Game/Materials/UI/M_UI_Gold")
    spawn_text("Music Volume: 75%", unreal.Vector(85, -10, -135), size=18.0, color=unreal.Color(95, 51, 31, 255))

    # Icon Buttons and Tokens
    spawn_mesh("/Game/Meshes/UI/SM_UI_ButtonIcon", unreal.Vector(-185, -10, 125), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(45, 1, 45), name="Btn_Icon_Back", mat_override="/Game/Materials/UI/M_UI_Cream")
    spawn_mesh("/Game/Meshes/UI/SM_UI_PauseIcon", unreal.Vector(-185, -16, 125), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(35, 1, 35), name="Icon_Pause", mat_override="/Game/Materials/UI/M_UI_ToastBrown")

    spawn_mesh("/Game/Meshes/UI/SM_UI_ButtonIcon", unreal.Vector(185, -10, 125), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(45, 1, 45), name="Btn_Icon_Map", mat_override="/Game/Materials/UI/M_UI_Cream")
    spawn_mesh("/Game/Meshes/UI/SM_UI_MapIcon", unreal.Vector(185, -16, 125), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(35, 1, 35), name="Icon_Map", mat_override="/Game/Materials/UI/M_UI_Gold")

    spawn_mesh("/Game/Meshes/UI/SM_UI_Star", unreal.Vector(-185, -10, -10), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(35, 1, 35), name="Token_Star", mat_override="/Game/Materials/UI/M_UI_Gold")
    spawn_mesh("/Game/Meshes/UI/SM_UI_Heart", unreal.Vector(185, -10, -10), rotation=unreal.Rotator(90, 0, 0), scale=unreal.Vector(35, 1, 35), name="Token_Heart", mat_override="/Game/Materials/UI/M_UI_CoralHeart")

    # 8. Save Level cleanly
    unreal.EditorLoadingAndSavingUtils.save_map(world, level_path)
    print("LVL_UI_TestStage freshly created, fully populated and saved via EditorLoadingAndSavingUtils!")

if __name__ == "__main__":
    build_stage()
