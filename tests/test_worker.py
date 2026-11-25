import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai.worker import MAX_FRAME, handle

ROOT = Path(__file__).resolve().parents[1]
PING = b'{"version":1,"id":"boot.1","op":"ping"}\n'


def test_ping():
    assert handle(PING) == {"version": 1, "id": "boot.1", "op": "pong", "capabilities": ["ping"]}


@pytest.mark.parametrize("payload", [b'{', b'\xff', b'{"x":NaN}', b'{"id":1,"id":2}', b'['*2000])
def test_invalid_json(payload):
    assert handle(payload)["error"] == "invalid_json"


@pytest.mark.parametrize("payload", [b'[]', b'{}', b'{"version":true,"id":"x","op":"ping"}', b'{"version":2,"id":"x","op":"ping"}', b'{"version":1,"id":"bad id","op":"ping"}', b'{"version":1,"id":"x","op":"ping","extra":0}'])
def test_invalid_schema(payload):
    assert handle(payload)["error"] == "invalid_schema"


def test_unknown_operation():
    assert handle(PING.replace(b'ping', b'decide'))["error"] == "unsupported_operation"


def test_oversize():
    assert handle(b'x'*(MAX_FRAME+1))["error"] == "frame_too_large"


def test_process_roundtrip():
    result = subprocess.run([sys.executable, str(ROOT/'ai/worker.py')], input=PING+b'bad\n'+PING,
                            capture_output=True, timeout=5, check=True)
    first, second, third = map(json.loads, result.stdout.splitlines())
    assert first == third and first['op'] == 'pong'
    assert second['error'] == 'invalid_json' and not result.stderr


def test_process_rejects_partial_and_oversize():
    for data in (PING.rstrip(b'\n'), b'x'*(MAX_FRAME+1)+b'\n'):
        result = subprocess.run([sys.executable, str(ROOT/'ai/worker.py')], input=data,
                                capture_output=True, timeout=5)
        assert result.returncode == 2
        assert json.loads(result.stdout)['error'] == 'invalid_frame'
