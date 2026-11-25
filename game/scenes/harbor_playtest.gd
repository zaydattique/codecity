extends Node3D
@onready var _prefs: Node = get_node("/root/GameSettings")
## Explicit candidate playtest; no finished animations, interiors or missions claimed.
signal leave_requested
const Layout = preload("res://core/harbor_layout.gd")
const Player = preload("res://core/street_player.gd")
const Map = preload("res://core/street_map.gd")
const Car = preload("res://core/street_vehicle.gd")
const Interaction = preload("res://core/world_interaction.gd")
const Academy = preload("res://core/academy_station.gd")
const Crowd = preload("res://core/npc_director.gd")
var crowd: Node3D
var _enable_npcs := true
const PauseSettings = preload("res://core/pause_settings.gd")
const Style = preload("res://core/ui_style.gd")
var _cursor_unlocked := false
var _pause_button: Button
signal academy_completed
var academy_mode := false
var station: Node3D
var _editor_open := false
var vehicle: VehicleBody3D
var _vehicle_hint: Label
var _driving := false
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

func prepare(character: String, education: bool=false, enable_npcs: bool=true) -> bool:
	academy_mode=education
	_enable_npcs=enable_npcs
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
	if not academy_mode and ResourceLoader.exists(Assets+"coupe.glb","PackedScene"):
		var coupe := load(Assets+"coupe.glb") as PackedScene
		vehicle=Car.new()
		if not vehicle.configure(coupe):
			vehicle.free()
			vehicle=null
			return false
		vehicle.name="SportsCoupe"
		vehicle.position=Vector3(-1.65,0.2,-1.0)
		vehicle.rotation.y=PI
		add_child(vehicle)
	return true

func _ready() -> void:
	if player == null:
		return
	process_mode=Node.PROCESS_MODE_ALWAYS
	player.process_mode=Node.PROCESS_MODE_PAUSABLE
	_make_collision()
	_make_light()
	_make_hud()
	if academy_mode:
		station=Academy.new()
		station.position=Vector3(-5.25,0.15,5.0)
		add_child(station)
		station.setup(_hud)
		station.completed.connect(func():
			academy_completed.emit()
			if is_instance_valid(crowd):crowd.perceive("lamp_restored",station.global_position,8.0))
		station.editor_changed.connect(_academy_editor)
		# Dusk lighting makes the real restored fixtures visibly affect the street.
		for node: Node in get_children():
			if node is DirectionalLight3D:node.light_energy=0.22
			if node is WorldEnvironment:node.environment.ambient_light_energy=0.23
	if _enable_npcs and Crowd.installed():
		var director := Crowd.new()
		if director.prepare(player,vehicle):
			crowd=director
			add_child(crowd)
		else:director.free()
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
	_make_road_closure(-16.0)
	_make_road_closure(16.0)
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
	_map.academy=academy_mode
	_map.position=Vector2(20,480)
	_map.size=Vector2(224,220)
	_map.clip_contents=true
	if DisplayServer.get_name()!="headless":
		_make_overhead_map()
	_hud.add_child(_map)
	_status=Label.new()
	_status.position=Vector2(20,20)
	_update_actor_hud()
	_hud.add_child(_status)
	_vehicle_hint=Label.new()
	_vehicle_hint.position=Vector2(20,435)
	_hud.add_child(_vehicle_hint)
	_vehicle_hint.visible=vehicle!=null
	_pause_button=Button.new()
	_pause_button.text="II   Pause"
	_pause_button.theme=Style.theme()
	_pause_button.position=Vector2(1130,20)
	_pause_button.custom_minimum_size=Vector2(130,42)
	_pause_button.pressed.connect(func(): _set_pause(true))
	_hud.add_child(_pause_button)
	_pause_panel=PanelContainer.new()
	_pause_panel.theme=Style.theme()
	_pause_panel.position=Vector2(315,30)
	_pause_panel.custom_minimum_size=Vector2(650,0)
	var menu := PauseSettings.new()
	menu.resume_requested.connect(func(): _set_pause(false))
	menu.leave_requested.connect(func(): leave_requested.emit())
	_pause_panel.add_child(menu)
	_hud.add_child(_pause_panel)
	_pause_panel.hide()
	_prefs.changed.connect(_refresh_hints)
	_refresh_hints()

func _refresh_hints() -> void:
	_status.visible=_prefs.show_hints and not _paused and not _editor_open and not _map.expanded

