"""Licensed MPFB teacher candidate, custom explanatory pose clip. Not a likeness."""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector, Quaternion
source=Path("build/teacher/sana/runtime.glb")
assert hashlib.sha256(source.read_bytes()).hexdigest()=="f88a7cd9ea11340f362b5e0ee71e31054b425b72db5ba0e884fdf9fc77d9e687"
report=json.loads(source.with_name("report.json").read_text())
assert report["source_license"]=="CC0-1.0" and report["bones"]==53
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
rig=next(o for o in bpy.context.scene.objects if o.type=="ARMATURE")
for o in bpy.context.scene.objects: o.animation_data_clear()
for action in list(bpy.data.actions): bpy.data.actions.remove(action)
for b in rig.pose.bones:
    b.rotation_mode="QUATERNION";b.rotation_quaternion=Quaternion();b.location=(0,0,0);b.scale=(1,1,1)
# Rest T-pose corrected to natural standing, with a bent left arm extended on cue.
# Desired vectors are in Blender world space. Solve parent-first using current pose.
def aim(name,direction):
    b=rig.pose.bones[name]
    current=(rig.matrix_world.to_3x3() @ (b.tail-b.head)).normalized()
    target=Vector(direction).normalized()
    delta=current.rotation_difference(target)
    world=(rig.matrix_world @ b.matrix).to_quaternion()
    b.rotation_quaternion=b.rotation_quaternion @ (world.inverted() @ delta @ world)
    bpy.context.view_layer.update()
def pose(frame,gesture):
    for b in rig.pose.bones:
        b.rotation_quaternion=Quaternion();b.location=(0,0,0)
    bpy.context.view_layer.update()
    aim("upperarm_r",(-.12,0,-1));aim("lowerarm_r",(-.04,-.12,-1))
    aim("upperarm_l",(.14+.45*gesture,-.12,-1))
    aim("lowerarm_l",(.10+.85*gesture,-.12-.45*gesture,-1+.85*gesture))
    for b in rig.pose.bones:
        b.keyframe_insert("rotation_quaternion",frame=frame,group=b.name)
for frame,g in [(1,0),(18,0),(42,1),(78,1),(105,0),(120,0)]:pose(frame,g)
rig.animation_data.action.name="explain"
bpy.context.scene.render.fps=30
bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=120
bpy.context.scene.frame_set(1)
out=Path("build/greenhouse-art/runtime")
bpy.ops.export_scene.gltf(filepath=str((out/"teacher.glb").resolve()),export_format="GLB",export_animations=True,export_animation_mode="ACTIONS")
bpy.ops.wm.save_as_mainfile(filepath=str((out.parent/"teacher.blend").resolve()))
(out/"teacher-provenance.json").write_text(json.dumps({"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"output_sha256":hashlib.sha256((out/"teacher.glb").read_bytes()).hexdigest(),"source":"MPFB CC0 Sana rig from run 45666586177","motion":"original authored explain gesture; pending visual approval","source_report":report},indent=2))
