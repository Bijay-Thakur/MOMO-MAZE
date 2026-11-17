import unreal

print("EditorLevelLibrary:", hasattr(unreal, "EditorLevelLibrary"))
print("LevelEditorSubsystem:", hasattr(unreal, "LevelEditorSubsystem"))
subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem) if hasattr(unreal, "LevelEditorSubsystem") else None
print("Subsystem instance:", subsystem)
