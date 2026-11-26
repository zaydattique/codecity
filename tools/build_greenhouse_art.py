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
scene.view_settings.exposure=-1.1
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
# Verified CC0 diffuse and normal textures are shared with the native runtime.
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from greenhouse_soil import acquire
soil_maps=acquire(OUT / "soil-source")
for key in ("diff","nor_gl","rough"):
    image=bpy.data.images.load(str(soil_maps[key]),check_existing=True)
    node=soil.node_tree.nodes.new("ShaderNodeTexImage");node.image=image
    if key=="diff":
        soil.node_tree.links.new(node.outputs["Color"],p.inputs["Base Color"])
    elif key=="rough":
        image.colorspace_settings.name="Non-Color"
        soil.node_tree.links.new(node.outputs["Color"],p.inputs["Roughness"])
    else:
        image.colorspace_settings.name="Non-Color"
        normal=soil.node_tree.nodes.new("ShaderNodeNormalMap")
        soil.node_tree.links.new(node.outputs["Color"],normal.inputs["Color"])
        soil.node_tree.links.new(normal.outputs["Normal"],p.inputs["Normal"])
    image.pack()
rootmat=material("Root | pale epidermis",(.72,.59,.37),.58)
stemmat=material("Stem | epidermis",(.11,.26,.035),.52)
leafmat=material("Leaf | healthy tissue",(.095,.34,.045),.38)
leafmat.node_tree.nodes.get("Principled BSDF").inputs["Subsurface Weight"].default_value=.08
veinmat=material("Leaf midrib",(.25,.42,.08),.55)
seedmat=material("Seed | testa",(.28,.13,.048),.57)
frame=material("Anodized dark metal",(.055,.075,.066),.32,.65)
bench=material("Work surface",(.29,.19,.105),.64)
floor=material("Concrete",(.30,.34,.30),.87)
aluminum=material("Brushed aluminum",(.43,.51,.46),.35,.7)
glass=material("Translucent glazing",(.59,.77,.68),.25)
rubber=material("Black rubber",(.028,.036,.030),.86)
blue=material("Valve blue",(.025,.16,.30),.38)
stone=material("Substrate grit",(.16,.105,.062),.92)
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
# Physical legs and floor for the wider explanation camera.
for x in (-.70,.70):
    for y in (-.28,.38):
        cube("Workbench leg",(x,y,-.636),(.046,.046,.69),frame,.003)
cube("Greenhouse floor",(0,0,-1.005),(7,7,.04),floor,.002)
# Real three-dimensional structural framing, workbench details and plumbing.
for x in (-.73,.73):
    cube("Bench cross brace",(x,.05,-.83),(.04,.69,.04),frame)
for y in (-.28,.38):
    cube("Bench longitudinal brace",(0,y,-.83),(1.43,.035,.04),frame)
for x in (-2.4,-1.2,0,1.2,2.4):
    cube("Architecture vertical mullion",(x,2.48,.58),(.055,.075,3.12),aluminum)
for z in (-.58,.48,1.52,2.12):
    cube("Architecture rear transom",(0,2.48,z),(4.86,.075,.05),aluminum)
for x in (-2.4,2.4):
    for y in (-1.5,-.2,1.15,2.48):
        cube("Architecture side column",(x,y,.58),(.055,.055,3.12),aluminum)
    for z in (-.58,.48,1.52,2.12):
        cube("Architecture side rail",(x,.49,z),(.055,3.98,.045),aluminum)
for y in (-1.5,-.2,1.15,2.48):
    for side in (-1,1):
        p=cube("Architecture roof rafter",(side*1.2,y,2.56),(2.56,.06,.06),aluminum)
        p.rotation_euler.y=side*.34
cube("Architecture ridge",(0,.49,3.02),(.075,4.0,.075),aluminum)
cube("Architecture rear foundation",(0,2.48,-.79),(4.86,.12,.4),floor)
for x in (-2.4,2.4):cube("Architecture side foundation",(x,.49,-.79),(.12,3.98,.4),floor)
# Exterior glazing is deliberately a lightly tinted opaque daylight backing in EGG.
# Do not call this physically accurate transmission.
cube("Architecture rear daylight",(0,2.58,.75),(4.85,.035,2.75),glass,.001)
for i in range(6):
    cube("Floor expansion joint",(0,-2.5+i,-.983),(6.9,.006,.002),rubber,0)
for i in range(6):cube("Floor longitudinal joint",(-2.5+i,0,-.983),(.006,6.9,.002),rubber,0)
substrate=cube("Rhizobox | substrate",(0,.085,-.095),(.48,.16,.30),soil,.001)
# Planar texture projection on each face, consistent with runtime EGG UVs.
for poly in substrate.data.polygons:
    for i in poly.loop_indices:
        co=substrate.matrix_world@substrate.data.vertices[substrate.data.loops[i].vertex_index].co
        n=poly.normal
        substrate.data.uv_layers.active.data[i].uv=((co.y if abs(n.x)>.5 else co.x)*3.2,(co.y if abs(n.z)>.5 else co.z)*3.2)
for x in (-.252,.252):
    cube("Rhizobox side rail",(x,0,-.095),(.022,.19,.32),frame)
