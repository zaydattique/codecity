# File map

Root README launch and status; AGENTS operating rules; HISTORY changes; ARCHITECTURE ownership and contracts; ROADMAP phase gates; ASSET_REGISTRY provenance; PERFORMANCE budgets/results; THIRD_PARTY_NOTICES upstream pins; FILEMAP this index. `docs/CodeCity_Project_Instructions.txt` and `docs/CodeCity_Production_Prompts.txt` are unchanged requirements; `docs/ASSET_PIPELINE.md` and `docs/QA.md` specify art and QA. `.gitignore` excludes generated/raw files; `.python-version` pins target Python; `pytest.ini` configures test discovery. `game/project.godot` defines engine, renderer, input, autoloads; `game/core/world_clock.gd` clock; `game/core/event_bus.gd` facts; `game/scenes/foundation.tscn` and `.gd` dev boot/smoke. `ai/worker.py` offline ping probe. `tests/test_worker.py` unit and process tests; `tools/check_foundation.py` static reference check. Planned but absent: approved asset sources, game/assets, player and NPC controllers, IPC bridge, save, traffic, world chunks, mission data, export preset, packaging scripts. No duplicate implementation directories.

`tools/validate_assets.py`, `art/intake.example.json` and `tests/test_asset_intake.py` implement fail-closed asset provenance preflight; no geometry generation.

Pilot: tools/fetch_pilot_asset.py downloads the fixed CC0 glTF source and dependencies with bounded integrity checks; tools/render_pilot_asset.py imports, validates, exports and renders using Blender CPU; tests/test_asset_pilot.py checks the download plan and failure cases. Output build/asset-pilot is ignored.

`.github/workflows/codecity.yml`: independent foundation verification and CC0 candidate render jobs; results uploaded as short-lived artifacts, never as automatically approved runtime assets.

`art/characters.json` is the two-protagonist authoring definition. `tools/build_character.py` is a Blender/MPFB candidate generator with bounded asset-pack extraction, geometry/material/rig checks, editable source and GLB export, real front/three-quarter/face previews. `tests/test_character_pipeline.py` tests profile count and archive path safety. New workflow job uses free CPU runner and uploads candidate-only artifacts.

`verification/bench_import.gd` checks the exact candidate imported mesh, material, triangle count and dimensions; `.github/workflows/phase01-verification.yml` runs Windows headless foundation and candidate import checks independently.
