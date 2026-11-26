# BloomLogic | File map

## Documentation
README.md current release and installation; AGENTS.md sole active engineering rules; CLAUDE.md entrypoint; ROADMAP.md phase gates and curriculum; ARCHITECTURE.md system design; HISTORY.md chronological changes; ASSET_REGISTRY.md asset evidence; PERFORMANCE.md measured results; THIRD_PARTY_NOTICES.md licenses; OPEN_GREENHOUSE.md packaged student instructions.

## Active Python application
- greenhouse.py: native app entrypoint, navigation, 3D scenes, UI, input, audio, diagnostics, walkthrough and benchmark flags.
- codecity/curriculum.py: fourteen exhibit concepts, greenhouse guide and code examples.
- codecity/model.py: immutable plant state and daily evolution.
- codecity/rules.py: finite AST compiler, execution and trace.
- codecity/session.py: experiment state, deterministic seek, exhaustive challenge, atomic profile.
- codecity/lesson.py: comparison, mature stress intervention, fan validation and trace.
- codecity/graphics.py: native filenames and optional PNG integrity/decoder handling.
- requirements.txt: pinned runtime dependencies.

The directory codecity/ is an existing import path, not product branding. No rename in this documentation-only change.

## Art and release tools
- tools/polyhaven.py, tools/fetch_greenhouse_sources.py, tools/greenhouse_soil.py: verified licensed asset acquisition.
- tools/build_greenhouse_art.py, tools/runtime_mesh_export.py: editable botanical/greenhouse Blender source and evaluated meshes.
- tools/build_teacher.py, tools/build_fan_art.py: teacher gesture and modeled ventilation equipment.
- tools/build_narration.py, tools/build_visual_media.py: local narration and derived material/audio.
- tools/release_manifest.py, tools/test_release.ps1: file inventory and clean offline Windows release audit.
- tools/test_input.sh: real X11 mouse and keyboard input.
- art/characters.json: retained authoring presets, not active gameplay roles.

## Verification
tests/test_greenhouse.py, tests/test_session.py, tests/test_lesson.py, tests/test_graphics.py: model, rules, persistence, traces, comparison, actuator and asset compatibility regressions.
.github/workflows/greenhouse.yml: core tests.
.github/workflows/greenhouse-art.yml: source and render jobs.
.github/workflows/greenhouse-windows.yml: BloomLogic Windows packaging, native GUI, input, offline and fault-injection gates.

Generated runtime/ assets, build outputs and exports are not tracked source. Earlier game documentation was removed during the product reset and remains in historical Git revisions only.
