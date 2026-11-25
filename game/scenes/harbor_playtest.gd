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
signal story_completed
const STORY_CONTACT := "nora"
var _story_stage := 0
var _story_start := Vector3.ZERO
var _story_label: Label
var _story_panel: PanelContainer
const STORY_OBJECTIVES := [
	"Nora is waiting for an update. Enter the parked coupe (F).",
	"Take the coupe for a short test drive (4 m).",
	"Stop safely and exit the coupe (F).",
	"Find Nora and report the test drive (E).",
	"Nora: Good. We can get the car back on the road."]
var _story_heading: Label
var _story_sound: AudioStreamPlayer
var _horn: AudioStreamPlayer3D
var _story_marker: Label3D
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
var _facade_counts: Array[int]=[0,0,0,0]
var _court_material: Material

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
	_relayout_art()
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
			if node is DirectionalLight3D:
				node.light_energy=0.32
				node.light_color=Color(1.0,0.76,0.55)
				node.rotation_degrees=Vector3(-16,-32,0)
			if node is WorldEnvironment:
				node.environment.ambient_light_energy=0.30
				node.environment.ambient_light_color=Color(0.61,0.71,0.91)
				var sky_material:=node.environment.sky.sky_material as ProceduralSkyMaterial
				sky_material.sky_top_color=Color(0.13,0.22,0.39)
				sky_material.sky_horizon_color=Color(0.68,0.46,0.39)
	if _enable_npcs and Crowd.installed():
		var director := Crowd.new()
		if director.prepare(player,vehicle):
			crowd=director
			add_child(crowd)
			# Exclude moving NPC geometry from the static aerial map.
			for node: Node in crowd.find_children("*","MeshInstance3D",true,false):
				(node as MeshInstance3D).layers=2
		else:director.free()
	if vehicle!=null:
		_horn=AudioStreamPlayer3D.new()
		_horn.stream=_feedback_clip(true)
		_horn.max_distance=18.0
		_horn.process_mode=Node.PROCESS_MODE_PAUSABLE
		vehicle.add_child(_horn)
	if not academy_mode and vehicle!=null and is_instance_valid(crowd):
		_setup_story()
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

# Move each reviewed facade assembly as a unit. Keep doors/windows and UVs intact.
func _relayout_art() -> void:
	var palette: Array[Color]=[Color(0.83,0.91,1.0),Color(1.0,0.84,0.65),Color(0.77,0.87,0.77),Color(1.0,0.74,0.64)]
	var cache: Dictionary={}
	for node: Node in get_node("HarborArt").find_children("*","MeshInstance3D",true,false):
		var m:=node as MeshInstance3D
		if m.mesh==null:continue
		var name_lower:=String(m.name).to_lower()
		if name_lower.begins_with("sidewalk") and _court_material==null:
			_court_material=m.get_active_material(0)
		for i: int in range(Layout.BUILDING_IDS.size()):
			if not name_lower.begins_with(Layout.BUILDING_IDS[i]):continue
			_facade_counts[i]+=1
			var depth: float=Layout.BUILDING_DEPTH_SCALE[i]
			var front: float=6.0 if i<2 else -6.0
			var reshape:=Transform3D(Basis.from_scale(Vector3(depth,1,1)),Vector3(front*(1.0-depth),0,0))
			m.global_transform=reshape*m.global_transform
			m.global_position+=Layout.BUILDING_OFFSETS[i]
			# Distinct exterior finish on wall surfaces only, not windows or doors.
			if "wall_" in name_lower or "crown_" in name_lower:
				for s: int in range(m.mesh.get_surface_count()):
					var original:=m.get_active_material(s)
					if not original is StandardMaterial3D:continue
					var key: String="%d:%d"%[i,original.get_instance_id()]
					if not cache.has(key):
						var finish:=original.duplicate() as StandardMaterial3D
						finish.albedo_color*=palette[i]
						cache[key]=finish
					m.set_surface_override_material(s,cache[key])
			break
	for count: int in _facade_counts:
		if count==0:push_error("Reviewed facade group not found; layout mismatch")
	if _court_material==null:push_error("Reviewed sidewalk paving not found; court material unavailable")
	for r: Rect2 in Layout.COURTS:
		var tile:=MeshInstance3D.new()
		var plane:=PlaneMesh.new()
		plane.size=r.size
		if _court_material is StandardMaterial3D:
			var paving:=_court_material.duplicate() as StandardMaterial3D
			paving.uv1_scale=Vector3(r.size.x/1.8,r.size.y/1.8,1)
			plane.material=paving
		else:plane.material=_court_material
		tile.mesh=plane
		tile.position=Vector3(r.get_center().x,0.15,r.get_center().y)
		add_child(tile)

