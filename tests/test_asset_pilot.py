import hashlib
import pytest
from tools.fetch_pilot_asset import plan, verify, safe_path, safe_url, check_gltf

def metadata():
    body = b'fixture'
    record = {'url': 'https://dl.polyhaven.org/bench.gltf', 'size': len(body), 'md5': hashlib.md5(body, usedforsecurity=False).hexdigest()}
    return {'gltf': {'1k': {'gltf': dict(record, include={'textures/test.png': record})}}}


def test_plan():
    assert [str(p) for p, _ in plan(metadata())] == ['bench.gltf', 'textures/test.png']


@pytest.mark.parametrize('name', ['../x', '/x', 'C:/x', 'a\\b', '.'])
def test_paths(name):
    with pytest.raises(ValueError): safe_path(name)


@pytest.mark.parametrize('url', ['http://dl.polyhaven.org/x', 'https://evil.example/x', 'https://dl.polyhaven.org@evil.example/x'])
def test_hosts(url):
    with pytest.raises(ValueError): safe_url(url)


def test_integrity():
    record = plan(metadata())[0][1]
    assert verify(b'fixture', record) == hashlib.sha256(b'fixture').hexdigest()
    with pytest.raises(ValueError): verify(b'changed', record)


def test_dependency():
    files = plan(metadata())
    check_gltf(b'{"asset":{"version":"2.0"},"meshes":[{}],"images":[{"uri":"textures/test.png"}]}', files)
    with pytest.raises(ValueError):
        check_gltf(b'{"asset":{"version":"2.0"},"meshes":[{}],"images":[{"uri":"outside.png"}]}', files)
