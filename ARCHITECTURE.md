# BloomLogic | Architecture

## Native system
Python 3.13 is the authoritative application and simulation layer. Panda3D renders the native desktop interface and real 3D geometry, panda3d-gltf imports skinned/prop GLBs, Blender authors the assets, PyInstaller bundles the offline Windows distribution. No network service is required. The internal directory codecity/ is retained for compatibility.

```text
Lesson library / native UI (greenhouse.py)
    -> curriculum and guide (curriculum.py)
    -> validated CPython rules (rules.py)
    -> Experiment / deterministic state (session.py, model.py)
    -> trace, replay, comparison and fan practice (lesson.py)
    -> Panda3D scene, geometry, audio, camera and feedback
    -> atomic local profile and release diagnostics
```

## Learning flow
Observe includes dry and moist predictions and correct-rule demonstrations. Understand explains conditions, indentation, equality, elif and Boolean operators with actual trace results. Experiment accepts edited code and starting moisture/light/temperature. Challenge checks all 78,982 finite sensor combinations, and independent fan practice applies a distinct temperature actuator. Other cards describe intended exhibits only.

## Rules and state
Finite AST validation permits supported sensor expressions and one permitted actuator action per execution path. Actual CPython executes the validated program. Trace instrumentation records evaluated conditions and executed action line while preserving short-circuit behavior. This is a restricted domain interpreter, not a general-purpose Python sandbox.
Experiment owns compiled rule, initial and current plant state, previous sensor reading and action. A fixed simulated day advances the illustrative plant model independently of rendering. Run starts fresh; Pause / Resume preserves state. Step advances one day; Seek replays deterministic history to the explicitly selected day, preventing delayed slider callbacks from resetting state. Guide, challenge and comparison do not mutate the saved experiment. A/B comparison uses identical starting conditions. Stop watering after day 20 is a scheduled intervention, not a sensor-only rule. Draft code and validated replay state persist separately under %LOCALAPPDATA%/BloomLogic. Load restores paused state; preferences and completion are atomic.

## Graphics and audio
The native interface uses a 1280x720 logical coordinate system. The scene uses separate bench, architecture, rhizobox, 41 evaluated plant samples, leaf attachment transforms, fan housing and rotor, teacher rig and licensed props. Health drives posture and tint. Water particles/contact rings and synthetic irrigation sound follow actuator state. Camera interpolation is independent of the simulated day. On supported graphics, normal/gloss maps and directional shadows are enabled; safe graphics uses a lower-quality fixed-function renderer. Narration WAVs are generated at build time and bundled. No fluid physics, species calibration, facial lip sync or photorealism claim.

## Asset compatibility
graphics.py validates optional PNG sizes, signatures and SHA-256 against material-integrity.json before decoding. Native paths use Filename.fromOsSpecific. Optional map failure is logged and diffuse remains available; required geometry stays strict. The normal JPEG is source evidence only, not a runtime fallback. Never pass corrupted bytes into native codecs. Fault injection separately exercises a real missing-path Loader error.

## Packaging and verification
The Windows workflow pins the verified runtime bundle, generates PNG normal derivative, runs core tests, actual native render/input, and builds BloomLogic.exe. The release manifest inventories packaged files and notices. The clean extraction audit runs from a separate working directory without external Python on PATH, blocks outbound executable traffic, tests full walkthrough and independent resume, injects optional texture failure and records benchmarks. Test profiles are isolated from student data. Hosted fixed-function results are not dedicated GPU verification. Current exact release evidence: 45792172356.
