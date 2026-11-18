import unreal
import time

def test_render():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    for map_path, name in [("/Game/Maps/LVL_MomoMaze_Game", "game_map"), ("/Game/MomoMaze/Maps/M_Maze_31x31", "maze_31x31")]:
        subsystem.load_level(map_path)
        out_file = f"D:/Projects/MOMO MAZE/Screenshots/editor_capture_{name}.png"
        cmd = f"HighResShot 1280x720 filename=\"{out_file}\""
        unreal.SystemLibrary.execute_console_command(None, cmd)
        print(f"Captured: {out_file}")

if __name__ == "__main__":
    test_render()
