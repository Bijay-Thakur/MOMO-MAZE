import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras, bpy.data.collections):
        for item in b:
            b.remove(item)

def create_ui_materials():
    mats = {}
    
    # 1. Gold Pill (Primary button, stars, active tabs)
    m_gold = bpy.data.materials.new("M_UI_Gold")
    m_gold.use_nodes = True
    b = m_gold.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (1.0, 0.78, 0.28, 1.0) # #FFC747
    b.inputs["Roughness"].default_value = 0.22
    b.inputs["Coat Weight"].default_value = 0.5
    b.inputs["Coat Roughness"].default_value = 0.1
    b.inputs["Subsurface Weight"].default_value = 0.2
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.7, 0.3)
    b.inputs["Emission Color"].default_value = (1.0, 0.75, 0.25, 1.0)
    b.inputs["Emission Strength"].default_value = 0.15 # subtle warm rim glow
    mats["Gold"] = m_gold

    # 2. Cream / Warm Card (Secondary button, card bodies, inactive tabs)
    m_cream = bpy.data.materials.new("M_UI_Cream")
    m_cream.use_nodes = True
    b = m_cream.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (1.0, 0.96, 0.91, 1.0) # #FFF5E8
    b.inputs["Roughness"].default_value = 0.38
    b.inputs["Subsurface Weight"].default_value = 0.25
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.85, 0.7)
    mats["Cream"] = m_cream

    # 3. Toast Brown (Ribbons, borders, dark text, tracks)
    m_toast = bpy.data.materials.new("M_UI_ToastBrown")
    m_toast.use_nodes = True
    b = m_toast.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.35, 0.18, 0.09, 1.0) # #5A2E17
    b.inputs["Roughness"].default_value = 0.35
    mats["ToastBrown"] = m_toast

    # 4. Orange Accent (Secondary accent, hover highlights)
    m_orange = bpy.data.materials.new("M_UI_Orange")
    m_orange.use_nodes = True
    b = m_orange.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.96, 0.55, 0.20, 1.0) # #F58C33
    b.inputs["Roughness"].default_value = 0.28
    mats["Orange"] = m_orange

    # 5. Leaf Green (Leaves, garden accents)
    m_leaf = bpy.data.materials.new("M_UI_LeafGreen")
    m_leaf.use_nodes = True
    b = m_leaf.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.45, 0.72, 0.20, 1.0) # #73B833
    b.inputs["Roughness"].default_value = 0.40
    b.inputs["Subsurface Weight"].default_value = 0.3
    mats["LeafGreen"] = m_leaf

    # 6. Coral Heart (Health, playful accents)
    m_coral = bpy.data.materials.new("M_UI_CoralHeart")
    m_coral.use_nodes = True
    b = m_coral.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.95, 0.35, 0.40, 1.0) # #F25966
    b.inputs["Roughness"].default_value = 0.25
    mats["CoralHeart"] = m_coral

    # 7. Spirit White (White ghost icon, daisy petals)
    m_white = bpy.data.materials.new("M_UI_SpiritWhite")
    m_white.use_nodes = True
    b = m_white.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (1.0, 0.99, 0.96, 1.0)
    b.inputs["Roughness"].default_value = 0.20
    b.inputs["Emission Color"].default_value = (1.0, 0.98, 0.95, 1.0)
    b.inputs["Emission Strength"].default_value = 0.2
    mats["SpiritWhite"] = m_white

    return mats

