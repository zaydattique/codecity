# Performance budgets and measurement

All numbers are provisional design budgets, not measurements. Targets: 720p/30 FPS low-spec (33.33 ms frame) and 1080p/60 FPS capable GPU (16.67 ms). Identify hardware before assigning minimum requirements. Initial budget on 60 FPS capable GPU: main-thread gameplay <= 4 ms, physics/navigation <= 3 ms, scene/render submission <= 4 ms, reserve <= 5.67 ms; GPU critical path <= 14 ms measured separately, not added to CPU total. Low target budgets scale only after profiling. AI worker < 5 ms per 32-agent batch as an initial target, max 50ms soft deadline; no sync waiting. Near NPC decisions 5 Hz, mid 1 Hz, far abstract 0.2 Hz; animation 60/30/15 Hz where visually safe. Stagger batches. Limit nav replans, avoid all-pairs scans, pool agents and vehicles, spatial partition queries.

Initial scene budgets: 40-70k hero triangles, nearby NPC 12-25k, distant 500-3000, hero vehicle 30-60k, traffic 5-15k, small exterior 5-20k. Begin with six NPCs and one car. Aim 1.5 GB total textures resident low, 3 GB capable preset only if VRAM permits; 2 GB/4 GB total game working set targets initially subject to actual hardware. Use GPU compression, atlases, mipmaps, LOD, culling, MultiMesh static instances and pooled actors. Avoid expensive low-tier reflections/shadows; evaluate Forward+ vs compatibility, not visual parity promise. Stream asynchronously, attach under 2 ms/frame target and preload by velocity. No expansion until measured evidence.

## Measurement protocol

Record revision/build, OS, CPU/GPU driver, RAM/VRAM, renderer, resolution, preset, seed, time/weather, counts, capture duration, warm-up, profiler overhead. Export native build. Warm 60s then record 120s per scenario, three runs. Report frame time median, p95, p99, worst, dropped/long frames, CPU/GPU split, process RAM, peak VRAM, worker per-batch duration, startup and chunk stalls. Capture raw CSV outside repo, record summarized results here. Scenarios: idle, walk, sprint, fast drive, six NPC interactions, crowd/intersection later, night, rain, interior entry, mission, save/load, extended 30min. No average FPS-only claims. Capture screenshots of artifacts and reproduce issues.

## Actual results

No GPU, Godot, Blender or Windows runtime available in local staging environment. No frame metrics, RAM/VRAM performance or startup measurements. Python functional tests are not performance measurements. No minimum hardware claims.

Hosted CPU smoke and pilot rendering are functional checks only. Do not report GitHub runner timings as target gaming FPS or Windows GPU benchmarks. Record actual workflow logs and exact versions before closing the engine gate.

Revised targets preserve 720p30/1080p60 as goals; add isolated Academy execution resource limits, zero game-thread wait, mode-specific load and terminal latency. Later 25–40 nearby NPCs only after six pass and hardware profiling. Hosted Windows/Linux boot and tests are functional evidence, not hardware benchmarks.

P08 Windows candidate export/boot and actual physics passed on GitHub windows-2025; rendered tests Ubuntu 24.04 software OpenGL (llvmpipe, Dummy audio for visual-only tests). This verifies functional execution, not gaming FPS. No real target GPU hardware measurements, frame percentiles, RAM/VRAM or load-time benchmark recorded. Keep 720p30 and 1080p60 as targets only.