func _make_collision() -> void:
	# Authored floor and facade collision proxies match the reviewed mesh footprint.
	_box("RoadCollision",Vector3(0,-0.15,0),Vector3(6.8,0.30,32))
	for r: Rect2 in Layout.SIDEWALKS:
		_box("SidewalkCollision",Vector3(r.get_center().x,-0.075,r.get_center().y),Vector3(r.size.x,0.45,r.size.y))
	for r: Rect2 in Layout.COURTS:
		_box("CourtCollision",Vector3(r.get_center().x,-0.075,r.get_center().y),Vector3(r.size.x,0.45,r.size.y))
	for i: int in range(Layout.BUILDINGS.size()):
		var r: Rect2=Layout.BUILDINGS[i]
		var h: float=Layout.HEIGHTS[i]
		_box("ClosedExterior%d"%i,Vector3(r.get_center().x,0.15+h*0.5,r.get_center().y),Vector3(r.size.x,h,r.size.y))
	# Existing road closures remain visible; the perimeter is a visible rail fence.
	_make_block_fence()
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

func _make_block_fence() -> void:
	var material:=StandardMaterial3D.new()
	material.albedo_color=Color(0.27,0.31,0.32)
	material.metallic=0.65
	material.roughness=0.53
	for x: float in [-20.0,20.0]:
		_box("BlockBoundary",Vector3(x,1.5,0),Vector3(0.2,3,36))
		_fence_rail(Vector3(x,0.65,0),Vector3(0.10,0.10,36),material)
		_fence_rail(Vector3(x,1.2,0),Vector3(0.10,0.10,36),material)
		for z: int in range(-18,19,3):
			_fence_rail(Vector3(x,0.65,z),Vector3(0.13,1.3,0.13),material)
	for z: float in [-18.0,18.0]:
		_box("BlockBoundary",Vector3(0,1.5,z),Vector3(40,3,0.2))
		_fence_rail(Vector3(0,0.65,z),Vector3(40,0.10,0.10),material)
		_fence_rail(Vector3(0,1.2,z),Vector3(40,0.10,0.10),material)
		for x: int in range(-20,21,4):
			_fence_rail(Vector3(x,0.65,z),Vector3(0.13,1.3,0.13),material)

func _fence_rail(center: Vector3,extent: Vector3,material: Material) -> void:
	var rail:=MeshInstance3D.new()
	var mesh:=BoxMesh.new()
	mesh.size=extent
	mesh.material=material
	rail.mesh=mesh
	rail.position=center
	add_child(rail)

func _make_light() -> void:
	var env := WorldEnvironment.new()
	env.environment=Environment.new()
	var sky := Sky.new()
	var mat := ProceduralSkyMaterial.new()
	mat.sky_top_color=Color(0.18,0.35,0.57)
	mat.sky_horizon_color=Color(0.78,0.83,0.88)
	sky.sky_material=mat
	env.environment.sky=sky
	env.environment.background_mode=Environment.BG_SKY
	env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color=Color(0.75,0.81,0.9)
	env.environment.ambient_light_energy=0.65
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees=Vector3(-52,-32,0)
	sun.light_energy=1.25
	sun.light_color=Color(1.0,0.93,0.83)
	sun.shadow_enabled=true
	add_child(sun)

func _make_hud() -> void:
	_hud=CanvasLayer.new()
	add_child(_hud)
	_map=Map.new()
	_map.actor=player
	_map.academy=academy_mode
	_map.rotate_with_actor=_prefs.rotate_minimap
	_map.expand_requested.connect(func():
		if not _paused and not _editor_open:_toggle_map())
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
	_map.rotate_with_actor=_prefs.rotate_minimap
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
	if event.is_action_pressed("interact") and _try_story_contact():
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("interact") and is_instance_valid(crowd) and not _driving and not _paused and not _map.expanded and not _cursor_unlocked:
		crowd.perceive("greet",player.global_position,2.5)
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("vehicle_horn") and _driving and not _paused and not _map.expanded and not _cursor_unlocked:
		if is_instance_valid(_horn):_horn.play()
		if is_instance_valid(crowd):crowd.perceive("horn",vehicle.global_position,8.0)
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
	_update_story()
	if _paused:return
	if academy_mode:
		_vehicle_hint.visible=not _editor_open and not _paused and not _map.expanded
		_vehicle_hint.text="E  Harbor utilities" if Interaction.within_range(player,station,2.5) else "Harbor utilities | Follow the map marker"
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
		_status.text="Harbor Boulevard | %s\nVehicle controls\nM map · Esc pause"%name
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
		if _story_stage==2:_story_stage=3
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
	if _story_stage==0 and is_instance_valid(_story_label):
		_story_start=vehicle.global_position
		_story_stage=1
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
	camera.size=Layout.MAP_EXTENT
	camera.cull_mask=1
	camera.position=Vector3(0,60,0)
	camera.rotation_degrees=Vector3(-90,0,0)
	camera.far=100
	overhead.add_child(camera)
	camera.current=true
	_map.aerial=overhead.get_texture()
	overhead.render_target_update_mode=SubViewport.UPDATE_ONCE

