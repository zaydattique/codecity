# QA and acceptance

Phase 01: inspect exact repo base and visibility; confirm owner-approved public main before publishing. Verify tool versions, static refs, Python tests and bounded malformed requests; engine import and smoke with explicit success marker; interactive exit at 720p/1080p. Record stdout/stderr, exit code, version, OS. No approval until required runs completed. Source candidates isolated, verify imports, compare behavior/performance, check full asset notices and file-level licenses. Missing engine, asset or hardware is a blocker, not a pass.

| Area | Scenario | Pass condition |
|---|---|---|
| Art | hero close-up, deformation, six faces, car cabin, street day/night | approved source+GLB, no unacceptable artifacts, real collisions, unique silhouettes |
| Movement | walk/run/crouch/jump, stairs/slopes, camera wall | no penetration, fall-through, camera clipping or lost control |
| Vehicle | entry occupied/blocked, drive reverse brake exit, collision | reservation safe, control transferred only on success, no teleport into obstruction |
| NPC | bump, stare, follow, familiar encounter, routine, rain later | differentiated context reactions with fixed seed, ordinary routines continue |
| IPC | oversized, duplicate, stale, invalid enum, process crash, timeout | bounded failure, no main-thread block, safe fallback labeled in dev logs, restart |
| Interior | enter/exit, doors, seating, NPC access | functional geometry and connected nav, no missing state |
| Mission | prerequisite fail, alternative outcome, retry, reload | actual facts drive state, no fake completion or dead-end |
| Persistence | invalid save, old/future schema, interrupted write | reject/recover safely, consistent world snapshot |
| Packaging | clean Windows offline without Godot/Blender/Python | game and required local worker launch; licenses present; no network requirement |
| Performance | scenarios from PERFORMANCE | measured target and percentile report; no expansion without review |

Use seeded fixtures, record exact reproduction, expected/actual, revision, logs and capture, prioritize crashes/data loss, gameplay blockers, visual/performance regressions. Re-run the failing test and full affected suite after root-cause fixes. No hidden overrides. Record owner approval for visual gate and build. No benchmark or screenshot may substitute for a playtest.
