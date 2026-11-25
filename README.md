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
