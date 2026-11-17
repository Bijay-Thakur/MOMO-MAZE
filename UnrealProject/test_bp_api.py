import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/test_bp_api.txt", "w") as f:
    try:
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        f.write(f"SubobjectDataSubsystem: {subsystem}\n")
    except Exception as e:
        f.write(f"SubobjectDataSubsystem error: {e}\n")

    # Check BP_GolumoluCharacter
    bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
    f.write(f"BP_GolumoluCharacter: {bp}\n")
    if bp:
        f.write(f"GeneratedClass: {bp.generated_class()}\n")
