"""Blender background script: export and render actual licensed mesh, not a substitute."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

BASE = Path('build/asset-pilot').resolve()
manifest = json.loads((BASE / 'provenance.json').read_text(encoding='utf-8'))
for name, digest in manifest['sha256'].items():
    path = (BASE / 'source' / name).resolve()
    if not path.is_relative_to(BASE / 'source') or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Source hash mismatch')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(BASE / 'source' / manifest['entry']))
objects = list(bpy.context.scene.objects)
meshes = [obj for obj in objects if obj.type == 'MESH']
triangles = 0
for obj in meshes:
    obj.data.calc_loop_triangles()
    triangles += len(obj.data.loop_triangles)
    if not obj.data.uv_layers or not obj.data.materials:
        raise ValueError('Missing UVs or materials')
if not 100 <= triangles <= 15000:
    raise ValueError(f'Unexpected triangle count: {triangles}')
for image in bpy.data.images:
    if image.source == 'FILE' and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).is_file():
        raise ValueError(f'Missing texture: {image.name}')
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
lo = Vector(tuple(min(v[i] for v in points) for i in range(3)))
hi = Vector(tuple(max(v[i] for v in points) for i in range(3)))
center = (hi + lo) / 2
span = max(hi - lo)
if not 0.8 <= span <= 1.6:
    raise ValueError(f'Unexpected bench scale: {span}')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE / 'bench.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(BASE / 'bench.glb'), export_format='GLB', use_selection=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new('Studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.18, 0.20, 0.23, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.7
bpy.ops.object.camera_add(location=center + Vector((2.5, -3.5, 2.1)) * span)
cam = bpy.context.object
cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = span * 1.65
scene.camera = cam
for name, offset, power in [('Key', (1, -2, 3), 450), ('Fill', (-2, 1, 2), 250)]:
    bpy.ops.object.light_add(type='AREA', location=center + Vector(offset) * span)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = power * span ** 2
    lamp.data.shape = 'DISK'
    lamp.data.size = span * 2
    lamp.rotation_euler = (center - lamp.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(BASE / 'preview.png')
bpy.ops.render.render(write_still=True)
report = {'status': 'candidate_only', 'triangles': triangles, 'dimensions_m': list(hi-lo), 'blender_version': bpy.app.version_string, 'outputs': {name: hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in ('bench.blend', 'bench.glb', 'preview.png')}}
(BASE / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CODECITY_ASSET_PILOT_OK')
