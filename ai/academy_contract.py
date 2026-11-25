"""Trusted result boundary for Academy mission 01.

This module NEVER executes student code. A separate, security-reviewed sandbox
broker must establish execution identity, success and quotas before calling it.
The game must independently validate the returned command and live terminal state.
"""
from dataclasses import dataclass
import re

MAX_STDOUT = 1024
MAX_DISPLAY = 160
_TOKEN = re.compile(r"[A-Za-z0-9_-]{16,64}\Z")


@dataclass(frozen=True)
class TerminalSession:
    mode: str
    mission_id: str
    target_id: str
    run_id: str
    world_revision: int


def display_command(session: TerminalSession, result: dict) -> dict:
    """Translate one broker-authenticated, successful execution into an intent.

    Exact schema; no arbitrary commands, filesystem paths or code strings.
    Only the fixed control-room display is supported at this milestone.
    """
    if (session.mode != "academy" or session.mission_id != "control_room"
            or session.target_id != "harbor.control_room.display"
            or not isinstance(session.run_id, str)
            or not _TOKEN.fullmatch(session.run_id)
            or type(session.world_revision) is not int or session.world_revision < 0):
        raise ValueError("inactive or invalid terminal session")
    if not isinstance(result, dict) or set(result) != {
        "version", "run_id", "world_revision", "status", "stdout"
    }:
        raise ValueError("invalid broker result schema")
    if (type(result["version"]) is not int or result["version"] != 1
            or result["run_id"] != session.run_id
            or type(result["world_revision"]) is not int
            or result["world_revision"] != session.world_revision
            or result["status"] != "success"):
        raise ValueError("failed, stale or mismatched execution")
    stdout = result["stdout"]
    if not isinstance(stdout, str):
        raise ValueError("stdout must be text")
    try:
        if len(stdout.encode("utf-8")) > MAX_STDOUT:
            raise ValueError("stdout limit exceeded")
    except UnicodeEncodeError as exc:
        raise ValueError("invalid text") from exc
    text = stdout.rstrip("\n")
    if not text.strip() or len(text) > MAX_DISPLAY or any(not c.isprintable() and c != "\n" for c in text):
        raise ValueError("invalid display text")
    return {
        "version": 1, "run_id": session.run_id,
        "world_revision": session.world_revision,
        "op": "set_display_text", "target_id": session.target_id, "text": text
    }
