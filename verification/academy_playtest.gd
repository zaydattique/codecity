extends SceneTree
const Harbor = preload("res://scenes/harbor_playtest.gd")
const Bridge = preload("res://core/academy_bridge.gd")

func _initialize() -> void:
	call_deferred("_verify")

func _wait_for_result(station: Node3D) -> bool:
	var deadline := Time.get_ticks_msec()+7000
	while station._run.disabled and Time.get_ticks_msec()<deadline:
		await create_timer(0.025).timeout
	return not station._run.disabled

func _verify() -> void:
	if Bridge.paths().is_empty():
		_fail("Python runtime missing")
		return
	var packed := load("res://scenes/foundation.tscn") as PackedScene
	var menu := packed.instantiate()
	root.add_child(menu)
	menu._name.text="Academy QA"
	menu._mode.select(1)
	menu._character.select(1)
	menu._on_apply_pressed()
	menu._open_street()
	var world: Node3D=menu._world
	if world==null or not world.academy_mode or world.station==null or world.vehicle!=null:
		_fail("Academy activation or mode separation")
		return
	var station: Node3D=world.station
	world.player.global_position=station.global_position+Vector3(0.9,0.03,0)
	for i: int in range(25):await physics_frame
	station.open_editor()
	if not station.opened or world.player.controls_enabled or station.lamps_online():
		_fail("editor focus or initial lamp state")
		return
	station._code.text="set_lamp(0, True)\nimport os"
	station._run.pressed.emit()
	if not await _wait_for_result(station) or station._lights[0].visible or not station._output.text.contains("Unsupported"):
		_fail("unsafe source or partial command application")
		return
	# Exercise selection and actual physical outcomes, not just console messages.
	station._lesson_picker.item_selected.emit(1)
	station._code.text="set_lamp(1, True)\nprint('Wrong lamp')"
	station._run.pressed.emit()
	if not await _wait_for_result(station) or station._practice_done.has(1) or not station._output.text.contains("Target not met"):
		_fail("incorrect practice result accepted")
		return
	station._code.text="lamp = 0\npower = True\nset_lamp(lamp, power)\nprint('North online')"
	station._run.pressed.emit()
	if not await _wait_for_result(station) or not station._practice_done.has(1) or not station._lights[0].visible or station._lights[1].visible:
		_fail("variables exercise and physical north lamp")
		return
	station._lesson_picker.item_selected.emit(2)
	station._code.text="for lamp in range(2):\n    if lamp == 1:\n        set_lamp(lamp, True)\nprint('South online')"
	station._run.pressed.emit()
	if not await _wait_for_result(station) or not station._practice_done.has(2) or station._lights[0].visible or not station._lights[1].visible:
		_fail("conditions exercise and physical south lamp")
		return
	var practice_profile: Dictionary=menu._sessions.snapshot(menu.active_snapshot()["profile_id"])
	if not practice_profile["progress"]["academy"].is_empty():
		_fail("practice completed the main mission")
		return
	station._lesson_picker.item_selected.emit(0)
	station._code.text="count = 2\nfor lamp in range(count):\n    set_lamp(lamp, True)\nprint('Restored', count)"
	station._run.pressed.emit()
	if not await _wait_for_result(station):
		_fail("Python process execution")
		return
	if not station.lamps_online() or not station._output.text.contains("Restored 2"):
		_fail("actual Python output and world lights")
		return
	var active: Dictionary=menu.active_snapshot()
	var progress: Dictionary=menu._sessions.snapshot(active["profile_id"])["progress"]
	if progress["academy"]!=["street_lighting"] or not progress["living_world"].is_empty():
		_fail("Academy mission progression")
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/academy_editor.png")!=OK:
			_fail("editor capture")
			return
	station.close_editor()
	if not world.player.controls_enabled:
		_fail("editor did not restore movement")
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/academy_lights.png")!=OK:
			_fail("world capture")
			return
	print("CODECITY_ACADEMY_PLAYTEST_OK Python process denial atomic lamps progression")
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
