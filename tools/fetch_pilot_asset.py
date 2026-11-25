"""Fetch one reviewed CC0 model; never publish automatically."""
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, unquote
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler

ASSET = 'painted_wooden_bench'
BASE = Path('build/asset-pilot')
LIMIT = 64 * 1024 * 1024
HOSTS = {'api.polyhaven.com', 'dl.polyhaven.org', 'cdn.polyhaven.com', 'polyhaven.com'}


def safe_url(url):
    u = urlsplit(url)
    if u.scheme != 'https' or u.hostname not in HOSTS or u.username or u.password or u.port not in (None, 443):
        raise ValueError('Unapproved download URL')
    return url


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, code, msg, headers, safe_url(newurl))


def get(url, cap):
    request = Request(safe_url(url), headers={'User-Agent': 'CodeCityAssetPipeline/1.0 (github.com/zaydattique/codecity)'})
    with build_opener(SafeRedirect()).open(request, timeout=30) as response:
        data = response.read(cap + 1)
    if len(data) > cap:
        raise ValueError('Download exceeds limit')
    return data


def safe_path(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or any(part == '..' for part in p.parts) or '\\' in name or ':' in name or not re.fullmatch(r'[A-Za-z0-9_./-]+', name) or str(p) == '.':
        raise ValueError('Unsafe relative asset path')
    return p


def plan(meta):
    entry = meta['gltf']['1k']['gltf']
    main = safe_path(unquote(urlsplit(entry['url']).path).rsplit('/', 1)[-1])
    if main.suffix != '.gltf':
        raise ValueError('Expected glTF source')
    files = [(main, entry)] + [(safe_path(name), record) for name, record in entry.get('include', {}).items()]
    if len(files) > 32 or len({str(p).lower() for p, _ in files}) != len(files):
        raise ValueError('Excessive or duplicate files')
    total = 0
    for _, record in files:
        safe_url(record['url'])
        size = record['size']
        if type(size) is not int or not 0 < size <= LIMIT or not re.fullmatch(r'[0-9a-fA-F]{32}', record['md5']):
            raise ValueError('Invalid size or checksum')
        total += size
    if total > LIMIT:
        raise ValueError('Excessive total size')
    return files


def verify(data, record):
    if len(data) != record['size'] or hashlib.md5(data, usedforsecurity=False).hexdigest() != record['md5'].lower():
        raise ValueError('Source integrity mismatch')
    return hashlib.sha256(data).hexdigest()


def check_gltf(data, files):
    doc = json.loads(data)
    allowed = {str(p) for p, _ in files}
    if doc['asset']['version'] != '2.0' or not doc.get('meshes'):
        raise ValueError('Expected mesh-bearing glTF 2.0')
    for obj in doc.get('buffers', []) + doc.get('images', []):
        if 'uri' in obj and str(safe_path(unquote(obj['uri']))) not in allowed:
            raise ValueError('Unlisted glTF dependency')


def main():
    if BASE.exists():
        raise FileExistsError('Use a clean build/asset-pilot directory')
    meta = json.loads(get(f'https://api.polyhaven.com/files/{ASSET}', 2 * 1024 * 1024))
    files = plan(meta)
    source = BASE / 'source'
    source.mkdir(parents=True)
    hashes = {}
    for path, record in files:
        data = get(record['url'], record['size'])
        hashes[str(path)] = verify(data, record)
        target = source / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    main_file = files[0][0]
    check_gltf((source / main_file).read_bytes(), files)
    (BASE / 'provenance.json').write_text(json.dumps({'asset': ASSET, 'author': 'Kirill Sannikov', 'license': 'CC0-1.0', 'source': f'https://polyhaven.com/a/{ASSET}', 'license_url': 'https://polyhaven.com/license', 'credit': 'Powered by Poly Haven', 'entry': str(main_file), 'sha256': hashes}, indent=2), encoding='utf-8')
    print('Licensed source downloaded; visual approval pending. Powered by Poly Haven.')


if __name__ == '__main__':
    main()
