"""Acquire bounded, fixed CC0 street art inputs using the existing Poly Haven validator."""
import json
from pathlib import Path
from tools.fetch_pilot_asset import get, plan, verify, check_gltf, safe_path

ROOT = Path("build/street-candidate")
MODELS = {
    "modular_urban_apartments_facade": "James Ray Cock",
    "street_lamp_01": "Josh Dean",
    "painted_wooden_bench": "Kirill Sannikov",
}
TEXTURES = ("asphalt_01", "concrete_pavement_02")
LIMIT = 128 * 1024 * 1024


def metadata(asset):
    return json.loads(get(f"https://api.polyhaven.com/files/{asset}", 4*1024*1024))


def save_record(directory, relative, record):
    if type(record["size"]) is not int or not 0 < record["size"] <= LIMIT:
        raise ValueError("Invalid asset size")
    data = get(record["url"], record["size"])
    digest = verify(data, record)
    target = directory / safe_path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return digest


def texture_plan(meta):
    # Poly Haven exposes texture maps by type, resolution and encoding.
    result = {}
    for role, aliases in {
        "color": {"diff", "diffuse", "albedo", "basecolor"},
        "normal": {"nor_gl", "normalgl", "normal_opengl"},
        "rough": {"rough", "roughness"},
    }.items():
        keys = [k for k in meta if k.lower().replace(" ", "_") in aliases]
        if len(keys) != 1:
            raise ValueError(f"Missing/ambiguous map {role}: {list(meta)}")
        formats = meta[keys[0]]["1k"]
        record = formats.get("jpg") or formats.get("png")
        if not record:
            raise ValueError("Missing supported 1K image")
        ext = "jpg" if "jpg" in formats else "png"
        result[role] = (f"{role}.{ext}", record)
    return result


def main():
    ROOT.mkdir(parents=True, exist_ok=False)
    manifest = {}
    for asset, author in MODELS.items():
        files = plan(metadata(asset), limit=LIMIT, max_files=128)
        target = ROOT/asset
        target.mkdir()
        hashes = {str(p):save_record(target,str(p),rec) for p,rec in files}
        entry = str(files[0][0])
        check_gltf((target/entry).read_bytes(),files)
        manifest[asset] = {"entry":entry,"sha256":hashes,"author":author,"license":"CC0-1.0","url":f"https://polyhaven.com/a/{asset}"}
    for asset in TEXTURES:
        target=ROOT/asset
        target.mkdir()
        selected=texture_plan(metadata(asset))
        hashes = {p:save_record(target,p,r) for p,r in selected.values()}
        manifest[asset] = {"maps":{k:p for k,(p,r) in selected.items()},"sha256":hashes,"license":"CC0-1.0","url":f"https://polyhaven.com/a/{asset}"}
    (ROOT/"sources.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("CODECITY_STREET_SOURCES_OK Powered by Poly Haven")


if __name__=="__main__":
    main()
