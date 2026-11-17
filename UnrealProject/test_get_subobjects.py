import unreal

bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
with open("D:/Projects/MOMO MAZE/UnrealProject/test_objects.txt", "w") as f:
    for h in handles:
        data = subsystem.k2_find_subobject_data_from_handle(h)
        name = lib.get_variable_name(data)
        disp = lib.get_display_name(data)
        obj = lib.get_object(data)
        f.write(f"Handle Name: {name}, Display: {disp}, Obj: {obj} ({type(obj)})\n")
