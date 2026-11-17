import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/mat_lib_methods.txt", "w") as f:
    for m in dir(unreal.MaterialEditingLibrary):
        if not m.startswith("_"):
            f.write(f"{m}\n")
