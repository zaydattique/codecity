# Third-party notices and source audit | 2026-11-25

No third-party code, assets, runtime or plugin integrated. This is a source evaluation ledger, not a redistribution clearance. Each GitHub revision was resolved via GitHub metadata and its relevant text files inspected; no upstream checkout or execution possible in staging (DNS resolution failed). All runtime compatibility and performance fields are **not tested**. Per-asset review remains mandatory.

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
