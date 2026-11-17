import unreal
import os

def import_textures():
    texture_dir = "D:/Projects/MOMO MAZE/UnrealProject/Content/Textures/UI"
    files = [f for f in os.listdir(texture_dir) if f.endswith(".png")]
    print(f"Importing {len(files)} UI textures into Unreal...")
    
    tasks = []
    for f in files:
        task = unreal.AssetImportTask()
        task.filename = f"{texture_dir}/{f}"
        task.destination_path = "/Game/Textures/UI"
        task.destination_name = f.replace(".png", "")
        task.replace_existing = True
        task.automated = True
        task.save = True
        tasks.append(task)
        
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    print("Texture import completed!")

if __name__ == "__main__":
    import_textures()
