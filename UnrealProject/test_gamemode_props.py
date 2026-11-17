import unreal

bp_mode = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoGameMode")
bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")

gen_golu = bp_golu.generated_class()
cdo = unreal.get_default_object(bp_mode.generated_class())
print(f"GameMode CDO: {cdo}")
print(f"Current default_pawn_class: {cdo.get_editor_property('default_pawn_class')}")

cdo.set_editor_property("default_pawn_class", gen_golu)
print(f"New default_pawn_class: {cdo.get_editor_property('default_pawn_class')}")

unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_MomoGameMode")
