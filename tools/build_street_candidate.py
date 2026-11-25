"""Real-scale street art test: licensed PBR road and sidewalks, street furniture.

The facade library is separately rendered and inventoried, not automatically
mistaken for a finished building. No primitive building substitutes or interiors.
"""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path("build/street-candidate").resolve()
MANIFEST=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
for asset,record in MANIFEST.items():
    for name,digest in record["sha256"].items():
        p=(ROOT/asset/name).resolve()
        if not p.is_relative_to(ROOT/asset) or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise ValueError("Street input hash mismatch")

bpy.ops.wm.read_factory_settings(use_empty=True)


def material(asset):
    mat=bpy.data.materials.new(asset)
    mat.use_nodes=True
    tree=mat.node_tree
    bsdf=tree.nodes.get("Principled BSDF")
    for role,filename in MANIFEST[asset]["maps"].items():
        node=tree.nodes.new("ShaderNodeTexImage")
        node.image=bpy.data.images.load(str(ROOT/asset/filename))
        if role!="color":
            node.image.colorspace_settings.name="Non-Color"
        if role=="normal":
            normal=tree.nodes.new("ShaderNodeNormalMap")
            tree.links.new(node.outputs["Color"],normal.inputs["Color"])
            tree.links.new(normal.outputs["Normal"],bsdf.inputs["Normal"])
        else:
            tree.links.new(node.outputs["Color"],bsdf.inputs["Base Color" if role=="color" else "Roughness"])
    return mat


def surface(name,x0,x1,y0,y1,z,mat,tile):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[],[(0,1,2,3)])
    mesh.update()
    uv=mesh.uv_layers.new()
    for loop in mesh.loops:
        p=mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(p.x/tile,p.y/tile)
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj


def curb(name,x0,x1,y0,y1,mat):
    # Authored beveled curb profile, meter-scale and UV mapped. No fake facade.
    vertices=[]
    for y in (y0,y1):
        vertices.extend([(x0,y,0),(x1,y,0),(x1,y,0.12),(x1-0.025,y,0.15),(x0,y,0.15)])
    faces=[(0,4,3,2,1),(5,6,7,8,9)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    uv=mesh.uv_layers.new()
    for loop in mesh.loops:
        p=mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(p.y/1.8,(p.x+p.z)/1.8)
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj


def import_model(asset):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/asset/MANIFEST[asset]["entry"]))
    objects=[o for o in bpy.context.scene.objects if o not in before]
    meshes=[o for o in objects if o.type=="MESH"]
    if not meshes or any(not o.data.materials or not o.data.uv_layers for o in meshes):
        raise ValueError("Missing licensed source geometry/materials")
    return objects,meshes


def bounds(meshes):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
    return (Vector(tuple(min(v[i] for v in pts) for i in range(3))),Vector(tuple(max(v[i] for v in pts) for i in range(3))))


def place_model(asset,x,y,z):
    objects,meshes=import_model(asset)
    lo,hi=bounds(meshes)
    if asset=="street_lamp_01" and not 3.5<=hi.z-lo.z<=4.3:
        raise ValueError("Lamp scale mismatch")
    center=(lo+hi)/2
    offset=Vector((x-center.x,y-center.y,z-lo.z))
    for obj in objects:
        if obj.parent not in objects:
            obj.location+=offset
    return meshes


asphalt=material("asphalt_01")
paving=material("concrete_pavement_02")
paint=bpy.data.materials.new("Road marking paint")
paint.diffuse_color=(0.72,0.70,0.60,1)
paint.use_nodes=True
paint.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=paint.diffuse_color
paint.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value=0.85
surface("Carriageway", -3.4,3.4,-16,16,0,asphalt,2.1)
surface("Sidewalk West",-6,-3.55,-16,16,0.15,paving,1.8)
surface("Sidewalk East",3.55,6,-16,16,0.15,paving,1.8)
curb("Curb West",-3.55,-3.4,-16,16,paving)
curb("Curb East",3.4,3.55,-16,16,paving)
for y in (-13,-7,-1,5,11):
    surface(f"Centre dash {y}",-0.055,0.055,y,y+2.5,0.002,paint,1)
for x in (-3.20,3.20):
    surface(f"Edge line {x}",x-0.04,x+0.04,-16,16,0.002,paint,1)
for y in (-10,10):
    place_model("street_lamp_01",5.35,y,0.15)
place_model("painted_wooden_bench",4.95,-2.0,0.15)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"street_surface.blend"))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=str(ROOT/"street_surface.glb"),export_format="GLB",use_selection=True)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("Daylight")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.45,0.55,0.72,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=0.5
bpy.ops.object.light_add(type="SUN")
bpy.context.object.data.energy=2.5
bpy.context.object.rotation_euler=(0.45,-0.65,-0.4)
bpy.ops.object.camera_add(location=(2.5,-13,2.5))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,9,1.4))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens=28
scene.camera=cam
scene.render.filepath=str(ROOT/"street_surface.png")
bpy.ops.render.render(write_still=True)
# Separately inspect real facade kit. Do not scatter its asset-library layout in the street.
bpy.ops.wm.read_factory_settings(use_empty=True)
objects,meshes=import_model("modular_urban_apartments_facade")
lo,hi=bounds(meshes)
inventory=[{"name":o.name,"dimensions_m":list(o.dimensions),"location":list(o.matrix_world.translation)} for o in meshes]
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"facade_library.blend"))
(ROOT/"facade_inventory.json").write_text(json.dumps({"source":MANIFEST["modular_urban_apartments_facade"],"objects":inventory,"dimensions_m":list(hi-lo)},indent=2),encoding="utf-8")
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("Studio")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.35,0.35,0.35,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=0.6
bpy.ops.object.light_add(type="SUN")
bpy.context.object.data.energy=2.0
bpy.context.object.rotation_euler=(0.5,-0.4,-0.7)
center=(lo+hi)/2
span=max(hi-lo)
bpy.ops.object.camera_add(location=center+Vector((0.35,-1.2,0.75))*span)
cam=bpy.context.object
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=span*1.15
scene.camera=cam
scene.render.filepath=str(ROOT/"facade_library.png")
bpy.ops.render.render(write_still=True)
print("CODECITY_STREET_SURFACE_CANDIDATE_OK")
