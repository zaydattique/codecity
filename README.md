# CodeCity: Living World

Original standalone Windows open-world game with two modes: Living World (non-educational story) and CodeCity Academy (physical Python programming missions). The player experiences autonomous characters through behavior, not through an AI dashboard. GTA V and VI are aspirations for visual craft and reactive behavior, not assets, source or claims of achieved quality.

## Status: Foundation and asset preflight; runtime gates open

Public main is owner-approved. Development boot scene and standalone Python ping probe only; no gameplay assets or executable yet. Hosted Linux engine smoke and Python tests passed; Windows and interactive checks remain pending.

## Toolchain baseline

Godot 4.7.2 stable (standard, not .NET); matching Windows export templates; Blender 4.5.17 LTS; CPython 3.14.10 x64; pytest for development. The local tests use Python 3.13.5; target Python tests now verified in hosted Linux CI. Pin any additional packages and record hashes after a real install. Use official downloads: https://godotengine.org/download/archive/4.7.2-stable/, https://www.blender.org/releases/4-5/, https://www.python.org/downloads/release/python-31410/.

## Windows verification (PowerShell, repository root)

Install tools and set PATH, or set `$Godot` and `$Blender` to their absolute executable paths. Install pytest in an isolated development environment. Do not commit that environment.

```powershell
git --version
python --version
$Godot = 'godot'
$Blender = 'blender'
& $Godot --version
& $Blender --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest==9.0.2
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/check_foundation.py
& $Godot --headless --path game --editor --import
if ($LASTEXITCODE -ne 0) { throw 'Godot import failed' }
& $Godot --headless --path game --quit-after 180 -- --smoke
if ($LASTEXITCODE -ne 0) { throw 'Godot smoke failed' }
& $Godot --path game
```

Require the exact `CODECITY_FOUNDATION_SMOKE_OK` log marker, exit zero and no script/import errors. The frame limit is a watchdog, not success. Interactive test: boot, confirm the development screen fits 720p and 1080p, Tab to Exit and activate by keyboard and mouse. Python ping tests exercise real subprocess I/O; Godot is not connected to the worker. No export preset is provided yet. Asset candidate scripts are described below.

## Project contracts

Read [AGENTS](AGENTS.md), both original [instructions](docs/CodeCity_Project_Instructions.txt) and [production prompts](docs/CodeCity_Production_Prompts.txt), [architecture](ARCHITECTURE.md), [roadmap](ROADMAP.md), [art standards](docs/ASSET_PIPELINE.md), [asset registry](ASSET_REGISTRY.md), [performance](PERFORMANCE.md), [source audit](THIRD_PARTY_NOTICES.md), [file map](FILEMAP.md), [history](HISTORY.md) and [QA plan](docs/QA.md).

## Publishing

Work on main with focused, tested changes. Do not force-push or commit generated builds, raw libraries, secrets or unapproved binary assets. Review LFS allowance before tracking approved large binaries.

## Free asset automation pilot

The pilot is a real CC0 Poly Haven painted wooden bench, not a character or finished street. From repository root run python tools/fetch_pilot_asset.py, then blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/render_pilot_asset.py. Outputs in ignored build/asset-pilot: bench.blend, bench.glb, preview.png, provenance.json and report.json. Powered by Poly Haven. Source downloads are size and hash checked. Art stays candidate-only until visual and engine inspection. Missing source or Blender is a hard failure. No paid API.

## GitHub Actions