cube("Rhizobox foot",(0,0,-.248),(.53,.22,.022),frame)
cube("Rhizobox rear frame",(0,.17,.057),(.53,.025,.025),frame)
cube("Rhizobox back plate",(0,.179,-.095),(.52,.016,.31),aluminum)
# Detailed irregular organic particles on the top surface, not a uniform brown slab.
for i in range(175):
    x=random.uniform(-.235,.235);y=random.uniform(.009,.16)
    z=.055+random.uniform(-.001,.003)
    size=random.uniform(.0012,.0046)
    o=ellipsoid("Rhizobox grain",(x,y,z),(size,size*.75,size*.55),stone)
    o.rotation_euler=(random.random(),random.random(),random.random())
for x in (-.251,.251):
    for z in (-.22,.035):ellipsoid("Rhizobox fastener",(x,-.099,z),(.004,.002,.004),aluminum)
seed=ellipsoid("Bean-like seed",(0,.004,.045),(.012,.007,.007),seedmat)
seed.rotation_euler[1]=.45
# Distinct darker hilum ridge at the seed attachment.
# Keep the seed front face in contact with the cutaway.
seed.keyframe_insert("scale",frame=1)
seed.scale=(.014,.008,.008);seed.keyframe_insert("scale",frame=25)
# Roots extend by tip reveal, with taper and independent lateral growth, not whole-plant scaling.
main=[(0,.003,.039),(.004,.002,.015),(-.003,.001,-.020),(.006,.001,-.06),(.002,.001,-.105),(.014,.001,-.155),(.01,.001,-.195)]
curve("Primary root",main,.0020,rootmat,12,82)
for i in range(1,6):
    x,y,z=main[i]
    for side in (-1,1):
        length=random.uniform(.025,.08)*(1-i*.07)
        pts=[(x,y,z),(x+side*length*.28,y-.002,z-.012),(x+side*length*.68,y-.001,z-.025),(x+side*length,y-.002,z-.047)]
        curve("Lateral root",pts,.00085,rootmat,26+i*11,min(120,82+i*7))
        for j in range(2):
            a=Vector(pts[j+1]);d=Vector((side*random.uniform(.008,.025),-.001,-random.uniform(.012,.035)))
            curve("Fine root",[a,a+d*.45,a+d],.00030,rootmat,58+i*9+j*3,min(120,110+i*2))
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
            midrib=.0018*math.exp(-abs(s)*13)*math.sin(math.pi*t)
            vein=.00055*math.cos(11*math.pi*t-abs(s)*4)*math.sin(math.pi*t)*abs(s)
            pos=u*(length*t)+v*(w*s)+Vector((0,0,.018*math.sin(math.pi*t)-.010*s*s*math.sin(math.pi*t)+midrib+vein))
            verts.append(tuple(pos))
    for i in range(N):
        for j in range(M):
            a=i*(M+1)+j;faces.append((a,a+1,a+M+2,a+M+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.location=base;assign(o,leafmat)
    o["wilt_sign"]=-1 if u.x<0 else 1
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
leaf("Cotyledon right",shoot[2],(1,.15,.28),.043,.014,58,80)
leaf("True leaf left",shoot[3],(-.85,.45,.23),.065,.022,72,106)
leaf("True leaf right",shoot[4],(.85,-.35,.33),.065,.022,82,116)
# Nozzle and falling droplets: illustrative animation, not fluid dynamics.
cube("Irrigation rail",(0,.12,.43),(.48,.024,.024),frame)
cube("Nozzle",(0,.035,.39),(.024,.025,.07),frame)
curve("Supply hose",[(.40,.24,-.21),(.43,.25,.1),(.37,.19,.42),(0,.12,.43)],.006,rubber)
cube("Valve housing",(.25,.12,.43),(.054,.05,.048),aluminum)
cube("Valve lever",(.25,.12,.468),(.065,.012,.012),blue)
cube("Sensor enclosure",(.34,.015,-.12),(.09,.045,.064),frame)
cube("Sensor display",(.34,-.011,-.12),(.068,.003,.036),glass,.001)
curve("Sensor cable",[(.34,.035,-.12),(.30,.07,-.20),(.19,.14,-.20),(.18,.14,.04)],.0025,rubber)
for x in (.17,.19):curve("Sensor electrode",[(x,.14,.045),(x,.14,-.035)],.0017,aluminum)
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
from runtime_mesh_export import export_runtime
export_runtime(scene, OUT / "runtime", soil_maps)
# Save editable source even on the runtime-only build.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"greenhouse-study.blend"))
if os.environ.get("CODECITY_RUNTIME_ONLY") == "1":
    print("CODECITY_RUNTIME_GEOMETRY_OK")
    raise SystemExit(0)
# Real camera render, full source retained, stage exports separate from Blender-only animation.
for f in (1,48,80,120):
    scene.frame_set(f);scene.render.filepath=str(OUT/f"frame-{f:03}.png");bpy.ops.render.render(write_still=True)
# Export a mesh-bearing static review derivative of the final frame, not a runtime animation.
scene.frame_set(120)
bpy.ops.export_scene.gltf(filepath=str(OUT/"greenhouse-final-review.glb"),export_format="GLB",export_animations=False)
(OUT/"report.json").write_text(json.dumps({"status":"candidate_only","blender":bpy.app.version_string,"frames":[1,48,80,120],"limitations":["Runtime leaf droop uses authored leaf pivots; no plant biomechanics","Opaque daylight glazing; no fluid simulation","Not species calibrated","GLB review is static; runtime growth is mesh samples"]},indent=2))
print("CODECITY_BOTANICAL_ART_CANDIDATE_OK")
