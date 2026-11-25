"""Deterministic classroom model, not a botanical prediction."""
from dataclasses import dataclass, replace

DEFAULT_CODE = "if moisture < 40:\n    irrigate(True)\nelse:\n    irrigate(False)"

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
    # Broad illustrative classroom range, not a species-specific prediction.
    # Seeds germinate using stored energy; later leaves require light.
    good_water = 30 <= moisture <= 85
    good_temp = 12 <= state.temperature <= 34
    enough_light = state.growth < .18 or 4 <= state.light <= 16
    health = state.health
    growth = state.growth
    if health > 0:
        if good_water and good_temp and enough_light:
            health = min(1.0, health + .08)
            growth = min(1.0, growth + .065 * health)
        else:
            health = max(0.0, health - .08)
    return replace(state,day=state.day+1,moisture=max(0,moisture-8),
                   growth=growth,health=health)
