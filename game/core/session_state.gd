extends RefCounted
## Authoritative in-memory profile selection and separate mode progression.
## Only a world loader that has successfully spawned the selected character may activate a session.
## Versioned local profile persistence; gameplay position is not saved.

const MODES: Array[String] = ["living_world", "academy"]
const CHARACTERS: Array[String] = ["adrian", "maya"]
var _profiles: Dictionary = {}
var _active: Dictionary = {}
var _draft: Dictionary = {}

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

## A menu choice is not a spawned gameplay session and does not change progression.
func select_draft(profile_id: String, mode: String, character: String) -> bool:
	if not _profiles.has(profile_id) or not MODES.has(mode) or not CHARACTERS.has(character):
		return false
	_draft = {"profile_id": profile_id, "mode": mode, "character": character}
	return true

func draft_selection() -> Dictionary:
	return _draft.duplicate(true)

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

func find_profile(display_name: String) -> String:
	for id: String in _profiles:
		if _profiles[id]["name"]==display_name.strip_edges():return id
	return ""

func next_profile_id() -> String:
	for i: int in range(1,17):
		var id:="local_%d"%i
		if not _profiles.has(id):return id
	return ""

func save_profiles(path: String="user://profiles.json") -> bool:
	var payload:=JSON.stringify({"version":1,"profiles":_profiles})
	if payload.to_utf8_buffer().size()>1048576:return false
	var temporary:=path+".tmp"
	var f:=FileAccess.open(temporary,FileAccess.WRITE)
	if f==null:return false
	f.store_string(payload)
	f.flush()
	var error:=f.get_error()
	f.close()
	if error!=OK:return false
	return DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary),ProjectSettings.globalize_path(path))==OK

func load_profiles(path: String="user://profiles.json") -> bool:
	if not _active.is_empty() or not FileAccess.file_exists(path):return false
	var f:=FileAccess.open(path,FileAccess.READ)
	if f==null or f.get_length()>1048576:return false
	var data: Variant=JSON.parse_string(f.get_as_text())
	f.close()
	if not data is Dictionary or data.get("version")!=1 or not data.get("profiles") is Dictionary or data["profiles"].size()>16:return false
	var prior:=_profiles
	_profiles={}
	var valid:=true
	var pattern:=RegEx.new()
	if pattern.compile("^[a-z0-9_]{1,64}$")!=OK:
		_profiles=prior
		return false
	for id: String in data["profiles"]:
		var item: Variant=data["profiles"][id]
		if not item is Dictionary or not item.get("name") is String or not create_profile(id,item["name"]) or not CHARACTERS.has(item.get("character")) or not item.get("progress") is Dictionary:
			valid=false
			break
		_profiles[id]["character"]=item["character"]
		for mode: String in MODES:
			var done: Variant=item["progress"].get(mode)
			if not done is Array or done.size()>512:
				valid=false
				break
			var seen: Dictionary={}
			for mission: Variant in done:
				if not mission is String or pattern.search(mission)==null or seen.has(mission):
					valid=false
					break
				seen[mission]=true
			if not valid:break
			_profiles[id]["progress"][mode]=done.duplicate()
		if not valid:break
	if not valid:
		_profiles=prior
		return false
	_draft.clear()
	return true
