import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/widget_api_output.txt", "w") as f:
    widgets = [x for x in dir(unreal) if "Widget" in x]
    f.write(f"Total widget related symbols: {len(widgets)}\n")
    for w in widgets:
        f.write(f"  {w}\n")

    wbf = [x for x in dir(unreal) if "Blueprint" in x]
    f.write(f"\nBlueprint symbols:\n")
    for b in wbf:
        f.write(f"  {b}\n")
