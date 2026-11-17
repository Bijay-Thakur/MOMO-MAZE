import unreal

subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
print(f"Handles count: {len(handles)}")
for h in handles:
    obj = subsystem.k2_find_subobject_data_from_handle(h)
    print(f"Handle: {h}, obj: {obj}")
