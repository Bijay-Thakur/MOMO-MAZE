import unreal

widget_bp = unreal.EditorAssetLibrary.load_asset("/Game/UI/WBP_TestWidget")

with open("D:/Projects/MOMO MAZE/UnrealProject/widget_bp_props.txt", "w") as f:
    f.write(f"WidgetBP methods/attrs:\n")
    for a in dir(widget_bp):
        if not a.startswith("__"):
            f.write(f"  {a}\n")
