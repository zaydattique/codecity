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

func _ready() -> void:
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
	cfg.save("user://settings.cfg")
