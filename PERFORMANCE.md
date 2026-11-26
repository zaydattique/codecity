# Performance
Targets only: 720p/30, 1080p/60. One compact scene, fixed simulation steps independent of rendering, pool droplets, LOD background props, budget transparent layers and shadows. Record exact hardware, resolution, median/p95/p99 frame time, RAM/VRAM, load time, stutters. No new measurements or Windows results yet.

Integration candidate caches 41 discrete mesh samples and pools eight droplets. Memory and frame pacing not measured. Package self-test only checks asset loading and logic, not actual display performance.

Initial package smoke passed; no interactive performance metrics. New teacher increases mesh/texture budget; software-render capture is not representative hardware profiling.

Actual 1280x720 software renderer capture succeeded on hosted Ubuntu run 45699394455, not a target GPU benchmark. No FPS claims.

New studio layout and packaged GUI capture pending. No hardware FPS claims.

Run 45713936738 rendered all eight native GUI screenshots successfully at 1280x720. No representative GPU frame-time measurements; props increase rendering cost.

Previous Windows GUI gate timed out (45714558040); no hardware metrics. Phase 1 captures startup milestones and Python fault traces, explicitly distinguishes software fallback from native desktop. No visual art changes.

Phase 1 packaged GUI verified on hosted Windows 45719638724, not user hardware. Phase 2 replay bounded to 60 days, comparison instances existing meshes, trace cached per day. No hardware measurements yet.

Phase 2 packaged GUI passed 45721130738. Phase 3 retains 41 mesh stages, adds bounded 175 grains, 18 pooled droplets, 1024 shadow map on supported normal graphics; additional geometry and shader cost not measured. No FPS claim. Software diagnostic separate.

First generated rhizobox had 172,968 triangles; optimization targets fewer than 10,000 by using low-poly grains instead of UV spheres. Actual count and frame times to verify after regeneration.

First Phase 3 native render/input pass was successful but visual shadow acne observed. Lighting corrected with narrower shadow lens depth and depth bias; no frame-time claims. Reference Panda3D 1.10 lighting manual https://docs.panda3d.org/1.10/python/programming/render-attributes/lighting .

Phase 3 corrected runtime and packaged Windows GUI passed 45774097576. Phase 4 benchmarks report 60 actual normal task frames per camera after 8 warmup frames, VSync disabled, paused mature plant; actual window resolution and renderer recorded. Separate process timer includes launch and peak working set sampled at 250 ms. CPU/OS/RAM/video adapter information from CIM, VRAM usage not measured. Results pending. No user GPU benchmark claim.

1.0 user-device texture load failed despite hosted Windows pass. 1.0.1 compatibility fallback may reduce material detail, not a measured speed improvement.
