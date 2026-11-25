# Asset registry

No binary assets acquired, generated, approved or imported. Candidate source licenses are not asset approval. See THIRD_PARTY_NOTICES for source pins and docs/ASSET_PIPELINE for acceptance. Planned IDs, not files:

| ID | Description | State |
|---|---|---|
| character.adrian_cole.v001 | 27, 181 cm, original hero per P02 | Not started |
| vehicle.sports_coupe.v001 | original performance coupe P09 | Not started |
| environment.slice_street.v001 | one original detailed street P15/P22 | Not started |
| character.npc_01.v001 through npc_06 | six distinct adult citizens P07 | Not started |
| interior.apartment.v001 | functional first interior candidate P21 | Not started |

Each accepted item records asset ID, author/source URL, source revision/download date, exact license and evidence, SHA-256 of inputs and outputs, modifications, source `.blend`, exported `.glb`, import settings, texture sizes, triangle counts by LOD, skeleton/animation version, collision/socket requirements, preview paths, in-engine evidence, reviewer/date and status. Only approved IDs may enter final scenes. Third-party license terms tracked per clothing, hair, material, sound and animation, not just base character. Keep raw assets outside game/ and git; approve LFS quota and selected paths before binary tracking.

Phase 02 preflight implemented for Adrian and the representative street only. Both remain blocked: no licensed source inputs, no Blender renders or in-engine validation. No assets approved.

Pilot candidate: prop.painted_wooden_bench.v001; Kirill Sannikov; CC0-1.0; https://polyhaven.com/a/painted_wooden_bench; documented 1.2m width, 630 tris; selected 1K source; live metadata and binary checks pending. Powered by Poly Haven. Not integrated or approved. Record exact source/output SHA-256 after a successful run.

### Bench pilot verified

Run 45585769664 artifact 15009260029. Actual studio render inspected; coherent wood grain, wear and shading. Candidate for indoor furniture only. 630 tris; dimensions 1.16494, 0.49654, 0.88929 m. GLB SHA-256 d4fb79f8662d62fc8c720dd82c1c0ee874688e04963761fdd8439c93b441ad39; preview SHA-256 bafbd5f3094195f518a9c62eb9143424638ad2a42911e6a58a898695889df2bc. Godot import/collision/interaction not verified, no binary committed.

Adrian/Maya candidates use MPFB 2.0.18 and official CC0 system pack (base, targets, rig, skin, clothing, hair, eyes, brows, lashes, teeth and tongue); record actual pack/output hashes from report. Generic source clothes and hair are not approved final character designs. No motion or LOD assets yet.

Godot imported exact bench GLB successfully in run 45587661323, job 139113299318. Albedo texture present, 630 triangles, 1.164944 x 0.889291 x 0.496543 m (Godot Y-up). Visual and import candidate gates pass; gameplay collision/seating and final integration remain pending.

Revised directive: exactly two heroes, six independently acting NPCs in slice; later 24 civilian configurations are not separately authored meshes. One bench candidate remains the only visually reviewed/imported model. No approved gameplay assets. System pack download has two official mirrors; actual character outputs still pending.

Vehicle candidate: vehicle.spectral_coupe.v001, source https://github.com/JaronKBragg7337/spectral-gt-rs (CC0), pinned GLB, cockpit and wheels declared by upstream. Render pipeline written, actual mesh counts and render approval pending. Do not rename as finished CodeCity coupe; evaluate budget and appearance first.

## Actual candidate review
Adrian v001: artifact 15011738854; 36,362 triangles, 8 meshes, one skin/53 joints, 9 images, no animation. Front and side visual inspection complete; missing footwear, generic clothes, hair/skin realism insufficient. REWORK, no final approval. Maya not yet confirmed. Shoes01/02 selected from official CC0 catalog for the next candidate. Spectral coupe v001: artifact 15011893756, 151,722 triangles, 258 meshes, four animations; 5.207 x 2.526 x 1.68m. Exterior and cutaway inspected; toy-like and substantially over budget. REJECT, not game-integrated. Khronos CarConcept is a new research candidate only (CC-BY-4.0 model/textures, separate logo rights). No street assembled.

