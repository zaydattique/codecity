extends Node3D
## Outdoor equipment station. Python results are validated before changing lamps.
signal completed
signal editor_changed(open: bool)
const Bridge = preload("res://core/academy_bridge.gd")
const Style = preload("res://core/ui_style.gd")
var _bridge: Node
var _lights: Array[SpotLight3D]=[]
var _panel: PanelContainer
var _code: CodeEdit
var _output: Label
var _run: Button
var _done := false
var _sound: AudioStreamPlayer
var opened := false

func setup(hud: CanvasLayer) -> void:
	_bridge=Bridge.new()
	add_child(_bridge)
	_bridge.finished.connect(_apply)
	_sound=AudioStreamPlayer.new()
	_sound.stream=_completion_tone()
	add_child(_sound)
	for z: float in [-10.0,10.0]:
		var lamp := SpotLight3D.new()
		lamp.position=Vector3(5.15,3.4,z)-global_position
		lamp.rotation_degrees=Vector3(-90,0,0)
		lamp.light_color=Color(1,0.80,0.48)
		lamp.light_energy=4.5
		lamp.spot_range=8.0
		lamp.spot_angle=55.0
		lamp.visible=false
		add_child(lamp)
		_lights.append(lamp)
	# A small physical outdoor control cabinet, not a fake enterable building.
	var cabinet := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size=Vector3(0.55,1.1,0.32)
	var material := StandardMaterial3D.new()
	material.albedo_color=Color(0.17,0.24,0.28)
	material.metallic=0.4
	mesh.material=material
	cabinet.mesh=mesh
	cabinet.position=Vector3(0,0.55,0)
	add_child(cabinet)
	var screen := MeshInstance3D.new()
	var display := BoxMesh.new()
	display.size=Vector3(0.018,0.31,0.24)
	var screen_material := StandardMaterial3D.new()
	screen_material.albedo_color=Color(0.08,0.20,0.22)
	screen_material.emission_enabled=true
	screen_material.emission=Color(0.10,0.45,0.47)
	screen_material.emission_energy_multiplier=1.3
	display.material=screen_material
	screen.mesh=display
	screen.position=Vector3(0.283,0.83,0)
	add_child(screen)
	var base := StaticBody3D.new()
	base.collision_layer=1
	base.collision_mask=0
	var shape := CollisionShape3D.new()
	var bounds := BoxShape3D.new()
	bounds.size=mesh.size
	shape.shape=bounds
	shape.position=cabinet.position
	base.add_child(shape)
	add_child(base)
	var sign := Label3D.new()
	sign.text="Lighting control"
	sign.position=Vector3(0,1.5,0)
	sign.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	sign.font_size=44
	sign.pixel_size=0.004
	add_child(sign)
	_panel=PanelContainer.new()
	_panel.position=Vector2(115,42)
	_panel.size=Vector2(1050,636)
	_panel.theme=Style.theme()
	var layout := VBoxContainer.new()
	layout.add_theme_constant_override("separation",12)
	_panel.add_child(layout)
	var eyebrow := Label.new()
	eyebrow.text="CODECITY ACADEMY   /   PYTHON FUNDAMENTALS"
	eyebrow.add_theme_font_size_override("font_size",14)
	eyebrow.add_theme_color_override("font_color",Color(0.48,0.85,0.89))
	layout.add_child(eyebrow)
	var heading := Label.new()
	heading.text="01   Restore the street lights"
	heading.add_theme_font_size_override("font_size",25)
	layout.add_child(heading)
	var desc := Label.new()
	desc.text="Two lamps are offline. Write Python using variables, range(), for, if, print() and set_lamp(id, True). Restore lamps 0 and 1 and print a status message."
	desc.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	layout.add_child(desc)
	_code=CodeEdit.new()
	_code.custom_minimum_size=Vector2(0,250)
	_code.add_theme_font_size_override("font_size",19)
	_code.add_theme_color_override("font_color",Color(0.91,0.94,0.96))
	_code.add_theme_color_override("line_number_color",Color(0.51,0.62,0.67))
	_code.size_flags_vertical=Control.SIZE_EXPAND_FILL
	_code.text="# Restore both lamps\ncount = 2\nfor lamp in range(count):\n    # Write your command here\n    print(lamp)\n"
	_code.gutters_draw_line_numbers=true
	var highlighter := CodeHighlighter.new()
	highlighter.number_color=Color(0.95,0.73,0.40)
	highlighter.symbol_color=Color(0.82,0.88,0.92)
	highlighter.function_color=Color(0.49,0.83,0.89)
	highlighter.member_variable_color=Color(0.90,0.94,0.96)
	highlighter.add_color_region("'","'",Color(0.65,0.87,0.67))
	highlighter.add_color_region("\"","\"",Color(0.65,0.87,0.67))
	highlighter.add_keyword_color("for",Color(0.66,0.76,1))
	highlighter.add_keyword_color("in",Color(0.66,0.76,1))
	highlighter.add_keyword_color("if",Color(0.66,0.76,1))
	highlighter.add_keyword_color("True",Color(0.55,0.88,0.69))
	highlighter.add_keyword_color("False",Color(0.55,0.88,0.69))
	highlighter.add_color_region("#","",Color(0.5,0.6,0.6),true)
	_code.syntax_highlighter=highlighter
	layout.add_child(_code)
	var output_panel := PanelContainer.new()
	output_panel.add_theme_stylebox_override("panel",Style.panel(Color(0.065,0.10,0.12),5,12))
	var console := VBoxContainer.new()
	output_panel.add_child(console)
	var output_heading := Label.new()
	output_heading.text="PYTHON CONSOLE"
	output_heading.add_theme_font_size_override("font_size",13)
	output_heading.add_theme_color_override("font_color",Color(0.49,0.83,0.89))
	console.add_child(output_heading)
	_output=Label.new()
	_output.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	_output.text="Python output will appear here."
	_output.custom_minimum_size=Vector2(0,58)
	console.add_child(_output)
	layout.add_child(output_panel)
	var buttons := HBoxContainer.new()
	_run=Button.new()
	_run.text="Run Python"
	_run.custom_minimum_size=Vector2(155,44)
	_run.add_theme_stylebox_override("normal",Style.panel(Color(0.12,0.40,0.44),5,10))
	_run.pressed.connect(func(): run_source(_code.text))
	buttons.add_child(_run)
	var hint := Button.new()
	hint.text="Hint"
	hint.pressed.connect(func(): _output.text="Inside the loop, call set_lamp(lamp, True). Then print a status message.")
	hint.custom_minimum_size=Vector2(100,44)
	buttons.add_child(hint)
	var spacer := Control.new()
	spacer.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	buttons.add_child(spacer)
	var close := Button.new()
	close.text="Return to street"
	close.custom_minimum_size=Vector2(180,44)
	close.pressed.connect(close_editor)
	buttons.add_child(close)
	layout.add_child(buttons)
	hud.add_child(_panel)
	_panel.hide()

