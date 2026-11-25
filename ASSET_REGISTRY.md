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
