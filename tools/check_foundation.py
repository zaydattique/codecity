"""Static checks. These do not replace Godot import or smoke execution."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'game'
DOCS = ['README.md','HISTORY.md','AGENTS.md','ARCHITECTURE.md','ROADMAP.md','ASSET_REGISTRY.md','PERFORMANCE.md','FILEMAP.md','THIRD_PARTY_NOTICES.md']


def check():
    for name in DOCS:
        if not (ROOT/name).is_file():
            raise ValueError(f'Missing {name}')
    for path in [GAME/'project.godot', *GAME.rglob('*.tscn')]:
        for ref in re.findall(r'res://[^"\s]+', path.read_text()):
            if not (GAME/ref[6:]).is_file():
                raise ValueError(f'{path}: missing {ref}')
    print('Static foundation references and required documentation: OK')


if __name__ == '__main__':
    check()
