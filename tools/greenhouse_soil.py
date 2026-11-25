"""Fetch exact verified CC0 soil maps, with provenance. No fallback to a fake texture."""
import json
from polyhaven import get,verify,safe_url
def acquire(out):
    out.mkdir(parents=True,exist_ok=False)
    meta=json.loads(get("https://api.polyhaven.com/files/dirt_floor",2*1024*1024))
    maps={}; hashes={}
    for kind in ("diff","nor_gl","rough"):
        variants=meta[kind]["1k"]
        record=variants.get("jpg") or variants.get("png")
        if not record or not 0<record["size"]<=16*1024*1024:
            raise ValueError("Missing or excessive soil map: "+kind)
        safe_url(record["url"])
        data=get(record["url"],record["size"])
        hashes[kind]={"sha256":verify(data,record),"url":record["url"]}
        dest=out/(kind+(".jpg" if "jpg" in variants and record==variants["jpg"] else ".png"))
        dest.write_bytes(data);maps[kind]=dest
    (out/"provenance.json").write_text(json.dumps({"asset":"dirt_floor","license":"CC0-1.0","source":"https://polyhaven.com/a/dirt_floor","credit":"Powered by Poly Haven","maps":hashes},indent=2))
    return maps
