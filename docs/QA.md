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

Hosted Windows smoke and exact reviewed bench GLB import are separate checks. The bench import uses run 45585769664 artifact before expiry; verify SHA-256 and stage only in an isolated copy of game. Collision, interaction and Windows interactive tests remain separate gates.

Revised tests: profile/mode isolation, invalid spawn, duplicate mission, mutation of snapshot and interaction range; Academy broker result rejects stale IDs, wrong mode/target, failed execution, invalid/unbounded text. Must additionally test actual WASM sandbox denial (filesystem/network/process, exhaustion, timeout, cancellation), genuine Python output and physical world updates before Academy is playable. Headless session fixture uses empty Nodes for state tests only, not placeholder game assets.

Character import height verification must evaluate active normalized/relative blend shapes before skin transforms; raw culling AABB and unweighted base geometry are recorded but not accepted as visible height. Validate all weight/shape arrays, bind indices and normalized skin weights, then inspect actual rendered output.

Candidate street test: exact assets, actual CharacterBody3D input actions, sidewalk spawn, forward movement, jump/land, closed building collision, full-map control capture, pause/resume and Maya spawn. Headless and rendered checks must both pass; no manual hardware or animation certification. Risk: step, camera occlusion and crouch pose need further tests.

First candidate playtest passed in 45620485315. New motion QA requires actual imported AnimationPlayer with idle/jog transitions and Maya clip availability, normalized bone rotations and unchanged target skin. Crouch collision without licensed pose, root-motion removal, foot sliding, wall camera and landing remain explicit limitations. Verify actual renders, don't call source motion capture unless documented.
