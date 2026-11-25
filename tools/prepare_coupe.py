"""Build a neutralized CC-BY-4.0 CarConcept derivative with actual vehicle sockets.

No source logo textures, branded plate or steering emblem in the derivative.
Original geometry, remaining PBR maps, cockpit, doors and wheel parts retained.
Output is a development candidate, not trademark/visual or handling approval.
"""
import hashlib
import json
from pathlib import Path
import math
import struct
import sys
import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.freeze_character_morphs import decode
from tools.optimize_mesh_candidates import triangles,groups_for_scene,reduced_mesh

SOURCE=ROOT/"build/coupe-input/CarConcept.glb"
OUT=ROOT/"build/coupe-ready"
SHA="c272098089d78c5cd9fd9f24ff50ee8acf8d932c55f2d55fc10adb6c8998966b"
PIN="e124e8d8d7330a5372bc2b4d00d39a4a9d7997ea"
# Exact pinned glTF companion inventory. Strip logo, dashboard artwork and tire side images.
REJECT_IMAGES={3,6,10,11}
REJECT_NAMES=("khronos","tireside_c","tireside_n","dash_e")
WHEELS={"FL":"WheelFrontL","FR":"WheelFrontR","RL":"WheelRearL","RR":"WheelRearR"}
BUDGET=60000


def neutralize(raw):
    doc,binary=decode(raw)
    if len(doc["images"])!=14 or len(doc["textures"])!=15:
        raise ValueError("Unexpected source texture inventory")
    blocked={i for i,t in enumerate(doc["textures"]) if t.get("source") in REJECT_IMAGES}
    if blocked!={3,7,11,12}:
        raise ValueError("Unexpected pinned texture indices")
    removed=[]
    def scrub(obj,path):
        if isinstance(obj,dict):
            for key,value in list(obj.items()):
                if key.lower().endswith("texture") and isinstance(value,dict) and value.get("index") in blocked:
                    removed.append(path+"."+key)
                    del obj[key]
                else:
                    scrub(value,path+"."+key)
        elif isinstance(obj,list):
            for i,v in enumerate(obj):
                scrub(v,f"{path}[{i}]")
    for i,mat in enumerate(doc["materials"]):
        scrub(mat,f"material[{i}]")
        if mat.get("name")=="Tireside":
            pbr=mat.setdefault("pbrMetallicRoughness",{})
            pbr["baseColorFactor"]=[0.024,0.024,0.024,1]
            pbr["roughnessFactor"]=0.83
        if i==2:
            mat["emissiveFactor"]=[0,0,0]
    marks={i for i,node in enumerate(doc["nodes"]) if node.get("name") in ("License Plate","InteriorSteeringEmblem")}
    if len(marks)!=2 or any(doc["nodes"][i].get("children") for i in marks):
        raise ValueError("Expected two leaf branding nodes")
    for node in doc["nodes"]:
        if "children" in node:
            node["children"]=[i for i in node["children"] if i not in marks]
    for scene in doc["scenes"]:
        scene["nodes"]=[i for i in scene["nodes"] if i not in marks]
    # Original showroom poses include 30-degree front steering and wheel roll.
    # Reset the four exact source wheel groups to straight local axle bases;
    # preserve their original translation and all actual descendant geometry.
    for name in WHEELS.values():
        matches=[n for n in doc["nodes"] if n.get("name")==name]
        if len(matches)!=1 or len(matches[0].get("matrix",[]))!=16:
            raise ValueError("Unexpected source wheel transform "+name)
        node=matches[0]
        m=node["matrix"]
        node["matrix"]=[1,0,0,0,0,1,0,0,0,0,1,0,m[12],m[13],m[14],1]
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            prim.get("extensions",{}).pop("KHR_materials_variants",None)
    doc.get("extensions",{}).pop("KHR_materials_variants",None)
    for key in ("extensionsUsed","extensionsRequired"):
        if key in doc:
            doc[key]=[x for x in doc[key] if x!="KHR_materials_variants"]
    j=json.dumps(doc,separators=(",",":"),allow_nan=False).encode()
    j+=b" "*(-len(j)%4)
    binary.extend(b"\0"*(-len(binary)%4))
    return struct.pack("<4sII",b"glTF",2,28+len(j)+len(binary))+struct.pack("<I4s",len(j),b"JSON")+j+struct.pack("<I4s",len(binary),b"BIN\0")+binary,removed


