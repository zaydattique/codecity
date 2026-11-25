"""Inspect a pinned CC0 car GLB; export evidence, not a driveable vehicle."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references/spectral/spectral_gt_rs_game_ready.glb"
OUT = ROOT / "build/vehicle-candidate"
PIN = "34499c501908818a2b08e589a7aecf963343cee7"
BLOB = "f5b814848453a6c75a48f5047fdadaa7bdc78969"


def main():
    raw = SOURCE.read_bytes()
    if len(raw) != 4688844 or hashlib.sha1(f"blob {len(raw)}\0".encode()+raw, usedforsecurity=False).hexdigest()!=BLOB:
        raise ValueError("Wrong pinned GLB bytes")
    OUT.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    meshes = [o for o in scene.objects if o.type == "MESH"]
    names = " ".join(o.name.lower() for o in meshes)
    roles = ("driver_seat", "passenger_seat", "steering_wheel", "dashboard", "front_left_tire", "front_right_tire", "rear_left_tire", "rear_right_tire")
    if not all(role in names for role in roles):
        raise RuntimeError("Missing required cockpit or wheel geometry")
    triangles = 0
    for mesh in meshes:
        mesh.data.calc_loop_triangles()
        triangles += len(mesh.data.loop_triangles)
        if not mesh.data.materials:
            raise RuntimeError("Missing material: "+mesh.name)
    if not 10000 <= triangles <= 2000000:
        raise RuntimeError("Unexpected source triangle count")
    points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
    lo = Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi = Vector(tuple(max(v[i] for v in points) for i in range(3)))
    size = hi-lo
    if not 3.0 <= max(size) <= 6.5 or not 0.8 <= size.z <= 2.2:
        raise ValueError(f"Unexpected car dimensions {size}")
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"candidate.blend"))
    (OUT/"candidate.glb").write_bytes(raw)
    center = (lo+hi)/2
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new("Studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.25,0.25,0.25,1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    for offset,power in [((4,-5,6),1800),((-4,4,4),1500),((0,-4,2),800)]:
        bpy.ops.object.light_add(type="AREA",location=center+Vector(offset))
        light=bpy.context.object
        light.data.energy=power
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
        scene.render.filepath=str(OUT/f"{name}.png")
        bpy.ops.render.render(write_still=True)
    render("exterior",center,(6,-8,4),max(size)*1.35)
    # Reveal existing cockpit, not a new invented interior.
    cutaway=[o for o in meshes if any(s in o.name.lower() for s in ("body_shell_hero","cabin_roof_shell","windshield","window","glass"))]
    if not cutaway:
        raise RuntimeError("No identifiable cutaway shell")
    for o in cutaway: o.hide_render=True
    focus=Vector((0,0,1.02))
    render("interior_cutaway",focus,(-2,-4,3),3.4)
    report={"status":"candidate_only","source_commit":PIN,"source_git_blob":BLOB,"license":"CC0-1.0","mesh_objects":len(meshes),"triangles":triangles,"dimensions_m":list(size),"source_sha256":hashlib.sha256(raw).hexdigest(),"animations":[a.name for a in bpy.data.actions],"within_hero_triangle_budget":30000<=triangles<=60000,"limitations":["cutaway for inspection only","no collision, drivetrain, LOD, optimization or final art approval"]}
    (OUT/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("CODECITY_VEHICLE_CANDIDATE_OK")


if __name__=="__main__":
    main()
