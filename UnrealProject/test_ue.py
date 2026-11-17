import unreal
with open(r"D:\Projects\MOMO MAZE\UnrealProject\ue_output.txt", "w") as f:
    f.write(f"Hello from UE 5.8! Engine: {unreal.SystemLibrary.get_engine_version()}\n")
