extends Node3D
## Development profile/mode selection. No world launch until approved assets exist.
const Sessions = preload("res://core/session_state.gd")
const Harbor = preload("res://scenes/harbor_playtest.gd")
const AcademyBridge = preload("res://core/academy_bridge.gd")
var _world: Node3D
var _launch: Button
var _sessions = Sessions.new()
var _profile_counter: int = 0
@onready var _menu: VBoxContainer = $CanvasLayer/Center/VBox
@onready var _name: LineEdit = _menu.get_node("ProfileName")
@onready var _mode: OptionButton = _menu.get_node("Mode")
@onready var _character: OptionButton = _menu.get_node("Character")
@onready var _status: Label = _menu.get_node("Status")

func _ready() -> void:
	_mode.add_item("Living World", 0)
	_mode.add_item("CodeCity Academy", 1)
	_character.add_item("Adrian Cole", 0)
	_character.add_item("Maya Bennett", 1)
	_launch=Button.new()
	_launch.text="Start"
	_launch.disabled=true
	_launch.visible=Harbor.installed()
	_launch.pressed.connect(_open_street)
	_menu.add_child(_launch)
	_menu.move_child(_launch,_menu.get_child_count()-2)
	if "--vehicle-smoke" in OS.get_cmdline_user_args():
		call_deferred("_vehicle_smoke")
	elif "--smoke" in OS.get_cmdline_user_args():
		call_deferred("_smoke")
	else:
		_name.grab_focus()

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

func _on_apply_pressed() -> void:
	# A single temporary profile per distinct name, bounded by existing state limits.
	var display_name := _name.text.strip_edges()
	if display_name.is_empty():
		_status.text = "Enter a profile name."
		return
	var current := _sessions.draft_selection()
	var id: String = current.get("profile_id", "")
	if id.is_empty() or _sessions.snapshot(id).get("name", "") != display_name:
		_profile_counter += 1
		id = "local_%d" % _profile_counter
		if not _sessions.create_profile(id, display_name):
			_status.text = "Profile name or session limit is invalid."
			return
	if not _sessions.select_draft(id, Sessions.MODES[_mode.selected], Sessions.CHARACTERS[_character.selected]):
		_status.text = "Invalid selection."
		return
	_launch.disabled=not Harbor.installed() or (_mode.selected==1 and AcademyBridge.paths().is_empty())
	_status.text = "Selected: %s / %s." % [_mode.get_item_text(_mode.selected), _character.get_item_text(_character.selected)]
	if _mode.selected==1:
		_status.text += " Python lighting mission ready." if not _launch.disabled else " Python mission runtime unavailable."
	elif not Harbor.installed():
		_status.text += " World not installed."
	else:
		_status.text += " Harbor Boulevard ready."

func _open_street() -> void:
	if _world != null:
		return
	var draft := _sessions.draft_selection()
	if draft.get("mode") not in ["living_world","academy"]:
		return
	if draft.get("mode")=="academy" and AcademyBridge.paths().is_empty():return
	var world = Harbor.new()
	if not world.prepare(draft.get("character",""),draft.get("mode")=="academy"):
		world.free()
		_status.text="Street candidate could not load."
		return
	add_child(world)
	if not _sessions.activate(draft["profile_id"],draft["mode"],draft["character"],world.player):
		world.queue_free()
		_status.text="Character spawn failed."
		return
	_world=world
	world.leave_requested.connect(_close_street)
	world.academy_completed.connect(func(): _sessions.complete_mission("street_lighting","academy"))
	$CanvasLayer.hide()

func _close_street() -> void:
	if is_instance_valid(_world):
		_world.queue_free()
	_world=null
	_sessions.deactivate()
	$CanvasLayer.show()
	_name.grab_focus()

func selection_snapshot() -> Dictionary:
	return _sessions.draft_selection()

func active_snapshot() -> Dictionary:
	return _sessions.active_selection()

func _on_exit_pressed() -> void:
	get_tree().quit()

## Standalone package QA: use the actual menu and installed candidate world.
func _vehicle_smoke() -> void:
	_name.text="Export verification"
	_mode.select(0)
	_character.select(0)
	_on_apply_pressed()
	_open_street()
	if not is_instance_valid(_world) or _world.vehicle==null or not _world.vehicle.built or active_snapshot().get("character")!="adrian":
		push_error("Exported candidate world or car missing")
		get_tree().quit(1)
		return
	for i: int in range(120):
		await get_tree().physics_frame
	if _world.vehicle.contacts()<3 or not _world.player.is_on_floor() or not _world.player.motion_installed:
		push_error("Exported candidate suspension or actor failed")
		get_tree().quit(1)
		return
	print("CODECITY_EXPORTED_VEHICLE_OK")
	get_tree().quit(0)
