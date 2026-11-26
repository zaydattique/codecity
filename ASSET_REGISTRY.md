# BloomLogic | Asset registry

## Current shipped asset set
Release 1.0.1 uses the verified Phase 3 runtime art with PNG material integrity checks. Art is suitable for the implemented educational experience, not a photorealism certification. Source and build artifacts are retained separately from tracked code.

| Asset | Source / license | Current status |
|---|---|---|
| Soil diffuse, normal, roughness | [Poly Haven dirt_floor](https://polyhaven.com/a/dirt_floor), CC0 | Integrated; native normal/gloss PNG optional |
| Potted plant | [Poly Haven potted_plant_01](https://polyhaven.com/a/potted_plant_01), CC0 | Integrated, source provenance bundled |
| Clay pot | [Poly Haven planter_pot_clay](https://polyhaven.com/a/planter_pot_clay), CC0 | Integrated, source provenance bundled |
| Teacher Dua | Prior MPFB CC0 graphical human rig, original Blender gesture | Integrated, not a likeness of real Dua |
| Seed, roots, stem, leaves, rhizobox, bench, greenhouse frame, irrigation, sensor | Original Blender geometry | Integrated |
| Fan housing and rotor | Original Blender geometry | Integrated |
| Narration | eSpeak NG synthesized WAV | Integrated, synthetic voice |
| Irrigation sound | Original synthesized waveform | Integrated |

Powered by Poly Haven. Exact source licenses and per-file digests remain in provenance files and THIRD_PARTY_NOTICES.md.

## Pinned evidence
- Prior teacher source GLB SHA-256: f88a7cd9ea11340f362b5e0ee71e31054b425b72db5ba0e884fdf9fc77d9e687 (run 45666586177). Source license CC0-1.0. Initial derivative from run 45699394455: d33a6d85d9fac191440ae24dbe706bc82817edde6960e9419f1b5c8bf43cb4dd; historical derivative, not the current rig digest.
- Soil source verified in run 45699394455: diffuse 6c2e7f1c5eab8239fec561f255c607d0e3a86046925ba3a8b9340805efc1ab62; normal 9481dc2cee97b240ca10dc1cd60fec834a85e455aaa7d2a584396ea10210c2c0; rough 093166ffda063b8fcf04ec645e1e12c24811f614468ba378437a3535c3c53f57.
- Licensed props artifact 15061584027 from 45699394380. Plant glTF digest 23b30294407684b02f14800d6685bd8938da5d2111e17753ac8dd3c37d8c88a0; clay pot f2989068dcff9737c9f3d49d435b70e36d553822ac87134daac055ae9706af1e.
- Optimized geometry 15094869197 and editable Blender source 15095540806 (45773845506). Corrected native review 15095271581 and runtime bundle 15095426144 (45774097576).
- Release 1.0.1 runtime artifact 15102823192 and release artifact 15102988213 (45792172356). Current exact asset digests in packaged release-manifest.json and material-integrity.json. PNG normal derived from verified JPEG; gloss derived from roughness. No runtime JPEG fallback for optional material maps.

## Known quality gaps
Discrete growth samples, simplified leaf stress, opaque daylight glazing, synthetic narration and no facial lip synchronization. No calibrated botany or fluid dynamics. Other thirteen exhibits have no authored runtime assets yet. Historical candidates and rejected renders remain in Git history, not current approval. Before new acquisition record exact asset license, source URL/version, checksum, geometry/material counts, source files, runtime import, actual render and performance evidence.
