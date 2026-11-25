"""Non-destructive, instance-weighted mesh budget experiment in Blender.

Only static environment/vehicle candidates. Do not use on skinned characters.
Preserve transforms, hierarchy, materials, UVs and bounds. Reject individual
unsafe reductions and report actual budget failure rather than falsifying it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector

SOURCES={
    "street":("build/optimization-input/harbor_exteriors.blend","be4c7ef3c87a688dcfb39a1951e5069a97774eefc9e27cebc8a42ba6ceebc005",110000),
    "coupe":("build/optimization-input/CarConcept.glb","c272098089d78c5cd9fd9f24ff50ee8acf8d932c55f2d55fc10adb6c8998966b",60000),
}

def triangles(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)

def bounds(mesh):
    if not mesh.vertices:
        raise ValueError("Empty mesh")
    return tuple((min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)) for i in range(3))

def groups_for_scene():
    groups={}
    for obj in bpy.context.scene.objects:
        if obj.type!="MESH": continue
        if any(m.type=="ARMATURE" for m in obj.modifiers) or obj.data.shape_keys:
            raise ValueError("Static optimizer cannot touch skinned or morph meshes")
        groups.setdefault(obj.data,[]).append(obj)
    return groups

def reduced_mesh(original,goal):
    original_count=triangles(original)
    if goal>=original_count: return None,"unchanged"
    old_bounds=bounds(original)
    span=max(hi-lo for lo,hi in old_bounds)
    work=original.copy()
    temp=bpy.data.objects.new("QA_Optimizer_Temporary",work)
    bpy.context.collection.objects.link(temp)
    result=None
    try:
        # First simplify coplanar tessellation, respecting UV/material/sharp boundaries.
        planar=temp.modifiers.new("Planar candidate","DECIMATE")
        planar.decimate_type="DISSOLVE"
        planar.angle_limit=0.0174532925
        planar.delimit={"NORMAL","MATERIAL","SEAM","SHARP","UV"}
        bpy.context.view_layer.update()
        depsgraph=bpy.context.evaluated_depsgraph_get()
        result=bpy.data.meshes.new_from_object(temp.evaluated_get(depsgraph),preserve_all_data_layers=True,depsgraph=depsgraph)
        planar_count=triangles(result)
        temp.modifiers.remove(planar)
        temp.data=result
        if planar_count>goal:
            collapse=temp.modifiers.new("Budget candidate","DECIMATE")
            collapse.decimate_type="COLLAPSE"
            collapse.ratio=max(0.001,min(1.0,goal/planar_count))
            collapse.use_collapse_triangulate=True
            bpy.context.view_layer.update()
            final=bpy.data.meshes.new_from_object(temp.evaluated_get(depsgraph),preserve_all_data_layers=True,depsgraph=depsgraph)
            temp.modifiers.remove(collapse)
            temp.data=final
            bpy.data.meshes.remove(result)
            result=final
        count=triangles(result)
        if count<4 or count>=original_count:
            return None,"no useful reduction"
        if len(result.materials)!=len(original.materials) or len(result.uv_layers)!=len(original.uv_layers):
            return None,"material or UV layer mismatch"
        if span>0 and any(abs(a-b)>max(0.002,0.035*span) for before,after in zip(old_bounds,bounds(result)) for a,b in zip(before,after)):
            return None,"bounds changed excessively"
        result.name=original.name+"_budget_candidate"
        accepted=result
        result=None
        return accepted,"reduced"
    finally:
        bpy.data.objects.remove(temp,do_unlink=True)
        if result is not None and result.users==0: bpy.data.meshes.remove(result)
        if work.users==0: bpy.data.meshes.remove(work)

def render_view(scene,name,location,target,lens,out):
    cam=scene.camera
    cam.location=Vector(location)
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    scene.render.filepath=str(out/(name+".png"))
    bpy.ops.render.render(write_still=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("kind",choices=SOURCES)
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    path,digest,budget=SOURCES[args.kind]
    source=Path(path).resolve()
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
        raise ValueError("Reviewed input hash mismatch")
    out=Path("build/optimization-"+args.kind).resolve()
    out.mkdir(parents=True,exist_ok=False)
    if source.suffix==".blend":
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source))
    scene=bpy.context.scene
    groups=groups_for_scene()
    before=sum(triangles(mesh)*len(objects) for mesh,objects in groups.items())
    if before<=0: raise ValueError("Missing candidate geometry")
    base={mesh:min(triangles(mesh),64) for mesh in groups}
    floor=sum(base[m]*len(groups[m]) for m in groups)
    excess=max(1,before-floor)
    ratio=max(0,min(1,(budget-floor)/excess))
    details=[]
    for mesh,objects in list(groups.items()):
        old=triangles(mesh)
        goal=max(base[mesh],int(base[mesh]+ratio*(old-base[mesh])))
        candidate,reason=reduced_mesh(mesh,goal)
        if candidate is not None:
            for obj in objects: obj.data=candidate
        details.append({"mesh":mesh.name,"instances":len(objects),"before":old,
                        "after":triangles(candidate) if candidate is not None else old,"reason":reason})
    bpy.context.view_layer.update()
    meshes=[o for o in scene.objects if o.type=="MESH"]
    after=sum(triangles(o.data) for o in meshes)
    if after<=0 or after>before:
        raise ValueError("Invalid optimized mesh count")
    # Strip named exterior marks from the inspection derivative only. Textured
    # logos can still be baked into tires/materials: no trademark clearance claim.
    removed=[]
    if args.kind=="coupe":
        for o in list(scene.objects):
            if o.type=="MESH" and any(s in o.name.lower() for s in ("emblem","logo","licenseplate","license_plate")):
                if not o.children:
                    removed.append(o.name)
                    bpy.data.objects.remove(o,do_unlink=True)
        meshes=[o for o in scene.objects if o.type=="MESH"]
        after=sum(triangles(o.data) for o in meshes)
    # Keep street source and GLB; car remains inspection-only because of logo rights.
    if args.kind=="street":
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"candidate.blend"))
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_scene.gltf(filepath=str(out/"candidate.glb"),export_format="GLB",use_selection=True)
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.render.resolution_x=1280 if args.kind=="street" else 960
    scene.render.resolution_y=720 if args.kind=="street" else 640
    scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new("QA daylight")
    scene.world.use_nodes=True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.52,0.64,0.8,1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value=0.55
    bpy.ops.object.light_add(type="SUN")
    bpy.context.object.data.energy=2.7
    bpy.context.object.rotation_euler=(0.55,-0.6,-0.45)
    bpy.ops.object.camera_add()
    scene.camera=bpy.context.object
    if args.kind=="street":
        render_view(scene,"street_eye",(1.2,-14.5,1.7),(0,8,2.8),24,out)
        render_view(scene,"overview",(25,-29,28),(0,0,2),36,out)
    else:
        pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
        lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)))
        hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)))
        center=(lo+hi)/2
        render_view(scene,"exterior",center+Vector((6,-5,3)),center,50,out)
    (out/"report.json").write_text(json.dumps({
        "status":"optimization_candidate_only","kind":args.kind,"source_sha256":digest,
        "triangles_before":before,"triangles_after":after,"budget":budget,"budget_pass":after<=budget,
        "instance_count":len(meshes),"named_marks_removed":removed,"mesh_results":details,
        "limitations":["Requires visual seam/silhouette/UV review","No physics, collision, navigation or runtime performance approval",
                       "Car baked logo review remains pending"] if args.kind=="coupe" else ["Requires visual seam/silhouette/UV review","No physics, collision, navigation or runtime performance approval"]
    },indent=2),encoding="utf-8")
    print("CODECITY_OPTIMIZATION_CANDIDATE_OK",before,after,"budget_pass",after<=budget)

if __name__=="__main__":
    main()
