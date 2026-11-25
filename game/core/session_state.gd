extends RefCounted
## Authoritative in-memory profile selection and separate mode progression.
## Only a world loader that has successfully spawned the selected character may activate a session.
## No disk persistence or player-facing menu is claimed yet.

const MODES: Array[String] = ["living_world", "academy"]
const CHARACTERS: Array[String] = ["adrian", "maya"]
var _profiles: Dictionary = {}
var _active: Dictionary = {}

func create_profile(id: String, display_name: String) -> bool:
	var pattern := RegEx.new()
	if pattern.compile("^[a-z0-9_-]{1,32}$") != OK:
		return false
	if pattern.search(id) == null or _profiles.has(id) or _profiles.size() >= 16:
		return false
	var name := display_name.strip_edges()
	if name.is_empty() or name.length() > 48:
		return false
	for i: int in range(name.length()):
		if name.unicode_at(i) < 32 or name.unicode_at(i) == 127:
			return false
	_profiles[id] = {"name": name, "character": "adrian",
		"progress": {"living_world": [], "academy": []}}
	return true

func activate(profile_id: String, mode: String, character: String, spawn: Node3D) -> bool:
	if not _profiles.has(profile_id) or not MODES.has(mode) or not CHARACTERS.has(character):
		return false
	if not is_instance_valid(spawn) or not spawn.is_inside_tree() or not spawn.is_node_ready():
		return false
	_profiles[profile_id]["character"] = character
	_active = {"profile_id": profile_id, "mode": mode, "character": character}
	return true

func complete_mission(mission_id: String, mode: String) -> bool:
	if _active.is_empty() or _active["mode"] != mode:
		return false
	var pattern := RegEx.new()
	if pattern.compile("^[a-z0-9_]{1,64}$") != OK or pattern.search(mission_id) == null:
		return false
	var done: Array = _profiles[_active["profile_id"]]["progress"][mode]
	if done.has(mission_id) or done.size() >= 512:
		return false
	done.append(mission_id)
	return true

func snapshot(profile_id: String) -> Dictionary:
	if not _profiles.has(profile_id):
		return {}
	var profile: Dictionary = _profiles[profile_id]
	return profile.duplicate(true)

func active_selection() -> Dictionary:
	return _active.duplicate(true)

func deactivate() -> void:
	_active.clear()
