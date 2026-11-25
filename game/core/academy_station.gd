extends Node3D
## Outdoor equipment station. Python results are validated before changing lamps.
signal completed
signal editor_changed(open: bool)
const Bridge = preload("res://core/academy_bridge.gd")
var _bridge: Node
var _lights: Array[SpotLight3D]=[]
var _panel: PanelContainer
var _code: CodeEdit
var _output: Label
var _run: Button
var _done := false
var opened := false

func setup(hud: CanvasLayer) -> void:
	_bridge=Bridge.new()
	add_child(_bridge)
	_bridge.finished.connect(_apply)
	for z: float in [-10.0,10.0]:
		var lamp := SpotLight3D.new()
		lamp.position=Vector3(5.15,3.4,z)
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
	var sign := Label3D.new()
	sign.text="ACADEMY\nLighting control"
	sign.position=Vector3(0,1.5,0)
	sign.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	sign.font_size=44
	sign.pixel_size=0.004
	add_child(sign)
	_panel=PanelContainer.new()
	_panel.position=Vector2(150,55)
	_panel.size=Vector2(980,610)
	var layout := VBoxContainer.new()
	layout.add_theme_constant_override("separation",12)
	_panel.add_child(layout)
	var heading := Label.new()
	heading.text="ACADEMY  /  01  /  RESTORE THE STREET LIGHTS"
	heading.add_theme_font_size_override("font_size",25)
	layout.add_child(heading)
	var desc := Label.new()
	desc.text="Two lamps are offline. Write Python using variables, range(), for, if, print() and set_lamp(id, True). Restore lamps 0 and 1 and print a status message."
	desc.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	layout.add_child(desc)
	_code=CodeEdit.new()
	_code.custom_minimum_size=Vector2(0,260)
	_code.size_flags_vertical=Control.SIZE_EXPAND_FILL
	_code.text="# Restore both lamps\ncount = 2\nfor lamp in range(count):\n    # Write your command here\n    print(lamp)\n"
	_code.gutters_draw_line_numbers=true
	var highlighter := CodeHighlighter.new()
	highlighter.add_keyword_color("for",Color(0.66,0.76,1))
	highlighter.add_keyword_color("in",Color(0.66,0.76,1))
	highlighter.add_keyword_color("if",Color(0.66,0.76,1))
	highlighter.add_keyword_color("True",Color(0.55,0.88,0.69))
	highlighter.add_keyword_color("False",Color(0.55,0.88,0.69))
	highlighter.add_color_region("#","",Color(0.5,0.6,0.6),true)
	_code.syntax_highlighter=highlighter
	layout.add_child(_code)
	_output=Label.new()
	_output.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	_output.text="Python output will appear here."
	_output.custom_minimum_size=Vector2(0,75)
	layout.add_child(_output)
	var buttons := HBoxContainer.new()
	_run=Button.new()
	_run.text="Run Python"
	_run.pressed.connect(func(): run_source(_code.text))
	buttons.add_child(_run)
	var hint := Button.new()
	hint.text="Hint"
	hint.pressed.connect(func(): _output.text="Inside the loop, call set_lamp(lamp, True). Then print a status message.")
	buttons.add_child(hint)
	var close := Button.new()
	close.text="Return to street"
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
			completed.emit()

func lamps_online() -> bool:
	return _lights.size()==2 and _lights[0].visible and _lights[1].visible
