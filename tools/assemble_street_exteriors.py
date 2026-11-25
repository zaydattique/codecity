"""Assemble real licensed facade modules around the existing street candidate.

Exterior art only. Closed entrances, no invented playable interiors. The actual
wall/door/window meshes, PBR materials and grid pivots come from the reviewed kit.
"""
import hashlib
import json
from math import pi
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ROOT = Path("build/street-candidate").resolve()
OUT = Path("build/street-exteriors").resolve()
OUT.mkdir(parents=True, exist_ok=False)
for name,digest in {
    "street_surface.blend":"3a9fc30da102c42bf2235161dc3723c0e1331457c3689201d49761d2c037b7e0",
    "facade_library.blend":"49835f90efce4d0c7d0fa96a0705874dbf1c85eae4bee4655829f832a7e443a2",
}.items():
    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
        raise ValueError("Reviewed source artifact changed: "+name)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"street_surface.blend"),load_ui=False)
street_scene=bpy.context.scene
library=ROOT/"facade_library.blend"
# Appended source meshes remain unlinked and are removed after building.
with bpy.data.libraries.load(str(library),link=False) as (src,dst):
    wanted=[n for n in src.objects if n.startswith(("wall_","door_","window_","cornice_","crown_","base_"))]
    dst.objects=wanted
modules={o.name:o for o in dst.objects if o and o.type=="MESH"}
required=("wall_standard_standard_01","wall_door_centered_small_01","door_centered_small_01",
          "wall_window_centered_large_01","window_centered_large_01",
          "wall_window_centered_double_01","window_centered_double_01",
          "wall_window_centered_small_01","window_centered_small_01",
          "cornice_standard_standard_01","crown_standard_standard_01")
if not all(n in modules for n in required):
    raise ValueError("Required reviewed facade modules missing")
geometry=bpy.data.collections.new("Harbor Boulevard exterior candidates")
street_scene.collection.children.link(geometry)
assemblies=[]

def corners(obj):
    return [obj.matrix_world @ Vector(v) for v in obj.bound_box]

def place_group(names,anchor,angle,label):
    wall=modules[names[0]]
    bounds=corners(wall)
    pivot=Vector(((min(p.x for p in bounds)+max(p.x for p in bounds))/2,
                  wall.matrix_world.translation.y,min(p.z for p in bounds)))
    rotation=Matrix.Rotation(angle,4,"Z")
    transform=Matrix.Translation(Vector(anchor)) @ rotation @ Matrix.Translation(-pivot)
    for name in names:
        source=modules[name]
        new=source.copy()
        new.parent=None
        new.name=f"{label}.{name}"
        geometry.objects.link(new)
        new.matrix_world=transform @ source.matrix_world
    return transform

def level(kind):
    if kind=="blank":
        return ["wall_standard_standard_01"]
    if kind=="door":
        return ["wall_door_centered_small_01","door_centered_small_01"]
    stem="window_centered_"+kind+"_01"
    return ["wall_"+stem,stem]

def roof(name,x0,x1,y0,y1,z):
    # Flat roof closure uses the existing licensed concrete paving material.
    mat=bpy.data.materials.get("concrete_pavement_02")
    if mat is None:
        raise ValueError("Roof material missing")
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[],[(0,1,2,3)])
    mesh.update()
    uv=mesh.uv_layers.new()
    for loop in mesh.loops:
        p=mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(p.x/1.8,p.y/1.8)
    obj=bpy.data.objects.new(name,mesh)
    geometry.objects.link(obj)
    mesh.materials.append(mat)

def building(label,x0,x1,y0,y1,floors,street_face):
    # All facade bays are authored 3m x 3m, with matched aperture meshes.
    sides=[
        ("south",(x0+1.5,y0), (3,0),0,round((x1-x0)/3)),
        ("east",(x1,y0+1.5),(0,3),pi/2,round((y1-y0)/3)),
        ("north",(x1-1.5,y1),(-3,0),pi,round((x1-x0)/3)),
        ("west",(x0,y1-1.5),(0,-3),-pi/2,round((y1-y0)/3)),
    ]
    for side,start,step,angle,count in sides:
        for bay in range(count):
            x=start[0]+step[0]*bay
            y=start[1]+step[1]*bay
            for floor in range(floors):
                if side==street_face:
                    kind="door" if floor==0 and bay==count//2 else ("double" if (bay+floor)%2 else "large")
                else:
                    kind="small" if (bay+floor)%2==0 else "blank"
                place_group(level(kind),(x,y,0.15+floor*3),angle,f"{label}.{side}.{bay}.{floor}")
            # Trim spans same bay; align by actual bounds, not kit display location.
            place_group(["crown_standard_standard_01"],(x,y,0.15+floors*3),angle,f"{label}.{side}.{bay}.crown")
    roof(label+".roof",x0,x1,y0,y1,0.15+floors*3)
    assemblies.append({"id":label,"bounds_m":[x0,x1,y0,y1,0.15,0.15+floors*3],
                       "floors":floors,"accessible":False,"source":"licensed modular exterior"})

building("harbor_east_01",6,15,-15,0,3,"west")
building("harbor_east_02",6,15,0,15,2,"west")
building("harbor_west_01",-15,-6,-15,3,2,"east")
building("harbor_west_02",-15,-6,3,15,3,"east")
# Remove only the appended unlinked authoring objects, not their shared meshes.
for obj in list(dst.objects):
    if obj is not None:
        bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update()
meshes=[o for o in street_scene.objects if o.type=="MESH"]
if not meshes or any(not o.data.materials or not o.data.uv_layers for o in meshes):
    raise ValueError("Missing geometry/material/UV")
triangles=0
for o in meshes:
    o.data.calc_loop_triangles()
    triangles+=len(o.data.loop_triangles)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"harbor_exteriors.blend"))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=str(OUT/"harbor_exteriors.glb"),export_format="GLB",use_selection=True)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("Harbor daylight")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.52,0.64,0.80,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=0.55
bpy.ops.object.light_add(type="SUN")
bpy.context.object.data.energy=2.7
bpy.context.object.rotation_euler=(0.55,-0.6,-0.45)
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
scene.render.image_settings.file_format="PNG"
for name,location,target,lens in [
    ("street_eye",(1.2,-14.5,1.7),(0,8,2.8),24),
    ("street_reverse",(-1.2,14.5,1.7),(0,-8,2.8),24),
    ("overview",(25,-29,28),(0,0,2),36),
]:
    cam.location=Vector(location)
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    scene.render.filepath=str(OUT/f"{name}.png")
    bpy.ops.render.render(write_still=True)
(OUT/"report.json").write_text(json.dumps({"status":"exterior_candidate_only","buildings":assemblies,"mesh_instances":len(meshes),"triangles":triangles,"source_run":45595559815,"source_artifact":15013880219,"license":"CC0-1.0","limitations":["No playable interiors, collision, navigation or approved gameplay integration","Exterior layout and seams still require visual QA"]},indent=2),encoding="utf-8")
print("CODECITY_STREET_EXTERIORS_OK")
