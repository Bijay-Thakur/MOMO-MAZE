import unreal

factory = unreal.BlueprintFactory()
print("Factory properties:", dir(factory))
try:
    factory.set_editor_property("parent_class", unreal.Actor)
    print("set_editor_property('parent_class') SUCCESS")
except Exception as e:
    print("set_editor_property error:", e)
