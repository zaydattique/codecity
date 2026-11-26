"""Prepare a portable Windows distribution and verify byte-for-byte inventory."""
import argparse,hashlib,importlib.metadata as md,json,shutil
from pathlib import Path
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def inventory(root):
    return {p.relative_to(root).as_posix():{"bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted(root.rglob("*")) if p.is_file() and p.name!="release-manifest.json"}
def verify(root):
    manifest=json.loads((root/"release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["files"]==inventory(root),"Release files differ from manifest"
    exe=root/"BloomLogic.exe"
    with exe.open("rb") as f:assert f.read(2)==b"MZ"
    for required in ("_internal/runtime/teacher.glb","_internal/runtime/rhizobox.egg","_internal/runtime/fan-rotor.glb","_internal/runtime/voice-guide0.wav","_internal/runtime/soil-normal.png","_internal/runtime/soil-gloss.png","_internal/runtime/material-integrity.json","THIRD_PARTY_NOTICES.md","README.txt"):
        assert (root/required).is_file(),required
    assert not (root/"CodeCity.exe").exists()
    print("Verified",len(manifest["files"]),"files")
def prepare(root,revision):
    licenses=root/"licenses";licenses.mkdir(exist_ok=True)
    packages={}
    # Bundled native dependencies have their original distribution notice text retained.
    for name in ("panda3d","panda3d-gltf","panda3d-simplepbr","pyinstaller"):
        try:d=md.distribution(name)
        except md.PackageNotFoundError:
            if name in ("panda3d","panda3d-gltf","pyinstaller"):raise
            continue
        packages[name]=d.version
        target=licenses/name;target.mkdir(exist_ok=True)
        count=0
        for entry in d.files or []:
            if not any(part.endswith(".dist-info") for part in entry.parts):continue
            base=entry.name.lower()
            if not base.startswith(("license","copying","notice","authors")):continue
            p=Path(d.locate_file(entry))
            if p.is_file():
                shutil.copyfile(p,target/entry.name);count+=1
        if name in ("panda3d","panda3d-gltf") and not count:raise RuntimeError("Missing license for "+name)
    # CPython's PSF notice accompanies the interpreter when installed by setup-python.
    import sys
    for candidate in (Path(sys.base_prefix)/"LICENSE.txt",Path(sys.base_prefix)/"LICENSE"):
        if candidate.is_file():shutil.copyfile(candidate,licenses/"CPython-LICENSE.txt");break
    assert (licenses/"CPython-LICENSE.txt").is_file(),"Missing CPython license"
    (root/"release-manifest.json").write_text(json.dumps({"product":"BloomLogic","version":"1.0.1","revision":revision,"bundled_build_packages":packages,"files":inventory(root)},indent=2),encoding="utf-8")
    verify(root)
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=("prepare","verify"));parser.add_argument("root",type=Path);parser.add_argument("--revision")
    args=parser.parse_args()
    if args.mode=="prepare":
        assert args.revision and len(args.revision)==40
        prepare(args.root,args.revision)
    else:verify(args.root)
