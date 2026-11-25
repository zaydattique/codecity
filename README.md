# CodeCity | Living Python Encyclopedia
A Python-first standalone interactive 3D learning application. No missions or games. First lesson: greenhouse conditionals. This branch begins the reset; the simulation/control core is implemented, art and desktop runtime are not yet complete.

Run core tests: `python -m unittest discover -s tests -v`. Python 3.13 is the baseline; Panda3D 1.10.16 candidate renderer, Blender 4.5 LTS authoring. See AGENTS.md, ROADMAP.md, ASSET_REGISTRY.md, THIRD_PARTY_NOTICES.md. Previous open-world source remains recoverable in Git history, not the active tree. No Windows demo is claimed.

Core verification: run 45693350645 passed Ubuntu and Windows unittest jobs. Art pipeline: `python tools/fetch_greenhouse_sources.py` and `blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/build_greenhouse_art.py`. Separate hosted jobs produce actual source and four review frames if successful. These are candidates, not the interactive demo.
