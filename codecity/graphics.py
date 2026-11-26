"""Cross-platform Panda3D texture loading; optional material maps cannot block a lesson."""
from pathlib import Path

def optional_texture(loader,root,names,report,filename_factory=None):
    if filename_factory is None:
        from panda3d.core import Filename
        filename_factory=Filename.fromOsSpecific
    for name in names:
        path=Path(root)/name
        if not path.is_file():
            report("Optional texture absent: "+name)
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
