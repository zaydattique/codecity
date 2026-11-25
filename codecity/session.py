"""Authoritative experiment and validated local profile. No renderer dependency."""
import json, os, tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from .model import Plant, advance, DEFAULT_CODE
from .rules import compile_rule, evaluate_compiled

@dataclass
class Experiment:
    initial: Plant=field(default_factory=Plant)
    state: Plant=field(default_factory=Plant)
    source: str=DEFAULT_CODE
    last_input: int=55
    water: bool=False
    playing: bool=False
    _code: object=field(init=False,repr=False)
    def __post_init__(self):
        self._code=compile_rule(self.source)
    def start(self,source,initial):
        code=compile_rule(source)  # validate before changing anything
        self.source=source;self._code=code;self.initial=initial;self.state=initial
        self.last_input=initial.moisture;self.water=False;self.playing=True
    def reset(self,initial):
        self.initial=self.state=initial;self.last_input=initial.moisture
        self.water=False;self.playing=False
    def step(self):
        if not self.playing:return False
        if self.state.day>=60:self.playing=False;return False
        self.last_input=self.state.moisture
        self.water=evaluate_compiled(self._code,self.state)
        self.state=advance(self.state,self.water)
        if self.state.day>=60:self.playing=False
        return True
    def snapshot(self):
        return dict(initial=asdict(self.initial),state=asdict(self.state),source=self.source,last_input=self.last_input,water=self.water)
    @classmethod
    def restore(cls,data):
        if not isinstance(data,dict):raise ValueError("Invalid experiment")
        initial=Plant(**data["initial"]);state=Plant(**data["state"])
        if initial.day!=0 or initial.growth!=0 or initial.health!=1:raise ValueError("Invalid starting state")
        if (initial.light,initial.temperature)!=(state.light,state.temperature):raise ValueError("Mismatched sensors")
        if type(data["last_input"]) is not int or not 0<=data["last_input"]<=100 or type(data["water"]) is not bool:raise ValueError("Invalid trace")
        obj=cls(initial=initial,state=state,source=data["source"],last_input=data["last_input"],water=data["water"])
        # Reproduce the exact deterministic history; refuse tampered or inconsistent state.
        check=cls();check.start(obj.source,initial)
        for _ in range(state.day):check.step()
        if check.state!=state or check.last_input!=obj.last_input or check.water!=obj.water:
            raise ValueError("Inconsistent saved experiment")
        return obj

def challenge(source):
    """Every integer moisture input AND every supported light/temperature combination."""
    code=compile_rule(source)
    failures=[];passed=0;total=0
    for moisture in range(101):
        expected=moisture<50
        for light in range(17):
            for temperature in range(46):
                actual=evaluate_compiled(code,Plant(moisture=moisture,light=light,temperature=temperature))
                total+=1
                if actual==expected:passed+=1
                elif len(failures)<5:failures.append((moisture,light,temperature,actual,expected))
    return passed,total,failures

def load_profile(path):
    defaults={"greenhouse_complete":False,"voice":True,"pace":.34,"experiment":None,"draft":DEFAULT_CODE}
    try:
        if path.stat().st_size>65536:return defaults
        data=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data,dict):return defaults
        for k in ("greenhouse_complete","voice"):
            if type(data.get(k)) is bool:defaults[k]=data[k]
        if type(data.get("pace")) in (float,int) and data["pace"] in (.7,.34,.16):defaults["pace"]=data["pace"]
        if isinstance(data.get("draft"),str) and len(data["draft"])<=2048:defaults["draft"]=data["draft"]
        if data.get("experiment") is not None:defaults["experiment"]=Experiment.restore(data["experiment"]).snapshot()
    except (OSError,ValueError,TypeError,KeyError,OverflowError,RecursionError):
        pass
    return defaults

def write_profile(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=path.parent,delete=False) as f:
        temp=Path(f.name)
        try:json.dump(data,f,allow_nan=False);f.flush();os.fsync(f.fileno())
        except Exception:
            f.close();temp.unlink(missing_ok=True);raise
    try:temp.replace(path)
    finally:temp.unlink(missing_ok=True)
