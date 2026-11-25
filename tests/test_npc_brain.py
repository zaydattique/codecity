import pytest
from ai.npc_brain import Brain, IDS, LOCATIONS

def observation(id,tick=1000,minute=600,event=None,near=5.0,reached=False):
    return {"id":id,"position":[-4.5,0],"minute":minute,"tick":tick,"reached":reached,
            "player_distance":near,"event":event}

def test_six_independent_routines_and_determinism():
    inputs=[observation(i) for i in IDS]
    a,b=Brain(),Brain()
    assert a.batch(inputs)==b.batch(inputs)
    assert len({x["destination"] for x in Brain().batch(inputs)})>=4
    assert all(x["destination"] in LOCATIONS for x in a.batch([observation(i,1100,reached=True) for i in IDS]))

def test_context_and_memory():
    b=Brain()
    greet={"id":1,"kind":"greet","distance":1.0}
    replies=b.batch([observation("nora",event=greet),observation("liam",event=greet)])
    assert replies[0]["action"]=="acknowledge" and replies[1]["action"]=="walk"
    assert b.states["nora"].affinity>0
    assert b.batch([observation("nora",1100,event=greet)])[0]["action"]!="acknowledge"
    assert b.states["nora"].affinity==.1

def test_atomic_stale_invalid_and_perception():
    b=Brain();b.batch([observation("nora")]);before=b.states.copy()
    with pytest.raises(ValueError):b.batch([observation("omar",1001),observation("nora",999)])
    assert b.states==before
    with pytest.raises(ValueError):b.batch([observation("omar"),observation("omar")])
    with pytest.raises(ValueError):b.batch([observation("nora",near=float("nan"))])
    far={"id":2,"kind":"horn","distance":100}
    assert b.batch([observation("nora",1200,event=far)])[0]["action"]=="walk"

def test_horn_changes_behavior():
    b=Brain()
    event={"id":1,"kind":"near_collision","distance":2}
    assert b.batch([observation("marcus",event=event)])[0]["action"]=="give_space"
    assert b.states["marcus"].stress>.4


def test_fictional_danger_response_and_memory():
    b=Brain()
    event={"id":10,"kind":"threat","distance":2}
    intents=b.batch([observation(i,event=event) for i in IDS])
    assert all(x["action"]=="give_space" and x["speed"]==2.0 for x in intents)
    assert all(b.states[i].stress>=.8 and b.states[i].affinity<0 for i in IDS)
    prior=b.states["nora"].affinity
    b.batch([observation("nora",1100,event=event)])
    assert b.states["nora"].affinity==prior


def test_twelve_city_routines_are_independent_and_bounded():
    from ai.npc_brain import CITY_IDS
    brain=Brain()
    observations=[observation(i) for i in IDS+CITY_IDS]
    for o in observations[6:]:
        o["position"]=[0,80]
        o["player_distance"]=1200
    intents=brain.batch(observations)
    assert len(intents)==12 and len({x["id"] for x in intents})==12
    assert all(x["destination"].startswith(("park_","shop_")) for x in intents[6:])
    assert len({x["destination"] for x in intents[6:]})>=3
    bad=observation("jules",1100)
    bad["position"]=[601,0]
    with pytest.raises(ValueError):brain.batch([bad])


def test_personality_dependent_fictional_retaliation():
    b=Brain()
    event={"id":3,"kind":"attack","distance":1.3}
    result=b.batch([observation("jules",event=event),observation("vincent",event=event)])
    assert result[0]["action"]=="defend"
    assert result[1]["action"]=="give_space"
