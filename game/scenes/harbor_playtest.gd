extends Node3D
## Explicit candidate playtest; no finished animations, interiors or missions claimed.
signal leave_requested
const Layout = preload("res://core/harbor_layout.gd")
const Player = preload("res://core/street_player.gd")
const Map = preload("res://core/street_map.gd")
const Assets := "res://candidate_assets/"
var player: CharacterBody3D
var _map: Control
var _hud: CanvasLayer
var _pause_panel: PanelContainer
var _status: Label
var _paused := false
var _character := ""
var _ready_world := false

static func installed() -> bool:
	for path: String in ["street.glb","adrian.glb","maya.glb"]:
		if not ResourceLoader.exists(Assets+path,"PackedScene"):
			return false
	return true

func prepare(character: String) -> bool:
	if is_inside_tree() or character not in ["adrian","maya"] or not installed():
		return false
	var street := load(Assets+"street.glb") as PackedScene
	var model := load(Assets+character+".glb") as PackedScene
	if street == null or model == null:
		return false
	var street_node := street.instantiate() as Node3D
	if street_node == null:
		return false
	street_node.name="HarborArt"
	add_child(street_node)
	player=Player.new()
	if not player.configure(model,1.81 if character=="adrian" else 1.69):
		player.free()
		return false
	player.name="Player"
	player.position=Layout.SPAWN
	_character=character
	add_child(player)
	return true

func _ready() -> void:
	if player == null:
		return
	process_mode=Node.PROCESS_MODE_ALWAYS
	player.process_mode=Node.PROCESS_MODE_PAUSABLE
	_make_collision()
	_make_light()
	_make_hud()
	_ready_world=true
	if DisplayServer.get_name()!="headless":
		Input.mouse_mode=Input.MOUSE_MODE_CAPTURED

func _box(label: String, center: Vector3, extent: Vector3) -> void:
	var body := StaticBody3D.new()
	body.name=label
	body.collision_layer=1
	body.collision_mask=0
	var shape := CollisionShape3D.new()
	var volume := BoxShape3D.new()
	volume.size=extent
	shape.shape=volume
	body.add_child(shape)
	add_child(body)
	body.position=center

func _make_collision() -> void:
	# Authored floor and facade collision proxies match the reviewed mesh footprint.
	_box("RoadCollision",Vector3(0,-0.15,0),Vector3(6.8,0.30,32))
	for r: Rect2 in Layout.SIDEWALKS:
		_box("SidewalkCollision",Vector3(r.get_center().x,-0.075,r.get_center().y),Vector3(r.size.x,0.45,r.size.y))
	for i: int in range(Layout.BUILDINGS.size()):
		var r: Rect2=Layout.BUILDINGS[i]
		var h: float=Layout.HEIGHTS[i]
		_box("ClosedExterior%d"%i,Vector3(r.get_center().x,0.15+h*0.5,r.get_center().y),Vector3(r.size.x,h,r.size.y))
	# Temporary playtest limits at actual open ends. No invisible city extension.
	_box("NorthTestLimit",Vector3(0,1.5,-16.1),Vector3(12,3,0.2))
	_box("SouthTestLimit",Vector3(0,1.5,16.1),Vector3(12,3,0.2))
	# Furniture collisions derived from actual imported source meshes.
	for node: Node in get_node("HarborArt").find_children("*","MeshInstance3D",true,false):
		var m := node as MeshInstance3D
		var n := String(m.name).to_lower()
		if m.mesh != null and ("bench" in n or "lamp" in n):
			m.create_trimesh_collision()

func _make_light() -> void:
	var env := WorldEnvironment.new()
	env.environment=Environment.new()
	var sky := Sky.new()
	var mat := ProceduralSkyMaterial.new()
	mat.sky_top_color=Color(0.22,0.40,0.66)
	mat.sky_horizon_color=Color(0.74,0.81,0.89)
	sky.sky_material=mat
	env.environment.sky=sky
	env.environment.background_mode=Environment.BG_SKY
	env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color=Color(0.75,0.81,0.9)
	env.environment.ambient_light_energy=0.65
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees=Vector3(-52,-32,0)
	sun.light_energy=1.35
	sun.shadow_enabled=true
	add_child(sun)

func _make_hud() -> void:
	_hud=CanvasLayer.new()
	add_child(_hud)
	_map=Map.new()
	_map.actor=player
	_map.position=Vector2(20,20)
	_map.size=Vector2(200,220)
	_map.clip_contents=true
	_hud.add_child(_map)
	_status=Label.new()
	_status.position=Vector2(20,252)
	_status.text="Street physics test | %s\nWASD move · Shift sprint · Alt walk\nSpace jump · C crouch collision · V camera\nM map · Esc pause\n%s"%[("Adrian Cole" if _character=="adrian" else "Maya Bennett"),("Licensed motion retarget test" if player.motion_installed else "Motion clips not installed.")]
	_hud.add_child(_status)
	_pause_panel=PanelContainer.new()
	_pause_panel.position=Vector2(470,240)
	_pause_panel.custom_minimum_size=Vector2(340,0)
	var menu := VBoxContainer.new()
	var title := Label.new()
	title.text="Paused"
	menu.add_child(title)
	var resume := Button.new()
	resume.text="Resume"
	resume.pressed.connect(func(): _set_pause(false))
	menu.add_child(resume)
	var back := Button.new()
	back.text="Return to profiles"
	back.pressed.connect(func(): leave_requested.emit())
	menu.add_child(back)
	_pause_panel.add_child(menu)
	_hud.add_child(_pause_panel)
	_pause_panel.hide()

func _unhandled_input(event: InputEvent) -> void:
	if not _ready_world:
		return
	if event.is_action_pressed("pause_game"):
		if _map.expanded:
			_toggle_map()
		else:
			_set_pause(not _paused)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("full_map") and not _paused:
		_toggle_map()
		get_viewport().set_input_as_handled()

func _toggle_map() -> void:
	_map.toggle_full()
	_map.position=Vector2(260,65) if _map.expanded else Vector2(20,20)
	_map.size=Vector2(760,580) if _map.expanded else Vector2(200,220)
	_status.visible=not _map.expanded
	player.stop_controls()
	player.controls_enabled=not _map.expanded
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE if _map.expanded else Input.MOUSE_MODE_CAPTURED

func _set_pause(value: bool) -> void:
	_paused=value
	get_tree().paused=value
	player.stop_controls()
	player.controls_enabled=not value
	_pause_panel.visible=value
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE if value else Input.MOUSE_MODE_CAPTURED

func _exit_tree() -> void:
	if get_tree()!=null and _paused:
		get_tree().paused=false
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
