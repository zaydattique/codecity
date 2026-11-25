"""Deterministic classroom model, not a botanical prediction."""
from dataclasses import dataclass, replace

DEFAULT_CODE = """if moisture >= 40 and light >= 6:
    irrigate(False)
else:
    irrigate(True)
"""

@dataclass(frozen=True)
class Plant:
    day: int = 0
    moisture: int = 55
    light: int = 8
    temperature: int = 22
    growth: float = 0.0
    health: float = 1.0

    def __post_init__(self):
        for name, low, high in (("day",0,60),("moisture",0,100),("light",0,16),("temperature",0,45)):
            value = getattr(self,name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError("Invalid " + name)
        if not 0 <= self.growth <= 1 or not 0 <= self.health <= 1:
            raise ValueError("Invalid plant state")

def advance(state, watering):
    """One simulated day. Control logic cannot override biology."""
    if type(watering) is not bool:
        raise ValueError("Watering must be boolean")
    if state.day >= 60:
        return state
    moisture = min(100,state.moisture + (25 if watering else 0))
    good = 35 <= moisture <= 80 and 6 <= state.light <= 14 and 15 <= state.temperature <= 30
    health = state.health
    growth = state.growth
    if health > 0:
        if good:
            health = min(1.0,health + 0.08)
            growth = min(1.0,growth + 0.065 * health)
        else:
            health = max(0.0,health - 0.12)
    return replace(state,day=state.day+1,moisture=max(0,moisture-8),
                   growth=growth,health=health)