func open_editor() -> void:
	if opened:return
	opened=true
	_panel.show()
	_code.grab_focus()
	editor_changed.emit(true)

func close_editor() -> void:
	if not opened or _run.disabled:return
	opened=false
	_panel.hide()
	editor_changed.emit(false)

func run_source(source: String) -> bool:
	if not opened or _run.disabled:return false
	if not _bridge.submit(source):
		_output.text="Python runtime unavailable or program exceeds 4096 bytes."
		return false
	_run.disabled=true
	_output.text="Running Python lesson..."
	return true

func _apply(result: Dictionary) -> void:
	_run.disabled=false
	var output: Variant=result.get("output","Invalid result.")
	if not output is String or output.length()>512:
		_output.text="Invalid Python result."
		return
	if result.get("ok")!=true:
		_output.text=output
		return
	var commands: Variant=result.get("commands")
	if not commands is Array or commands.size()>16:
		_output.text="Invalid command batch."
		return
	# Each run is a fresh trial. Reject the entire batch before mutating lights.
	var state: Array[bool]=[false,false]
	for command: Variant in commands:
		if not command is Dictionary or command.size()!=2 or not command.has("lamp") or not command.has("on"):
			_output.text="Invalid command."
			return
		var id: Variant=command["lamp"]
		if not (id is float or id is int) or id!=int(id) or int(id)<0 or int(id)>1 or not command["on"] is bool:
			_output.text="Invalid lamp command."
			return
		state[int(id)]=command["on"]
	for i: int in range(2):_lights[i].visible=state[i]
	_output.text=output+"\nLamps online: %d / 2"%(int(state[0])+int(state[1]))
	if state[0] and state[1] and not output.strip_edges().is_empty():
		_output.text+="\nMission complete. The street lights are restored."
		if not _done:
			_done=true
			_sound.play()
			completed.emit()

func lamps_online() -> bool:
	return _lights.size()==2 and _lights[0].visible and _lights[1].visible

# Original short two-tone feedback, no third-party sound asset.
func _completion_tone() -> AudioStreamWAV:
	var samples := PackedByteArray()
	var rate := 22050
	var count := 6615
	samples.resize(count*2)
	for i: int in range(count):
		var t := float(i)/rate
		var freq := 660.0 if t<0.14 else 880.0
		var env := minf(1.0,t/0.025)*maxf(0.0,minf(1.0,(0.3-t)/0.06))
		var val := int(sin(TAU*freq*t)*env*4800)
		samples.encode_s16(i*2,val)
	var clip := AudioStreamWAV.new()
	clip.format=AudioStreamWAV.FORMAT_16_BITS
	clip.mix_rate=rate
	clip.data=samples
	return clip
