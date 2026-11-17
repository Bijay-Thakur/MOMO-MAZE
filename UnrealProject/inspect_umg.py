import unreal

umg_classes = [
    "Button", "Image", "TextBlock", "ProgressBar", "Slider", 
    "CanvasPanel", "CanvasPanelSlot", "VerticalBox", "VerticalBoxSlot", 
    "HorizontalBox", "HorizontalBoxSlot", "Overlay", "OverlaySlot", 
    "Border", "BorderSlot", "SafeZone", "SafeZoneSlot", "WidgetSwitcher",
    "ScrollBox", "SizeBox", "ScaleBox"
]

results = {}
for name in umg_classes:
    cls = getattr(unreal, name, None)
    results[name] = bool(cls)

with open("D:/Projects/MOMO MAZE/UnrealProject/umg_check.txt", "w") as f:
    for k, v in results.items():
        f.write(f"{k}: {v}\n")
    f.write(f"\nWidgetTree methods: {[m for m in dir(unreal.WidgetTree) if not m.startswith('_')]}\n")
    f.write(f"WidgetBlueprintFactory methods: {[m for m in dir(unreal.WidgetBlueprintFactory) if not m.startswith('_')]}\n")
