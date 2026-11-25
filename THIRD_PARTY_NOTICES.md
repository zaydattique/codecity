# Third-party notices and source audit | 2026-11-25

One small MIT camera geometry adaptation is now in source (see actual integration ledger below); no upstream demo gameplay scene integrated. One CC0 bench has been downloaded, rendered and imported in isolated verification; MPFB authoring tool is checked out by CI. This is a source evaluation ledger, not a redistribution clearance. Each GitHub revision was resolved via GitHub metadata and its relevant text files inspected; no upstream checkout or execution possible in staging (DNS resolution failed). All runtime compatibility and performance fields are **not tested**. Per-asset review remains mandatory.

| Candidate / pinned commit | Evidence and license | Compatibility / evaluation decision |
|---|---|---|
| [OpenCity](https://github.com/webgl-games/opencity/tree/ba9514cdd88ecc2d40ecad503a644449fc98e665) | README.md, LICENSE (MIT, Charan Raj Kandula), CREDITS.md, project.godot. Quaternius UAL1_Standard.glb declared CC0; other city/vehicle primitives MIT. | Godot 4.7 Forward+, standard GDScript. Consider scripts/player.gd, scripts/game.gd, traffic lane/entry and exit patterns; reject primitive assets and demo HUD. Isolate walk/drive/traffic, compare costs. |
| [GDQuest TPS](https://github.com/gdquest-demos/godot-4-3d-third-person-controller/tree/b3bd6e81084f568be8aa44a69a0c2b1e52e806b3) | LICENSE MIT (GDQuest) source; CC BY-NC-SA 4.0 models/textures. project.godot read, README requested names returned 404; public listing inspected. | 4.7 Forward+. Evaluate camera/movement code and AnimationTree; do not import NC art or scenes depending on it into shipping game. Keep source copyright. |
| [Godot demos](https://github.com/godotengine/godot-demo-projects/tree/6ad6167e0577fe3622c18546138f456b107ce93c) | README.md, LICENSE.md MIT Godot contributors and founders, 3d/truck_town/README.md and project.godot inspected. Demo has credited ambient audio requiring individual terms. | Release 4.7-6ad6167; branch `4.7` lookup failed, pin release commit instead. Truck Town uses VehicleBody3D and joints; compare handling, navigation and physics examples; verify each asset separately. |
| [Vehicle](https://github.com/ogeeice/Vehicle/tree/a3e0221eed2dd6daa88af7e7165668c3c356b8ac) | LICENSE CC0, project.godot config_version=4 and scancode fields; README paths returned 404. | Legacy Godot 3 project format despite listing referring to VehicleBody3D. Reject direct import; compare only concepts if needed. |
| [MPFB2](https://github.com/makehumancommunity/mpfb2/tree/650c5c53bd6989a8ac264f31fa1d11d4a0c7bd8a) | README.md, LICENSE.md GPLv3 program logic, LICENSE.ASSETS.md CC0 core graphics. | Blender >=4.2 declared; evaluate 4.5.17. Use as authoring tool, not copied runtime logic. Check skin/hair/clothing add-on licenses and output conditions. |
| [Easy Vehicle Physics](https://github.com/DAShoe1/Godot-Easy-Vehicle-Physics/tree/c392257f54f6ca537dc10bc5badad0c060f18982) | README.md, LICENSE MIT David Shoemaker, Dechode, Baron Wittman; project.godot 4.3. | Godot 4.2+ declared. Raycast rigidbody vehicle, ABS, traction and assists; recommends >=120Hz. Evaluate 60/120Hz costs and handling; do not globally raise ticks without profiling. Preserve all notices; demo art unapproved. |
| [Road Generator](https://github.com/TheDuckCow/godot-road-generator/tree/7cbefde04e57a84499c5d8ba636c9cb4fd7d22c0) | README.md, LICENSE MIT Moo-Ack! Productions, project.godot 4.4, GUT plugin and road-generator enabled. | Declares 4.4+, incomplete features. Evaluate editor road generation/lane graph, not runtime dependency until needed; inspect GUT and materials separately. |

Additional source references: [Godot NavigationAgent3D](https://docs.godotengine.org/en/stable/classes/class_navigationagent3d.html) and [NavigationServer](https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_using_navigationservers.html): use native navigation first; avoidance can be expensive. [VehicleBody3D](https://docs.godotengine.org/en/stable/classes/class_vehiclebody3d.html) explicitly notes realism limitations. [Kenney City Kit Roads](https://kenney.nl/assets/city-kit-roads) CC0, candidate for dimensions/layout study only, not approved final art. [Godot animation toolkit](https://github.com/michaltomczykowski/godot-ai-animation-toolkit) MIT claimed by listing, unpinned/unreviewed; defer until AnimationTree baseline; no procedural motion accepted as final without review. [MPFB docs](https://static.makehumancommunity.org/mpfb/docs.html) installation/rig/export guides. [Poly Haven](https://polyhaven.com/license) and [ambientCG](https://docs.ambientcg.com/license/) CC0 assets; check item source and usage terms; no assets selected/downloaded. [Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) royalty-free use in games, not blanket clearance to republish raw source clips; review terms before sharing sources or packaging. No login bypass or automation. Preserve full licenses and attribution for selected files, including transitive dependencies; no commercial restricted art, leaked or ripped assets. Godot engine and export templates require their MIT and third-party notices; Python distribution requires PSF and included notices; Blender/MPFB only authoring tools. Verify exact packaged files later.

## Isolation commands (PowerShell, not executed)

Run from repo root with Git and pinned Godot installed; clones stay ignored and outside game/. Audit specific files and asset notices at pins before copying any code. Clone/check out candidates individually, run Godot import then scene for each actual project path, capture exact engine/version and logs, compare frame/physics behavior. For MPFB use isolated Blender installation, install approved release or build from audited pin following upstream instructions; export one licensed human and inspect topology, scale, rig and GLB. Do not distribute add-on code with game. For restricted demo art, do not redistribute; assess source in isolation only as license permits.

```powershell
New-Item -ItemType Directory -Force references
$refs = @(
  @('webgl-games/opencity','ba9514cdd88ecc2d40ecad503a644449fc98e665','opencity'),
  @('gdquest-demos/godot-4-3d-third-person-controller','b3bd6e81084f568be8aa44a69a0c2b1e52e806b3','third-person'),
  @('godotengine/godot-demo-projects','6ad6167e0577fe3622c18546138f456b107ce93c','godot-demos'),
  @('ogeeice/Vehicle','a3e0221eed2dd6daa88af7e7165668c3c356b8ac','vehicle-legacy'),
  @('makehumancommunity/mpfb2','650c5c53bd6989a8ac264f31fa1d11d4a0c7bd8a','mpfb2'),
  @('DAShoe1/Godot-Easy-Vehicle-Physics','c392257f54f6ca537dc10bc5badad0c060f18982','easy-vehicle'),
  @('TheDuckCow/godot-road-generator','7cbefde04e57a84499c5d8ba636c9cb4fd7d22c0','road-generator')
)
foreach ($ref in $refs) {
  git clone "https://github.com/$($ref[0]).git" "references/$($ref[2])"
  if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
  git -C "references/$($ref[2])" checkout --detach $ref[1]
  if ($LASTEXITCODE -ne 0) { throw 'Pin checkout failed' }
}
foreach ($path in @('references/opencity','references/third-person','references/godot-demos/3d/truck_town','references/easy-vehicle','references/road-generator')) {
  godot --headless --path $path --editor --import
  if ($LASTEXITCODE -ne 0) { throw "Import failed: $path" }
  godot --path $path
}
```

Inspect logs manually for errors even when exit zero. Legacy Vehicle requires separate migration or matching Godot 3; do not use 4.7 migration on canonical reference. Record actual test results before approving any import. Account Git LFS storage/bandwidth unknown; no binary tracking configured.

## Asset automation pilot

Poly Haven painted_wooden_bench (Kirill Sannikov), CC0-1.0: https://polyhaven.com/a/painted_wooden_bench ; license https://polyhaven.com/license ; API terms https://github.com/Poly-Haven/Public-API/blob/master/ToS.md . The live API is used with a distinct CodeCity user-agent and visible Powered by Poly Haven credit. No API server code copied; no raw model yet included. Download, render and isolated Godot import verified; gameplay approval pending.

MPFB candidate tool uses exact source commit 650c5c53bd6989a8ac264f31fa1d11d4a0c7bd8a (2.0.18), Blender 4.2+ requirement, GPL-3.0-or-later authoring tool only; no program code packaged in game. Official makehuman_system_assets_cc0.zip catalog at https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html and pinned catalog https://github.com/makehumancommunity/makehuman-static-website/blob/c80cd4e19a723cb0cbfa947db2f9e490efa06be8/content/Assets/AssetPacks/makehuman_system_assets.md lists selected assets under CC0. Official pack https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip (hash captured on execution; source pack not vendored). Upstream license distinguishes graphical output from program logic. Verify archive provenance and selected file-level notices before approving redistribution.

Official secondary system pack mirror: https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip . Both URLs are listed in the pinned official catalog/config. Download hash records provenance; no upstream published pack hash has been established. OpenCity/GDQuest/Easy Vehicle/Road Generator still research-only until isolated tests complete.

Upstream isolation workflow now checks out exact five audited compatible Godot references into separate runners and performs bounded import/startup under pinned Godot. Only logs are uploaded, no demo assets or code redistributed. Runtime handling and module extraction still require tests; check workflow conclusions before claiming compatibility.

## Actual isolation results, run 45593883936 (Godot 4.7.2 Linux)

- OpenCity (job 139134782433): bounded headless import/startup passed.
- Godot Truck Town (job 139134782530): bounded headless import/startup passed.
- GDQuest (job 139134781995): failed strict exit-resource check (one resource still in use).
- Road Generator (job 139134782523): failed strict exit check (dummy renderer allocation/resource leaks).
- Easy Vehicle Physics (job 139134782565): failed strict exit-resource check (one resource still in use).

These are headless smoke results, not handling, navigation, visual or performance approvals. Do not mask resource errors; isolate minimal source and investigate root causes before integration. No demo art included.

### First code reuse: OpenCity camera math

Adapted the spherical offset formula from scripts/follow_camera.gd at ba9514cdd88ecc2d40ecad503a644449fc98e665 into game/core/camera_orbit.gd. Removed all demo-specific group/vehicle/input dependencies, added finite-value validation and replaced linear smoothing with frame-rate-independent exponential smoothing. Regression verifies axis, length, invalid distance and smoothing composition in Godot. It is a reusable geometry module, not yet a connected third-person controller; no character or vehicle behavior claimed. Upstream smoke passed; new module test pending.

MIT License

Copyright (c) 2026 Charan Raj Kandula

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Legacy system pack fallback: Makehuman-2/MH2_Asset_Repository_CCO, catalog pin bce7f85e476d70e3c6120a93145fb2037324060d, README declares original legacy unaltered CC0 assets, LICENSE CC0. Release legacy-mh_system_CC0.zip SHA-256 d38970b0a2a06dbcb2d3f55aa3d673c45bc88e7bd1f4afa0368a0782938d55bc. Candidate compatibility and provenance review still required. Spectral GT RS by JaronKBragg7337, CC0-1.0, pin 34499c501908818a2b08e589a7aecf963343cee7, GLB git blob f5b814848453a6c75a48f5047fdadaa7bdc78969, source license https://github.com/JaronKBragg7337/spectral-gt-rs/blob/34499c501908818a2b08e589a7aecf963343cee7/LICENSE . Source declares cockpit, separated geometry, four clips, +X front. No browser code copied. Import/render candidate only; no handling or fidelity approval.

Alternative car source research: https://github.com/KhronosGroup/glTF-Sample-Assets/tree/e124e8d8d7330a5372bc2b4d00d39a4a9d7997ea/Models/CarConcept ; model/textures CC-BY-4.0 Eric Chadwick, Darmstadt Graphics Group GmbH (2024); separate Khronos trademarks/logos require removal or permission. Source documents actual interior, separate door pivots and optimized wheels. Not acquired, no integration. Spectral GT RS source retained as rejected candidate only. Official CC0 shoes01 and shoes02 from pinned MakeHuman system catalog selected for next build.

Poly Haven CC0 street art inputs: https://polyhaven.com/a/asphalt_01 , https://polyhaven.com/a/concrete_pavement_02 , https://polyhaven.com/a/modular_urban_apartments_facade , https://polyhaven.com/a/street_lamp_01 ; existing bench reused. See source manifest captured at download. Powered by Poly Haven. The facade kit is not an assembled street, and raw source libraries are not committed.

Khronos CarConcept review workflow fetches only pinned GLB, checks Git blob, renders actual source. Model/textures attribution: Eric Chadwick / Darmstadt Graphics Group GmbH (2024), CC-BY-4.0, based on Unity Fan CC0 concept car. Separate trademark rights excluded; do not integrate marked asset or release candidate binary. Candidate-only render inspection, no browser code copied.
