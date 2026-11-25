"""Original animated botanical macro study. Blender 4.5 LTS. Candidate only."""
import bpy
import math
import random
import json
import os
from pathlib import Path
from mathutils import Vector

OUT=Path("build/greenhouse-art").resolve()
OUT.mkdir(parents=True,exist_ok=False)
random.seed(42)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=960
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_end=120
scene.world=bpy.data.worlds.new("Studio daylight")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(0.28,0.34,0.39,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.35
def material(name,color,rough=.45,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m
soil=material("Substrate | organic grains",(.075,.035,.018),.94)
p=soil.node_tree.nodes.get("Principled BSDF")
n=soil.node_tree.nodes.new("ShaderNodeTexNoise");n.inputs["Scale"].default_value=125;n.inputs["Detail"].default_value=5
r=soil.node_tree.nodes.new("ShaderNodeValToRGB")
r.color_ramp.elements[0].position=.15;r.color_ramp.elements[0].color=(.026,.012,.005,1)
r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=(.21,.10,.041,1)
soil.node_tree.links.new(n.outputs["Fac"],r.inputs[0]);soil.node_tree.links.new(r.outputs[0],p.inputs["Base Color"])
b=soil.node_tree.nodes.new("ShaderNodeBump");b.inputs["Strength"].default_value=.65;b.inputs["Distance"].default_value=.006
soil.node_tree.links.new(n.outputs["Fac"],b.inputs["Height"]);soil.node_tree.links.new(b.outputs[0],p.inputs["Normal"])
rootmat=material("Root | pale epidermis",(.62,.44,.23),.58)
stemmat=material("Stem | epidermis",(.11,.26,.035),.52)
leafmat=material("Leaf | healthy tissue",(.095,.34,.045),.38)
leafmat.node_tree.nodes.get("Principled BSDF").inputs["Subsurface Weight"].default_value=.08
veinmat=material("Leaf midrib",(.25,.42,.08),.55)
seedmat=material("Seed | testa",(.28,.13,.048),.57)
frame=material("Anodized dark metal",(.055,.075,.066),.32,.65)
bench=material("Work surface",(.22,.26,.24),.68)
water=material("Water",(.72,.89,.98),.08)
water.node_tree.nodes.get("Principled BSDF").inputs["Transmission Weight"].default_value=1
water.node_tree.nodes.get("Principled BSDF").inputs["IOR"].default_value=1.333
def assign(obj,mat):
    obj.data.materials.append(mat);return obj
def cube(name,pos,dimensions,mat,bevel=.004):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name=name;o.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new("Edge radii","BEVEL");mod.width=bevel;mod.segments=3
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return assign(o,mat)
def ellipsoid(name,pos,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=pos)
    o=bpy.context.object;o.name=name;o.scale=scale
    for f in o.data.polygons:f.use_smooth=True
    return assign(o,mat)
def curve(name,points,radius,mat,start=None,end=None):
    c=bpy.data.curves.new(name,"CURVE");c.dimensions="3D";c.resolution_u=12;c.bevel_depth=radius;c.bevel_resolution=4;c.use_fill_caps=True
    s=c.splines.new("BEZIER");s.bezier_points.add(len(points)-1)
    for i,(p,co) in enumerate(zip(s.bezier_points,points)):
        p.co=co;p.handle_left_type=p.handle_right_type="AUTO";p.radius=max(.10,1-i/(len(points)-1)*.85)
    o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);assign(o,mat)
    if start is not None:
        c.bevel_factor_end=0;c.keyframe_insert("bevel_factor_end",frame=start)
        c.bevel_factor_end=1;c.keyframe_insert("bevel_factor_end",frame=end)
    return o
# Meter-scale rhizobox: front is intentionally open in the visualization, not fake transparent soil.
cube("Workbench",(0,.05,-.265),(1.6,.8,.055),bench,.012)
cube("Rhizobox | substrate",(0,.085,-.095),(.48,.16,.30),soil,.001)
for x in (-.252,.252):
    cube("Rhizobox side rail",(x,0,-.095),(.022,.19,.32),frame)
cube("Rhizobox foot",(0,0,-.248),(.53,.22,.022),frame)
cube("Rhizobox rear frame",(0,.17,.057),(.53,.025,.025),frame)
seed=ellipsoid("Bean-like seed",(0,.004,.045),(.012,.007,.007),seedmat)
seed.rotation_euler[1]=.45
seed.keyframe_insert("scale",frame=1)
seed.scale=(.014,.008,.008);seed.keyframe_insert("scale",frame=25)
# Roots extend by tip reveal, with taper and independent lateral growth, not whole-plant scaling.
main=[(0,.004,.039),(.004,.004,.015),(-.003,.004,-.020),(.006,.004,-.06),(.002,.004,-.105),(.014,.004,-.155),(.01,.004,-.195)]
curve("Primary root",main,.0016,rootmat,12,82)
for i in range(1,6):
    x,y,z=main[i]
    for side in (-1,1):
        length=random.uniform(.025,.08)*(1-i*.07)
        pts=[(x,y,z),(x+side*length*.28,y-.002,z-.012),(x+side*length*.68,y-.001,z-.025),(x+side*length,y-.002,z-.047)]
        curve("Lateral root",pts,.00055,rootmat,29+i*10,76+i*7)
        for j in range(2):
            a=Vector(pts[j+1]);d=Vector((side*random.uniform(.008,.025),-.001,-random.uniform(.012,.035)))
            curve("Fine root",[a,a+d*.45,a+d],.00020,rootmat,51+i*10+j*3,110+i*2)
shoot=[(0,.004,.05),(-.004,.004,.067),(-.006,.007,.095),(.005,.012,.13),(.008,.015,.17)]
curve("Hypocotyl and shoot",shoot,.0022,stemmat,29,78)
def leaf(name,origin,direction,length,width,start,end):
    base=Vector(origin);u=Vector(direction).normalized();v=Vector((-u.y,u.x,0)).normalized()
    verts=[];faces=[];N=24;M=12
    for i in range(N+1):
        t=i/N
        w=width*(math.sin(math.pi*t)**.78)*(1+.035*math.sin(t*math.pi*18))
        for j in range(M+1):
            s=2*j/M-1
            pos=u*(length*t)+v*(w*s)+Vector((0,0,.024*math.sin(math.pi*t)-.014*s*s*math.sin(math.pi*t)))
            verts.append(tuple(pos))
    for i in range(N):
        for j in range(M):
            a=i*(M+1)+j;faces.append((a,a+1,a+M+2,a+M+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.location=base;assign(o,leafmat)
    for poly in mesh.polygons:poly.use_smooth=True
    thick=o.modifiers.new("Leaf thickness","SOLIDIFY");thick.thickness=.0004
    # Unfold shape key from tightly curled blade; topology remains stable.
    o.shape_key_add(name="Basis");fold=o.shape_key_add(name="Folded")
    for i,vert in enumerate(fold.data):
        t=(i//(M+1))/N
        vert.co=u*(length*t*.15)+v*((2*(i%(M+1))/M-1)*width*.10)+Vector((0,0,length*t*.65))
    fold.value=1;fold.keyframe_insert("value",frame=start)
    fold.value=0;fold.keyframe_insert("value",frame=end)
    # Hide blade until its attachment has grown.
    for f,val in ((1,True),(start-1,True),(start,False)):
        o.hide_render=val;o.keyframe_insert("hide_render",frame=f)
    return o
leaf("Cotyledon left",shoot[2],(-1,-.15,.28),.043,.014,58,80)
leaf("Cotyledon right",shoot[2],(1,.15,.28),.10,.029,52,75)
leaf("True leaf left",shoot[3],(-.85,.45,.23),.065,.022,72,106)
leaf("True leaf right",shoot[4],(.85,-.35,.33),.065,.022,82,116)
# Nozzle and falling droplets: illustrative animation, not fluid dynamics.
cube("Irrigation rail",(0,.12,.43),(.48,.024,.024),frame)
cube("Nozzle",(0,.035,.39),(.024,.025,.07),frame)
for i in range(12):
    o=ellipsoid("Water droplet",(random.uniform(-.011,.011),.035,.36),(.002,.002,.0035),water)
    first=2+i*3
    o.keyframe_insert("location",frame=first)
    o.location.z=.058;o.keyframe_insert("location",frame=first+10)
    for f,val in ((1,True),(first,False),(first+10,True)):
        o.hide_render=val;o.keyframe_insert("hide_render",frame=f)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
def area(name,pos,power,size,color,target):
    bpy.ops.object.light_add(type="AREA",location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape="DISK";o.data.size=size;o.data.color=color;aim(o,target)
area("Large daylight",(-.6,-.7,1.0),220,.7,(1,.88,.71),(0,0,.04))
area("Cool fill",(.5,-.2,.55),95,.55,(.7,.85,1),(0,0,.05))
area("Rim",(.0,.65,.8),190,.5,(1,.94,.78),(0,0,.1))
bpy.ops.object.camera_add(location=(.40,-1.05,.27));cam=bpy.context.object
aim(cam,(0,0,.075));cam.data.lens=55;scene.camera=cam
# Native preview mesh cache: evaluated Blender geometry, no frame images.
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime_mesh_export import export_runtime
export_runtime(scene, OUT / "runtime")
if os.environ.get("CODECITY_RUNTIME_ONLY") == "1":
    print("CODECITY_RUNTIME_GEOMETRY_OK")
    raise SystemExit(0)
# Real camera render, full source retained, stage exports separate from Blender-only animation.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"greenhouse-study.blend"))
for f in (1,48,80,120):
    scene.frame_set(f);scene.render.filepath=str(OUT/f"frame-{f:03}.png");bpy.ops.render.render(write_still=True)
# Export a mesh-bearing static review derivative of the final frame, not a runtime animation.
scene.frame_set(120)
bpy.ops.export_scene.gltf(filepath=str(OUT/"greenhouse-final-review.glb"),export_format="GLB",export_animations=False)
(OUT/"report.json").write_text(json.dumps({"status":"candidate_only","blender":bpy.app.version_string,"frames":[1,48,80,120],"limitations":["No wilt branch, actual wetting shader, authored leaf veins, glass or runtime animation integration yet","Procedural substrate; licensed materials not integrated","Not species calibrated","GLB is static; animation is in Blender source only"]},indent=2))
print("CODECITY_BOTANICAL_ART_CANDIDATE_OK")