def make_beveled_pill(name, width, height, depth, bevel_r, mat_primary, mat_rim=None):
    """Creates a rounded pill with front bevel and optional rim"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # Create base cylinder or rounded box
    # Cylinder oriented along X (left/right hemisphere caps)
    cap_r = height * 0.5
    straight_w = max(0.001, width - height)
    
    # Segments
    seg = 24
    
    # Right cap center = (+straight_w*0.5, 0, 0), Left cap center = (-straight_w*0.5, 0, 0)
    pts_front = []
    pts_back = []
    
    # Sweep around circle in XY plane
    for i in range(seg):
        angle = 2.0 * math.pi * i / seg
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Determine X offset for stadium pill shape
        x_center = straight_w * 0.5 if cos_a >= 0 else -straight_w * 0.5
        x = x_center + cap_r * cos_a
        y = cap_r * sin_a
        
        # Front face at Z = depth, back face at Z = 0
        v_back = bm.verts.new((x, y, 0.0))
        v_front = bm.verts.new((x, y, depth))
        pts_back.append(v_back)
        pts_front.append(v_front)
        
    bm.verts.ensure_lookup_table()
    
    # Side quads
    for i in range(seg):
        i_next = (i + 1) % seg
        bm.faces.new([pts_back[i], pts_back[i_next], pts_front[i_next], pts_front[i]])
        
    # Back face
    bm.faces.new(list(reversed(pts_back)))
    # Front face
    front_face = bm.faces.new(pts_front)
    
    bm.to_mesh(mesh)
    bm.free()
    
    # Add Bevel Modifier for clean rounded 3D ceramic feel
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = bevel_r
    bev.segments = 4
    bev.profile = 0.7
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    
    # Add Subdivision Surface (simple level 1 for smooth shading)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    
    # Smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    # Assign materials
    obj.data.materials.append(mat_primary)
    if mat_rim:
        obj.data.materials.append(mat_rim)
        
    return obj

def make_chunky_star(name, outer_r, inner_r, depth, bevel_r, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    points = 5
    front_verts = []
    back_verts = []
    
    for i in range(points * 2):
        angle = math.pi / 2.0 + i * math.pi / points
        r = outer_r if (i % 2 == 0) else inner_r
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        back_verts.append(bm.verts.new((x, y, 0.0)))
        front_verts.append(bm.verts.new((x, y, depth)))
        
    bm.verts.ensure_lookup_table()
    total_pts = points * 2
    for i in range(total_pts):
        i_next = (i + 1) % total_pts
        bm.faces.new([back_verts[i], back_verts[i_next], front_verts[i_next], front_verts[i]])
        
    bm.faces.new(list(reversed(back_verts)))
    bm.faces.new(front_verts)
    
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = bevel_r
    bev.segments = 3
    obj.data.materials.append(mat)
    return obj

def make_chunky_heart(name, scale, depth, bevel_r, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    steps = 32
    front_verts = []
    back_verts = []
    
    for i in range(steps):
        t = 2.0 * math.pi * i / steps
        # Heart equation
        x = 16.0 * (math.sin(t) ** 3)
        y = 13.0 * math.cos(t) - 5.0 * math.cos(2*t) - 2.0 * math.cos(3*t) - math.cos(4*t)
        # Scale and center
        x *= scale * 0.06
        y = (y + 2.5) * scale * 0.06
        back_verts.append(bm.verts.new((x, y, 0.0)))
        front_verts.append(bm.verts.new((x, y, depth)))
        
    bm.verts.ensure_lookup_table()
    for i in range(steps):
        i_next = (i + 1) % steps
        bm.faces.new([back_verts[i], back_verts[i_next], front_verts[i_next], front_verts[i]])
        
    bm.faces.new(list(reversed(back_verts)))
    bm.faces.new(front_verts)
    
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = bevel_r
    bev.segments = 3
    obj.data.materials.append(mat)
    return obj

def make_toggle_track(name, width, height, depth, mat_track):
    # Recessed capsule trough
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    cap_r = height * 0.5
    straight_w = width - height
    seg = 24
    
    outer_back = []
    outer_front = []
    
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        x_c = straight_w * 0.5 if cos_a >= 0 else -straight_w * 0.5
        x = x_c + cap_r * cos_a
        y = cap_r * sin_a
        outer_back.append(bm.verts.new((x, y, 0.0)))
        outer_front.append(bm.verts.new((x, y, depth)))
        
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        i_next = (i + 1) % seg
        bm.faces.new([outer_back[i], outer_back[i_next], outer_front[i_next], outer_front[i]])
        
    bm.faces.new(list(reversed(outer_back)))
    bm.faces.new(outer_front)
    
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.04
    bev.segments = 3
    obj.data.materials.append(mat_track)
    return obj

def make_slider_knob(name, radius, depth, bevel_r, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    seg = 32
    fb = []
    ff = []
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        x = radius * math.cos(a)
        y = radius * math.sin(a)
        fb.append(bm.verts.new((x, y, 0.0)))
        ff.append(bm.verts.new((x, y, depth)))
        
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        i_next = (i + 1) % seg
        bm.faces.new([fb[i], fb[i_next], ff[i_next], ff[i]])
    bm.faces.new(list(reversed(fb)))
    bm.faces.new(ff)
    
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = bevel_r
    bev.segments = 3
    obj.data.materials.append(mat)
    return obj

def make_slider_track(name, length, thickness, depth, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale cube: length along X, thickness along Y, depth along Z
    for v in bm.verts:
        v.co.x *= length
        v.co.y *= thickness
        v.co.z = (v.co.z + 0.5) * depth # bottom at 0
        
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.03
    bev.segments = 3
    obj.data.materials.append(mat)
    return obj

def make_card_frame(name, width, height, depth, corner_r, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    seg_corner = 8
    hw = width * 0.5 - corner_r
    hh = height * 0.5 - corner_r
    
    corners = [
        (hw, hh, 0),        # Top-Right (0 to pi/2)
        (-hw, hh, math.pi/2), # Top-Left (pi/2 to pi)
        (-hw, -hh, math.pi),  # Bottom-Left (pi to 3pi/2)
        (hw, -hh, 3*math.pi/2) # Bottom-Right (3pi/2 to 2pi)
    ]
    
    fb = []
    ff = []
    for cx, cy, start_a in corners:
        for i in range(seg_corner):
            a = start_a + (math.pi * 0.5) * i / seg_corner
            x = cx + corner_r * math.cos(a)
            y = cy + corner_r * math.sin(a)
            fb.append(bm.verts.new((x, y, 0.0)))
            ff.append(bm.verts.new((x, y, depth)))
            
    bm.verts.ensure_lookup_table()
    total_v = len(fb)
    for i in range(total_v):
        i_next = (i + 1) % total_v
        bm.faces.new([fb[i], fb[i_next], ff[i_next], ff[i]])
    bm.faces.new(list(reversed(fb)))
    bm.faces.new(ff)
    
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.04
    bev.segments = 3
    obj.data.materials.append(mat)
    return obj

def make_flower_corner(name, size, depth, mat_petal, mat_center):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    # 5 petals + center dome
    petals = 5
    petal_r = size * 0.35
    dist = size * 0.45
    
    for p in range(petals):
        angle = 2.0 * math.pi * p / petals
        cx = dist * math.cos(angle)
        cy = dist * math.sin(angle)
        # Petal circle
        seg = 12
        p_fb = []
        p_ff = []
        for i in range(seg):
            a = 2.0 * math.pi * i / seg
            x = cx + petal_r * math.cos(a)
            y = cy + petal_r * math.sin(a)
            p_fb.append(bm.verts.new((x, y, 0.0)))
            p_ff.append(bm.verts.new((x, y, depth * 0.8)))
        bm.verts.ensure_lookup_table()
        for i in range(seg):
            i_next = (i + 1) % seg
            bm.faces.new([p_fb[i], p_fb[i_next], p_ff[i_next], p_ff[i]])
        bm.faces.new(list(reversed(p_fb)))
        bm.faces.new(p_ff)
        
    # Center disc
    seg = 16
    c_fb = []
    c_ff = []
    center_r = size * 0.28
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        x = center_r * math.cos(a)
        y = center_r * math.sin(a)
        c_fb.append(bm.verts.new((x, y, depth * 0.3)))
        c_ff.append(bm.verts.new((x, y, depth * 1.25))) # raised dome
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        i_next = (i + 1) % seg
        f = bm.faces.new([c_fb[i], c_fb[i_next], c_ff[i_next], c_ff[i]])
        f.material_index = 1
    f_b = bm.faces.new(list(reversed(c_fb)))
    f_b.material_index = 1
    f_f = bm.faces.new(c_ff)
    f_f.material_index = 1
    
    bm.to_mesh(mesh)
    bm.free()
    
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.02
    bev.segments = 2
    obj.data.materials.append(mat_petal)
    obj.data.materials.append(mat_center)
    return obj

def make_leaf_pair(name, size, depth, mat_leaf):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    # Two teardrop / ellipse leaves angled at 45 deg
    for leaf_idx, angle_deg in enumerate([25, 65]):
        rad = math.radians(angle_deg)
        cos_l = math.cos(rad)
        sin_l = math.sin(rad)
        
        # Teardrop curve
        pts_b = []
        pts_f = []
        steps = 16
        for s in range(steps):
            t = 2.0 * math.pi * s / steps
            lx = size * 0.6 * math.sin(t)
            ly = size * 0.3 * (1.0 - math.cos(t)) * math.sin(t) * 1.5 + size * 0.3 * (1.0 - math.cos(t))
            
            # Rotate
            rx = lx * cos_l - ly * sin_l
            ry = lx * sin_l + ly * cos_l
            pts_b.append(bm.verts.new((rx, ry, 0.0)))
            pts_f.append(bm.verts.new((rx, ry, depth)))
            
        bm.verts.ensure_lookup_table()
        for i in range(steps):
            i_next = (i + 1) % steps
            bm.faces.new([pts_b[i], pts_b[i_next], pts_f[i_next], pts_f[i]])
        bm.faces.new(list(reversed(pts_b)))
        bm.faces.new(pts_f)
        
    bm.to_mesh(mesh)
    bm.free()
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.015
    bev.segments = 2
    obj.data.materials.append(mat_leaf)
    return obj

def make_header_ribbon(name, width, height, depth, mat_ribbon):
    # Curved banner ribbon with swallowtail notched ends
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    hw = width * 0.5
    hh = height * 0.5
    notch = height * 0.4
    
    # 2D contour points around perimeter:
    # Top-right -> right notch -> bottom-right -> bottom-left -> left notch -> top-left
    contour = [
        (hw, hh),
        (hw - notch, 0),
        (hw, -hh),
        (-hw, -hh),
        (-hw + notch, 0),
        (-hw, hh)
    ]
    
    fb = []
    ff = []
    for x, y in contour:
        fb.append(bm.verts.new((x, y, 0.0)))
        ff.append(bm.verts.new((x, y, depth)))
        
    bm.verts.ensure_lookup_table()
    total = len(contour)
    for i in range(total):
        i_next = (i + 1) % total
        bm.faces.new([fb[i], fb[i_next], ff[i_next], ff[i]])
        
    bm.faces.new(list(reversed(fb)))
    bm.faces.new(ff)
    
    bm.to_mesh(mesh)
    bm.free()
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.03
    bev.segments = 3
    obj.data.materials.append(mat_ribbon)
    return obj

def make_pause_icon(name, height, bar_w, gap, depth, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    for bar_x in [-gap * 0.5 - bar_w * 0.5, gap * 0.5 + bar_w * 0.5]:
        bmesh.ops.create_cube(bm, size=1.0)
        # Scale and position
        for v in bm.verts[-8:]:
            v.co.x = bar_x + v.co.x * bar_w
            v.co.y *= height
            v.co.z = (v.co.z + 0.5) * depth
            
    bm.to_mesh(mesh)
    bm.free()
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.02
    bev.segments = 2
    obj.data.materials.append(mat)
    return obj

def make_map_icon(name, size, depth, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    # 3-fold folded map parchment
    fold_w = size / 3.0
    for fold_i, offset_z in enumerate([0.0, depth * 0.4, 0.0]):
        x_min = -size * 0.5 + fold_i * fold_w
        x_max = x_min + fold_w
        fb = [
            bm.verts.new((x_min, -size*0.5, offset_z)),
            bm.verts.new((x_max, -size*0.5, offset_z)),
            bm.verts.new((x_max, size*0.5, offset_z)),
            bm.verts.new((x_min, size*0.5, offset_z))
        ]
        ff = [
            bm.verts.new((x_min, -size*0.5, offset_z + depth)),
            bm.verts.new((x_max, -size*0.5, offset_z + depth)),
            bm.verts.new((x_max, size*0.5, offset_z + depth)),
            bm.verts.new((x_min, size*0.5, offset_z + depth))
        ]
        bm.verts.ensure_lookup_table()
        for i in range(4):
            i_next = (i + 1) % 4
            bm.faces.new([fb[i], fb[i_next], ff[i_next], ff[i]])
        bm.faces.new(list(reversed(fb)))
        bm.faces.new(ff)
        
    bm.to_mesh(mesh)
    bm.free()
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.015
    bev.segments = 2
    obj.data.materials.append(mat)
    return obj

def main():
    reset_scene()
    mats = create_ui_materials()
    
    items = []
    
    # 1. SM_UI_ButtonPrimary_Pill (Main Play, Start, Next, Continue)
    items.append(make_beveled_pill("SM_UI_ButtonPrimary_Pill", width=3.4, height=1.1, depth=0.35, bevel_r=0.08, mat_primary=mats["Gold"], mat_rim=mats["Orange"]))
    
    # 2. SM_UI_ButtonSecondary_Pill (Replay, Settings, Levels, Back)
    items.append(make_beveled_pill("SM_UI_ButtonSecondary_Pill", width=2.6, height=0.9, depth=0.28, bevel_r=0.06, mat_primary=mats["Cream"], mat_rim=mats["ToastBrown"]))
    
    # 3. SM_UI_ButtonIcon (Circular icon button: home, pause, retry)
    items.append(make_beveled_pill("SM_UI_ButtonIcon", width=1.1, height=1.1, depth=0.30, bevel_r=0.07, mat_primary=mats["Cream"], mat_rim=mats["ToastBrown"]))
    
    # 4. SM_UI_Tab_Pill (Bottom nav tabs, closet tabs, settings side tabs)
    items.append(make_beveled_pill("SM_UI_Tab_Pill", width=2.2, height=0.75, depth=0.22, bevel_r=0.05, mat_primary=mats["Cream"], mat_rim=mats["Gold"]))
    
    # 5. SM_UI_ChoiceChip (Ghost counts, maze sizes, speed options)
    items.append(make_beveled_pill("SM_UI_ChoiceChip", width=1.5, height=0.65, depth=0.20, bevel_r=0.04, mat_primary=mats["Cream"], mat_rim=mats["Gold"]))
    
    # 6. SM_UI_LevelNode (Level map nodes 1-25)
    items.append(make_beveled_pill("SM_UI_LevelNode", width=1.0, height=1.0, depth=0.25, bevel_r=0.06, mat_primary=mats["Cream"], mat_rim=mats["Gold"]))
    
    # 7. SM_UI_ToggleTrack
    items.append(make_toggle_track("SM_UI_ToggleTrack", width=1.6, height=0.75, depth=0.18, mat_track=mats["ToastBrown"]))
    
    # 8. SM_UI_ToggleKnob
    items.append(make_slider_knob("SM_UI_ToggleKnob", radius=0.32, depth=0.28, bevel_r=0.05, mat=mats["Gold"]))
    
    # 9. SM_UI_SliderTrack
    items.append(make_slider_track("SM_UI_SliderTrack", length=3.0, thickness=0.22, depth=0.15, mat=mats["ToastBrown"]))
    
    # 10. SM_UI_SliderKnob
    items.append(make_slider_knob("SM_UI_SliderKnob", radius=0.28, depth=0.24, bevel_r=0.04, mat=mats["Gold"]))
    
    # 11. SM_UI_CardFrame (Center menu modal cards)
    items.append(make_card_frame("SM_UI_CardFrame", width=7.2, height=4.8, depth=0.25, corner_r=0.6, mat=mats["Cream"]))
    
    # 12. SM_UI_HeaderRibbon
    items.append(make_header_ribbon("SM_UI_HeaderRibbon", width=4.5, height=0.9, depth=0.22, mat_ribbon=mats["ToastBrown"]))
    
    # 13. SM_UI_LeafPair
    items.append(make_leaf_pair("SM_UI_LeafPair", size=0.9, depth=0.12, mat_leaf=mats["LeafGreen"]))
    
    # 14. SM_UI_FlowerCorner
    items.append(make_flower_corner("SM_UI_FlowerCorner", size=0.9, depth=0.15, mat_petal=mats["SpiritWhite"], mat_center=mats["Gold"]))
    
    # 15. SM_UI_Star
    items.append(make_chunky_star("SM_UI_Star", outer_r=0.55, inner_r=0.26, depth=0.24, bevel_r=0.04, mat=mats["Gold"]))
    
    # 16. SM_UI_Heart
    items.append(make_chunky_heart("SM_UI_Heart", scale=0.7, depth=0.25, bevel_r=0.04, mat=mats["CoralHeart"]))
    
    # 17. SM_UI_PauseIcon
    items.append(make_pause_icon("SM_UI_PauseIcon", height=0.5, bar_w=0.15, gap=0.14, depth=0.15, mat=mats["ToastBrown"]))
    
    # 18. SM_UI_MapIcon
    items.append(make_map_icon("SM_UI_MapIcon", size=0.65, depth=0.12, mat=mats["Gold"]))

    # Apply modifiers and prepare clean exports
    export_dir = r"D:\Projects\MOMO MAZE\BlenderSources\exports\fbx"
    os.makedirs(export_dir, exist_ok=True)
    
    # Save the master blend
    scene_dir = r"D:\Projects\MOMO MAZE\BlenderSources\scenes"
    os.makedirs(scene_dir, exist_ok=True)
    blend_path = os.path.join(scene_dir, "ui_library.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved master UI library blend to: {blend_path}")

    # Export each mesh cleanly to FBX
    for obj in items:
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        fbx_name = f"{obj.name}.fbx"
        fbx_path = os.path.join(export_dir, fbx_name)
        
        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            use_selection=True,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            mesh_smooth_type='FACE',
            add_leaf_bones=False
        )
        print(f"Exported FBX: {fbx_name} ({len(obj.data.vertices)} vertices)")

if __name__ == "__main__":
    main()
