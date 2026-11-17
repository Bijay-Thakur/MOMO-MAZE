import unreal

lib = unreal.SubobjectDataBlueprintFunctionLibrary
with open("D:/Projects/MOMO MAZE/UnrealProject/subobject_lib_methods.txt", "w") as f:
    for m in dir(lib):
        if not m.startswith("_"):
            f.write(f"{m}\n")
