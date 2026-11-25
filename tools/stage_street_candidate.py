"""Stage the exact reviewed street and adult rigs for local or hosted playtesting.

Inputs may be extracted artifact directories or downloaded ZIPs. Only the three
pinned GLBs are read, never extract arbitrary entries. The animation source is
an independently hash-verified CC0 GLB. No tracked source files modified.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import zipfile
import json

from tools.retarget_motion import retarget, PIN, BLOB

ROOT=Path(__file__).resolve().parents[1]
MAX_ASSET=64*1024*1024
ASSETS={
    "adrian":("frozen/adrian.glb","e5be310d7245ef986d2492f52ee003646973a92f3104294b34881dcd10681e9d"),
    "maya":("frozen/maya.glb","41de3978d7d36870c1d7d7114125701085345edc56dfd27dc7d7d2333ab51c94"),
    "street":("optimization-street/candidate.glb","cbd75043c055ea6b15275670c2dd540410559a5b47c585ab4f411a3eca3529f9"),
}


def read_asset(path,member,digest):
    if path.is_dir():
        file=(path/member).resolve()
        if not file.is_relative_to(path.resolve()) or not 0<file.stat().st_size<=MAX_ASSET:
            raise ValueError("Invalid artifact source file")
        data=file.read_bytes()
    else:
        with zipfile.ZipFile(path) as archive:
            items=[i for i in archive.infolist() if i.filename==member]
            if len(items)!=1 or not 0<items[0].file_size<=MAX_ASSET:
                raise ValueError("Missing, duplicate or oversized artifact member")
            data=archive.read(items[0])
    if hashlib.sha256(data).hexdigest()!=digest:
        raise ValueError("Candidate source digest mismatch: "+member)
    return data


def stage(characters,street,motion,out):
    if out.exists():
        raise FileExistsError("Use a fresh staging directory")
    if not motion.is_file() or motion.stat().st_size!=7618436:
        raise ValueError("Missing exact CC0 source GLB")
    clip=motion.read_bytes()
    if hashlib.sha1(f"blob {len(clip)}\0".encode()+clip,usedforsecurity=False).hexdigest()!=BLOB:
        raise ValueError("Motion source blob mismatch")
    raw={name:read_asset(street if name=="street" else characters,*entry) for name,entry in ASSETS.items()}
    # Complete validation before making the staging directory.
    generated={}
    reports={}
    for name in ("adrian","maya"):
        data,counts=retarget(clip,raw[name])
        generated[name]=data
        reports[name]={"source_commit":PIN,"source_blob":BLOB,"license":"CC0-1.0",
                       "clips":counts,"output_sha256":hashlib.sha256(data).hexdigest()}
    generated["street"]=raw["street"]
    shutil.copytree(ROOT/"game",out/"game",ignore=shutil.ignore_patterns(".godot","candidate_assets","*.import","_qa"))
    assets=out/"game/candidate_assets"
    assets.mkdir()
    for name,data in generated.items():
        (assets/(name+".glb")).write_bytes(data)
    qa=out/"game/_qa"
    qa.mkdir()
    shutil.copy2(ROOT/"verification/street_playtest.gd",qa)
    shutil.copy2(ROOT/"verification/candidate_export_presets.cfg",out/"game/export_presets.cfg")
    (out/"motion-report.json").write_text(json.dumps(reports,indent=2),encoding="utf-8")
    shutil.copy2(ROOT/"THIRD_PARTY_NOTICES.md",out)
    print("CODECITY_STREET_STAGE_OK",out)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--characters",required=True,type=Path)
    p.add_argument("--street",required=True,type=Path)
    p.add_argument("--motion",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    stage(a.characters,a.street,a.motion,a.out)

if __name__=="__main__":
    main()
