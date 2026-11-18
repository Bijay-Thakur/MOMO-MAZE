import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/bp_editor_lib.txt", "w") as f:
    f.write("\n".join(dir(unreal.BlueprintEditorLibrary)))
