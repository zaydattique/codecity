extends SceneTree
const Sessions = preload("res://core/session_state.gd")
const Interaction = preload("res://core/world_interaction.gd")

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
	var snap: Dictionary = state.snapshot("local_1")
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
