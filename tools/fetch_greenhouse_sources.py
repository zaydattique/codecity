"""Acquire exact candidate prop sources, preserve all hashes; no approval."""
import json
from pathlib import Path
from polyhaven import get, plan, verify, check_gltf

ASSETS=("potted_plant_01","planter_pot_clay")
def main():
    root=Path("build/greenhouse-sources")
    if root.exists():
        raise FileExistsError("Use a fresh greenhouse sources directory.")
    for asset in ASSETS:
        base=root/asset
        source=base/"source"
        source.mkdir(parents=True)
        meta=json.loads(get("https://api.polyhaven.com/files/"+asset,2*1024*1024))
        files=plan(meta)
        hashes={}
        for path,record in files:
            data=get(record["url"],record["size"])
            hashes[str(path)]=verify(data,record)
            dest=source/path
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
        entry=files[0][0]
        check_gltf((source/entry).read_bytes(),files)
        (base/"provenance.json").write_text(json.dumps({"asset":asset,"source":"https://polyhaven.com/a/"+asset,"license":"CC0-1.0","license_url":"https://polyhaven.com/license","credit":"Powered by Poly Haven","entry":str(entry),"sha256":hashes},indent=2),encoding="utf-8")
if __name__=="__main__": main()