Street art candidates: asphalt_01 (Charlotte Baglioni/Dario Barresi), concrete_pavement_02, modular_urban_apartments_facade (James Ray Cock), street_lamp_01 (Josh Dean), painted_wooden_bench (Kirill Sannikov), all Poly Haven CC0. Fixed model/material acquisition, exact downloaded hashes, authored road surface and separately staged facade library. Output candidate only until actual renders reviewed. No assembled buildings or enterable interiors claimed.

Complete Adrian v001 artifact 15013111694 includes five actual views; 36,362 tris, 53 bones, 1.574 m height vs 1.81 m target, no clips. REWORK. Street surface v001 and 147-piece facade kit generated in 45595559815 artifact 15013880219, both visually inspected. No complete buildings at this checkpoint. New assembly script targets four closed exteriors using exact source .blend hashes; not accepted until rerender. No gameplay approvals.

Replacement vehicle research candidate: CarConcept pinned GLB c0f38c989a78cc4ba63253b5338705e0afb0142f. Actual review pipeline committed; no generated output or approval yet. Do not ship before removal/clearance of logos and passing visual, budget, physics and import gates.

Dual candidate run 45595560052: Adrian with footwear generated, Maya failed 1.3809m. Previous age values were incorrect child-to-young morphs per pinned MPFB. Both adult profile presets corrected to 0.5; reject prior age-morphed visual candidates as final. Rebuild pending.

Actual four exterior buildings assembled (artifact 15013172003): 347 mesh instances, 829,727 tris. Visually reviewed; REWORK for variation and budget. No enterable rooms, collision or navigation. Replacement CarConcept (artifact 15012938859): 97 meshes, 213,347 tris, 42 named cabin meshes, visual candidate, REWORK for triangle count and marks. No gameplay-approved assets. Optimization candidate workflow added, pending actual output.

Adult protagonists generated, artifact 15014252428: Adrian 35,154 tris, 1.81m, 53 bones, GLB c2c5c5425b03133f0dc995fb1c7d6cc3788b4df7d0dbfcac050658e1bb1503e1; Maya 38,588 tris, 1.69m, 53 bones, GLB fa575b54117955bb5095ed8fd7fbf91318f436160193456e8e69ce82960482ee. Both five-view renders inspected; generic clothes/hair and flat skin remain, no animations/LODs. Candidate-only. Optimized street 279,555 tris (budget failed); GLB 2a966c0acc2d8a251c7cc15f5ccb9dd634c4b12cad0f609173bf458a298a695c. Coupe 59,454 tris (budget passed), named emblem removed, baked logos and actual derivative cabin still pending. Neither approved. Exact candidate import/engine render workflow staged, pending run.

Revised optimization run 45601941130: street 69,111 tris (110k budget pass), coupe 59,454 tris (60k pass), visuals and derivative runtime remain pending. Actual character import first attempt found raw combined AABB mismatch (2.342m Adrian); skinned vertex check added, pending retest. No approval claimed.

Frozen runtime candidate GLBs passed Godot skin/height/material check in run 45603090341; Adrian 1.81m, Maya 1.69m, 53 bones each, street 347 mesh nodes. Optimized street GLB SHA256 cbd75043c055ea6b15275670c2dd540410559a5b47c585ab4f411a3eca3529f9, 69,111 tris. Rendering success marker present, workflow failed missing hosted ALSA audio; explicit visual-only dummy audio rerun pending. Source and runtime derivatives are candidates, not gameplay assets.

Motion candidate source Quaternius UAL1 Standard (CC0) pinned OpenCity copy; selected Idle, Walk, Jog_Fwd, Sprint, Jump. Only rotation channels, no source mannequin. Motion retarget and deformation review pending; no approved motion asset yet.
