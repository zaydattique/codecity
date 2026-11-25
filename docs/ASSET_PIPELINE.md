# Professional 3D asset pipeline

## Direction and input gate

Original contemporary coastal city. Natural light, believable street dimensions, varied architecture, practical clothes, restrained weathering and ordinary people. No GTA likeness or extracted asset. Start Adrian and a representative street material/architecture segment; obtain review before six NPCs, car and expanded street. MPFB2 CC0 core base mesh is a starting point, not a final character; preserve individual source licenses. Work from licensed scans/materials, anatomy references and professional or captured motion. Missing input must fail build, never trigger a primitive substitute.

## Character pipeline

Use MPFB-compatible Blender LTS locally. Create bespoke proportions, asymmetric face, realistic hair cards, eyebrows/lashes, eyes, teeth, nails, skin detail, cloth seam and layered clothing. Sculpt and retopologize deformation loops at eyes, mouth, shoulders, elbows, knees and fingers; inspect non-manifold defects, UV distortion and weights. Use meter scale, apply object transforms before rigging, canonical rest pose, standard humanoid skeleton with fingers and optional facial morphs. Bind and normalize skin weights (target 4 influences per vertex); use corrective shapes for shoulders/hips; retarget licensed clips with BoneMap/SkeletonProfileHumanoid, test root motion and in-place conventions explicitly. Shared skeleton where suitable, distinct body/face/hair/clothes and gait. No duplicate nearby NPC identity.

Hero initial 40-70k rendered triangles, 4k face/body only if budget permits; 2k clothing atlas, hair cards and lower mip tiers. Nearby NPC 12-25k, mid 5-12k, distant 0.5-3k. Triangle counts include clothes/hair, not just body. LOD preserves silhouette and material slots; reduce bones and morphs at distance; sample gait and face after decimation. PBR albedo sRGB, normal/roughness/metallic data linear, glTF metallic-roughness channel mapping (G roughness, B metallic), no baked lighting in albedo; skin detail and wetness tested under neutral daylight, indoor and night light. Texture budgets are starting points, not art or GPU guarantees.

Animation: idle/walk/jog/sprint, turn, jump, crouch, stairs, sit, phone, door, vehicle enter/exit/steer and carry. Author or retarget motion; review feet, root drift, knee/elbow bends, finger grip, lip/eye shapes and transitions. Use AnimationTree blend spaces, upper body layers and IK only as necessary. Do not generate stick-figure cycles. Capture close-up and full-body turntable, wireframe, UV, extreme joint poses, animation loop and three lighting conditions.

## Street and vehicle

Street measured from realistic reference proportions, lane width 3.0-3.5m initial, continuous walkable sidewalk and curb, crossings, road grade, doorways, believable facade depth and variation, material trim sheets and modular props. Seamless road/nav/collision edges; author traffic graph separately; no facades advertised as interiors. Original coupe with independently pivoted wheels, doors, hood, trunk, steering and interior, lights, glass and tires. Validate wheelbase, cabin clearance, entry sockets and collision proxy. Hero 30-60k triangles; traffic 5-15k. Static exterior 5-20k typical small building. LODs, shared materials, instance repeated props, simplified convex moving colliders, static triangle collision only where justified.

## Build and publish contract

Stages: acquire -> record license/hash -> source in art/work -> sculpt/retopo/UV/bake -> rig/motion -> LOD/collision/socket -> export GLB -> Godot import review -> registry approval. Approved editable source may be tracked via selected LFS patterns only after quota check. Store previews externally or selected approved compact images. Avoid absolute paths and missing textures. Use GLB for runtime and .blend for editable handoff. Do not import .blend directly into the shipping project. Missing inputs fail; no substitute primitives. Build output deterministic names, stage then publish only after human visual review. Godot import settings are version-controlled, caches ignored. A validator cannot certify realism by itself.

Acceptance: no missing texture/import warnings, correct world scale/orientation, no visible z-fighting or broken normals/rig, close-up facial quality, natural motion, no gross clipping, appropriate triangle/texture budget, functional collisions and sockets, original identity and approved attribution. Record actual reviewer and screenshots, not a generic pass flag.

## Implemented intake preflight

Copy art/intake.example.json to art/intake.json and keep all source files and their license evidence inside art/raw/. Each record requires role, path, SHA-256 (lowercase hex), license (CC0-1.0, CC-BY-4.0 or original), author, source and evidence (local nonempty file). Adrian requires base_mesh, skin, hair, clothing and motion; street requires geometry and materials. Run python tools/validate_assets.py --all or --id character.adrian_cole.v001. Only source integrity and metadata are checked. A human must review the actual evidence, geometry and rights before import. Restricted/custom licenses, including Mixamo, require separate review and explicit extension of the policy. Never use synthetic fixtures as assets.