func _unhandled_input(event: InputEvent) -> void:
	if not _ready_world:return
	if _editor_open:
		if event.is_action_pressed("pause_game"):
			station.close_editor()
			get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("menu_cursor") and not _paused and not _map.expanded:
		_cursor_unlocked=not _cursor_unlocked
		player.stop_controls()
		_sync_controls()
		Input.mouse_mode=Input.MOUSE_MODE_VISIBLE if _cursor_unlocked else Input.MOUSE_MODE_CAPTURED
		get_viewport().set_input_as_handled()
		return
	if academy_mode and event.is_action_pressed("interact") and not _paused and not _map.expanded and not _cursor_unlocked and Interaction.within_range(player,station,2.5):
		station.open_editor()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("interact") and is_instance_valid(crowd) and not _driving and not _paused and not _map.expanded and not _cursor_unlocked:
		crowd.perceive("greet",player.global_position,2.5)
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("vehicle_horn") and is_instance_valid(crowd) and _driving and not _paused and not _map.expanded:
		crowd.perceive("horn",vehicle.global_position,8.0)
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("pause_game"):
		if _map.expanded:
			_toggle_map()
		else:
			_set_pause(not _paused)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("vehicle_toggle") and not _paused and not _map.expanded and not _cursor_unlocked:
		try_toggle_vehicle()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("vehicle_lights") and _driving and not _paused and not _map.expanded and not _cursor_unlocked:
		vehicle.toggle_headlights()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("full_map") and not _paused:
		_toggle_map()
		get_viewport().set_input_as_handled()

func _toggle_map() -> void:
	_map.toggle_full()
	_cursor_unlocked=false
	_map.position=Vector2(160,55) if _map.expanded else Vector2(20,480)
	_map.size=Vector2(960,610) if _map.expanded else Vector2(224,220)
	_refresh_hints()
	_pause_button.visible=not _map.expanded
	player.stop_controls()
	_sync_controls()
	_vehicle_hint.visible=vehicle!=null and not _map.expanded
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE if _map.expanded else Input.MOUSE_MODE_CAPTURED

func _set_pause(value: bool) -> void:
	_paused=value
	_cursor_unlocked=false
	get_tree().paused=value
	player.stop_controls()
	_sync_controls()
	_pause_panel.visible=value
	_pause_button.visible=not value
	_refresh_hints()
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE if value else Input.MOUSE_MODE_CAPTURED

func _exit_tree() -> void:
	if get_tree()!=null and _paused:
		get_tree().paused=false
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE

func _process(_delta: float) -> void:
	if not _ready_world:return
	if _paused:return
	if academy_mode:
		_vehicle_hint.visible=not _editor_open and not _paused and not _map.expanded
		_vehicle_hint.text="E  Lighting control" if Interaction.within_range(player,station,2.5) else "Restore street lighting | Walk to the Academy cabinet"
		return
	if vehicle==null or not vehicle.built:return
	if _driving:
		_vehicle_hint.text="%.0f km/h"%vehicle.speed_kmh()
		_vehicle_hint.visible=not _map.expanded
	elif player.global_position.distance_to(vehicle.entry_point())<=2.1:
		_vehicle_hint.text="F  Enter coupe" if vehicle.stopped() else "Wait until the coupe stops."
	else:
		_vehicle_hint.text=""

func _update_actor_hud() -> void:
	if _status==null:
		return
	var name := "Adrian Cole" if _character=="adrian" else "Maya Bennett"
	if _driving:
		_status.text="Harbor Boulevard | %s\nVehicle controls\nM map · Esc pause\nCandidate driving test"%name
	else:
		_status.text="Harbor Boulevard | %s\nWASD move · Shift sprint · Alt walk\nSpace jump · C crouch · V camera\nM map · Esc pause"%name

func _sync_controls() -> void:
	_update_actor_hud()
	var enabled: bool=not _paused and not _map.expanded and not _editor_open and not _cursor_unlocked
	player.controls_enabled=enabled and not _driving
	if vehicle!=null:
		vehicle.input_enabled=enabled and _driving

