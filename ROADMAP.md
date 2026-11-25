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

One detailed street with continuous sidewalks and collision/nav, two fully rigged playable protagonists (Adrian and Maya), one original driveable coupe, six distinguishable adults, one enterable functional interior, one short A New Beginning mission and one physical Control Room Academy mission, real map/minimap, pause/settings, sound and saved independent progress. Initial sequence: arrive, explore, interact, enter/exit vehicle, drive, meet a story contact only if role and assets approved, demonstrate different reactions and one real consequence. Include save/reload and offline rehearsal before public demo. Art signoff on close-up, movement, day/night/indoor shots; six fixed-seed scenarios; no crashes or broken progression; budgets in PERFORMANCE and QA. Expansion requires owner signoff after measured Windows build.

## Hosted automation checkpoint

Public main source transfer and free render-pilot scripts are now committed. The pilot uses an actual CC0 prop to verify the toolchain before character production. Local Python tests passed; first hosted execution and visual approval remain pending. Phase 01 runtime gates still open. Do not expand city or generate the full cast before hero/street acceptance.

## Current gates after hosted pilot

Linux pinned engine smoke and Python target tests passed; real Blender bench export/render passed and preview reviewed. Phase 01 still requires Windows interactive and upstream candidate isolation. Phase 02 character candidate job is a controlled art feasibility test, not a completed vertical slice. Two playable characters: Adrian and Maya, other principal characters remain story NPCs. First detailed street remains Harbor Boulevard; no full city generation before vertical slice gate. Character selection, profile UI, shared real minimap/full map, waypoints and location graph are acceptance criteria after actual characters and street exist. No decorative/fake controls or location previews.

Bench candidate visual and structural Godot import gates now pass. Windows headless suite exposed a platform-specific test fixture defect; corrected and queued for verification. Interactive Windows, upstream isolation and gameplay remain open.

## Revised Phase A continuation

Hosted Windows 44/44 and Godot headless boot passed (45588073887); Linux 44/44 and Godot boot passed (45588073883). Bench candidate verified, interactive/export/GPU and upstream source isolation still open. Current focused work: restore MPFB source acquisition, validate session/interaction and Academy result contracts; next actual character/street/coupe and isolated gameplay references. Do not build city or mark Academy executable until sandbox security and actual world gates pass. Phase 02 art and functional dual-mode slice gates remain open.

Dual-mode profile/session and range contract passed hosted Windows; Python 65 tests pass. Upstream isolated smoke passed for OpenCity and Truck Town, failed strict leak checks for GDQuest/Easy Vehicle/Road Generator. First small camera math adaptation added, pending regression; no demo art copied. Art candidate acquisition remains blocking the real vertical slice.

Phase A remains open: Windows/Linux foundation and camera regression verified, two-mode contracts implemented, actual threaded load regression queued, legacy character archive fallback added, sports coupe candidate render workflow added. Real characters, car inspection, detailed street, interactive UI and source-specific gameplay checks pending; no expansion.

Phase A art progress: one real Adrian candidate (rework), one rejected coupe candidate; Maya and detailed street missing. Foundation, session, camera and threaded loading contracts passed hosted Windows/Linux. Do not mark Phase A complete until actual acceptable hero/street/coupe and relevant interaction/interactive evidence exist. No city expansion.

First street art pipeline now authored: real textured 32m road/sidewalk and street furniture, separately inspect licensed facade modules before assembling buildings. Render/QA pending, no street acceptance or city expansion.

Phase A checkpoint: complete Adrian five-view artifact verified but scale/style need correction. Street surface + modular source library passed render; actual four-building exterior assembly queued. Maya and replacement vehicle still outstanding; no expansion.

Actual four-building exterior street candidate and second coupe candidate generated; both over budget. Run candidate mesh optimization and inspect before approval. Adult character morph corrected, both full revised renders pending. Phase A not closed; remaining interactive, art and source-specific behavior gates explicitly open.

Both adult rigged candidates generated and inspected; height and triangle gates pass, art and animation remain open. Optimized coupe hits 60k budget, street exceeds 110k. Direct-collapse retry and real Godot staged candidate import/render checks queued. Phase A remains open pending actual tests, approval and remaining art work.

