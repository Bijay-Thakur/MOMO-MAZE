import bpy
import os

out_dir = r"D:\Projects\MOMO MAZE\UnrealProject\Content\Textures\UI"
export_dir = r"D:\Projects\MOMO MAZE\BlenderSources\exports\fbx"

def setup_render():
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

# 1. Momo Icon
bpy.ops.wm.read_factory_settings(use_empty=True)
setup_render()
bpy.ops.import_scene.fbx(filepath=os.path.join(export_dir, "SM_UI_MomoIcon.fbx"))
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 1.3
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -5, 3)
cam_obj.rotation_euler = (1.0, 0, 0)

sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 5.0
sun.color = (1.0, 0.95, 0.85)
sun_obj = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (0.8, -0.5, 0)

bpy.context.scene.render.resolution_x = 192
bpy.context.scene.render.resolution_y = 192
bpy.context.scene.render.filepath = os.path.join(out_dir, "T_UI_Momo_Icon.png")
bpy.ops.render.render(write_still=True)
print("Rendered T_UI_Momo_Icon.png")

# 2. Spirit Icon
bpy.ops.wm.read_factory_settings(use_empty=True)
setup_render()
bpy.ops.import_scene.fbx(filepath=os.path.join(export_dir, "SM_UI_SpiritIcon.fbx"))
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 1.6
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -5, 1)
cam_obj.rotation_euler = (1.4, 0, 0)

sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 5.0
sun.color = (1.0, 0.98, 0.95)
sun_obj = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (0.8, -0.5, 0)

bpy.context.scene.render.resolution_x = 192
bpy.context.scene.render.resolution_y = 192
bpy.context.scene.render.filepath = os.path.join(out_dir, "T_UI_Spirit_Icon.png")
bpy.ops.render.render(write_still=True)
print("Rendered T_UI_Spirit_Icon.png")
