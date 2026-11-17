import unreal

def configure_core():
    # 1. PlayerController
    pc_bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoPlayerController")
    if pc_bp:
        pc_cdo = unreal.get_default_object(pc_bp.generated_class())
        pc_cdo.set_editor_property("show_mouse_cursor", True)
        pc_cdo.set_editor_property("enable_click_events", True)
        pc_cdo.set_editor_property("enable_touch_events", True)
        pc_cdo.set_editor_property("enable_touch_over_events", True)
        unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_MomoPlayerController")
        print("Configured BP_MomoPlayerController defaults")

    # 2. GameMode
    gm_bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoGameMode")
    if gm_bp and pc_bp:
        gm_cdo = unreal.get_default_object(gm_bp.generated_class())
        gm_cdo.set_editor_property("player_controller_class", pc_bp.generated_class())
        unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_MomoGameMode")
        print("Configured BP_MomoGameMode defaults")

    # 3. In LVL_UI_TestStage, set the CameraActor as AutoPlayer0 / Active view target
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem.load_level("/Game/Maps/LVL_UI_TestStage")
    
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    cam_actor = None
    for a in actors:
        if isinstance(a, unreal.CameraActor):
            cam_actor = a
            # Set Auto Player Activation to Player 0
            cam_actor.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
            print(f"Set auto_activate_for_player on {cam_actor.get_name()}")
            break
            
    unreal.EditorLevelLibrary.save_current_level()
    print("Level updated and saved!")

if __name__ == "__main__":
    configure_core()
