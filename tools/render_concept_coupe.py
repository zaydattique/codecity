"""Evaluate the actual Khronos CarConcept mesh; no automatic license/art approval."""
import hashlib
import json
import struct
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path("build/concept-coupe").resolve()
SOURCE=ROOT/"CarConcept.glb"
PIN="e124e8d8d7330a5372bc2b4d00d39a4a9d7997ea"
BLOB="c0f38c989a78cc4ba63253b5338705e0afb0142f"
raw=SOURCE.read_bytes()
if len(raw)!=11778688 or hashlib.sha1(f"blob {len(raw)}\0".encode()+raw,usedforsecurity=False).hexdigest()!=BLOB:
    raise ValueError("Pinned source mismatch")
magic,version,total=struct.unpack_from("<4sII",raw)
if magic!=b"glTF" or version!=2 or total!=len(raw):
    raise ValueError("Invalid GLB")
length,kind=struct.unpack_from("<I4s",raw,12)
if kind!=b"JSON":
    raise ValueError("Missing glTF JSON")
doc=json.loads(raw[20:20+length])
if any("uri" in v for key in ("images","buffers") for v in doc.get(key,[])):
    raise ValueError("Unexpected external dependency")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
scene=bpy.context.scene
bpy.context.view_layer.update()
meshes=[o for o in scene.objects if o.type=="MESH"]
if not meshes:
    raise ValueError("No meshes")
names=" ".join(o.name.lower() for o in meshes)
allnames=" ".join(o.name.lower() for o in scene.objects)
for role,alternates in {"wheels":("wheel","tire","tyre"),"door":("door",),"interior":("seat","interior","dashboard","cockpit")}.items():
    if not any(x in allnames for x in alternates):
        raise ValueError("Missing named "+role+" source geometry")
triangles=0
for o in meshes:
    o.data.calc_loop_triangles()
    triangles+=len(o.data.loop_triangles)
    if not o.data.materials:
        raise ValueError("Missing material")
pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)))
span=hi-lo
if not 3<=max(span)<=7 or not 0.7<=span.z<=2.3:
    raise ValueError("Unexpected scale: "+str(span))
# Do not distribute as finished CodeCity vehicle. Marks and baked logos require review.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"candidate.blend"))
center=(lo+hi)/2
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=960
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("Studio")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.25,0.28,0.32,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=0.65
long_x=span.x>=span.y
def direction(x,y,z):
    return Vector((x,y,z) if long_x else (y,x,z))
for offset,power in [((4,-5,6),1800),((-4,4,4),1200),((0,4,2),700)]:
    bpy.ops.object.light_add(type="AREA",location=center+direction(*offset))
    o=bpy.context.object
    o.data.energy=power
    o.data.size=4
    o.rotation_euler=(center-o.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
cam.data.type="ORTHO"
def render(name,focus,offset,scale):
    cam.location=focus+direction(*offset)
    cam.rotation_euler=(focus-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.ortho_scale=scale
    scene.render.filepath=str(ROOT/(name+".png"))
    bpy.ops.render.render(write_still=True)
render("exterior",center,(5,-6,3),max(span)*1.35)
render("reverse",center,(-5,6,3),max(span)*1.35)
# Isolate actual cabin components by name for a transparent QA cutaway.
# Keep the original source unmodified. No substitute seat or dashboard geometry.
cabin=[o for o in meshes if any(x in o.name.lower() for x in ("interior","seat","dash","steer","cockpit","console","pedal","carpet"))]
if cabin:
    hidden=[(o,o.hide_render) for o in meshes if o not in cabin]
    for o,_ in hidden:o.hide_render=True
    cpts=[o.matrix_world@Vector(v) for o in cabin for v in o.bound_box]
    cl=Vector(tuple(min(v[i] for v in cpts) for i in range(3)))
    ch=Vector(tuple(max(v[i] for v in cpts) for i in range(3)))
    render("interior_isolated",(cl+ch)/2,(-2,-3,2),max(ch-cl)*1.4)
    for o,state in hidden:o.hide_render=state
else:
    print("Interior components require manual hierarchy review; no cabin render claimed")
report={"status":"research_candidate_only","source_commit":PIN,"source_git_blob":BLOB,
        "sha256":hashlib.sha256(raw).hexdigest(),"license":"CC-BY-4.0 model/textures; separate trademark rights",
        "attribution":"Eric Chadwick / Darmstadt Graphics Group GmbH, 2024; based on Unity Fan public-domain model",
        "dimensions_m":list(span),"triangles":triangles,"mesh_objects":len(meshes),
        "named_cabin_meshes":[o.name for o in cabin],"nodes":[o.name for o in scene.objects],
        "budget_pass":30000<=triangles<=60000,
        "limitations":["Trademark/logo clearance or removal pending; no redistribution approval","No vehicle physics or collision","No accepted LOD or engine test"]}
(ROOT/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("CODECITY_CONCEPT_COUPE_REVIEW_OK")
