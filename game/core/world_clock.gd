extends Node
## Authoritative game clock, integer simulation ticks. Paused with the scene tree.
const TICKS_PER_GAME_MINUTE: int = 120
const MINUTES_PER_DAY: int = 1440
var tick: int = 0
var start_minute: int = 480

func _physics_process(_delta: float) -> void:
	advance(1)

func advance(count: int) -> void:
	if count >= 0:
		tick += count

func minute_of_day() -> int:
	@warning_ignore("integer_division")
	return (start_minute + tick / TICKS_PER_GAME_MINUTE) % MINUTES_PER_DAY

func restore(new_tick: int, new_start_minute: int) -> bool:
	if new_tick < 0 or new_start_minute < 0 or new_start_minute >= MINUTES_PER_DAY:
		return false
	tick = new_tick
	start_minute = new_start_minute
	return true
