"""Download the official CC0 MakeHuman pack from either published mirror.

No unreviewed sources. A local existing ZIP can be supplied to build_character
directly. A captured SHA-256 records provenance, not independent authenticity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

MIRRORS = (
    "https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip",
    "https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip",
)
LEGACY_URL = "https://github.com/Makehuman-2/MH2_Asset_Repository_CCO/releases/download/CC0/legacy-mh_system_CC0.zip"
LEGACY_SHA256 = "d38970b0a2a06dbcb2d3f55aa3d673c45bc88e7bd1f4afa0368a0782938d55bc"
MAX_BYTES = 450_000_000

def record_source(path, url, digest):
    path.with_suffix(".source.json").write_text(json.dumps({
        "url": url, "sha256": digest, "license": "CC0-1.0",
        "pinned_digest": url == LEGACY_URL
    }, indent=2), encoding="utf-8")


def check(path):
    if not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError("Invalid pack size")
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        if len(entries) > 20000 or sum(e.file_size for e in entries) > 1024**3:
            raise ValueError("Invalid archive limits")
        if not entries:
            raise ValueError("Empty pack")
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("destination", type=Path)
    dest = p.parse_args().destination
    if dest.exists():
        print("Existing pack:", check(dest))
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    for url in (*MIRRORS, LEGACY_URL):
        try:
            tmp.unlink(missing_ok=True)
            subprocess.run(["curl", "--fail", "--location", "--proto", "=https",
                            "--proto-redir", "=https", "--connect-timeout", "15",
                            "--max-time", "180", "--max-filesize", str(MAX_BYTES),
                            "--output", str(tmp), url], check=True, timeout=195)
            digest = check(tmp)
            if url == LEGACY_URL and digest != LEGACY_SHA256:
                raise ValueError("Legacy release SHA-256 mismatch")
            tmp.replace(dest)
            record_source(dest, url, digest)
            print("Official pack mirror:", url, "SHA-256:", digest)
            return
        except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as e:
            print("Mirror failed:", url, str(e))
        finally:
            tmp.unlink(missing_ok=True)
    raise SystemExit("All audited pack sources failed; use a locally acquired verified official pack.")


if __name__ == "__main__":
    main()
