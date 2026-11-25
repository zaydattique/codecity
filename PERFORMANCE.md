# Performance
Targets only: 720p/30, 1080p/60. One compact scene, fixed simulation steps independent of rendering, pool droplets, LOD background props, budget transparent layers and shadows. Record exact hardware, resolution, median/p95/p99 frame time, RAM/VRAM, load time, stutters. No new measurements or Windows results yet.

Integration candidate caches 41 discrete mesh samples and pools eight droplets. Memory and frame pacing not measured. Package self-test only checks asset loading and logic, not actual display performance.

Initial package smoke passed; no interactive performance metrics. New teacher increases mesh/texture budget; software-render capture is not representative hardware profiling.

Actual 1280x720 software renderer capture succeeded on hosted Ubuntu run 45699394455, not a target GPU benchmark. No FPS claims.

New studio layout and packaged GUI capture pending. No hardware FPS claims.

Run 45713936738 rendered all eight native GUI screenshots successfully at 1280x720. No representative GPU frame-time measurements; props increase rendering cost.

Previous Windows GUI gate timed out (45714558040); no hardware metrics. Phase 1 captures startup milestones and Python fault traces, explicitly distinguishes software fallback from native desktop. No visual art changes.
