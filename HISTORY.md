# History

## Phase 01 staging | 2026-11-25

Inspected `zaydattique/codecity` at `5b7b3234320a50e68da02102bb2c9a555a12e82d`: only README existed, no AGENTS or CLAUDE. GitHub reported public visibility conflicting with required private status; no remote commit or PR made. Prepared the local `phase/01-foundation` branch with the original requirements, foundational documents, minimal development boot scene, clock, event bus, input configuration, Python protocol probe, tests and static checks. Audited seven pinned source candidates, including non-commercial GDQuest art and legacy Vehicle project risks; no imported third-party code or assets. Godot, Blender and Windows/GPU runtime are unavailable; candidate clones and engine download failed due to DNS. No art or export claimed. Verification results below; Phase 01 remains open pending Windows engine and source-isolation checks.

Verification on Linux x86_64 with Git 2.47.3 and Python 3.13.5: `python -m pytest -q` returned 16 passed in 2.51s; `python tools/check_foundation.py` passed. Process tests used actual stdin/stdout and a five-second test timeout. Exact production Python 3.14.10, Godot import/smoke, visual QA, upstream runtime compatibility and Windows export are unverified. Local commit only; private-repo gate remains open.

## Foundation transfer and preflight | 2026-11-25

Owner approved public main. Re-ran the local Phase 01/02 Python suite: 27 passed in 2.48s; static references OK. Transferred the foundation, source audit and preflight to the remote repository. The Godot runtime gate, actual artwork and upstream isolation remain open. No approved binary assets.

## Free asset automation pilot | 2026-11-25

Selected Kirill Sannikov's CC0 painted wooden bench from Poly Haven to prove the asset toolchain before character production. Implemented bounded HTTPS acquisition, relative-path validation, provider size/MD5 verification, SHA-256 provenance, glTF dependency checks, Blender source packing, GLB export and CPU preview rendering with geometry/scale/material checks. Local Python suite: 38 passed in 2.55s; Python compilation and static foundation checks passed. DNS access to Poly Haven/Blender failed locally and Blender/Godot binaries are absent, so real download, export and render are not yet verified. Synthetic tests are not actual art. No assets approved or committed.

## Hosted verification wiring | 2026-11-25

Committed a free hosted workflow with pinned actions, Python tests, Godot Linux import and explicit smoke marker, Blender LTS download/checksum and CPU-render pilot. Artifacts have seven-day retention and read-only repository permissions; no automatic commits of binary art. GitHub confirmed the main ref update and recursive tree with 31 source files. The Actions runs endpoint returned zero runs at the initial check; first execution still pending and manual workflow dispatch may be required. No runtime or visual pass is claimed.

## Hosted pilot verification and character candidate | 2026-11-25

Fetched the completed run 45585769664 and inspected both job logs. Python 3.14.10 38 tests passed (0.21s), Godot 4.7.2 import and boot marker succeeded, Blender 4.5.17 LTS rendered the actual licensed bench. Downloaded artifact 15009260029 and inspected its 960x720 preview and report: 630 triangles, dimensions 1.165 x 0.497 x 0.889 m, consistent grain and visible edge wear. Candidate appropriate for indoor furniture, pending Godot import/collision review. No gameplay build or GPU benchmark claimed. Added a two-protagonist authoring profile and MPFB candidate build job using pinned upstream 650c5c53 and official CC0 system assets. Actual character runtime, texture/mesh preview, LOD/motion and art approval are still unverified. Windows interactive and isolated upstream runtime gates remain open.

Added independent Windows headless verification and a real bench Godot import check for the exact reviewed GLB digest, staged outside the shipping project. The source artifact expires after its retention period; later reruns must use a new reviewed asset digest. Workflow execution pending. Windows headless is not interactive or GPU verification.

Run 45587501836: 44 Python tests passed (0.25 s), Godot boot marker and bench rendering passed again. Separate character job failed at Blender download (HTTP 403), before MPFB execution. Removed redundant installation by sequencing the character build after the successful bench render/upload on the same runner. No bypass of checksum or source validation; new run pending.

Run 45587661323: bench GLB SHA-256 matched, Godot import and mesh check passed with 630 triangles and dimensions (1.164944, 0.889291, 0.496543) in Y-up coordinates. Windows Python suite had 43 passes and one failure: ZipFile.writestr(name,...) normalizes a Windows backslash before validation. Constructed ZipInfo explicitly to test a literal malformed archive member rather than weakening the path validator. Re-run pending; no Windows engine claim yet. The reviewed bench is structurally importable, collision and interaction remain later tests.
