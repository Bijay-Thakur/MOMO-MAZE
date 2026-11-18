import unreal

def test_render():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem.load_level("/Game/Maps/LVL_MomoMaze_Game")
    out_file = "D:/Projects/MOMO MAZE/Screenshots/editor_capture_game_map.png"
    cmd = f"HighResShot 1280x720 filename=\"{out_file}\""
    unreal.SystemLibrary.execute_console_command(None, cmd)

if __name__ == "__main__":
    test_render()
