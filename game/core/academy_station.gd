extends Node3D
## Outdoor equipment station. Python results are validated before changing lamps.
signal completed
signal exercise_completed(id: String)
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
var _lesson := 0
var _lesson_picker: OptionButton
var _description: Label
var _practice_done: Dictionary = {}
const LESSON_TITLES := ["01   Power restoration | for", "02   North circuit | variables", "03   South circuit | conditions", "04   Dispatch notice | print", "05   Circuit inspection | while", "06   Maintenance schedule | lists", "07   Backup power | logic"]
const LESSON_IDS := ["street_lighting","north_circuit","south_circuit","dispatch_notice","circuit_inspection","maintenance_schedule","backup_power"]
const LESSON_DESCRIPTIONS := [
	"Harbor's two street lights are offline. Restore both with a for loop and send a status message.",
	"Isolate the north circuit. Store its ID and power state in variables. Turn on lamp 0 only.",
	"Inspect each circuit. Use an if condition to enable lamp 1 only.",
	"Send a dispatch message to the cabinet's physical display. Leave both test circuits off.",
	"Inspect both circuits with a while loop. Increment the counter until both lamps are online.",
	"Use a list containing lamp IDs 0 and 1. Read the IDs by index and restore both circuits.",
	"Use arithmetic and Boolean logic to decide whether backup power can supply both lamps. Each lamp needs 30 units; available power is 80."]
const LESSON_STARTERS := [
	"# Restore both lamps\ncount = 2\nfor lamp in range(count):\n    # Write your command here\n    print(lamp)\n",
	"# Use variables to power lamp 0\nlamp = 0\npower = True\n# Write your command here\n",
	"# Power only lamp 1\nfor lamp in range(2):\n    if lamp == 1:\n        # Write your command here\n        print(lamp)\n",
	"# Send a message to dispatch\n# Use print() to send the notice\n",
	"lamp = 0\nwhile lamp < 2:\n    # Power the current lamp\n    lamp = lamp + 1\nprint('Inspection complete')\n",
	"schedule = [0, 1]\n# Read each list item by index\nprint('Schedule complete')\n",
	"available = 80\nrequired = 30 * 2\nbackup_ready = True\n# Check capacity and readiness\n"]
const LESSON_HINTS := [
	"Inside the loop, call set_lamp(lamp, True). Then print a status message.",
	"Call set_lamp(lamp, power), then print a message. Leave lamp 1 off.",
	"Inside the if block, call set_lamp(lamp, True). Leave lamp 0 off.",
	"Try print('Harbor ready'). Your actual output appears on the cabinet.",
	"Use set_lamp(lamp, True) inside the while loop, before incrementing lamp.",
	"Try set_lamp(schedule[0], True) and set_lamp(schedule[1], True).",
	"Use if available >= required and backup_ready: then switch on both lamps and print a status."]
const LESSON_REQUIREMENTS := [["for"],["assignment"],["if"],["print"],["while"],["list","index"],["arithmetic","boolean","if"]]
const TARGETS := [[true,true],[true,false],[false,true],[false,false],[true,true],[true,true],[true,true]]
var _progress: Label
var _circuit_status: Label
var _display: Label3D
var _assist: OptionButton
var _hint: Button
var _drafts: Dictionary={}
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
	sign.text="Harbor utilities"
	sign.position=Vector3(0,1.5,0)
	sign.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	sign.font_size=44
	sign.pixel_size=0.004
	add_child(sign)
	_display=Label3D.new()
	_display.text="STANDBY"
	_display.position=Vector3(0,1.19,0)
	_display.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	_display.font_size=26
	_display.pixel_size=0.003
	_display.modulate=Color(0.45,0.95,0.86)
	add_child(_display)
	_panel=PanelContainer.new()
	_panel.position=Vector2(62,36)
	_panel.size=Vector2(1156,648)
	_panel.theme=Style.theme()
	var layout := VBoxContainer.new()
	layout.add_theme_constant_override("separation",12)
	_panel.add_child(layout)
	var eyebrow := Label.new()
	eyebrow.text="CODECITY ACADEMY   /   PYTHON FUNDAMENTALS"
	eyebrow.add_theme_font_size_override("font_size",14)
	eyebrow.add_theme_color_override("font_color",Color(0.48,0.85,0.89))
	layout.add_child(eyebrow)
	_progress=Label.new()
	_progress.add_theme_color_override("font_color",Color(0.65,0.83,0.82))
	layout.add_child(_progress)
	_lesson_picker=OptionButton.new()
	_lesson_picker.add_theme_font_size_override("font_size",22)
	for title: String in LESSON_TITLES:
		_lesson_picker.add_item(title)
	layout.add_child(_lesson_picker)
	_description=Label.new()
	_description.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	_description.text=LESSON_DESCRIPTIONS[0]
	layout.add_child(_description)
	var workspace:=HBoxContainer.new()
	workspace.size_flags_vertical=Control.SIZE_EXPAND_FILL
	workspace.add_theme_constant_override("separation",16)
	layout.add_child(workspace)
	var left:=VBoxContainer.new()
	left.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	workspace.add_child(left)
	var right:=VBoxContainer.new()
	right.custom_minimum_size=Vector2(345,0)
	right.add_theme_constant_override("separation",10)
	workspace.add_child(right)
	_assist=OptionButton.new()
	for title: String in ["Guided","Independent","Challenge"]:_assist.add_item(title)
	right.add_child(_assist)
	_assist.item_selected.connect(_set_assistance)
	_circuit_status=Label.new()
	_circuit_status.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	_circuit_status.add_theme_color_override("font_color",Color(0.60,0.89,0.78))
	right.add_child(_circuit_status)
	_code=CodeEdit.new()
	_code.custom_minimum_size=Vector2(0,280)
	_code.add_theme_font_size_override("font_size",19)
	_code.add_theme_color_override("font_color",Color(0.91,0.94,0.96))
	_code.add_theme_color_override("line_number_color",Color(0.51,0.62,0.67))
	_code.size_flags_vertical=Control.SIZE_EXPAND_FILL
	_code.text=LESSON_STARTERS[0]
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
	left.add_child(_code)
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
	var scroll:=ScrollContainer.new()
	scroll.custom_minimum_size=Vector2(0,150)
	scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL
	_output.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	scroll.add_child(_output)
	console.add_child(scroll)
	output_panel.size_flags_vertical=Control.SIZE_EXPAND_FILL
	right.add_child(output_panel)
	var buttons := HBoxContainer.new()
	_run=Button.new()
	_run.text="Run Python"
	_run.custom_minimum_size=Vector2(155,44)
	_run.add_theme_stylebox_override("normal",Style.panel(Color(0.12,0.40,0.44),5,10))
	_run.pressed.connect(func(): run_source(_code.text))
	buttons.add_child(_run)
	_hint=Button.new()
	_hint.text="Hint"
	_hint.pressed.connect(func(): _output.text=LESSON_HINTS[_lesson])
	_hint.custom_minimum_size=Vector2(100,44)
	buttons.add_child(_hint)
	var reset:=Button.new()
	reset.text="Reset code"
	reset.pressed.connect(func():
		if not _run.disabled:_code.text=LESSON_STARTERS[_lesson] if _assist.selected==0 else "")
	buttons.add_child(reset)
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
	_lesson_picker.item_selected.connect(_select_lesson)
	_refresh_progress()

