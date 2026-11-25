extends VBoxContainer
@onready var _prefs: Node = get_node("/root/GameSettings")
signal resume_requested
signal leave_requested
var _settings: VBoxContainer
var _binding_buttons: Dictionary={}
var _binding_note: Label
var _listening:=""

func _ready() -> void:
	add_theme_constant_override("separation",10)
	var title := Label.new()
	title.text="CODECITY  /  PAUSED"
	title.add_theme_font_size_override("font_size",26)
	add_child(title)
	_button("Resume",func(): resume_requested.emit())
	_button("Settings & controls",func(): _settings.visible=not _settings.visible)
	var scroll:=ScrollContainer.new()
	scroll.custom_minimum_size=Vector2(0,410)
	scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	add_child(scroll)
	_settings=VBoxContainer.new()
	_settings.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	_settings.add_theme_constant_override("separation",8)
	scroll.add_child(_settings)
	_settings.visibility_changed.connect(func():scroll.visible=_settings.visible)
	_check("Auto-follow camera",_prefs.auto_camera,func(v): _prefs.auto_camera=v)
	_check("Invert vertical look",_prefs.invert_y,func(v): _prefs.invert_y=v)
	_slider("Mouse sensitivity",0.001,0.006,0.00025,_prefs.sensitivity,func(v): _prefs.sensitivity=v)
	_slider("Field of view",55,90,1,_prefs.fov,func(v): _prefs.fov=v)
	_slider("Master volume",0,1,0.05,_prefs.master_volume,func(v): _prefs.master_volume=v)
	_check("Show gameplay hints",_prefs.show_hints,func(v): _prefs.show_hints=v)
	_check("Fullscreen",_prefs.fullscreen,func(v): _prefs.fullscreen=v)
	_check("Subtitles",_prefs.subtitles,func(v):_prefs.subtitles=v)
	_check("Rotate minimap",_prefs.rotate_minimap,func(v): _prefs.rotate_minimap=v)
	_check("VSync",_prefs.vsync,func(v): _prefs.vsync=v)
	_select("Frame limit",["30 FPS","60 FPS","120 FPS","Unlimited"],_prefs.FPS_LIMITS.find(_prefs.fps_limit),func(i):_prefs.fps_limit=_prefs.FPS_LIMITS[i])
	_select("Window resolution",["960 × 540","1280 × 720","1600 × 900","1920 × 1080"],_prefs.resolution_index,func(i):_prefs.resolution_index=i)
	var instructions := Label.new()
	instructions.text="ON FOOT   WASD move | Mouse look | Shift sprint\nAlt walk | Space jump | C crouch | V camera\nDRIVING   F enter/exit | WASD drive | Space brake | L lights | H horn\nCOMBAT   Left mouse punch (Living World)\nWORLD   E interact | M map | Esc pause | Tab cursor / click minimap"
	instructions.add_theme_font_size_override("font_size",15)
	_settings.add_child(instructions)
	_binding_note=Label.new()
	_binding_note.text="KEY BINDINGS | Select a key to change it"
	_settings.add_child(_binding_note)
	var names:=["Move forward","Move backward","Move left","Move right","Sprint","Walk slowly","Jump / vehicle brake","Crouch","Interact","Camera view","Enter / exit vehicle","Headlights","Horn","Full map","Free cursor"]
	for i: int in range(_prefs.REMAP_ACTIONS.size()):
		var action: String=_prefs.REMAP_ACTIONS[i]
		var row:=HBoxContainer.new()
		var caption:=Label.new()
		caption.text=names[i]
		caption.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		row.add_child(caption)
		var key:=Button.new()
		key.custom_minimum_size=Vector2(155,32)
		key.text=_prefs.binding_label(action)
		key.pressed.connect(func():
			_listening=action
			_binding_note.text="Press a new key, or Esc to cancel.")
		row.add_child(key)
		_binding_buttons[action]=key
		_settings.add_child(row)
	var defaults:=Button.new()
	defaults.text="Restore default keys"
	defaults.pressed.connect(func():
		_listening=""
		_prefs.reset_bindings()
		_refresh_binding_labels()
		_binding_note.text="Default keys restored.")
	_settings.add_child(defaults)
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

func _select(caption: String,choices: Array,index: int,callback: Callable) -> void:
	var row:=HBoxContainer.new()
	var label:=Label.new()
	label.text=caption
	label.custom_minimum_size.x=180
	row.add_child(label)
	var choice:=OptionButton.new()
	for value: String in choices:choice.add_item(value)
	choice.select(index)
	choice.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	choice.item_selected.connect(func(i: int):callback.call(i);_prefs.apply();_prefs.save())
	row.add_child(choice)
	_settings.add_child(row)

func _refresh_binding_labels() -> void:
	for action: String in _binding_buttons:
		_binding_buttons[action].text=_prefs.binding_label(action)

func _input(event: InputEvent) -> void:
	if _listening.is_empty() or not is_visible_in_tree() or not is_instance_valid(_settings) or not _settings.is_visible_in_tree():
		_listening=""
		return
	if event is InputEventKey and event.pressed and not event.echo:
		get_viewport().set_input_as_handled()
		if event.physical_keycode==KEY_ESCAPE:
			_binding_note.text="Key change cancelled."
			_listening=""
			return
		if not _prefs.rebind(_listening,event.physical_keycode):
			_binding_note.text="Key already used or invalid. Choose another."
			return
		_listening=""
		_refresh_binding_labels()
		_binding_note.text="Key binding saved."
