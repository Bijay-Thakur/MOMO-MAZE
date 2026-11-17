import unreal

subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
with open("D:/Projects/MOMO MAZE/UnrealProject/subobject_methods.txt", "w") as f:
    for m in dir(subsystem):
        if not m.startswith("_"):
            f.write(f"{m}\n")
