"""Freeze authored glTF default morphs in runtime characters, without changing rig.

The editable Blender source retains MPFB targets. This offline build step is
restricted to self-contained GLB 2.0, static default weights, float attributes
and bounded buffers. No animation weights or inconsistent instance overrides.
"""
import argparse
import json
import math
from pathlib import Path
import struct

MAX_BYTES = 128 * 1024 * 1024
MAX_VERTICES = 200000
TYPES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
FORMATS = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}


def decode(raw):
    if len(raw) < 28 or len(raw) > MAX_BYTES:
        raise ValueError("Invalid GLB size")
    if struct.unpack_from("<4sII", raw) != (b"glTF", 2, len(raw)):
        raise ValueError("Invalid GLB header")
    size, kind = struct.unpack_from("<I4s", raw, 12)
    end = 20 + size
    if kind != b"JSON" or size % 4 or end + 8 > len(raw):
        raise ValueError("Invalid JSON chunk")
    doc = json.loads(raw[20:end])
    length, kind = struct.unpack_from("<I4s", raw, end)
    if kind != b"BIN\0" or length % 4 or end + 8 + length != len(raw):
        raise ValueError("Invalid BIN chunk")
    buffers = doc["buffers"]
    if len(buffers) != 1 or "uri" in buffers[0] or not 0 <= length - buffers[0]["byteLength"] <= 3:
        raise ValueError("Expected one embedded buffer")
    return doc, bytearray(raw[end+8:end+8+buffers[0]["byteLength"]])


def read_rows(doc, binary, view_index, offset, count, fmt, columns):
    view = doc["bufferViews"][view_index]
    if view.get("buffer", 0) != 0:
        raise ValueError("External buffer")
    row = struct.Struct("<" + fmt * columns)
    stride = view.get("byteStride", row.size)
    start = view.get("byteOffset", 0) + offset
    end = start + (count-1)*stride + row.size if count else start
    if offset < 0 or stride < row.size or start < 0 or end > view.get("byteOffset", 0)+view["byteLength"] or end > len(binary):
        raise ValueError("Accessor out of bounds")
    return [list(row.unpack_from(binary, start+i*stride)) for i in range(count)]


def accessor(doc, binary, index):
    a = doc["accessors"][index]
    count = a["count"]
    if type(count) is not int or not 0 <= count <= MAX_VERTICES or a.get("normalized"):
        raise ValueError("Unsupported accessor")
    fmt = FORMATS[a["componentType"]]
    cols = TYPES[a["type"]]
    values = read_rows(doc, binary, a["bufferView"], a.get("byteOffset", 0), count, fmt, cols) if "bufferView" in a else [[0]*cols for _ in range(count)]
    if "sparse" in a:
        s = a["sparse"]
        ix, val = s["indices"], s["values"]
        if type(s["count"]) is not int or not 0 <= s["count"] <= count or ix["componentType"] not in (5121,5123,5125):
            raise ValueError("Unsupported sparse accessor")
        indices = read_rows(doc,binary,ix["bufferView"],ix.get("byteOffset",0),s["count"],FORMATS[ix["componentType"]],1)
        delta = read_rows(doc,binary,val["bufferView"],val.get("byteOffset",0),s["count"],fmt,cols)
        last = -1
        for (idx,), item in zip(indices, delta):
            if not last < idx < count:
                raise ValueError("Invalid sparse indices")
            values[idx] = item
            last = idx
    return values


def append_float(doc, binary, values, kind):
    if not values or any(not math.isfinite(x) for v in values for x in v):
        raise ValueError("Invalid morphed values")
    cols = len(values[0])
    while len(binary) % 4:
        binary.append(0)
    start = len(binary)
    row = struct.Struct("<" + "f"*cols)
    for v in values:
        binary.extend(row.pack(*v))
    view = len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer":0,"byteOffset":start,"byteLength":len(binary)-start,"target":34962})
    a = {"bufferView":view,"componentType":5126,"count":len(values),"type":"VEC"+str(cols)}
    if kind == "POSITION":
        a["min"] = [min(v[c] for v in values) for c in range(cols)]
        a["max"] = [max(v[c] for v in values) for c in range(cols)]
    idx = len(doc["accessors"])
    doc["accessors"].append(a)
    return idx


def freeze(raw):
    doc,binary = decode(raw)
    if any(c["target"].get("path")=="weights" for a in doc.get("animations",[]) for c in a["channels"]):
        raise ValueError("Animated morph weights cannot be frozen")
    changed = 0
    for mi, mesh in enumerate(doc["meshes"]):
        morphs = [p for p in mesh["primitives"] if p.get("targets")]
        if not morphs:
            continue
        weights = mesh.get("weights", [0]*len(morphs[0]["targets"]))
        if any(not isinstance(w,(int,float)) or isinstance(w,bool) or not math.isfinite(w) or abs(w)>4 for w in weights):
            raise ValueError("Invalid morph weights")
        for node in doc.get("nodes",[]):
            if node.get("mesh")==mi:
                if node.get("weights",weights)!=weights:
                    raise ValueError("Instance overrides differ")
                node.pop("weights",None)
        for prim in mesh["primitives"]:
            targets = prim.get("targets",[])
            if len(targets)!=len(weights):
                raise ValueError("Inconsistent target count")
            for semantic in ("POSITION","NORMAL","TANGENT"):
                if not any(semantic in t for t in targets):
                    continue
                source = prim["attributes"][semantic]
                if doc["accessors"][source]["componentType"]!=5126:
                    raise ValueError("Unsupported base format")
                values = accessor(doc,binary,source)
                for weight,target in zip(weights,targets):
                    if semantic not in target or weight==0:
                        continue
                    idx=target[semantic]
                    if doc["accessors"][idx]["componentType"]!=5126 or doc["accessors"][idx]["type"]!="VEC3":
                        raise ValueError("Unsupported morph delta")
                    delta=accessor(doc,binary,idx)
                    if len(delta)!=len(values):
                        raise ValueError("Morph length mismatch")
                    for v,d in zip(values,delta):
                        for c in range(3):
                            v[c]+=weight*d[c]
                if semantic in ("NORMAL","TANGENT"):
                    for v in values:
                        length=math.sqrt(sum(x*x for x in v[:3]))
                        if length>1e-8:
                            for c in range(3):v[c]/=length
                prim["attributes"][semantic]=append_float(doc,binary,values,semantic)
            prim.pop("targets",None)
            changed+=1
        mesh.pop("weights",None)
        if "extras" in mesh:mesh["extras"].pop("targetNames",None)
    doc["buffers"][0]["byteLength"]=len(binary)
    j=json.dumps(doc,separators=(",",":"),allow_nan=False).encode()
    j+=b" "*(-len(j)%4)
    binary.extend(b"\0"*(-len(binary)%4))
    out=struct.pack("<4sII",b"glTF",2,12+8+len(j)+8+len(binary))+struct.pack("<I4s",len(j),b"JSON")+j+struct.pack("<I4s",len(binary),b"BIN\0")+binary
    if len(out)>MAX_BYTES:raise ValueError("Output exceeds bounds")
    return out,changed


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    if args.source.resolve()==args.output.resolve() or args.output.exists():
        raise ValueError("Preserve original source and choose a fresh output")
    result,changed=freeze(args.source.read_bytes())
    args.output.write_bytes(result)
    print("CODECITY_FROZEN_CHARACTER_OK primitives=",changed)


if __name__=="__main__":
    main()