func try_toggle_vehicle() -> bool:
	if not _ready_world or _paused or _map.expanded or _cursor_unlocked or vehicle==null or not vehicle.stopped():
		return false
	if _driving:
		var exit := _safe_exit()
		if not exit.is_finite():
			return false
		vehicle.set_occupied(false)
		player.leave_vehicle(exit)
		_driving=false
		_map.actor=player
		_sync_controls()
		return true
	if not Interaction.within_range(player,vehicle,3.2) or not player.is_on_floor() or player.global_position.distance_to(vehicle.entry_point())>2.1:
		return false
	var start := player.global_position+Vector3.UP*0.85
	var query := PhysicsRayQueryParameters3D.create(start,vehicle.entry_point(),1,[player.get_rid(),vehicle.get_rid()])
	if not get_world_3d().direct_space_state.intersect_ray(query).is_empty():
		return false
	player.board_vehicle()
	vehicle.set_occupied(true)
	_driving=true
	_map.actor=vehicle
	_sync_controls()
	return true

func _safe_exit() -> Vector3:
	var space := get_world_3d().direct_space_state
	for guess: Vector3 in vehicle.exit_candidates():
		var ray := PhysicsRayQueryParameters3D.create(guess+Vector3.UP,guess-Vector3.UP*1.8,1,[vehicle.get_rid(),player.get_rid()])
		var floor_hit := space.intersect_ray(ray)
		if floor_hit.is_empty() or floor_hit.normal.y<0.7:
			continue
		var feet: Vector3=floor_hit.position+Vector3.UP*0.035
		if not Layout.street_contains(feet) or not vehicle.clear_of_door(feet):
			continue
		var capsule := CapsuleShape3D.new()
		capsule.radius=0.29
		capsule.height=player.height_m
		var shape := PhysicsShapeQueryParameters3D.new()
		shape.shape=capsule
		shape.transform=Transform3D(Basis.IDENTITY,feet+Vector3.UP*capsule.height*0.5)
		shape.collision_mask=13
		shape.exclude=[player.get_rid()]
		if space.intersect_shape(shape,1).is_empty():
			return feet
	return Vector3.INF

func _academy_editor(value: bool) -> void:
	_editor_open=value
	_cursor_unlocked=false
	player.stop_controls()
	_sync_controls()
	_map.visible=not value
	_refresh_hints()
	_pause_button.visible=not value
	_vehicle_hint.visible=not value
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE if value else Input.MOUSE_MODE_CAPTURED

func _make_road_closure(z: float) -> void:
	# Honest visible development boundary, matching the existing collider.
	# Authored panels are road-closure equipment, not substitute city buildings.
	var material := StandardMaterial3D.new()
	material.albedo_color=Color(0.23,0.28,0.30)
	material.roughness=0.88
	var stripe := StandardMaterial3D.new()
	stripe.albedo_color=Color(0.85,0.50,0.12)
	for i: int in range(6):
		var barrier := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size=Vector3(1.96,1.5,0.14)
		mesh.material=material
		barrier.mesh=mesh
		barrier.position=Vector3(-5+i*2,0.75,z)
		add_child(barrier)
		var band := MeshInstance3D.new()
		var marking := BoxMesh.new()
		marking.size=Vector3(1.94,0.17,0.16)
		marking.material=stripe
		band.mesh=marking
		band.position=barrier.position+Vector3.UP*0.48
		add_child(band)
	var notice := Label3D.new()
	notice.text="ROAD CLOSED"
	notice.font_size=68
	notice.pixel_size=0.006
	notice.outline_size=5
	notice.position=Vector3(0,1.05,z-signf(z)*0.10)
	notice.rotation.y=PI if z>0 else 0.0
	add_child(notice)

func _make_overhead_map() -> void:
	var overhead := SubViewport.new()
	overhead.size=Vector2i(512,512)
	overhead.render_target_update_mode=SubViewport.UPDATE_DISABLED
	overhead.world_3d=get_viewport().world_3d
	add_child(overhead)
	# Exclude dynamic actors from the static map image. Their markers stay live.
	for actor: Node3D in [player,vehicle]:
		if actor!=null:
			for node: Node in actor.find_children("*","MeshInstance3D",true,false):
				(node as MeshInstance3D).layers=2
	var camera := Camera3D.new()
	camera.projection=Camera3D.PROJECTION_ORTHOGONAL
	camera.size=36
	camera.cull_mask=1
	camera.position=Vector3(0,60,0)
	camera.rotation_degrees=Vector3(-90,0,0)
	camera.far=100
	overhead.add_child(camera)
	camera.current=true
	_map.aerial=overhead.get_texture()
	overhead.render_target_update_mode=SubViewport.UPDATE_ONCE
