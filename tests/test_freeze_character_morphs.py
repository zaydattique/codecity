import json
import struct
import pytest
from tools.freeze_character_morphs import decode, freeze, accessor


def fixture():
    data=struct.pack("<9f",0,0,0,0,1,0,1,0,0)+struct.pack("<B",1)+b"\0"*3+struct.pack("<3f",0,.4,0)
    doc={"asset":{"version":"2.0"},"buffers":[{"byteLength":len(data)}],
         "bufferViews":[{"buffer":0,"byteOffset":0,"byteLength":36},{"buffer":0,"byteOffset":36,"byteLength":1},{"buffer":0,"byteOffset":40,"byteLength":12}],
         "accessors":[{"bufferView":0,"componentType":5126,"count":3,"type":"VEC3"},
                      {"componentType":5126,"count":3,"type":"VEC3","sparse":{"count":1,"indices":{"bufferView":1,"componentType":5121},"values":{"bufferView":2}}}],
         "meshes":[{"weights":[.5],"primitives":[{"attributes":{"POSITION":0},"targets":[{"POSITION":1}]}]}],
         "nodes":[{"mesh":0,"skin":0}],"skins":[{"joints":[0]}]}
    return doc,data


def glb(doc,data):
    j=json.dumps(doc).encode()
    j+=b" "*(-len(j)%4)
    return struct.pack("<4sII",b"glTF",2,28+len(j)+len(data))+struct.pack("<I4s",len(j),b"JSON")+j+struct.pack("<I4s",len(data),b"BIN\0")+data


def test_freeze_sparse_and_keep_skin():
    d,b=fixture()
    raw=glb(d,b)
    out,n=freeze(raw)
    assert n==1
    doc,binary=decode(out)
    p=doc["meshes"][0]["primitives"][0]
    assert "targets" not in p and "weights" not in doc["meshes"][0]
    assert doc["skins"]==d["skins"]
    assert accessor(doc,binary,p["attributes"]["POSITION"])[1][1]==pytest.approx(1.2)


def test_reject_instance_mismatch():
    d,b=fixture()
    d["nodes"][0]["weights"]=[.1]
    with pytest.raises(ValueError):freeze(glb(d,b))


def test_reject_animated_morphs():
    d,b=fixture()
    d["animations"]=[{"channels":[{"target":{"path":"weights"}}]}]
    with pytest.raises(ValueError):freeze(glb(d,b))
