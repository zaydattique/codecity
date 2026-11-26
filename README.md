# BloomLogic
A native Python 3D learning encyclopedia. Fourteen distinct real-life exhibits are listed in the lesson library; the greenhouse conditional lesson is the active implementation. Other lesson cards show their scope without pretending to be playable.
Python 3.13, Panda3D 1.10.16, panda3d-gltf 1.3.0, Blender 4.5 LTS authoring. Run `python -m unittest discover -s tests -v`. The Windows workflow builds BloomLogic.exe, verifies the packaged logic and attempts actual GUI capture. The prior package was rejected; do not distribute it as BloomLogic. Current verification pending.

Core and first native UI verification passed on 45713936738; a corrective layout and prop integration is being tested. The new package is built from source and uses the BloomLogic window title and EXE.

Phase 1 reliability work: authoritative resumable experiment, exhaustive 78,982 sensor combinations, isolated diagnostics, actual X11 mouse and keyboard test, and Windows release gated on GUI verification. Prior run 45714558040 failed GUI timeout despite passing package self-test. Do not treat that artifact as release approved. New checks pending.

Phase 1 baseline 657f7e0 passed full native render, X11 keyboard/mouse and packaged Windows GUI in run 45719638724 (artifact 15070534455). Phase 2 adds real executed-line tracing, both predictions, interactive boundary checks, deterministic timeline and A/B comparison, independent ventilation controller. New candidate verification pending; fan equipment is an instructional geometry study, not final visual art.

Phase 2 verified at 06da8576 in run 45721130738: core, real input, native render and packaged Windows GUI passed, artifact 15072835791. Phase 3 candidate generates fresh Blender workbench, architecture, rhizobox, fan and teacher assets, adds leaf pivot stress, normal/gloss/shadow rendering, contact effects, camera transitions and flat UI refinements. New runtime and package gates pending. No photorealism claim.

Phase 3 corrected revision a779d2c passed normal native render/input and packaged Windows GUI (45774097576, artifact 15095118694). Phase 4 prepares a portable ZIP with release-manifest, dependency notices, clean extraction into a path containing spaces, separate empty working directory, removed Python PATH, outbound firewall block on extracted EXE, new-process save restore and timed 720p/1080p renderer sampling. Hosted runner validation does not prove user-device compatibility. Current Phase 4 checks pending.

Release 1.0 passed hosted checks but failed on a physical user Windows device when Panda3D could not load soil-nor_gl.jpg. Hotfix 1.0.1 uses converted native filenames, PNG normal map and explicitly logged optional texture fallback. Normal and deliberately corrupted-map walkthrough gates; pending verification. Do not distribute 1.0 as compatible.
