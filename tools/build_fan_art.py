"""Original modeled greenhouse exhaust fan, separable rotor and housing."""
import bpy, math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
out=Path("build/greenhouse-art/runtime")
def material(name,c,rough,metal):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*c,1);p.inputs["Roughness"].default_value=rough;p.inputs["Metallic"].default_value=metal
    return m
metal=material("Powder coated aluminum",(.24,.31,.27),.46,.5)
dark=material("Motor housing",(.055,.073,.064),.56,.3)
blade=material("Anodized blades",(.43,.53,.47),.33,.65)
steel=material("Fasteners",(.52,.55,.50),.27,.85)
def finish(o,m):
    o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def box(name,pos,size,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    b=o.modifiers.new("Edge rounding","BEVEL");b.width=.008;b.segments=3
    return finish(o,m)
def cylinder(name,r,depth,pos,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=pos,rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name=name;return finish(o,m)
def torus(name,r,t,y,m):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=(0,y,0),rotation=(math.pi/2,0,0),major_radius=r,minor_radius=t)
    o=bpy.context.object;o.name=name;return finish(o,m)
housing=[];rotor=[]
for x in (-.51,.51):housing.append(box("Mounting rail",(x,.09,0),(.08,.22,1.1),metal))
for z in (-.51,.51):housing.append(box("Mounting rail",(0,.09,z),(1.02,.22,.08),metal))
for y in (-.10,.11):housing.append(torus("Shroud rim",.47,.036,y,metal))
for i in range(12):
    a=i*math.pi/6
    o=box("Safety grille spoke",(0,-.137,0),(.009,.015,.91),steel);o.rotation_euler.y=a;housing.append(o)
for r in (.19,.32,.43):housing.append(torus("Safety grille ring",r,.004,-.15,steel))
housing.append(cylinder("Rear motor",.13,.18,(0,.18,0),dark))
for x in (-.51,.51):
    for z in (-.51,.51):housing.append(cylinder("Mount bolt",.022,.035,(x,-.035,z),steel))
rotor.append(cylinder("Rotor hub",.115,.12,(0,-.005,0),dark))
for i in range(5):
    a=i*2*math.pi/5
    v=[];faces=[];N=12
    for j in range(N+1):
        t=j/N;r=.105+.32*t
        sweep=.50*t*t
        for side in (-1,1):
            angle=a+sweep+side*(.28-.10*t)*math.sin(.4+2.2*t)
            v.append((r*math.cos(angle),.04*t+side*.018*math.sin(math.pi*t),r*math.sin(angle)))
    for j in range(N):faces.append((2*j,2*j+1,2*j+3,2*j+2))
    mesh=bpy.data.meshes.new("Curved impeller");mesh.from_pydata(v,[],faces);mesh.update()
    o=bpy.data.objects.new("Impeller blade",mesh);bpy.context.collection.objects.link(o);finish(o,blade)
    s=o.modifiers.new("Blade thickness","SOLIDIFY");s.thickness=.009
    b=o.modifiers.new("Rounded edge","BEVEL");b.width=.002;b.segments=2;rotor.append(o)
def export(objects,name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str((out/name).resolve()),export_format="GLB",use_selection=True,export_animations=False,export_apply=True)
export(housing,"fan-housing.glb");export(rotor,"fan-rotor.glb")
bpy.ops.wm.save_as_mainfile(filepath=str((out.parent/"fan.blend").resolve()))