# A New Beginning uses the actual car and existing NPC.
func _setup_story() -> void:
	_story_panel=PanelContainer.new()
	_story_panel.position=Vector2(20,120)
	_story_panel.custom_minimum_size=Vector2(350,0)
	_story_panel.add_theme_stylebox_override("panel",Style.panel(Color(0.035,0.055,0.075,0.93),6,12))
	var layout:=VBoxContainer.new()
	layout.add_theme_constant_override("separation",5)
	_story_panel.add_child(layout)
	_story_heading=Label.new()
	_story_heading.add_theme_font_size_override("font_size",13)
	_story_heading.add_theme_color_override("font_color",Color(0.96,0.82,0.52))
	layout.add_child(_story_heading)
	_story_label=Label.new()
	_story_label.custom_minimum_size=Vector2(326,0)
	_story_label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	_story_label.add_theme_font_size_override("font_size",18)
	_story_label.add_theme_color_override("font_color",Color(0.96,0.82,0.52))
	_story_label.add_theme_color_override("font_shadow_color",Color(0.02,0.03,0.04))
	_story_label.add_theme_constant_override("shadow_offset_x",2)
	_story_label.add_theme_constant_override("shadow_offset_y",2)
	layout.add_child(_story_label)
	_hud.add_child(_story_panel)
	_story_marker=Label3D.new()
	_story_marker.text="Nora"
	_story_marker.font_size=42
	_story_marker.pixel_size=0.004
	_story_marker.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	_story_marker.position=Vector3(0,2.05,0)
	_story_marker.hide()
	crowd.actors[STORY_CONTACT].add_child(_story_marker)
	_story_sound=AudioStreamPlayer.new()
	_story_sound.stream=_feedback_clip(false)
	add_child(_story_sound)
	_update_story()

func _update_story() -> void:
	if not is_instance_valid(_story_label):return
	var contact: Node3D=crowd.actors[STORY_CONTACT]
	if _story_stage==1 and _driving and not _paused:
		var distance:=Vector2(vehicle.global_position.x-_story_start.x,vehicle.global_position.z-_story_start.z)
		if distance.length()>=4.0:_story_stage=2
	_story_heading.text="MISSION COMPLETE" if _story_stage==4 else "A NEW BEGINNING  |  %d / 4"%(_story_stage+1)
	_story_label.text=STORY_OBJECTIVES[_story_stage]
	_story_panel.visible=not _paused and not _map.expanded
	_story_marker.visible=_story_stage==3 and not _paused
	_map.story_target=Layout.map_position(contact.global_position) if _story_stage==3 else Vector2.INF

func _try_story_contact() -> bool:
	if _story_stage!=3 or academy_mode or _driving or _paused or _map.expanded or _cursor_unlocked or not is_instance_valid(crowd):return false
	var contact: Node3D=crowd.actors[STORY_CONTACT]
	if not Interaction.within_range(player,contact,2.5):return false
	var ray:=PhysicsRayQueryParameters3D.create(player.global_position+Vector3.UP*0.8,contact.global_position+Vector3.UP*0.8,1)
	if not get_world_3d().direct_space_state.intersect_ray(ray).is_empty():return false
	_story_stage=4
	crowd.perceive("greet",player.global_position,2.5)
	_story_sound.play()
	_update_story()
	story_completed.emit()
	return true

# Short original synthesized feedback; not final sound design.
func _feedback_clip(horn: bool) -> AudioStreamWAV:
	var rate:=22050
	var count:=int(rate*(0.32 if horn else 0.42))
	var samples:=PackedByteArray()
	samples.resize(count*2)
	for i: int in range(count):
		var t:=float(i)/float(rate)
		var envelope:=minf(1.0,t/0.02)*minf(1.0,float(count-i)/float(rate)/0.06)
		var freq:=360.0 if horn else (523.25 if t<0.18 else 783.99)
		var wave:=sin(TAU*freq*t)+0.35*sin(TAU*(freq+90.0)*t)
		samples.encode_s16(i*2,int(wave*envelope*4200))
	var clip:=AudioStreamWAV.new()
	clip.format=AudioStreamWAV.FORMAT_16_BITS
	clip.mix_rate=rate
	clip.data=samples
	return clip
