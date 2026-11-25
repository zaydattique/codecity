extends Node
signal changed
var auto_camera := true
var invert_y := false
var sensitivity := 0.0025
var fov := 68.0
var master_volume := 0.8
var show_hints := false
var fullscreen := false

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
	apply()

func apply() -> void:
	var bus := AudioServer.get_bus_index("Master")
	if bus>=0:
		AudioServer.set_bus_mute(bus,master_volume<=0.001)
		AudioServer.set_bus_volume_db(bus,linear_to_db(maxf(0.001,master_volume)))
	if DisplayServer.get_name()!="headless":
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
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
	cfg.save("user://settings.cfg")
