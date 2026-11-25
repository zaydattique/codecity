# BloomLogic
A native Python 3D learning encyclopedia. Fourteen distinct real-life exhibits are listed in the lesson library; the greenhouse conditional lesson is the active implementation. Other lesson cards show their scope without pretending to be playable.
Python 3.13, Panda3D 1.10.16, panda3d-gltf 1.3.0, Blender 4.5 LTS authoring. Run `python -m unittest discover -s tests -v`. The Windows workflow builds BloomLogic.exe, verifies the packaged logic and attempts actual GUI capture. The prior package was rejected; do not distribute it as BloomLogic. Current verification pending.

Core and first native UI verification passed on 45713936738; a corrective layout and prop integration is being tested. The new package is built from source and uses the BloomLogic window title and EXE.

Phase 1 reliability work: authoritative resumable experiment, exhaustive 78,982 sensor combinations, isolated diagnostics, actual X11 mouse and keyboard test, and Windows release gated on GUI verification. Prior run 45714558040 failed GUI timeout despite passing package self-test. Do not treat that artifact as release approved. New checks pending.
