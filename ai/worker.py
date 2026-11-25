"""Phase 01 transport probe. No NPC decisions are implemented in this phase."""
import json
import re
import sys

VERSION = 1
MAX_FRAME = 65536
ID = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")


def reject_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate key")
        obj[key] = value
    return obj


def handle(frame: bytes) -> dict:
    """Return a bounded response; never execute request data."""
    if len(frame) > MAX_FRAME:
        return {"version": VERSION, "id": None, "error": "frame_too_large"}
    try:
        req = json.loads(frame.decode("utf-8"), parse_constant=reject_constant,
                         object_pairs_hook=unique_keys)
    except (UnicodeError, ValueError, RecursionError):
        return {"version": VERSION, "id": None, "error": "invalid_json"}
    if not isinstance(req, dict):
        return {"version": VERSION, "id": None, "error": "invalid_schema"}
    rid = req.get("id")
    if not isinstance(rid, str) or not ID.fullmatch(rid):
        rid = None
    if (set(req) != {"version", "id", "op"} or rid is None
            or type(req.get("version")) is not int
            or req["version"] != VERSION or not isinstance(req.get("op"), str)):
        return {"version": VERSION, "id": rid, "error": "invalid_schema"}
    if req["op"] != "ping":
        return {"version": VERSION, "id": rid, "error": "unsupported_operation"}
    return {"version": VERSION, "id": rid, "op": "pong", "capabilities": ["ping"]}


def main() -> int:
    while True:
        line = sys.stdin.buffer.readline(MAX_FRAME + 1)
        if not line:
            return 0
        if len(line) > MAX_FRAME or not line.endswith(b"\n"):
            # Close on framing violation, so partial data cannot become a request.
            result = {"version": VERSION, "id": None, "error": "invalid_frame"}
            print(json.dumps(result, separators=(",", ":")), flush=True)
            return 2
        print(json.dumps(handle(line), separators=(",", ":")), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
