import unreal

subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
with open("D:/Projects/MOMO MAZE/UnrealProject/subobject_data_info.txt", "w") as f:
    for h in handles:
        data = subsystem.k2_find_subobject_data_from_handle(h)
        obj = subsystem.get_object_for_subobject_data(data)
        f.write(f"Handle: {h} -> Object: {obj} ({obj.get_class().get_name() if obj else 'None'})\n")
