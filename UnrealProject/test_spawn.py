import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/test_spawn_log.txt", "w") as f:
    try:
        world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
        f.write(f"New blank map: {world}\n")
        sm_hedge = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Environment/SM_Hedge_Straight")
        f.write(f"sm_hedge: {sm_hedge}\n")
        
        # Test 1: spawn_actor_from_object
        try:
            actor1 = unreal.EditorLevelLibrary.spawn_actor_from_object(sm_hedge, unreal.Vector(0,0,0))
            f.write(f"actor1 spawn_actor_from_object: {actor1}\n")
        except Exception as e:
            f.write(f"actor1 exception: {e}\n")

        # Test 2: spawn_actor_from_class StaticMeshActor
        try:
            actor2 = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(100,0,0))
            f.write(f"actor2 spawn_actor_from_class: {actor2}\n")
            if actor2:
                actor2.static_mesh_component.set_static_mesh(sm_hedge)
                f.write(f"actor2 mesh set successfully!\n")
        except Exception as e:
            f.write(f"actor2 exception: {e}\n")

    except Exception as e:
        f.write(f"Fatal error: {e}\n")
