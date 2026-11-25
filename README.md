# CodeCity: Living World

Original, non-educational, story-driven open-world Windows game. The player experiences autonomous characters through behavior, not through an AI dashboard. GTA V and VI are aspirations for visual craft and reactive behavior, not assets, source or claims of achieved quality.

## Status: Foundation and asset preflight; runtime gates open

Public main is owner-approved. Development boot scene and standalone Python ping probe only; no gameplay assets or executable yet. Local Phase 01/02 tests passed, engine execution remains pending.

## Toolchain baseline

Godot 4.7.2 stable (standard, not .NET); matching Windows export templates; Blender 4.5.17 LTS; CPython 3.14.10 x64; pytest for development. The local tests use Python 3.13.5; exact target runtime compatibility is unverified. Pin any additional packages and record hashes after a real install. Use official downloads: https://godotengine.org/download/archive/4.7.2-stable/, https://www.blender.org/releases/4-5/, https://www.python.org/downloads/release/python-31410/.

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

Require the exact `CODECITY_FOUNDATION_SMOKE_OK` log marker, exit zero and no script/import errors. The frame limit is a watchdog, not success. Interactive test: boot, confirm the development screen fits 720p and 1080p, Tab to Exit and activate by keyboard and mouse. Python ping tests exercise real subprocess I/O; Godot is not connected to the worker. No export preset is provided yet. No asset build scripts are claimed to exist.

## Project contracts

Read [AGENTS](AGENTS.md), both original [instructions](docs/CodeCity_Project_Instructions.txt) and [production prompts](docs/CodeCity_Production_Prompts.txt), [architecture](ARCHITECTURE.md), [roadmap](ROADMAP.md), [art standards](docs/ASSET_PIPELINE.md), [asset registry](ASSET_REGISTRY.md), [performance](PERFORMANCE.md), [source audit](THIRD_PARTY_NOTICES.md), [file map](FILEMAP.md), [history](HISTORY.md) and [QA plan](docs/QA.md).

## Publishing

Work on main with focused, tested changes. Do not force-push or commit generated builds, raw libraries, secrets or unapproved binary assets. Review LFS allowance before tracking approved large binaries.

## Free asset automation pilot

The pilot is a real CC0 Poly Haven painted wooden bench, not a character or finished street. From repository root run python tools/fetch_pilot_asset.py, then blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/render_pilot_asset.py. Outputs in ignored build/asset-pilot: bench.blend, bench.glb, preview.png, provenance.json and report.json. Powered by Poly Haven. Source downloads are size and hash checked. Art stays candidate-only until visual and engine inspection. Missing source or Blender is a hard failure. No paid API.

## GitHub Actions

[CodeCity verification and asset pilot](https://github.com/zaydattique/codecity/actions) uses standard public-repository Ubuntu runners, pinned action revisions, target Python, Godot archive SHA-256 and Blender official checksums. The two jobs run Python/engine smoke and the separate real asset pilot. If no push run appears, open Actions, select CodeCity verification and asset pilot, then Run workflow on main. Download foundation-logs and cc0-bench-pilot-not-approved from a successful run; inspect preview.png and report.json. Artifacts are not game-ready approvals. Initial API check returned zero runs; workflow execution remains unverified.
