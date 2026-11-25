extends Node
signal changed
var auto_camera := true
var invert_y := false
var sensitivity := 0.0025
var fov := 68.0
var master_volume := 0.8
var show_hints := false
var fullscreen := false
var rotate_minimap := true
var subtitles := true
var vsync := true
var fps_limit := 60
var resolution_index := 1
const RESOLUTIONS := [Vector2i(960,540),Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080)]
const FPS_LIMITS := [30,60,120,0]
const REMAP_ACTIONS := ["move_forward","move_back","move_left","move_right","sprint","walk","jump","crouch","interact","camera_view","vehicle_toggle","vehicle_lights","vehicle_horn","full_map","menu_cursor"]
var _defaults: Dictionary={}
var _bindings: Dictionary={}

func _ready() -> void:
	for action: String in REMAP_ACTIONS:
		for event: InputEvent in InputMap.action_get_events(action):
			if event is InputEventKey:
				_defaults[action]=event.physical_keycode
				break
	_bindings=_defaults.duplicate()
	var cfg := ConfigFile.new()
	if cfg.load("user://settings.cfg")==OK:
		auto_camera=bool(cfg.get_value("camera","auto",true))
		invert_y=bool(cfg.get_value("camera","invert",false))
		sensitivity=clampf(float(cfg.get_value("camera","sensitivity",0.0025)),0.001,0.006)
		fov=clampf(float(cfg.get_value("camera","fov",68.0)),55,90)
		master_volume=clampf(float(cfg.get_value("audio","master",0.8)),0,1)
		show_hints=bool(cfg.get_value("ui","hints",false))
		fullscreen=bool(cfg.get_value("display","fullscreen",false))
		rotate_minimap=bool(cfg.get_value("ui","rotate_minimap",true))
		subtitles=bool(cfg.get_value("ui","subtitles",true))
		vsync=bool(cfg.get_value("display","vsync",true))
		fps_limit=int(cfg.get_value("display","fps_limit",60))
		if not FPS_LIMITS.has(fps_limit):fps_limit=60
		resolution_index=clampi(int(cfg.get_value("display","resolution",1)),0,RESOLUTIONS.size()-1)
		var stored: Variant=cfg.get_value("controls","keys",{})
		if stored is Dictionary and _valid_bindings(stored):_bindings=stored.duplicate()
	_apply_bindings()
	apply()

func apply() -> void:
	var bus := AudioServer.get_bus_index("Master")
	if bus>=0:
		AudioServer.set_bus_mute(bus,master_volume<=0.001)
		AudioServer.set_bus_volume_db(bus,linear_to_db(maxf(0.001,master_volume)))
	if DisplayServer.get_name()!="headless" and DisplayServer.window_get_mode()!=(DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED):
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
	Engine.max_fps=fps_limit
	if DisplayServer.get_name()!="headless":
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if vsync else DisplayServer.VSYNC_DISABLED)
		if not fullscreen and DisplayServer.window_get_size()!=RESOLUTIONS[resolution_index]:DisplayServer.window_set_size(RESOLUTIONS[resolution_index])
	changed.emit()

func save() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("camera","auto",auto_camera)
	cfg.set_value("camera","invert",invert_y)
	cfg.set_value("camera","sensitivity",sensitivity)
	cfg.set_value("camera","fov",fov)
	cfg.set_value("audio","master",master_volume)
	cfg.set_value("ui","hints",show_hints)
	cfg.set_value("display","fullscreen",fullscreen)
	cfg.set_value("ui","rotate_minimap",rotate_minimap)
	cfg.set_value("ui","subtitles",subtitles)
	cfg.set_value("display","vsync",vsync)
	cfg.set_value("display","fps_limit",fps_limit)
	cfg.set_value("display","resolution",resolution_index)
	cfg.set_value("controls","keys",_bindings)
	cfg.save("user://settings.cfg")

func _valid_bindings(candidate: Dictionary) -> bool:
	if candidate.size()!=REMAP_ACTIONS.size():return false
	var used: Dictionary={}
	for action: String in REMAP_ACTIONS:
		var key: Variant=candidate.get(action)
		if not key is int or key<=0 or key==KEY_ESCAPE or OS.get_keycode_string(key).is_empty() or used.has(key):return false
		used[key]=true
	return true

func _apply_bindings() -> void:
	for action: String in REMAP_ACTIONS:
		if not _bindings.has(action):continue
		var event:=InputEventKey.new()
		event.physical_keycode=int(_bindings[action])
		InputMap.action_erase_events(action)
		InputMap.action_add_event(action,event)
	# Jump and vehicle brake share a key because their ownership is exclusive.
	if _bindings.has("jump"):
		var brake:=InputEventKey.new()
		brake.physical_keycode=int(_bindings["jump"])
		InputMap.action_erase_events("vehicle_brake")
		InputMap.action_add_event("vehicle_brake",brake)

func binding_label(action: String) -> String:
	return OS.get_keycode_string(int(_bindings.get(action,0)))

func rebind(action: String,key: int) -> bool:
	if not REMAP_ACTIONS.has(action):return false
	var candidate:=_bindings.duplicate()
	candidate[action]=key
	if not _valid_bindings(candidate):return false
	_bindings=candidate
	_apply_bindings()
	save()
	changed.emit()
	return true

func reset_bindings() -> void:
	_bindings=_defaults.duplicate()
	_apply_bindings()
	save()
	changed.emit()
