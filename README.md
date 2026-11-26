# BloomLogic

BloomLogic is a native, offline Python learning application built around interactive 3D real-world exhibits. Learners predict an outcome, read and edit Python conditions, observe physical consequences, compare results and practice independently.

## Current release: 1.0.1
The If / Else greenhouse controller is the implemented lesson. The library contains fourteen exhibit concepts; the remaining thirteen are not playable simulations. The lesson includes guided voice and text, dry/moist predictions, actual executed-line tracing, comparisons and Boolean concepts, irrigation experiments, timeline seek/step, plant stress comparison and a temperature-controlled ventilation exercise.

### Windows installation
Download the release artifact from [the successful 1.0.1 workflow](https://github.com/zaydattique/codecity/actions/runs/45792172356/artifacts/15102988213). GitHub wraps the portable ZIP in an artifact archive; extract that outer archive if necessary, then extract BloomLogic-Windows.zip. Open BloomLogic.exe in the extracted BloomLogic folder. Keep _internal and licenses beside it. No separately installed Python, Blender or internet is needed for normal operation. See OPEN_GREENHOUSE.md for controls and troubleshooting.

Release revision: `901ef49a1e4b90aae0a30d2d7afea405936a1aca`; merged in `708642dbce03163b6dd71e23ac1a4a8bd261fd00`.
Portable archive SHA-256: `550778e2546dfbf9aded1816cfaf3d253527eece9b4a7877f2a46eaa671c5e41`.
Archive bytes: 103,272,636; 1,668 files verified. Evidence artifact: [release audit](https://github.com/zaydattique/codecity/actions/runs/45792172356/artifacts/15103411879).

### Verification and limitations
Hosted Linux and Windows core tests, native rendering, X11 real input, clean packaged Windows extraction, blocked-network walkthrough, independent process resume and texture-failure regression passed. Version 1.0 had a real physical Windows texture crash; 1.0.1 converts native filenames, verifies PNG maps and disables failed optional maps instead of terminating the lesson. Physical user-device retest is still required. Do not distribute 1.0.
Graphics are not photorealistic, narration is synthetic, facial lip sync is absent, plant growth uses discrete geometry samples, and the model is illustrative rather than scientific. Performance targets remain unverified on physical GPUs.

## Development
Python 3.13, Panda3D 1.10.16, panda3d-gltf 1.3.0, Blender 4.5 LTS for art, PyInstaller 6.16.0 for Windows packaging. Install pinned dependencies with `python -m pip install -r requirements.txt`, then run `python -m unittest discover -s tests -v`. Actual GUI requires the verified runtime asset bundle in runtime/; follow FILEMAP.md and the Windows workflow. The internal Python package retains its existing technical name.

## Documentation
- AGENTS.md / CLAUDE.md: active rules.
- ROADMAP.md: curriculum, current gate and next work.
- ARCHITECTURE.md / FILEMAP.md: runtime and source structure.
- ASSET_REGISTRY.md / THIRD_PARTY_NOTICES.md: provenance and licenses.
- PERFORMANCE.md: measured results and targets.
- HISTORY.md: chronological changes and failures.
- OPEN_GREENHOUSE.md: student installation and controls.
