import bpy
import math
import os
from mathutils import Vector

def setup_render_engine():
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

def render_ui_library():
    scene_path = r"D:\Projects\MOMO MAZE\BlenderSources\scenes\ui_library.blend"
    out_dir = r"D:\Projects\MOMO MAZE\UnrealProject\Content\Textures\UI"
    os.makedirs(out_dir, exist_ok=True)
    
    bpy.ops.wm.open_mainfile(filepath=scene_path)
    setup_render_engine()
    
    # Setup orthographic camera looking along +Z onto the XY plane
    cam_data = bpy.data.cameras.new("UICam")
    cam_data.type = 'ORTHO'
    cam_obj = bpy.data.objects.new("UICam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_obj.location = (0, 0, 10)
    cam_obj.rotation_euler = (0, 0, 0)
    
    # Warm golden sunlight angled to give beautiful bevel highlights and bottom drop shadows
    sun_data = bpy.data.lights.new("UISun", 'SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.94, 0.85)
    sun_obj = bpy.data.objects.new("UISun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(35), math.radians(-25), 0)
    
    # Fill light from bottom-left
    fill_data = bpy.data.lights.new("UIFill", 'SUN')
    fill_data.energy = 1.8
    fill_data.color = (0.9, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("UIFill", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(-40), math.radians(45), 0)

    # Hide all objects first
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = True
            o.location = (0, 0, 0)
            o.rotation_euler = (0, 0, 0)
            
    # List of objects to render: (obj_name, filename, ortho_scale, res_x, res_y)
    render_list = [
        ("SM_UI_ButtonPrimary_Pill", "T_UI_Button_Primary_Gold.png", 3.8, 512, 170),
        ("SM_UI_ButtonSecondary_Pill", "T_UI_Button_Secondary_Cream.png", 3.0, 440, 150),
        ("SM_UI_ButtonIcon", "T_UI_Button_Icon_Round.png", 1.4, 256, 256),
        ("SM_UI_Tab_Pill", "T_UI_Tab_Gold.png", 2.6, 380, 130),
        ("SM_UI_ChoiceChip", "T_UI_Choice_Chip.png", 1.8, 256, 110),
        ("SM_UI_LevelNode", "T_UI_Level_Node.png", 1.3, 192, 192),
        ("SM_UI_ToggleTrack", "T_UI_Toggle_Track.png", 1.9, 256, 120),
        ("SM_UI_ToggleKnob", "T_UI_Toggle_Knob.png", 0.9, 128, 128),
        ("SM_UI_SliderTrack", "T_UI_Slider_Track.png", 3.4, 512, 48),
        ("SM_UI_SliderKnob", "T_UI_Slider_Knob.png", 0.8, 128, 128),
        ("SM_UI_CardFrame", "T_UI_Card_Frame.png", 8.0, 768, 512),
        ("SM_UI_HeaderRibbon", "T_UI_Header_Ribbon.png", 5.0, 640, 140),
        ("SM_UI_LeafPair", "T_UI_Leaf_Pair.png", 1.2, 192, 192),
        ("SM_UI_FlowerCorner", "T_UI_Flower_Corner.png", 1.2, 192, 192),
        ("SM_UI_Star", "T_UI_Star_Gold.png", 1.3, 192, 192),
        ("SM_UI_Heart", "T_UI_Heart_Coral.png", 1.3, 192, 192),
        ("SM_UI_PauseIcon", "T_UI_Pause_Bars.png", 0.8, 128, 128),
        ("SM_UI_MapIcon", "T_UI_Map_Icon.png", 0.9, 128, 128),
        ("SM_UI_MomoIcon", "T_UI_Momo_Icon.png", 1.0, 160, 160),
        ("SM_UI_SpiritIcon", "T_UI_Spirit_Icon.png", 1.0, 160, 160),
    ]

    for obj_name, file_name, ortho_s, rx, ry in render_list:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            print(f"Warning: {obj_name} not found in blend file!")
            continue
            
        obj.hide_render = False
        cam_data.ortho_scale = ortho_s
        bpy.context.scene.render.resolution_x = rx
        bpy.context.scene.render.resolution_y = ry
        
        out_path = os.path.join(out_dir, file_name)
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {file_name} ({rx}x{ry})")
        obj.hide_render = True

    # Render inactive cream tab
    tab_obj = bpy.data.objects.get("SM_UI_Tab_Pill")
    cream_mat = bpy.data.materials.get("M_UI_Cream")
    if tab_obj and cream_mat:
        tab_obj.hide_render = False
        old_mat = tab_obj.data.materials[0]
        tab_obj.data.materials[0] = cream_mat
        cam_data.ortho_scale = 2.6
        bpy.context.scene.render.resolution_x = 380
        bpy.context.scene.render.resolution_y = 130
        bpy.context.scene.render.filepath = os.path.join(out_dir, "T_UI_Tab_Cream.png")
        bpy.ops.render.render(write_still=True)
        tab_obj.data.materials[0] = old_mat
        tab_obj.hide_render = True
        print("Rendered: T_UI_Tab_Cream.png")

    print("All 3D UI textures successfully baked!")

if __name__ == "__main__":
    render_ui_library()
