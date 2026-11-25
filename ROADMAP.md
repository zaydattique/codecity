# Roadmap and phase gates

Every gate requires inspection, implementation, tests and root-cause fixes, recorded against exact revision. No gate passes based on a document or screenshot alone.

| Phase | Scope and affected areas | Main risk / rules | Exit evidence |
|---|---|---|---|
| 01 P00/P01 | Boot, input, clock, event bus, protocol probe; root docs, game/core, ai, tests, tools, docs | Public main, licensed candidates only; no art | Windows Godot import/smoke, Python target tests, candidate isolation results, source/license audit; currently blocked |
| 02 P02/P09/P07/P15/P22 | Adrian, one sports coupe, six adults, one street; art/source and game/assets | Real base meshes and original look; first hero/street reviewed before batch | Source+GLB+LOD+license, day/night/interior views, art signoff |
| 03 P08 | Player locomotion, camera, animation, car transition; actors/vehicles | No primitive actors or animation shortcuts | Slopes, stairs, camera collisions, foot plant, entry/exit, keyboard/controller |
| 04 P23 | Python decision worker, bridge, memory, perception; ai/game/core/actors | Bounded IPC and safe honest fallback | Six autonomous NPCs, seeded scenarios, stale/timeout tests, measured cost |
| 05 P21/P26 | One apartment/store interior and first short mission | Real interior and state-driven consequence | Enter/leave, objective checks, alternative outcome, reload checkpoint |
| 06 P30 | Vertical slice QA, profile/export rehearsal | No city expansion until approved | Hardware baseline, measured frame percentiles, asset and gameplay acceptance |
| 07 P03-P07/P10-P22 | Other protagonists, vehicles, 5 districts incrementally | 800x800 m only if profiling supports it; no mass generation | Per-district streaming, topology, varied identities, budget regression |
| 08 P24/P25/P27 | Traffic, phone, economy, world time/weather/audio | Genuine controls, no unbounded simulation | Traffic stress, accessible jobs, persistence and weather reactions |
| 09 P26/P28 | Full story, UI/cinematics | Consequences and real progress, original art | Multiple mission paths, skip/retry, responsive controls |
| 10 P29-P32 | Persistence, Windows packaging, optimization/demo | Offline clean-machine test; no fabricated metrics | Export, complete playthrough, save recovery, licenses, benchmarks |

## Phase 01 execution and pending gates

Inspected remote metadata, main commit and root tree: README only. AGENTS/CLAUDE absent. Source visibility public; local branch staged, no remote writes. Read source requirements. Pinned release candidates and upstream revisions, identified restrictions. Authored boot, clock/event contract, input map, Python transport probe and structural verification. Risks: no engine/Blender binaries, GitHub DNS unavailable from local container, no Windows/GPU testing, storage quota unknown, no isolated candidate runtime. Owner subsequently approved public main; publish tested sources there, run exact-version import/smoke and upstream isolated tests, fix root causes. Do not enter Phase 02 until Phase 01 gates pass.

## Vertical slice acceptance

One detailed street with continuous sidewalks and collision/nav, one fully rigged Adrian, one original driveable coupe, six distinguishable adults, one enterable functional interior, one short A New Beginning mission. Initial sequence: arrive, explore, interact, enter/exit vehicle, drive, meet a story contact only if role and assets approved, demonstrate different reactions and one real consequence. Include save/reload and offline rehearsal before public demo. Art signoff on close-up, movement, day/night/indoor shots; six fixed-seed scenarios; no crashes or broken progression; budgets in PERFORMANCE and QA. Expansion requires owner signoff after measured Windows build.

## Hosted automation checkpoint

Public main source transfer and free render-pilot scripts are now committed. The pilot uses an actual CC0 prop to verify the toolchain before character production. Local Python tests passed; first hosted execution and visual approval remain pending. Phase 01 runtime gates still open. Do not expand city or generate the full cast before hero/street acceptance.

## Current gates after hosted pilot

Linux pinned engine smoke and Python target tests passed; real Blender bench export/render passed and preview reviewed. Phase 01 still requires Windows interactive and upstream candidate isolation. Phase 02 character candidate job is a controlled art feasibility test, not a completed vertical slice. Two playable characters: Adrian and Maya, other principal characters remain story NPCs. First detailed street remains Harbor Boulevard; no full city generation before vertical slice gate. Character selection, profile UI, shared real minimap/full map, waypoints and location graph are acceptance criteria after actual characters and street exist. No decorative/fake controls or location previews.

Bench candidate visual and structural Godot import gates now pass. Windows headless suite exposed a platform-specific test fixture defect; corrected and queued for verification. Interactive Windows, upstream isolation and gameplay remain open.
