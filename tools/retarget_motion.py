"""Retarget licensed UAL rotation clips onto the two frozen MPFB runtime rigs.

No source mannequin meshes, skins or textures are copied. Convert rotations via
global rest bases, retain target bone lengths and discard root motion. This is
a first retarget candidate, not a foot-IK or animation-art approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct

from tools.freeze_character_morphs import decode, accessor

PIN = "ba9514cdd88ecc2d40ecad503a644449fc98e665"
BLOB = "473e59080288428d0b6da826ba19324d07b191f0"
CLIPS = {"Idle_Loop":"idle", "Walk_Loop":"walk", "Jog_Fwd_Loop":"jog", "Sprint_Loop":"sprint", "Crouch_Idle_Loop":"crouch_idle", "Crouch_Fwd_Loop":"crouch_walk", "Jump_Start":"jump_start", "Jump_Loop":"jump_loop", "Jump_Land":"jump_land"}
CORE = ("pelvis","spine_01","spine_02","spine_03","neck_01","head",
        "clavicle_l","upperarm_l","lowerarm_l","hand_l",
        "clavicle_r","upperarm_r","lowerarm_r","hand_r",
        "thigh_l","calf_l","foot_l","ball_l","thigh_r","calf_r","foot_r","ball_r")
Q = (0.,0.,0.,1.)


def unit(q):
    if len(q)!=4 or not all(math.isfinite(x) for x in q):
        raise ValueError("Invalid quaternion")
    n=math.sqrt(sum(x*x for x in q))
    if n<1e-7:
        raise ValueError("Zero quaternion")
    return tuple(x/n for x in q)


def mul(a,b):
    x,y,z,w=a
    X,Y,Z,W=b
    return (w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)


def inv(q):
    return (-q[0],-q[1],-q[2],q[3])


def transfer(src_local, src_global, dst_local, dst_global, animated):
    delta=mul(inv(src_local),unit(animated))
    world=mul(mul(src_global,delta),inv(src_global))
    mapped=mul(mul(inv(dst_global),world),dst_global)
    return unit(mul(dst_local,mapped))


def canonical(name):
    name=name.split(":")[-1].lower().replace(".","_").replace("-","_")
    compact=re.sub(r"[^a-z0-9]","",name)
    aliases={"hips":"pelvis","hip":"pelvis","neck":"neck_01","neck01":"neck_01",
        "spine":"spine_01","spine1":"spine_01","spine2":"spine_02","spine3":"spine_03",
        "spine01":"spine_01","spine02":"spine_02","spine03":"spine_03"}
    for bone in CORE:
        aliases[re.sub(r"[^a-z0-9]","",bone)]=bone
    for side,word in (("l","left"),("r","right")):
        for stem,alt in (("clavicle","shoulder"),("upperarm","arm"),("lowerarm","forearm"),
                         ("hand","hand"),("thigh","upleg"),("calf","leg"),("foot","foot"),("ball","toebase")):
            aliases[word+alt]=stem+"_"+side
            aliases[word+stem]=stem+"_"+side
    return aliases.get(compact,name)


def skeleton(doc):
    nodes=doc["nodes"]
    if len(nodes)>4096 or len(doc.get("skins",[]))!=1:
        raise ValueError("Expected one bounded skin")
    joints=doc["skins"][0]["joints"]
    parents={}
    for i,node in enumerate(nodes):
        for child in node.get("children",[]):
            if child in parents:raise ValueError("Multiple parents")
            parents[child]=i
    local={i:unit(node.get("rotation",Q)) for i,node in enumerate(nodes)}
    cache={}
    def rest(i,active):
        if i in cache:return cache[i]
        if i in active or "matrix" in nodes[i]:
            raise ValueError("Unsupported rest hierarchy")
        p=parents.get(i)
        cache[i]=unit(mul(rest(p,active|{i}),local[i])) if p is not None else local[i]
        return cache[i]
    names={}
    for i in joints:
        n=canonical(nodes[i].get("name",""))
        if n in names:raise ValueError("Duplicate bone "+n)
        names[n]=i
    missing=set(CORE)-set(names)
    if missing:
        raise ValueError(f"Missing core joints {sorted(missing)}; available={sorted(names)}")
    return names,local,{i:rest(i,set()) for i in joints}


def write_accessor(doc,binary,rows,kind):
    if not rows or len(rows)>200000:
        raise ValueError("Invalid animation rows")
    n=1 if kind=="SCALAR" else 4
    if any(len(r)!=n or not all(math.isfinite(x) for x in r) for r in rows):
        raise ValueError("Invalid sample data")
    binary.extend(b"\0"*(-len(binary)%4))
    start=len(binary)
    for row in rows:binary.extend(struct.pack("<"+"f"*n,*row))
    view=len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer":0,"byteOffset":start,"byteLength":len(binary)-start})
    a={"bufferView":view,"componentType":5126,"count":len(rows),"type":kind}
    if kind=="SCALAR":a.update(min=[rows[0][0]],max=[rows[-1][0]])
    idx=len(doc["accessors"])
    doc["accessors"].append(a)
    return idx


def retarget(source,target):
    src,sbin=decode(source)
    dst,dbin=decode(target)
    sn,sl,sg=skeleton(src)
    dn,dl,dg=skeleton(dst)
    reverse={i:n for n,i in sn.items()}
    common=set(sn)&set(dn)
    if dst.get("animations"):raise ValueError("Target already animated")
    available={a.get("name"):a for a in src.get("animations",[])}
    if not set(CLIPS)<=set(available):raise ValueError(f"Missing clips; available={sorted(available)}")
    result=[]
    counts={}
    for source_name,name in CLIPS.items():
        anim=available[source_name]
        samplers=[]
        channels=[]
        used=set()
        for ch in anim["channels"]:
            target_node=ch["target"].get("node")
            bone=reverse.get(target_node)
            if ch["target"].get("path")!="rotation" or bone not in common:
                continue
            sample=anim["samplers"][ch["sampler"]]
            interp=sample.get("interpolation","LINEAR")
            if interp not in ("LINEAR","STEP"):
                raise ValueError("Unsupported animation interpolation "+interp)
            times=accessor(src,sbin,sample["input"])
            values=accessor(src,sbin,sample["output"])
            if len(times)!=len(values) or not times or times[0][0]<0 or times[-1][0]>30 or any(a[0]>=b[0] for a,b in zip(times,times[1:])):
                raise ValueError("Invalid keyframe times")
            si=sn[bone];di=dn[bone]
            if bone=="root":continue
            out=[]
            for q in values:
                value=transfer(sl[si],sg[si],dl[di],dg[di],q)
                if out and sum(a*b for a,b in zip(out[-1],value))<0:
                    value=tuple(-v for v in value)
                out.append(value)
            inp=write_accessor(dst,dbin,times,"SCALAR")
            val=write_accessor(dst,dbin,out,"VEC4")
            channels.append({"sampler":len(samplers),"target":{"node":di,"path":"rotation"}})
            samplers.append({"input":inp,"output":val,"interpolation":interp})
            used.add(bone)
        if len(used.intersection(CORE))<16 or not {"thigh_l","thigh_r","upperarm_l","upperarm_r"}<=used:
            raise ValueError(f"Insufficient real rotation tracks for {name}: {sorted(used)}")
        result.append({"name":name,"samplers":samplers,"channels":channels})
        counts[name]=len(channels)
    dst["animations"]=result
    dst["buffers"][0]["byteLength"]=len(dbin)
    j=json.dumps(dst,separators=(",",":"),allow_nan=False).encode()
    j+=b" "*(-len(j)%4)
    dbin.extend(b"\0"*(-len(dbin)%4))
    output=struct.pack("<4sII",b"glTF",2,28+len(j)+len(dbin))+struct.pack("<I4s",len(j),b"JSON")+j+struct.pack("<I4s",len(dbin),b"BIN\0")+dbin
    return output,counts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("target",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    raw=a.source.read_bytes()
    if len(raw)!=7618436 or hashlib.sha1(f"blob {len(raw)}\0".encode()+raw,usedforsecurity=False).hexdigest()!=BLOB:
        raise ValueError("Unrecognized licensed motion source")
    if a.output.exists():raise ValueError("Preserve original assets")
    data,counts=retarget(raw,a.target.read_bytes())
    a.output.write_bytes(data)
    report={"source_commit":PIN,"source_blob":BLOB,"license":"CC0-1.0","author":"Quaternius",
            "clips":counts,"output_sha256":hashlib.sha256(data).hexdigest(),
            "limitations":["rotation retarget candidate; root translation removed","foot planting, finger poses, crouch and landing not approved"]}
    a.output.with_suffix(".motion.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("CODECITY_MOTION_RETARGET_OK",counts)

if __name__=="__main__":
    main()
