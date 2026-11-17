import unreal

bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

# Inspect subobject data
subobject_handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
print(f"Subobject handles count: {len(subobject_handles)}")
for h in subobject_handles:
    data = subsystem.k2_find_subobject_data_from_handle(h)
    print(f"Handle data: {subsystem.get_subobject_display_name(data)}")
