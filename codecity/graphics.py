"""Optional PNG material maps. Never send unverified JPEG or corrupt bytes to native codecs."""
import hashlib,json
from pathlib import Path

def optional_texture(loader,root,names,report,filename_factory=None):
    if filename_factory is None:
        from panda3d.core import Filename
        filename_factory=Filename.fromOsSpecific
    root=Path(root)
    try:
        manifest=json.loads((root/"material-integrity.json").read_text(encoding="utf-8"))
    except (OSError,ValueError):
        report("Optional material integrity manifest unavailable")
        return None
    if not isinstance(manifest,dict):
        report("Invalid optional material manifest")
        return None
    for name in names:
        path=root/name
        try:
            if path.suffix.lower()!=".png" or path.stat().st_size>16*1024*1024:
                raise ValueError("Only bounded PNG derivatives permitted")
            data=path.read_bytes()
            if not data.startswith(b"\x89PNG\r\n\x1a\n") or hashlib.sha256(data).hexdigest()!=manifest.get(name):
                raise ValueError("Integrity mismatch")
        except (OSError,ValueError) as exc:
            report(f"Optional texture integrity rejected: {name}: {exc}")
            continue
        try:
            texture=loader.loadTexture(filename_factory(str(path.resolve())))
            if texture is None:raise OSError("Decoder returned no texture")
            report("Optional texture loaded: "+name)
            return texture
        except (OSError,RuntimeError,ValueError) as exc:
            report(f"Optional texture unavailable: {name}: {exc}")
    report("Optional material map disabled; diffuse texture retained")
    return None