[CodeCity verification and asset pilot](https://github.com/zaydattique/codecity/actions) uses standard public-repository Ubuntu runners, pinned action revisions, target Python, Godot archive SHA-256 and Blender official checksums. The two jobs run Python/engine smoke and the separate real asset pilot. If no push run appears, open Actions, select CodeCity verification and asset pilot, then Run workflow on main. Download foundation-logs and cc0-bench-pilot-not-approved from a successful run; inspect preview.png and report.json. Artifacts are not game-ready approvals. First workflow passed; details below.

## Verified hosted results and next candidate

Run 45585769664 succeeded on Linux with Python 3.14.10 (38 tests), Godot 4.7.2 import/boot and Blender 4.5.17 LTS export/render. The actual CC0 bench studio render was visually inspected; wood grain, edge wear and shading are coherent, appropriate for indoor furniture. 630 triangles; 1.165 x 0.497 x 0.889 m. Godot import of this exact mesh passed in run 45587661323; collision/interaction remain pending. See https://github.com/zaydattique/codecity/actions/runs/45585769664 . The new character-candidate job builds a rigged MPFB Adrian using the official CC0 system pack and pinned tool, then exports source, GLB and three real previews. Its first run is unverified; do not treat it as final hero art. Exactly two planned playable characters: Adrian and Maya. No real navigation UI or map implemented yet.

Character attempt 45587501836 failed during a duplicate Blender download (HTTP 403); installer now reused from bench job. Windows test fixture corrected after 43 passes and one ZIP path fixture failure; reruns pending.

## Revised production requirements

Read [master directive](docs/MASTER_PRODUCTION_DIRECTIVE.md), [Academy curriculum](docs/ACADEMY_CURRICULUM.md), [NPC intelligence](docs/NPC_INTELLIGENCE.md), [gameplay systems](docs/GAMEPLAY_SYSTEMS.md), [audio/VFX](docs/AUDIO_VFX.md), [controls](docs/CONTROLS.md) and [render review](docs/RENDER_REVIEW.md). Hosted Windows/Linux boot and 44 tests passed at 2a170e4. New mode/session and trusted Academy result contracts are development foundations, not playable modes. Student code execution remains disabled. Official system pack downloader supports both mirrors; alternatively pass a locally acquired official ZIP to build_character.py. Character build remains pending.

Local PowerShell (install pytest and pinned tools first): `powershell -ExecutionPolicy Bypass -File tools/verify_local.ps1 -Godot godot -Python python`. Optional `-AssetPilot` and `-Character adrian -SystemPack art/raw/system-assets.zip` require Blender and enabled pinned MPFB. Use a fresh build/local-verification directory for each run. Upstream isolation runs separately; no demo copied into game. Windows export remains unavailable until real slice is implemented.

Latest verified Windows run 45593768569: 65 Python tests, Godot boot, exact bench import. Foundation and licensed asset production now run independently. Select Adrian or Maya in the asset workflow's manual Run workflow action; generated front/side/rear/three-quarter/face previews remain candidates. No automatic approval.

Verified at 58f9591: Windows 65 tests, foundation and session markers passed; exact bench import passed. Upstream OpenCity/Truck Town passed headless smoke, three other candidates failed cleanup checks. Camera orbit math adapted from MIT OpenCity, not yet wired to an actual player controller.

Phase A: a pinned CC0 legacy system pack fallback is available through the character downloader; candidate output provenance records actual URL and SHA-256. A threaded resource loader has been added for future real loading UI. Independent sports coupe candidate workflow checks pinned CC0 GLB and renders exterior/cockpit. Neither character nor car outputs are claimed until actual workflow results are reviewed.

Actual candidate results: Adrian front/side rendered with GLB/source (run 45594030806 partial artifact 15011738854), 36,362 triangles and 53-joint skin, no clips. Needs art rework. Spectral coupe rendered (45594790740) but rejected for toy-like shape and 151,722 tris. No vehicle or character approved. Windows/Linux foundation and resource loader checks at 67bb99f passed. Default art run now builds Adrian and Maya separately with selected footwear. No whole-city generation.

Latest Phase A checkpoint: both adult rigs generated, street 69,111 triangles and coupe 59,454 triangles after optimization. Actual Godot import confirmed both frozen runtime characters at correct heights and 347 street mesh nodes. 70 tests and session/menu checks passed on hosted Windows/Linux. Real rendering was blocked from artifact upload by hosted audio initialization error; visual-only CI uses Dummy audio for next run. Final art, animation, car marks clearance, interactive play and Windows gameplay export remain open.

Phase A actual Godot visual review passed (45603398478), both frozen adult rigs and street. Candidate-only street controller/menu integration now implemented, CI pending. No playable final animation, car or Academy mission yet. Candidate asset package staged only in verification project; normal source checkout still boots profile selection without assets. No fake start.

Candidate Windows export is configured behind successful street motion and physics QA. If run completes, the CodeCity-Windows-Street-Test artifact contains EXE, PCK and license notices, not a finished game. The export gate checks native Windows physics and standalone headless boot; no interactive hardware or performance claim until separately tested.

### Local candidate street staging (offline after downloads)

Download the exact [character archive](https://github.com/zaydattique/codecity/actions/runs/45603398478/artifacts/15016622099), [street archive](https://github.com/zaydattique/codecity/actions/runs/45601941130/artifacts/15015299272) and [CC0 UAL1 motion GLB](https://raw.githubusercontent.com/webgl-games/opencity/ba9514cdd88ecc2d40ecad503a644449fc98e665/assets/characters/UAL1_Standard.glb). Keep copies outside git; hosted artifacts expire. With pinned Python/Godot and downloaded files:

```powershell
python -m tools.stage_street_candidate --characters phaseA_verified_engine.zip --street phaseA_optimized_v2.zip --motion UAL1_Standard.glb --out build/local-street
godot --headless --path build/local-street/game --editor --import
godot --headless --path build/local-street/game --script res://_qa/street_playtest.gd -- --motion
godot --path build/local-street/game
```
With matching Windows export templates installed and a fresh output folder, use `godot --headless --path build/local-street/game --export-release "Windows Candidate" <absolute-output-path>/CodeCity_Street_Test.exe`. Include PCK, engine license/COPYRIGHT and third-party notices. Local physical-input and performance verification are still required. These are development candidate builds only.

## First standalone Windows candidate

[Download Windows Street Test (latest verified candidate)](https://github.com/zaydattique/codecity/actions/runs/45622243827/artifacts/15023914487). Extract and keep EXE/PCK together. Create local temporary profile, choose Living World, select Adrian or Maya and open street physics test. Nine licensed clips, real collision, minimap/full map and pause. No installed development tools required. Hosted native Windows physics and standalone boot passed; manual user playtest, GPU metrics, art approval, vehicle, NPCs, missions, save and Academy execution are not complete. Artifacts expire; local staging instructions above preserve reproducibility. See exact run logs; do not describe as finished game.

## First driving-enabled Windows candidate

[Download Driving Test v2](https://github.com/zaydattique/codecity/actions/runs/45631491513/artifacts/15031685807). Extract, keep EXE and PCK together, choose Living World and either character; approach the parked coupe, press F, W/S drive/reverse, A/D steer, Space brake, L headlights, stop before F exit. Latest actual Linux/Windows street and vehicle tests plus standalone exported car/actor/suspension smoke passed. Candidate includes exact reviewed CC-BY derivative, not a final car or game. No seated driver mesh, final IK, NPCs, interior, missions, save or Academy execution. Hosted artifacts expire; retain candidate files outside git.

Academy demo checkpoint: 45664681340 passed Linux/Windows street, vehicle and actual Python lesson, including standalone bundled CPython. A separate public v0.2.0 Academy prerelease workflow is configured; verify release before using the link. Six new NPC candidates are being built separately and are not in that package.

## Current public Academy demo

[Download CodeCity Academy Demo v0.2.0](https://github.com/zaydattique/codecity/releases/download/v0.2.0-academy-demo/CodeCity_Academy_Demo_v0.2.0.zip). Public prerelease published successfully in 45666920642 from the previously verified Windows build 45664681340. Extract all files and start CodeCity_Academy_Demo.exe. Includes bundled CPython and the physical lighting mission, revised camera, settings and driving. Hybrid GDScript/Python, not a pure Python game. Six-NPC work is not in this release.

### Upcoming demo practice extension (unverified source branch)
The review branch adds north-lamp variables and south-lamp conditional exercises to the original physical lighting mission, with starter code and hints. These are not in public v0.2.0. The original mission is still the only profile-level completion; practice is session-local. Hosted and manual Windows verification required before a new release.
