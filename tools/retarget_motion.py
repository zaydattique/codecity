"""Retarget licensed UAL rotation clips onto the two frozen MPFB runtime rigs.

No source mannequin meshes, skins or textures are copied. Convert rotations via
global rest bases, retain target bone lengths and discard root motion. This is
a first retarget candidate, not a foot-IK or animation-art approval.
"""
import argparse
from bisect import bisect_right
import hashlib
import json
import math
from pathlib import Path
import re
import struct

from tools.freeze_character_morphs import decode, accessor

PIN = "ba9514cdd88ecc2d40ecad503a644449fc98e665"
BLOB = "473e59080288428d0b6da826ba19324d07b191f0"
CLIPS = {"Idle_Loop":"idle", "Walk_Loop":"walk", "Jog_Fwd_Loop":"jog", "Sprint_Loop":"sprint", "Crouch_Idle_Loop":"crouch_idle", "Crouch_Fwd_Loop":"crouch_walk", "Jump_Start":"jump_start", "Jump_Loop":"jump_air", "Jump_Land":"jump_land"}
COMBAT_CLIPS = {"Punch_Jab":"punch_jab", "Punch_Cross":"punch_cross", "Hit_Chest":"hit_chest", "Death01":"death"}
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


def vector(q,v):
    return mul(mul(q,(*v,0.0)),inv(q))[:3]


def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def norm(v):
    n=math.sqrt(dot(v,v))
    if n<1e-8:raise ValueError("Zero arm direction")
    return tuple(x/n for x in v)


def aim_rotation(a,b):
    a,b=norm(a),norm(b)
    cosine=max(-1,min(1,dot(a,b)))
    if cosine < -0.999999:
        axis=norm(cross(a,(1,0,0) if abs(a[0])<0.8 else (0,1,0)))
        return (*axis,0.0)
    return unit((*cross(a,b),1+cosine))


def parent_map(doc):
    return {child:i for i,node in enumerate(doc["nodes"]) for child in node.get("children",[])}


def rest_positions(doc,local,indices):
    parents=parent_map(doc)
    cache={}
    def pose(i):
        if i in cache:return cache[i]
        node=doc["nodes"][i]
        scale=node.get("scale",[1,1,1])
        if min(scale)<=0 or max(scale)-min(scale)>1e-4:
            raise ValueError("Nonuniform skeleton rest scale")
        t=node.get("translation",[0,0,0])
        if i in parents:
            p,q,k=pose(parents[i])
            offset=vector(q,tuple(x*k for x in t))
            result=(tuple(x+y for x,y in zip(p,offset)),unit(mul(q,local[i])),k*scale[0])
        else:result=(tuple(t),local[i],scale[0])
        cache[i]=result
        return result
    return {i:pose(i)[0] for i in indices}


def sample_track(track,t):
    times,values,interpolation=track
    i=bisect_right(times,t)-1
    if i<0:return unit(values[0])
    if i>=len(times)-1 or interpolation=="STEP":return unit(values[i])
    u=(t-times[i])/(times[i+1]-times[i])
    a,b=unit(values[i]),unit(values[i+1])
    if dot(a,b)<0:b=tuple(-x for x in b)
    return unit(tuple((1-u)*x+u*y for x,y in zip(a,b)))


def correct_arm_tracks(src,dst,sn,dn,sl,dl,sg,dg,source_tracks,target_tracks):
    # MPFB's A-pose and UAL's different bind pose make rotation-only transfer
    # insufficient for arm placement. Preserve actual animated upper/forearm
    # directions using anatomically aligned source global poses. Keep target
    # lengths, original skin and twist, solve local rotations parent-first.
    sp,dp=parent_map(src),parent_map(dst)
    spos=rest_positions(src,sl,sn.values())
    dpos=rest_positions(dst,dl,dn.values())
    ss=sub(spos[sn["upperarm_l"]],spos[sn["upperarm_r"]])
    ds=sub(dpos[dn["upperarm_l"]],dpos[dn["upperarm_r"]])
    ss=norm((ss[0],0,ss[2]));ds=norm((ds[0],0,ds[2]))
    yaw=math.atan2(cross(ss,ds)[1],dot(ss,ds))
    align=(0,math.sin(yaw/2),0,math.cos(yaw/2))
    axes={}
    for side in ("l","r"):
        for a,b in (("upperarm","lowerarm"),("lowerarm","hand")):
            name=a+"_"+side;child=b+"_"+side
            si,di=sn[name],dn[name]
            sa=vector(inv(sg[si]),norm(sub(spos[sn[child]],spos[si])))
            da=vector(inv(dg[di]),norm(sub(dpos[dn[child]],dpos[di])))
            axes[di]=(si,sa,da)
    duration=max(track[0][-1] for track in target_tracks.values())
    count=max(1,math.ceil(duration*30))
    times=[duration*i/count for i in range(count+1)]
    outputs={i:[] for i in axes}
    for t in times:
        src_cache={};dst_cache={}
        def source_pose(i):
            if i not in src_cache:
                local=sample_track(source_tracks[i],t) if i in source_tracks else sl[i]
                src_cache[i]=unit(mul(source_pose(sp[i]),local)) if i in sp else local
            return src_cache[i]
        def target_pose(i):
            if i in dst_cache:return dst_cache[i]
            parent=target_pose(dp[i]) if i in dp else Q
            local=sample_track(target_tracks[i],t) if i in target_tracks else dl[i]
            current=unit(mul(parent,local))
            if i in axes:
                si,sa,da=axes[i]
                desired=vector(align,vector(source_pose(si),sa))
                correction=aim_rotation(vector(current,da),desired)
                current=unit(mul(correction,current))
                local=unit(mul(inv(parent),current))
                values=outputs[i]
                if values and dot(values[-1],local)<0:local=tuple(-x for x in local)
                values.append(local)
                if dot(norm(vector(current,da)),norm(desired))<0.999:
                    raise ValueError("Arm direction transfer failed")
            dst_cache[i]=current
            return current
        for i in axes:target_pose(i)
    for i,values in outputs.items():
        target_tracks[i]=(times,values,"LINEAR")


