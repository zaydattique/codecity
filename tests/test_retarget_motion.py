import math
import pytest
from tools.retarget_motion import Q, unit, mul, inv, transfer, canonical


def same(a,b):
    return abs(sum(x*y for x,y in zip(a,b)))==pytest.approx(1.0)


def test_bind_pose_unchanged():
    src=unit((0.1,.4,.3,.8))
    dst=unit((.2,-.3,.1,.9))
    assert same(transfer(src,src,dst,dst,src),dst)


def test_world_delta_is_preserved():
    src=unit((.2,.1,.4,.7)); dst=unit((.2,-.2,.5,.8))
    sglobal=unit((.3,-.4,.1,.7));dglobal=unit((.4,.2,-.2,.9))
    rotation=unit((0,.3,0,.9))
    animated=mul(src,rotation)
    result=transfer(src,sglobal,dst,dglobal,animated)
    world_s=mul(mul(sglobal,rotation),inv(sglobal))
    world_t=mul(mul(dglobal,mul(inv(dst),result)),inv(dglobal))
    assert same(unit(world_s),unit(world_t))


def test_invalid_and_aliases():
    with pytest.raises(ValueError):unit((0,0,0,0))
    assert canonical("Armature:upperarm_l")=="upperarm_l"
    assert canonical("LeftForeArm")=="lowerarm_l"


def test_arm_direction_correction():
    from tools.retarget_motion import aim_rotation,vector,norm
    for a,b in [((1,0,0),(0,-1,0)),((0,1,0),(0,-1,0)),((1,2,3),(-2,1,4))]:
        assert vector(aim_rotation(a,b),norm(a))==pytest.approx(norm(b))
