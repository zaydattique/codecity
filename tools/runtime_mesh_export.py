"""Export evaluated Blender geometry as native Panda3D EGG meshes.
Candidate runtime derivative. No still images or video.
"""
import math
import random

def export_runtime(scene, out):
    import bpy
    out.mkdir(parents=True, exist_ok=False)
    moving=("Bean-like seed","Primary root","Lateral root","Fine root","Hypocotyl","Cotyledon","True leaf")
    def write(path, objects):
        dg=bpy.context.evaluated_depsgraph_get()
        with path.open("w",encoding="utf-8") as f:
            f.write("<CoordinateSystem> { Z-up }\n")
            for index,obj in enumerate(objects):
                if obj.type not in ("MESH","CURVE") or obj.hide_render: continue
                if obj.type=="CURVE" and obj.data.bevel_factor_end<.0001: continue
                ev=obj.evaluated_get(dg)
                mesh=ev.to_mesh()
                try:
                    if not mesh.polygons: continue
                    mesh.calc_loop_triangles()
                    mat=obj.data.materials[0] if obj.data.materials else None
                    p=mat.node_tree.nodes.get("Principled BSDF") if mat and mat.use_nodes else None
                    c=tuple(p.inputs["Base Color"].default_value) if p else (.5,.5,.5,1)
                    # EGG vertex colors are display-space; procedural node graphs are not exported.
                    color=tuple(max(0,min(1,v))**(1/2.2) for v in c[:3])
                    pool="v"+str(index)
                    f.write("<Group> "+pool+" {\n<VertexPool> "+pool+" {\n")
                    inv=ev.matrix_world.to_3x3().inverted_safe().transposed()
                    for j,v in enumerate(mesh.vertices):
                        co=ev.matrix_world@v.co
                        n=(inv@v.normal).normalized()
                        f.write(f"<Vertex> {j} {{ {co.x:.7f} {co.y:.7f} {co.z:.7f} <Normal> {{ {n.x:.5f} {n.y:.5f} {n.z:.5f} }} }}\n")
                    f.write("}\n")
                    for t in mesh.loop_triangles:
                        f.write("<Polygon> { <RGBA> { "+" ".join(f"{v:.5f}" for v in (*color,1))+" } <BFace> { 1 } <VertexRef> { "+" ".join(str(i) for i in t.vertices)+" <Ref> { "+pool+" } } }\n")
                    f.write("}\n")
                finally: ev.to_mesh_clear()
    scene.frame_set(1)
    static=[o for o in scene.objects if not o.name.startswith(moving+("Water droplet",))]
    write(out/"bench.egg",static)
    for frame in range(1,121,3):
        scene.frame_set(frame)
        write(out/f"plant-{frame:03}.egg",[o for o in scene.objects if o.name.startswith(moving)])
    scene.frame_set(120)
    write(out/"plant-120.egg",[o for o in scene.objects if o.name.startswith(moving)])
    # Rendered droplets are separate from the growth snapshots; one mesh drives live irrigation.
    scene.frame_set(8)
    droplet=next(o for o in scene.objects if o.name.startswith("Water droplet") and not o.hide_render)
    old=droplet.location.copy();droplet.location=(0,0,0);bpy.context.view_layer.update()
    write(out/"drop.egg",[droplet]);droplet.location=old
    scene.frame_set(1)
