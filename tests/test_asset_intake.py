import hashlib
import json
from pathlib import Path

import pytest

from tools.validate_assets import REQUIRED, validate


def fixture(tmp_path):
    raw = tmp_path / 'art' / 'raw'
    raw.mkdir(parents=True)
    evidence = raw / 'notice.txt'
    evidence.write_text('Synthetic test fixture only')
    assets = {}
    for aid, roles in REQUIRED.items():
        records = []
        for role in sorted(roles):
            path = raw / (aid + '.' + role)
            path.write_bytes(b'synthetic fixture, not an asset')
            records.append(dict(role=role, path=path.relative_to(tmp_path).as_posix(),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(), license='original',
                author='test', source='test fixture', evidence=evidence.relative_to(tmp_path).as_posix()))
        assets[aid] = records
    return {'version': 1, 'assets': assets}


def run(tmp_path, data):
    manifest = tmp_path / 'intake.json'
    manifest.write_text(json.dumps(data))
    return validate(tmp_path, manifest)


def test_complete(tmp_path):
    assert run(tmp_path, fixture(tmp_path)) == sorted(REQUIRED)


@pytest.mark.parametrize('fault', ['hash', 'license', 'traversal', 'missing', 'duplicate', 'role', 'evidence', 'symlink', 'version'])
def test_reject(tmp_path, fault):
    data = fixture(tmp_path)
    records = data['assets']['character.adrian_cole.v001']
    first = records[0]
    if fault == 'hash': first['sha256'] = '0' * 64
    elif fault == 'license': first['license'] = 'CC-BY-NC-SA-4.0'
    elif fault == 'traversal': first['path'] = '../outside'
    elif fault == 'missing': (tmp_path / first['path']).unlink()
    elif fault == 'duplicate': records.append(first.copy())
    elif fault == 'role': records.pop()
    elif fault == 'evidence': first['evidence'] = 'art/raw/absent.txt'
    elif fault == 'version': data['version'] = True
    elif fault == 'symlink':
        outside = tmp_path / 'outside'
        outside.write_bytes((tmp_path / first['path']).read_bytes())
        (tmp_path / first['path']).unlink()
        (tmp_path / first['path']).symlink_to(outside)
    with pytest.raises(ValueError):
        run(tmp_path, data)


def test_empty_manifest(tmp_path):
    with pytest.raises(ValueError):
        run(tmp_path, {'version': 1, 'assets': {}})
