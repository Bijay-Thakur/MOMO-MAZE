import unreal

def create_bp(asset_name, package_path, parent_class=unreal.Actor):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_class)
    
    full_path = f"{package_path}/{asset_name}"
    existing = unreal.EditorAssetLibrary.load_asset(full_path)
    if existing:
        return existing
        
    bp = asset_tools.create_asset(asset_name, package_path, unreal.Blueprint, factory)
    unreal.EditorAssetLibrary.save_asset(full_path)
    print(f"Created blueprint: {full_path}")
    return bp

def main():
    package_path = "/Game/Blueprints/UI_3D"
    
    create_bp("BP_3DUIButton", package_path)
    create_bp("BP_3DTab", package_path)
    create_bp("BP_3DToggle", package_path)
    create_bp("BP_3DSlider", package_path)
    
    core_path = "/Game/Blueprints/Core"
    create_bp("BP_MomoGameMode", core_path, unreal.GameModeBase)
    create_bp("BP_MomoPlayerController", core_path, unreal.PlayerController)
    create_bp("BP_MomoGameInstance", core_path, unreal.GameInstance)
    create_bp("BP_GolumoluCharacter", core_path, unreal.Character)
    create_bp("BP_MomoMazeManager", core_path, unreal.Actor)
    create_bp("BP_SpiritDirector", core_path, unreal.Actor)
    create_bp("BP_SpiritCharacter", core_path, unreal.Character)
    create_bp("BP_MomoUIManager", core_path, unreal.Actor)
    create_bp("SG_MomoSaveGame", core_path, unreal.SaveGame)

    print("All core and UI blueprints successfully initialized!")

if __name__ == "__main__":
    main()
