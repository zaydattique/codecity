extends Node3D
## Development boot scene only. No art, player controller or gameplay claims.

func _ready() -> void:
	if "--smoke" in OS.get_cmdline_user_args():
		call_deferred("_smoke")
	else:
		$CanvasLayer/Center/VBox/Exit.grab_focus()

func _smoke() -> void:
	var previous: int = WorldClock.tick
	await get_tree().physics_frame
	await get_tree().physics_frame
	if WorldClock.tick <= previous:
		push_error("Foundation clock did not advance")
		get_tree().quit(1)
		return
	if not WorldClock.restore(120, 1439) or WorldClock.minute_of_day() != 0:
		push_error("Clock rollover failed")
		get_tree().quit(1)
		return
	if WorldClock.restore(-1, 0) or not InputMap.has_action("interact"):
		push_error("Clock validation or input configuration failed")
		get_tree().quit(1)
		return
	print("CODECITY_FOUNDATION_SMOKE_OK")
	get_tree().quit(0)

func _on_exit_pressed() -> void:
	get_tree().quit()
