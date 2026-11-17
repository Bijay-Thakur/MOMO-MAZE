import unreal
import time

def capture():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem.load_map("/Game/Maps/LVL_UI_TestStage")
    
    # We can execute console commands via SystemLibrary
    out_dir = r"D:/Projects/MOMO MAZE/Screenshots"
    import os
    os.makedirs(out_dir, exist_ok=True)
    
    # Let's verify console command execution
    cmd_1080 = f"HighResShot 1920x1080 filename={out_dir}/Stage1_3D_UI_1920x1080.png"
    cmd_720 = f"HighResShot 1280x720 filename={out_dir}/Stage1_3D_UI_1280x720.png"
    
    unreal.SystemLibrary.execute_console_command(None, cmd_1080)
    unreal.SystemLibrary.execute_console_command(None, cmd_720)
    print("Executed screenshot console commands!")

if __name__ == "__main__":
    capture()