def retarget(source,target,append_combat=False):
    src,sbin=decode(source)
    dst,dbin=decode(target)
    sn,sl,sg=skeleton(src)
    dn,dl,dg=skeleton(dst)
    reverse={i:n for n,i in sn.items()}
    common=set(sn)&set(dn)
    existing=dst.get("animations",[])
    if append_combat:
        if {a.get("name") for a in existing}!=set(CLIPS.values()):raise ValueError("Combat append requires exactly the validated locomotion clips")
    elif existing:raise ValueError("Target already animated")
    selected=COMBAT_CLIPS if append_combat else CLIPS
    available={a.get("name"):a for a in src.get("animations",[])}
    if not set(selected)<=set(available):raise ValueError(f"Missing clips; available={sorted(available)}")
    result=list(existing)
    counts={}
    for source_name,name in selected.items():
        anim=available[source_name]
        samplers=[]
        channels=[]
        used=set()
        source_tracks={}
        target_tracks={}
        for ch in anim["channels"]:
            target_node=ch["target"].get("node")
            if ch["target"].get("path")!="rotation":
                continue
            sample=anim["samplers"][ch["sampler"]]
            interp=sample.get("interpolation","LINEAR")
            if interp not in ("LINEAR","STEP"):
                raise ValueError("Unsupported animation interpolation "+interp)
            times=accessor(src,sbin,sample["input"])
            values=accessor(src,sbin,sample["output"])
            if len(times)!=len(values) or not times or times[0][0]<0 or times[-1][0]>30 or any(a[0]>=b[0] for a,b in zip(times,times[1:])):
                raise ValueError("Invalid keyframe times")
            source_tracks[target_node]=([row[0] for row in times],values,interp)
            bone=reverse.get(target_node)
            if bone not in common or bone=="root":continue
            si=sn[bone];di=dn[bone]
            out=[]
            for q in values:
                value=transfer(sl[si],sg[si],dl[di],dg[di],q)
                if out and dot(out[-1],value)<0:
                    value=tuple(-v for v in value)
                out.append(value)
            target_tracks[di]=([row[0] for row in times],out,interp)
            used.add(bone)
        if len(used.intersection(CORE))<16 or not {"thigh_l","thigh_r","upperarm_l","upperarm_r"}<=used:
            raise ValueError(f"Insufficient real rotation tracks for {name}: {sorted(used)}")
        correct_arm_tracks(src,dst,sn,dn,sl,dl,sg,dg,source_tracks,target_tracks)
        for di,(times,values,interp) in target_tracks.items():
            inp=write_accessor(dst,dbin,[(t,) for t in times],"SCALAR")
            val=write_accessor(dst,dbin,values,"VEC4")
            channels.append({"sampler":len(samplers),"target":{"node":di,"path":"rotation"}})
            samplers.append({"input":inp,"output":val,"interpolation":interp})
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
    p.add_argument("--append-combat",action="store_true")
    a=p.parse_args()
    raw=a.source.read_bytes()
    if len(raw)!=7618436 or hashlib.sha1(f"blob {len(raw)}\0".encode()+raw,usedforsecurity=False).hexdigest()!=BLOB:
        raise ValueError("Unrecognized licensed motion source")
    if a.output.exists():raise ValueError("Preserve original assets")
    data,counts=retarget(raw,a.target.read_bytes(),a.append_combat)
    a.output.write_bytes(data)
    report={"source_commit":PIN,"source_blob":BLOB,"license":"CC0-1.0","author":"Quaternius",
            "clips":counts,"output_sha256":hashlib.sha256(data).hexdigest(),
            "limitations":["rotation retarget candidate; source arm directions solved parent-first; root translation removed","foot planting, finger poses, crouch and landing not approved"]}
    a.output.with_suffix(".motion.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("CODECITY_MOTION_RETARGET_OK",counts)

if __name__=="__main__":
    main()
