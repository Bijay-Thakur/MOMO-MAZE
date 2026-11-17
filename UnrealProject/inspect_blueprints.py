import unreal

bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
bp_mode = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoGameMode")
bp_mgr = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoMazeManager")

with open("D:/Projects/MOMO MAZE/UnrealProject/bp_inspect.txt", "w") as f:
    f.write(f"bp_golu: {bp_golu}, class: {bp_golu.generated_class()}\n")
    f.write(f"bp_mode: {bp_mode}, class: {bp_mode.generated_class()}\n")
    f.write(f"bp_mgr: {bp_mgr}, class: {bp_mgr.generated_class()}\n")