func _select_lesson(index: int) -> void:
	if _run.disabled or index<0 or index>=LESSON_TITLES.size():
		_lesson_picker.select(_lesson)
		return
	if index==_lesson:return
	_drafts[_lesson]=_code.text
	_lesson=index
	_lesson_picker.select(index)
	_description.text=LESSON_DESCRIPTIONS[index]
	_code.text=_drafts.get(index,LESSON_STARTERS[index] if _assist.selected==0 else "")
	_output.text="Practice completed earlier. Run again to test your code." if _practice_done.has(index) else "Run your code to test the lamps. Each run starts with both lamps off."

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
	_lesson_picker.disabled=true
	_assist.disabled=true
	_hint.disabled=true
	_output.text="Running Python lesson..."
	return true

func _apply(result: Dictionary) -> void:
	_run.disabled=false
	_lesson_picker.disabled=false
	_assist.disabled=false
	_hint.disabled=_assist.selected==2
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
	_display.text=output.strip_edges().replace("\n"," ").left(42) if not output.strip_edges().is_empty() else "NO MESSAGE"
	_refresh_progress()
	var concepts: Variant=result.get("concepts",[])
	var matches: bool=state[0]==TARGETS[_lesson][0] and state[1]==TARGETS[_lesson][1]
	var taught:=true
	if not concepts is Array:taught=false
	else:
		for concept: String in LESSON_REQUIREMENTS[_lesson]:
			if not concepts.has(concept):taught=false
	if not matches or output.strip_edges().is_empty() or not taught:
		_output.text+="\nTarget not met. Check the required Python concept and circuit state."
		return
	_output.text+="\nAssignment complete. Results applied to Harbor utilities."
	if not _practice_done.has(_lesson):
		_practice_done[_lesson]=true
		_sound.play()
		exercise_completed.emit(LESSON_IDS[_lesson])
		if _lesson==0:
			_done=true
			completed.emit()
	_refresh_progress()

func _set_assistance(index: int) -> void:
	_hint.visible=index!=2
	_hint.disabled=index==2
	_description.text=LESSON_DESCRIPTIONS[_lesson]

func restore_progress(ids: Array) -> void:
	for i: int in range(LESSON_IDS.size()):
		if ids.has(LESSON_IDS[i]):_practice_done[i]=true
	_done=_practice_done.has(0)
	_refresh_progress()

func _refresh_progress() -> void:
	_progress.text="%d / %d assignments completed"%[_practice_done.size(),LESSON_IDS.size()]
	for i: int in range(LESSON_IDS.size()):
		_lesson_picker.set_item_text(i,LESSON_TITLES[i]+("  |  Complete" if _practice_done.has(i) else ""))
	_circuit_status.text="LIVE CIRCUITS\nNorth  |  %s\nSouth  |  %s"%["ONLINE" if _lights[0].visible else "OFFLINE","ONLINE" if _lights[1].visible else "OFFLINE"]

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
