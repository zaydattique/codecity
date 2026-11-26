"""Export evaluated Blender geometry as native Panda3D EGG meshes.
Candidate runtime derivative. No still images or video.
"""
import shutil

def export_runtime(scene, out, soil_maps):
    import bpy
    out.mkdir(parents=True, exist_ok=False)
    for kind,path in soil_maps.items():
        shutil.copy2(path,out/("soil-"+path.name))
    shutil.copy2(next(iter(soil_maps.values())).parent/"provenance.json",out/"soil-provenance.json")
    moving=("Bean-like seed","Primary root","Lateral root","Fine root","Hypocotyl","Cotyledon","True leaf")
    def write(path, objects):
        dg=bpy.context.evaluated_depsgraph_get()
        with path.open("w",encoding="utf-8") as f:
            f.write("<CoordinateSystem> { Z-up }\n")
            if any(o.name.startswith("Rhizobox | substrate") for o in objects):
                f.write('<Texture> soil { "soil-'+soil_maps["diff"].name+'" <Scalar> envtype { modulate } <Scalar> wrap { repeat } }\n')
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
                    color=tuple(max(0,min(1,v))**(1/2.2) for v in c[:3])
                    is_soil=obj.name.startswith("Rhizobox | substrate")
                    is_leaf=obj.name.startswith(("Cotyledon","True leaf"))
                    pool="soil_surface" if is_soil else ("leaf_"+("left_" if obj.get("wilt_sign",1)<0 else "right_")+str(index) if is_leaf else "v"+str(index))
                    f.write("<Group> "+pool+" {\n")
                    pivot=ev.matrix_world.translation if is_leaf else ev.matrix_world.translation*0
                    if is_leaf:f.write(f"<Transform> {{ <Translate> {{ {pivot.x:.7f} {pivot.y:.7f} {pivot.z:.7f} }} }}\n")
                    f.write("<VertexPool> "+pool+" {\n")
                    inv=ev.matrix_world.to_3x3().inverted_safe().transposed()
                    if is_soil:
                        for j,loop in enumerate(mesh.loops):
                            co=ev.matrix_world@mesh.vertices[loop.vertex_index].co
                            n=(inv@mesh.polygons[next(p.index for p in mesh.polygons if j in p.loop_indices)].normal).normalized()
                            u=(co.y if abs(n.x)>.5 else co.x)*3.2
                            v=(co.y if abs(n.z)>.5 else co.z)*3.2
                            from mathutils import Vector
                            tangent=Vector((0,1,0)) if abs(n.x)>.5 else Vector((1,0,0))
                            tangent=(tangent-n*tangent.dot(n)).normalized()
                            binormal=n.cross(tangent).normalized()
                            f.write(f"<Vertex> {j} {{ {co.x:.7f} {co.y:.7f} {co.z:.7f} <Normal> {{ {n.x:.5f} {n.y:.5f} {n.z:.5f} }} <UV> {{ {u:.6f} {v:.6f} <Tangent> {{ {tangent.x:.5f} {tangent.y:.5f} {tangent.z:.5f} }} <Binormal> {{ {binormal.x:.5f} {binormal.y:.5f} {binormal.z:.5f} }} }} }}\n")
                    else:
                        for j,v in enumerate(mesh.vertices):
                            co=(ev.matrix_world@v.co)-pivot;n=(inv@v.normal).normalized()
                            f.write(f"<Vertex> {j} {{ {co.x:.7f} {co.y:.7f} {co.z:.7f} <Normal> {{ {n.x:.5f} {n.y:.5f} {n.z:.5f} }} }}\n")
                    f.write("}\n")
                    for t in mesh.loop_triangles:
                        rgba=(1,1,1,1) if is_soil else (*color,1)
                        tex="<TRef> { soil } " if is_soil else ""
                        indices=t.loops if is_soil else t.vertices
                        f.write("<Polygon> { "+tex+"<RGBA> { "+" ".join(f"{v:.5f}" for v in rgba)+" } <BFace> { 1 } <VertexRef> { "+" ".join(str(i) for i in indices)+" <Ref> { "+pool+" } } }\n")
                    f.write("}\n")
                finally: ev.to_mesh_clear()
    scene.frame_set(1)
    static=[o for o in scene.objects if not o.name.startswith(moving+("Water droplet",))]
    box=[o for o in static if o.name.startswith("Rhizobox")]
    write(out/"rhizobox.egg",box)
    write(out/"bench.egg",[o for o in static if o not in box and not o.name.startswith("Architecture")])
    write(out/"architecture.egg",[o for o in static if o.name.startswith("Architecture")])
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