Numerical street/coupe budgets now pass on revised optimizer; latest Windows/Linux 67 tests and smoke/session pass. Imported character raw AABB check failed; measuring actual skinned world-space vertices and preserving both bounds in QA. Engine-render and actual art review still required.

Profile/mode/character draft UI now implemented and connected to authoritative in-memory state, engine regression pending. Both numerical geometry budgets pass, actual optimized street visual inspection passed geometry-preservation review only; real character render/import test still running. No production approval or gameplay.

Both corrected adult characters and numerical street/coupe budgets pass source review. Actual profile/mode UI regression and 67 Python tests passed Windows/Linux. Maya engine morph discrepancy remains, default morph freeze candidate build now queued. Phase A still open until in-engine candidate check and remaining art/interactive approval.

Actual runtime import passed both adult character derivatives and budget-passing street. 70 tests, menu selection and foundation passed Windows/Linux. Software-rendered review reached success marker but audio device initialization failed strict log gate; fixed isolated render runner configuration. No production art approval, actual user-input playtest or performance measurements yet.

## P08 focused playable candidate street

Goal: actual character physics and camera on verified street, not full vertical-slice approval. Files: game/core/harbor_layout.gd, street_player.gd, street_map.gd; game/scenes/harbor_playtest.gd, foundation.gd, input config, verification and isolated workflow. Real colliders derived from the reviewed layout and furniture; test limits at street ends, closed buildings inaccessible. Candidate-only (unanimated rigs); do not ship as final. Test both spawn, movement, jumping, collision, map and pause, camera/step further checks; actual engine screenshot. Remaining P08: licensed motion, deformation, stairs/curb, vehicle entry/exit, controller and interactive Windows. No city expansion.

P08 first physical street test passed actual engine headless and software rendering. Candidate remains rest-pose at that revision. New licensed rotation retarget pipeline with five required clips and real runtime selection added, pending CI. Actual pause now pauses scene tree; map and controls tested again. Remaining foot IK, crouch/turn transitions, stair/camera tests, vehicle and interactive Windows gate remain open.

## P08 technical candidate milestone verified

Linux and Windows candidate physics and nine licensed motion clips passed, actual thigh rotation changes, camera collision proxy, crouch/sprint, jump, map control, actual paused clock and two character spawns. Standalone Windows export/boot passed twice (45622041590, 45622243827). Candidate artifact 15023914487 is the later verified export. No city expansion. Remaining P08: artist review of stride, feet, wall clipping, slopes/stairs, input/controller, animation transitions, vehicle sockets/enter/exit. First complete vertical slice still requires real licensed cleared driveable car, six Python NPCs, one functional interior, story and actual Academy sandbox mission, persistence, audio/settings and hardware QA. Candidate gameplay is not production-ready.

## P09 driveable street candidate

Goal: one licensed neutralized coupe with real wheels/cockpit and physical driving in existing 32m slice. First build/review derivative, then integrate vehicle body, suspension, entry/exit ownership and collision, map and pause. Files: tools/prepare_coupe.py, isolated coupe-ready workflow, forthcoming focused runtime/test changes. Risks: logo texture references, wheel orientation, seating, short street and wheel stability. No original marks/vehicle binary committed or final approval until actual renders, handling and manual QA pass.

P09 vehicle runtime candidate implemented with four measured wheels, basic raycast physics, real door/headlight action and safe range/LOS/speed/capsule entry/exit, map/pause ownership; dedicated actual-model regression written. Remaining art build, integration, real driving tests, rendering and seated/IK, controller/manual/hardware gates. No vehicle in prior Windows export.

P09 first actual neutralized car art and physics candidate passed in 45629610589/45629868579. Source material rework for verified emission/glass defects and HUD ownership correction committed, rerender and physics retest pending. Candidate Windows export still pending, no seated driver or final vehicle approval.

Revised vehicle v002 actual driving and material render tests passed 45630744693; fixed observed exit leg/door overlap with geometry-derived swept clearance. Latest full candidate regression and Windows export required before delivery. No final vehicle art or seating/handling approval.
