# File map

Root README launch and status; AGENTS operating rules; HISTORY changes; ARCHITECTURE ownership and contracts; ROADMAP phase gates; ASSET_REGISTRY provenance; PERFORMANCE budgets/results; THIRD_PARTY_NOTICES upstream pins; FILEMAP this index. `docs/CodeCity_Project_Instructions.txt` and `docs/CodeCity_Production_Prompts.txt` are unchanged requirements; `docs/ASSET_PIPELINE.md` and `docs/QA.md` specify art and QA. `.gitignore` excludes generated/raw files; `.python-version` pins target Python; `pytest.ini` configures test discovery. `game/project.godot` defines engine, renderer, input, autoloads; `game/core/world_clock.gd` clock; `game/core/event_bus.gd` facts; `game/scenes/foundation.tscn` and `.gd` dev boot/smoke. `ai/worker.py` offline ping probe. `tests/test_worker.py` unit and process tests; `tools/check_foundation.py` static reference check. Planned but absent: approved asset sources, game/assets, player and NPC controllers, IPC bridge, save, traffic, world chunks, mission data, export preset, packaging scripts. No duplicate implementation directories.

`tools/validate_assets.py`, `art/intake.example.json` and `tests/test_asset_intake.py` implement fail-closed asset provenance preflight; no geometry generation.

Pilot: tools/fetch_pilot_asset.py downloads the fixed CC0 glTF source and dependencies with bounded integrity checks; tools/render_pilot_asset.py imports, validates, exports and renders using Blender CPU; tests/test_asset_pilot.py checks the download plan and failure cases. Output build/asset-pilot is ignored.

`.github/workflows/codecity.yml`: independent foundation verification and CC0 candidate render jobs; results uploaded as short-lived artifacts, never as automatically approved runtime assets.

`art/characters.json` is the two-protagonist authoring definition. `tools/build_character.py` is a Blender/MPFB candidate generator with bounded asset-pack extraction, geometry/material/rig checks, editable source and GLB export, real front/three-quarter/face previews. `tests/test_character_pipeline.py` tests profile count and archive path safety. New workflow job uses free CPU runner and uploads candidate-only artifacts.

`verification/bench_import.gd` checks the exact candidate imported mesh, material, triangle count and dimensions; `.github/workflows/phase01-verification.yml` runs Windows headless foundation and candidate import checks independently.

New authoritative docs: MASTER_PRODUCTION_DIRECTIVE.md and the six specialized docs linked in README. `game/core/session_state.gd` in-memory selection/progression; `game/core/world_interaction.gd` shared range/tree helper; `verification/session_contract.gd` engine regression fixture; `ai/academy_contract.py` trusted result-only translation and `tests/test_academy_contract.py` validation tests. `tools/fetch_system_pack.py` official mirror downloader. No sandbox, physical display, or save persistence yet.

`.github/workflows/upstream-isolation.yml` isolated pinned reference import/startup matrix; `tools/verify_local.ps1` local equivalent foundation/session smoke and optional asset builds. No engine binary or source pack committed.

Foundation `.github/workflows/codecity.yml` is now independent from `.github/workflows/asset-production.yml` (licensed bench/selected character candidate and five rendered views). Supersedes earlier combined workflow references.

`game/core/camera_orbit.gd`: first MIT OpenCity camera geometry adaptation, pure functions, tested by the expanded session fixture; not connected to player camera yet.

`game/core/scene_loader.gd` threaded allowlisted resource load contract; session fixture exercises the actual boot scene resource. `tools/render_vehicle_candidate.py` pinned source GLB inspection and real exterior/cockpit renders; `.github/workflows/vehicle-candidate.yml` separate free candidate pipeline. Character fallback source provenance stored alongside input ZIP.

`tools/fetch_street_sources.py` reuses Poly Haven validation and adds texture-map selection; `tools/build_street_candidate.py` authored meter-scale street surfaces and licensed furniture, plus separate facade kit inventory; `.github/workflows/street-candidate.yml` independent hosted rendering; `tests/test_street_sources.py` map-plan regression.

`tools/assemble_street_exteriors.py` composes matched wall/door/window/trim modules into four enclosed exterior candidates around reviewed road; `.github/workflows/street-exteriors.yml` retrieves exact reviewed artifact and renders three views. Character generator now checks actual height against profile after uniform hierarchy scaling.

`tools/render_concept_coupe.py` and `.github/workflows/concept-coupe.yml` render and inventory exact alternative coupe for review, not integration. Report retains license and logo restrictions.

`tools/optimize_mesh_candidates.py` shared static non-destructive mesh reduction with instance-weighted target, UV/material/bounds checks and real comparison renders. `.github/workflows/asset-optimization.yml` stages exact inspected street and car geometry; car only inspection images/report are uploaded.

`verification/phase_a_asset_review.gd` and `.github/workflows/phase-a-art-review.yml`: staged exact candidate GLB import and real Godot software-rendered views, no shipping asset changes. Optimizer retries intact source after overaggressive planar dissolve.

Existing foundation scene now contains the working temporary profile, two modes and two protagonist selectors. Session contract regression exercises the actual UI signal connections and draft selection; no fake launch or save. Real art review references exact budget-passing street GLB.

`tools/freeze_character_morphs.py`: offline GLB default-morph runtime derivative, keeps skin hierarchy/materials, no animated morphs accepted. `tests/test_freeze_character_morphs.py`: sparse accessors, skin retention, rejection. Art review stages separate derivatives, records hashes and still verifies actual imported geometry.

P08 candidate: game/core/harbor_layout.gd, street_player.gd, street_map.gd; game/scenes/harbor_playtest.gd; verification/street_playtest.gd and .github/workflows/street-playtest.yml. Existing boot menu launches only installed candidate street; exact asset staging outside tracked game. No approved asset binary committed.
