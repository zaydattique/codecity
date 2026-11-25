"""Fail-closed source intake. This validates provenance, not visual quality."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'art' / 'intake.json'
REQUIRED = {
    'character.adrian_cole.v001': {'base_mesh', 'skin', 'hair', 'clothing', 'motion'},
    'environment.slice_street.v001': {'geometry', 'materials'},
}
ALLOWED = {'CC0-1.0', 'CC-BY-4.0', 'original'}


def validate(root: Path, manifest: Path, asset_ids=None):
    """Validate local licensed inputs, never generate or approve geometry."""
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'assets'} or type(data['version']) is not int or data['version'] != 1 or not isinstance(data['assets'], dict):
        raise ValueError('invalid manifest schema')
    unknown = set(data['assets']) - set(REQUIRED)
    if unknown:
        raise ValueError(f'unknown asset IDs: {sorted(unknown)}')
    selected = set(asset_ids) if asset_ids is not None else set(REQUIRED)
    if not selected or not selected <= set(REQUIRED):
        raise ValueError('unknown or empty asset selection')
    raw = (root / 'art' / 'raw').resolve()
    for asset_id in sorted(selected):
        records = data['assets'].get(asset_id)
        if not isinstance(records, list) or not records or len(records) > 64:
            raise ValueError(f'{asset_id}: missing or excessive source records')
        roles = set()
        paths = set()
        for record in records:
            keys = {'role', 'path', 'sha256', 'license', 'author', 'source', 'evidence'}
            if not isinstance(record, dict) or set(record) != keys or any(not isinstance(v, str) or not v.strip() for v in record.values()):
                raise ValueError(f'{asset_id}: invalid source record')
            if record['role'] not in REQUIRED[asset_id] or record['license'] not in ALLOWED:
                raise ValueError(f'{asset_id}: unsupported role or license')
            if not re.fullmatch(r'[0-9a-f]{64}', record['sha256']):
                raise ValueError(f'{asset_id}: invalid SHA-256')
            for field in ('path', 'evidence'):
                relative = Path(record[field])
                if relative.is_absolute() or '..' in relative.parts or '\\' in record[field] or ':' in record[field]:
                    raise ValueError(f'{asset_id}: unsafe {field}')
                resolved = (root / relative).resolve()
                if not resolved.is_relative_to(raw) or not resolved.is_file() or resolved.stat().st_size == 0:
                    raise ValueError(f'{asset_id}: missing or unsafe {field}: {relative}')
            path = (root / record['path']).resolve()
            if path in paths:
                raise ValueError(f'{asset_id}: duplicate source path')
            paths.add(path)
            roles.add(record['role'])
            with path.open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != record['sha256']:
                    raise ValueError(f'{asset_id}: source hash mismatch')
        if roles != REQUIRED[asset_id]:
            raise ValueError(f'{asset_id}: missing roles {sorted(REQUIRED[asset_id] - roles)}')
    return sorted(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true')
    group.add_argument('--id', choices=sorted(REQUIRED))
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    args = parser.parse_args()
    try:
        result = validate(ROOT, args.manifest, None if args.all else [args.id])
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f'Asset intake blocked: {exc}\n')
    print('Provenance preflight only (not art approval): ' + ', '.join(result))


if __name__ == '__main__':
    main()
