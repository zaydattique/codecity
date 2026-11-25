extends VBoxContainer
@onready var _prefs: Node = get_node("/root/GameSettings")
signal resume_requested
signal leave_requested
var _settings: VBoxContainer

func _ready() -> void:
	add_theme_constant_override("separation",10)
	var title := Label.new()
	title.text="CODECITY  /  PAUSED"
	title.add_theme_font_size_override("font_size",26)
	add_child(title)
	_button("Resume",func(): resume_requested.emit())
	_button("Settings & controls",func(): _settings.visible=not _settings.visible)
	_settings=VBoxContainer.new()
	_settings.add_theme_constant_override("separation",8)
	add_child(_settings)
	_check("Auto-follow camera",_prefs.auto_camera,func(v): _prefs.auto_camera=v)
	_check("Invert vertical look",_prefs.invert_y,func(v): _prefs.invert_y=v)
	_slider("Mouse sensitivity",0.001,0.006,0.00025,_prefs.sensitivity,func(v): _prefs.sensitivity=v)
	_slider("Field of view",55,90,1,_prefs.fov,func(v): _prefs.fov=v)
	_slider("Master volume",0,1,0.05,_prefs.master_volume,func(v): _prefs.master_volume=v)
	_check("Show gameplay hints",_prefs.show_hints,func(v): _prefs.show_hints=v)
	_check("Fullscreen",_prefs.fullscreen,func(v): _prefs.fullscreen=v)
	var instructions := Label.new()
	instructions.text="ON FOOT   WASD move | Mouse look | Shift sprint\nAlt walk | Space jump | C crouch | V camera\nDRIVING   F enter/exit | WASD drive | Space brake | L lights\nWORLD   E interact | M map | Esc pause | Tab cursor"
	instructions.add_theme_font_size_override("font_size",15)
	_settings.add_child(instructions)
	_settings.hide()
	_button("Return to profiles",func(): leave_requested.emit())

func _button(label: String, callback: Callable) -> void:
	var btn := Button.new()
	btn.text=label
	btn.custom_minimum_size=Vector2(0,38)
	btn.pressed.connect(callback)
	add_child(btn)

func _check(label: String, checked: bool, callback: Callable) -> void:
	var btn := CheckButton.new()
	btn.text=label
	btn.button_pressed=checked
	btn.toggled.connect(func(v: bool): callback.call(v); _prefs.apply(); _prefs.save())
	_settings.add_child(btn)

func _slider(label: String, low: float, high: float, step: float, value: float, callback: Callable) -> void:
	var row := HBoxContainer.new()
	var caption := Label.new()
	caption.text=label
	caption.custom_minimum_size.x=180
	row.add_child(caption)
	var slider := HSlider.new()
	slider.min_value=low
	slider.max_value=high
	slider.step=step
	slider.value=value
	slider.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	slider.value_changed.connect(func(v: float): callback.call(v); _prefs.apply(); _prefs.save())
	row.add_child(slider)
	_settings.add_child(row)
