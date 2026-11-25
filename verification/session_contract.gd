extends SceneTree
const Sessions = preload("res://core/session_state.gd")
const Interaction = preload("res://core/world_interaction.gd")
const Orbit = preload("res://core/camera_orbit.gd")
const Loader = preload("res://core/scene_loader.gd")

func _initialize() -> void:
	call_deferred("_verify")

func _verify() -> void:
	var state = Sessions.new()
	var actor := Node3D.new()
	var target := Node3D.new()
	if not state.create_profile("local_1", "Player One") or not state.create_profile("local_2", "Player Two"):
		_fail("profile creation")
		return
	if state.create_profile("../bad", "Bad") or state.create_profile("local_1", "Duplicate"):
		_fail("invalid profile")
		return
	if state.activate("local_1", "living_world", "adrian", actor):
		_fail("unspawned selection")
		return
	root.add_child(actor)
	root.add_child(target)
	if not state.activate("local_1", "living_world", "adrian", actor):
		_fail("valid selection")
		return
	if not state.complete_mission("new_beginning", "living_world") or state.complete_mission("new_beginning", "living_world") or state.complete_mission("control_room", "academy"):
		_fail("mode or duplicate completion")
		return
	if not state.activate("local_1", "academy", "maya", actor) or not state.complete_mission("control_room", "academy"):
		_fail("academy mode")
		return
	if state.cash_balance()!=500:
		_fail("independent mode cash")
		return
	var snap: Dictionary = state.snapshot("local_1")
	if snap["cash"]["living_world"]!=650 or snap["cash"]["academy"]!=500:
		_fail("wallet isolation")
		return
	if snap["progress"]["living_world"] != ["new_beginning"] or snap["progress"]["academy"] != ["control_room"] or not state.snapshot("local_2")["progress"]["academy"].is_empty():
		_fail("progress isolation")
		return
	snap["progress"]["academy"].clear()
	if state.snapshot("local_1")["progress"]["academy"].is_empty():
		_fail("mutable snapshot escaped")
		return
	target.position = Vector3(2, 0, 0)
	if not Interaction.within_range(actor, target, 2.1) or Interaction.within_range(actor, target, 1.9) or Interaction.within_range(actor, actor, 2.1):
		_fail("world interaction radius")
		return
	if not Orbit.offset(0.0, 0.0, 5.0).is_equal_approx(Vector3(0, 0, 5)) or not Orbit.offset(PI / 2.0, 0.0, 5.0).is_equal_approx(Vector3(5, 0, 0)):
		_fail("camera orbit directions")
		return
	if not is_equal_approx(Orbit.offset(0.3, -0.5, 5.0).length(), 5.0) or Orbit.offset(0.0, 0.0, -1.0) != Vector3.ZERO:
		_fail("camera orbit distance")
		return
	var whole: float = Orbit.follow_weight(9.0, 1.0 / 30.0)
	var half: float = Orbit.follow_weight(9.0, 1.0 / 60.0)
	if not is_equal_approx(whole, 1.0 - (1.0 - half) * (1.0 - half)):
		_fail("camera smoothing frame invariance")
		return
	var loader = Loader.new()
	var approved := PackedStringArray(["res://scenes/foundation.tscn"])
	if loader.request("res://unapproved.tscn", approved) or not loader.request(approved[0], approved) or loader.request(approved[0], approved):
		_fail("loading request admission")
		return
	var deadline := Time.get_ticks_msec() + 5000
	while loader.poll() == Loader.Status.LOADING and Time.get_ticks_msec() < deadline:
		await create_timer(0.01).timeout
	if loader.status != Loader.Status.READY or loader.progress != 1.0 or loader.take_scene() == null or loader.take_scene() != null:
		_fail("threaded load completion")
		return
	# Exercise the actual menu scene and its connected controls, not a duplicate mock.
	var menu_scene := load("res://scenes/foundation.tscn") as PackedScene
	var menu := menu_scene.instantiate()
	root.add_child(menu)
	var fields := menu.get_node("CanvasLayer/Center/VBox")
	var profile_input := fields.get_node("ProfileName") as LineEdit
	var mode_input := fields.get_node("Mode") as OptionButton
	var character_input := fields.get_node("Character") as OptionButton
	var apply := fields.get_node("Apply") as Button
	if mode_input.item_count != 2 or character_input.item_count != 2:
		_fail("menu options")
		return
	apply.pressed.emit()
	if not menu.selection_snapshot().is_empty():
		_fail("empty profile accepted")
		return
	profile_input.text = "Review Player"
	mode_input.select(1)
	character_input.select(1)
	apply.pressed.emit()
	var selection: Dictionary = menu.selection_snapshot()
	if selection.get("mode") != "academy" or selection.get("character") != "maya" or not menu.active_snapshot().is_empty():
		_fail("menu selection activated nonexistent world")
		return
	mode_input.select(0)
	character_input.select(0)
	apply.pressed.emit()
	if menu.selection_snapshot().get("mode") != "living_world" or menu.selection_snapshot().get("character") != "adrian":
		_fail("menu mode switching")
		return
	menu.queue_free()
	state.deactivate()
	if state.complete_mission("other", "academy"):
		_fail("inactive completion")
		return
	actor.queue_free()
	target.queue_free()
	print("CODECITY_SESSION_CONTRACT_OK")
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
