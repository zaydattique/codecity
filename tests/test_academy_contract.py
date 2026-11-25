from dataclasses import replace
import pytest
from ai.academy_contract import TerminalSession, display_command

SESSION = TerminalSession("academy", "control_room", "harbor.control_room.display", "run_0123456789abcdef", 4)
RESULT = dict(version=1, run_id=SESSION.run_id, world_revision=4, status="success", stdout="Harbor online\n")


def test_display_intent():
    cmd = display_command(SESSION, RESULT)
    assert cmd == dict(version=1, run_id=SESSION.run_id, world_revision=4,
                       op="set_display_text", target_id=SESSION.target_id, text="Harbor online")


@pytest.mark.parametrize("patch", [
    {"version":True}, {"version":2}, {"run_id":"other"}, {"world_revision":3},
    {"world_revision":True}, {"status":"timeout"}, {"status":"error"},
    {"stdout":""}, {"stdout":" "}, {"stdout":"x"*161}, {"stdout":"é"*600},
    {"stdout":"x\x00y"}, {"stdout":42}, {"stdout":"\ud800"}, {"op":"arbitrary"}
])
def test_bad_results(patch):
    with pytest.raises(ValueError):
        display_command(SESSION, RESULT | patch)


@pytest.mark.parametrize("patch", [
    {"mode":"living_world"}, {"mission_id":"other"}, {"target_id":"anything"},
    {"run_id":"short"}, {"world_revision":-1}
])
def test_wrong_session(patch):
    with pytest.raises(ValueError):
        display_command(replace(SESSION, **patch), RESULT)
