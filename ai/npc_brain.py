"""Deterministic, bounded NPC decision policy for the CodeCity street.

This is the Python decision layer only. Godot must validate and execute intents
on real distinct rigs. State changes come from observed world events, not
imagined successful actions. No external AI or network.
"""
from dataclasses import dataclass, replace
import math

MAX_AGENTS=6
LOCATIONS={
    "west_south":(-4.6,11.5),
    "west_north":(-4.6,-11.5),
    "east_south":(4.5,11.5),
    "east_north":(4.5,-11.5),
    "bench":(4.0,2.0),
    "crossing":(0.0,0.0),
}
EVENTS={"greet","crowd","horn","near_collision","lamp_restored"}
IDS=("nora","omar","elena","marcus","sana","liam")


@dataclass(frozen=True)
class Profile:
    id:str
    name:str
    occupation:str
    sociability:float
    patience:float
    caution:float
    route:tuple[str,...]
    work_start:int
    work_end:int


PROFILES={
    p.id:p for p in (
        Profile("nora","Nora Silva","shop assistant",.7,.7,.65,("west_south","west_north"),480,1020),
        Profile("omar","Omar Rahman","delivery courier",.35,.3,.55,("east_north","east_south"),420,960),
        Profile("elena","Elena Park","student",.65,.55,.7,("west_north","bench"),540,900),
        Profile("marcus","Marcus Reed","maintenance worker",.3,.8,.8,("east_south","east_north"),360,840),
        Profile("sana","Sana Malik","designer",.55,.6,.6,("bench","east_south"),600,1080),
        Profile("liam","Liam Walsh","shift worker",.2,.4,.85,("west_north","west_south"),720,1320),
    )
}


@dataclass(frozen=True)
class State:
    id:str
    route_index:int=0
    energy:float=1.0
    stress:float=0.0
    affinity:float=0.0
    last_event:int=-1
    last_reaction:int=-10000
    last_tick:int=-1


def clamp(v,lo=0.0,hi=1.0):return max(lo,min(hi,v))


def number(v,lo,hi):
    return type(v) in (int,float) and math.isfinite(v) and lo<=v<=hi


def validate_observation(o):
    if type(o) is not dict or set(o)!={"id","position","minute","tick","reached","player_distance","event"}:
        raise ValueError("Invalid NPC observation shape")
    if o["id"] not in PROFILES or type(o["minute"]) is not int or not 0<=o["minute"]<1440:
        raise ValueError("Invalid NPC identity or time")
    if type(o["tick"]) is not int or not 0<=o["tick"]<=10**9 or type(o["reached"]) is not bool:
        raise ValueError("Invalid NPC tick")
    if type(o["position"]) is not list or len(o["position"])!=2 or not number(o["position"][0],-6,6) or not number(o["position"][1],-16,16):
        raise ValueError("NPC outside installed street")
    if not number(o["player_distance"],0,1000):raise ValueError("Invalid player distance")
    event=o["event"]
    if event is not None:
        if type(event) is not dict or set(event)!={"id","kind","distance"} or type(event["id"]) is not int or event["id"]<0 or event["kind"] not in EVENTS or not number(event["distance"],0,1000):
            raise ValueError("Invalid perceived event")
    return o


def decide(state,o):
    o=validate_observation(o)
    if state.id!=o["id"] or o["tick"]<=state.last_tick:
        raise ValueError("Mismatched or stale NPC observation")
    p=PROFILES[state.id]
    tick=o["tick"]
    elapsed=min(120,max(0,tick-state.last_tick)) if state.last_tick>=0 else 0
    stress=clamp(state.stress-elapsed*.0015)
    energy=clamp(state.energy-elapsed*.00035)
    affinity=state.affinity
    route=state.route_index
    last_event=state.last_event
    reaction=None
    event=o["event"]
    if event and event["id"]>last_event and event["distance"]<=8:
        last_event=event["id"]
        kind=event["kind"]
        if kind in ("horn","near_collision"):
            stress=clamp(stress+(0.25 if kind=="horn" else 0.6)*p.caution)
            affinity=clamp(affinity-0.15,-1,1)
            if tick-state.last_reaction>=90:reaction="avoid" if p.caution>.65 else "complain"
        elif kind=="crowd":
            stress=clamp(stress+(1-p.patience)*.24)
            if tick-state.last_reaction>=90 and p.patience<.6:reaction="give_space"
        elif kind=="greet" and event["distance"]<=2.5:
            if p.sociability+affinity*.2-stress*.4>.55 and tick-state.last_reaction>=90:
                reaction="acknowledge"
                affinity=clamp(affinity+.1,-1,1)
        elif kind=="lamp_restored" and p.occupation=="maintenance worker":
            reaction="inspect"
    if o["player_distance"]<.65 and reaction is None and tick-state.last_reaction>=90:
        reaction="give_space"
    working=p.work_start<=o["minute"]<p.work_end
    if o["reached"]:
        route=(route+1)%len(p.route)
        if not working:energy=clamp(energy+.07)
    destination=p.route[route]
    action="walk"
    if energy<.25 and not working:
        destination="bench"
        action="rest" if math.dist(o["position"],LOCATIONS["bench"])<.75 else "walk"
    elif reaction in ("avoid","give_space"):
        # Pick a valid sidewalk endpoint furthest from the current position;
        # world must still route around other actors/collision.
        options=[x for x in p.route if x in LOCATIONS]
        destination=max(options,key=lambda x:math.dist(o["position"],LOCATIONS[x]))
        action="give_space"
    elif reaction in ("acknowledge","complain","inspect"):
        action=reaction
    new=replace(state,route_index=route,energy=energy,stress=stress,affinity=affinity,
                last_event=last_event,last_reaction=tick if reaction else state.last_reaction,last_tick=tick)
    return new,{"id":p.id,"action":action,"destination":destination,"speed":1.2 if not working else 1.6,
                "valid_until":tick+120}


class Brain:
    def __init__(self):self.states={i:State(i) for i in IDS}
    def batch(self,observations):
        if type(observations) is not list or not 1<=len(observations)<=MAX_AGENTS:
            raise ValueError("Invalid NPC batch size")
        ids=[validate_observation(o)["id"] for o in observations]
        if len(set(ids))!=len(ids):raise ValueError("Duplicate NPC")
        candidate=dict(self.states);intents=[]
        for o in observations:
            candidate[o["id"]],intent=decide(candidate[o["id"]],o)
            intents.append(intent)
        self.states=candidate
        return intents
