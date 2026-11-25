"""MPFB character candidate build. Run inside Blender; no procedural substitute."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PIN = "650c5c53bd6989a8ac264f31fa1d11d4a0c7bd8a"
PACK = "https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip"


def extract_pack(pack, destination):
    """Bound extraction and reject traversal, links and duplicate paths."""
    with zipfile.ZipFile(pack) as z:
        entries = z.infolist()
        if len(entries) > 20000 or sum(e.file_size for e in entries) > 1024**3:
            raise ValueError("Asset archive exceeds limits")
        names = set()
        for e in entries:
            name = e.filename
            p = PurePosixPath(name)
            if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or str(p) == '.' or stat.S_ISLNK(e.external_attr >> 16):
                raise ValueError("Unsafe archive path")
            key = str(p).casefold()
            if key in names:
                raise ValueError("Duplicate archive path")
            names.add(key)
            target = (destination / p).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Archive escapes destination")
            if e.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(e) as source, target.open('xb') as out:
                    shutil.copyfileobj(source, out)


def load_profile(character_id):
    data = json.loads((ROOT/'art/characters.json').read_text(encoding='utf-8'))
    if data['version'] != 1 or len(data['playable']) != 2:
        raise ValueError("Exactly two playable profiles required")
    return next(p for p in data['playable'] if p['id'] == character_id)


def main():
    import bpy
    from mathutils import Vector
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', required=True, choices=['adrian','maya'])
    parser.add_argument('--pack', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    profile = load_profile(args.id)
    preset = profile['candidate']
    base = ROOT/'build'/'characters'/args.id
    base.mkdir(parents=True, exist_ok=False)
    # Use installed extension, not copied GPL program code in the game.
    import importlib
    modules = [m.module for m in bpy.context.preferences.addons if m.module.endswith('.mpfb')]
    if len(modules) != 1:
        raise RuntimeError("Install and enable the pinned MPFB extension")
    mpfb = importlib.import_module(modules[0])
    if tuple(mpfb.VERSION) != (2,0,18):
        raise RuntimeError("Wrong MPFB version")
    services = mpfb.MPFB_CONTEXTUAL_INFORMATION['SERVICES']
    H, T, L, A, E = (services[k] for k in ('HumanService','TargetService','LocationService','AssetService','ExportService'))
    # Separate extraction from MPFB lookup. Official packs are rooted at user data.
    staged = base/'pack'
    staged.mkdir()
    extract_pack(args.pack, staged)
    user_data = Path(L.get_user_data())
    user_data.mkdir(parents=True, exist_ok=True)
    categories = ('clothes','hair','skins','eyes','eyebrows','eyelashes','teeth','tongue')
    roots = [p for p in (staged, staged/'data', *[p for p in staged.iterdir() if p.is_dir()]) if (p/'skins').is_dir() and (p/'clothes').is_dir()]
    roots = list(dict.fromkeys(roots))
    if len(roots) != 1:
        raise ValueError("Unexpected system asset pack structure")
    for category in categories:
        shutil.copytree(roots[0]/category, user_data/category, dirs_exist_ok=True)
    A.update_all_asset_lists()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    info = H._create_default_human_info_dict()
    info['name'] = profile['name']
    info['phenotype'].update({k:preset[k] for k in ('gender','age','height','muscle','weight','race')})
    info.update({
        'rig':'game_engine', 'eyes':'high-poly/high-poly.mhclo',
        'eyebrows':'eyebrow001/eyebrow001.mhclo', 'eyelashes':'eyelashes01/eyelashes01.mhclo',
        'hair':f"{preset['hair']}/{preset['hair']}.mhclo",
        'clothes':[f"{preset['clothes']}/{preset['clothes']}.mhclo"],
        'skin_mhmat':f"{preset['skin']}/{preset['skin']}.mhmat",
        'skin_material_type':'GAMEENGINE', 'eyes_material_type':'MAKESKIN',
        'teeth':'teeth_base/teeth_base.mhclo', 'tongue':'tongue01/tongue01.mhclo'
    })
    settings = H.get_default_deserialization_settings()
    settings.update(subdiv_levels=0, override_clothes_model='GAMEENGINE')
    body = H.deserialize_from_dict(info, settings)
    if body is None:
        raise RuntimeError("No body generated")
    meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
    rigs = [o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    # Do not silently accept missing assets even if the upstream library logs a warning.
    required = (preset['hair'],preset['clothes'],'eyebrow001','eyelashes01','high-poly','teeth_base','tongue01')
    asset_names = ' '.join(o.name.lower() for o in meshes)
    if len(rigs)!=1 or len(rigs[0].data.bones)<20 or any(s not in asset_names for s in required):
        raise RuntimeError(f"Missing rig or body parts: {asset_names}")
    if any(not o.data.uv_layers or not o.data.materials for o in meshes):
        raise RuntimeError("Missing UVs or materials")
    if not any(n.type=='TEX_IMAGE' and n.image for m in body.data.materials if m and m.use_nodes for n in m.node_tree.nodes):
        raise RuntimeError("Body has no direct skin image texture")
    for image in bpy.data.images:
        if image.source=='FILE' and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).is_file():
            raise RuntimeError(f"Missing texture: {image.name}")
    # Preserve editable human source first; then bake modelling masks for the candidate GLB.
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(base/f"{args.id}.blend"))
    E.bake_modifiers_remove_helpers(body,bake_masks=True,bake_subdiv=False,remove_helpers=True)
    bpy.context.view_layer.update()
    objects=list(bpy.context.scene.objects)
    meshes=[o for o in objects if o.type=='MESH']
    triangles=0
    for o in meshes:
        o.data.calc_loop_triangles()
        triangles+=len(o.data.loop_triangles)
    if not 5000<=triangles<=100000:
        raise RuntimeError(f"Invalid candidate triangle count: {triangles}")
    pts=[o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)))
    hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    height=hi.z-lo.z
    if not 1.45<=height<=2.1:
        raise RuntimeError(f"Unexpected human height: {height}")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(base/f"{args.id}.glb"),export_format='GLB',use_selection=True,export_animations=False)
    # Neutral studio renders show the real mesh; no AI imagery.
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.device='CPU'
    scene.cycles.samples=32
    scene.cycles.use_denoising=True
    scene.render.resolution_x=768
    scene.render.resolution_y=1024
    scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('Neutral studio')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.25,0.27,0.30,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.7
    center=(lo+hi)/2
    for offset,power in [((2,-3,3),600),((-2,-1,2),350),((0,2,3),400)]:
        bpy.ops.object.light_add(type='AREA',location=center+Vector(offset))
        lamp=bpy.context.object
        lamp.data.energy=power
        lamp.data.size=2
        lamp.rotation_euler=(center-lamp.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    scene.camera=cam
    cam.data.type='ORTHO'
    scene.render.image_settings.file_format='PNG'
    for name,focus,offset,scale in [
        ('front',center,(0,-4,0.1),height*1.25),
        ('three_quarter',center,(2,-4,0.1),height*1.25),
        ('face',Vector((center.x,center.y,hi.z-0.13)),(0,-4,0.03),0.48)]:
        cam.location=focus+Vector(offset)
        cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=scale
        scene.render.filepath=str(base/f'{name}.png')
        bpy.ops.render.render(write_still=True)
    names=[f'{args.id}.blend',f'{args.id}.glb','front.png','three_quarter.png','face.png']
    report={'status':'candidate_only','profile':args.id,'triangles':triangles,'bones':len(rigs[0].data.bones),'height_m':height,'mpfb_commit':PIN,'pack_url':PACK,'pack_sha256':hashlib.file_digest(args.pack.open('rb'),'sha256').hexdigest(),'source_license':'CC0-1.0','output_hashes':{n:hashlib.sha256((base/n).read_bytes()).hexdigest() for n in names},'limitations':['generic CC0 outfit and hair; not final design','no motion clips or LODs','no Godot deformation or gameplay approval']}
    (base/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('CODECITY_CHARACTER_CANDIDATE_OK')


if __name__=='__main__':
    main()