def bounds(objects):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in objects if o.type=="MESH" for v in o.data.vertices]
    if not pts:raise ValueError("Missing actual mesh geometry")
    return (Vector(tuple(min(p[i] for p in pts) for i in range(3))),Vector(tuple(max(p[i] for p in pts) for i in range(3))))


def descendants(obj):
    return [obj,*list(obj.children_recursive)]


def reparent(obj,parent):
    saved=obj.matrix_world.copy()
    obj.parent=parent
    obj.matrix_world=saved
    bpy.context.view_layer.update()


def empty(name,where,parent=None):
    obj=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(obj)
    obj.parent=parent
    obj.location=where
    bpy.context.view_layer.update()
    return obj


def main():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("Pinned source digest mismatch")
    OUT.mkdir(parents=True,exist_ok=False)
    prepared,removed=neutralize(raw)
    scratch=SOURCE.with_name("neutralized-intermediate.glb")
    scratch.write_bytes(prepared)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(scratch))
    scene=bpy.context.scene
    # Some glTF importers also instantiate disconnected nodes. Remove only
    # the two explicitly audited leaf meshes, then retain the original guard.
    detached_marks=[]
    for o in list(scene.objects):
        if o.name in ("License Plate","InteriorSteeringEmblem"):
            if o.children or o.type!="MESH":
                raise ValueError("Unexpected branding node hierarchy")
            detached_marks.append(o.name)
            bpy.data.objects.remove(o,do_unlink=True)
    roots=[o for o in scene.objects if o.parent is None]
    original=[o for o in scene.objects if o.type=="MESH"]
    flagged=[o.name for o in original if "emblem" in o.name.lower() or "license" in o.name.lower()]
    print("COUPE_IMPORT meshes",len(original),"detached_marks",detached_marks,"flagged",flagged,flush=True)
    if len(original)<90 or flagged:
        raise ValueError("Missing geometry or retained named branding: "+str(flagged))
    wheel_nodes={k:bpy.data.objects.get(v) for k,v in WHEELS.items()}
    if any(v is None for v in wheel_nodes.values()):
        raise ValueError("Missing actual wheel groups")
    lo,hi=bounds(original)
    centers={k:(a+b)/2 for k,v in wheel_nodes.items() for a,b in [bounds(descendants(v))]}
    front=(centers["FL"]+centers["FR"])/2
    rear=(centers["RL"]+centers["RR"])/2
    if abs(front.y-rear.y)<2 or abs(front.x-rear.x)>0.15:
        raise ValueError("Unexpected source longitudinal axis")
    # Blender -Y maps to Godot +Z (VehicleBody3D local forward).
    turn=Matrix.Rotation(math.pi if front.y>rear.y else 0,4,"Z")
    middle=(front+rear)/2
    floor=min(bounds(descendants(v))[0].z for v in wheel_nodes.values())
    transform=turn@Matrix.Translation(Vector((-middle.x,-middle.y,-floor)))
    for o in roots:o.matrix_world=transform@o.matrix_world
    bpy.context.view_layer.update()
    root=empty("CoupeRoot",Vector((0,0,0)))
    for o in roots:reparent(o,root)
    wheel_report={}
    for key,node in wheel_nodes.items():
        low,high=bounds(descendants(node))
        center=(low+high)/2
        radius=(high.z-low.z)/2
        if not 0.24<=radius<=0.49:
            raise ValueError(f"Unexpected wheel radius {key}: {radius}")
        socket=empty("WheelVisual_"+key,center,root)
        reparent(node,socket)
        wheel_report[key]={"godot_center":[center.x,center.z,-center.y],"radius":radius}
    # Preserve original door pivots and actual meshes, not new dummy doors.
    for key,name in (("L","BodyDoorLColor1"),("R","BodyDoorRColor1")):
        node=bpy.data.objects.get(name)
        if node is None or len(node.children_recursive)<8:raise ValueError("Door hierarchy missing")
        node.name="DoorPivot_"+key
    if not bpy.data.objects.get("InteriorSeatsColor1") or not bpy.data.objects.get("InteriorSteeringWheel01"):
        raise ValueError("Cockpit missing")
    groups=groups_for_scene()
    before=sum(triangles(mesh)*len(objects) for mesh,objects in groups.items())
    base={m:min(triangles(m),64) for m in groups}
    floor=sum(base[m]*len(groups[m]) for m in groups)
    ratio=max(0,min(1,(BUDGET-floor)/max(1,before-floor)))
    for mesh,objects in list(groups.items()):
        old=triangles(mesh)
        goal=max(base[mesh],int(base[mesh]+ratio*(old-base[mesh])))
        replacement,_=reduced_mesh(mesh,goal)
        if replacement is not None:
            for o in objects:o.data=replacement
    bpy.context.view_layer.update()
    meshes=[o for o in scene.objects if o.type=="MESH"]
    after=sum(triangles(o.data) for o in meshes)
    if not 30000<=after<=BUDGET:
        raise ValueError(f"Coupe budget failed: {after}")
    # Purge unused original data from the editable derivative.
    bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    for image in bpy.data.images:
        if any(name in image.name.lower() for name in REJECT_NAMES):
            raise ValueError("Excluded artwork still present: "+image.name)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"coupe.blend"))
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(OUT/"coupe.glb"),export_format="GLB",use_selection=True,export_animations=False)
    doc,_=decode((OUT/"coupe.glb").read_bytes())
    if any(any(n in image.get("name","").lower() for n in REJECT_NAMES) for image in doc.get("images",[])):
        raise ValueError("Excluded image exported")
    # Check actual exported wheel centers and source hierarchy in runtime derivative.
    names={n.get("name") for n in doc["nodes"]}
    if not {"WheelVisual_"+k for k in WHEELS}<=names or not {"DoorPivot_L","DoorPivot_R"}<=names:
        raise ValueError("Missing exported sockets")
    lo,hi=bounds(meshes)
    span=hi-lo
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.render.resolution_x=960
    scene.render.resolution_y=640
    scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new("Review Studio")
    scene.world.use_nodes=True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.32,0.37,0.45,1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value=0.65
    center=(lo+hi)/2
    for off,energy in [((4,-5,6),1600),((-4,4,4),1200),((0,5,3),800)]:
        bpy.ops.object.light_add(type="AREA",location=center+Vector(off))
        light=bpy.context.object
        light.data.energy=energy
        light.data.size=4
        light.rotation_euler=(center-light.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    scene.camera=cam
    cam.data.type="ORTHO"
    def render(name,focus,offset,scale):
        cam.location=focus+Vector(offset)
        cam.rotation_euler=(focus-cam.location).to_track_quat("-Z","Y").to_euler()
        cam.data.ortho_scale=scale
        scene.render.filepath=str(OUT/(name+".png"))
        bpy.ops.render.render(write_still=True)
    render("front",center,(5,-7,3.5),max(span)*1.35)
    render("rear",center,(-5,7,3.5),max(span)*1.35)
    # Open actual hinged geometry, retaining complete interior.
    door=bpy.data.objects["DoorPivot_L"]
    previous=door.matrix_world.copy()
    pivot=previous.translation
    sign=-1 if pivot.x<0 else 1
    door.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(sign*math.radians(55),4,"Z")@Matrix.Translation(-pivot)@previous
    bpy.context.view_layer.update()
    render("door_open",Vector((pivot.x*0.25,0,0.7)),(sign*5,-1.5,3.3),4.5)
    door.matrix_world=previous
    report={"status":"development_candidate_only","source_sha256":SHA,"source_commit":PIN,
            "license":"CC-BY-4.0","attribution":"Eric Chadwick / Darmstadt Graphics Group GmbH (2024); based on Unity Fan CC0 model",
            "modifications":"mesh reduction, excluded branding textures/plate/emblem, normalized orientation, neutral wheel pose and wheel sockets",
            "excluded_texture_references":removed,"triangles_before":before,"triangles_after":after,
            "dimensions_godot_m":[span.x,span.z,span.y],"wheels":wheel_report,
            "door_pivots":["DoorPivot_L","DoorPivot_R"],"glb_sha256":hashlib.sha256((OUT/"coupe.glb").read_bytes()).hexdigest(),
            "limitations":["Visual review of remaining marks required","No final art, LOD, seated animation or handling approval"]}
    (OUT/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("CODECITY_COUPE_READY_OK",after,wheel_report)

if __name__=="__main__":main()
