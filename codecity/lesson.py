"""Independent lesson operations, shared rule engine and deterministic timeline."""
from .model import Plant, DEFAULT_CODE
from .session import Experiment
from .rules import compile_rule, evaluate_actuator, trace_rule

DRY_RULE="if True:\n    irrigate(False)\nelse:\n    irrigate(True)"
WET_RULE="if True:\n    irrigate(True)\nelse:\n    irrigate(False)"
FAN_START="if temperature > 30:\n    ventilate(False)\nelse:\n    ventilate(False)"
FAN_EXAMPLE="if temperature > 30:\n    ventilate(True)\nelse:\n    ventilate(False)"
def comparison(source,initial,day,reference=DEFAULT_CODE):
    left=Experiment();left.start(source,initial);left.seek(day)
    right=Experiment();right.start(reference,initial);right.seek(day)
    return left,right

def fan_check(source):
    code=compile_rule(source,"ventilate")
    passed=total=0;first=None
    for temperature in range(46):
        for moisture in range(101):
            for light in range(17):
                state=Plant(temperature=temperature,moisture=moisture,light=light)
                actual=evaluate_actuator(code,state,"ventilate")
                expected=temperature>30
                total+=1;passed+=actual==expected
                if actual!=expected and first is None:first=(state,actual,expected)
    return passed,total,first

def trace_day(experiment):
    if not experiment.state.day:return None
    before=Experiment();before.start(experiment.source,experiment.initial);before.seek(experiment.state.day-1)
    return trace_rule(experiment.source,before.state)
