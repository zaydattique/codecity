extends Node3D
## Distinct real rigs, one batch per 30 simulation ticks; no player-facing AI data.
const Bridge = preload("res://core/npc_bridge.gd")
const Actor = preload("res://core/street_npc.gd")
const IDS := ["nora","omar","elena","marcus","sana","liam"]
const CITY_IDS := ["jules","rhea","vincent","farah","theo","iris"]
const CITY_HEIGHTS := [1.72,1.64,1.77,1.76,1.67,1.60]
const CITY_SPAWNS := [Vector3(-80,0.04,72),Vector3(13.3,0.18,-9.0),Vector3(0,0.04,72),Vector3(0,0.04,91),Vector3(80,0.04,72),Vector3(80,0.04,91)]
const CITY_POINTS := {"park_west_a":Vector3(-80,0,66),"park_west_b":Vector3(-80,0,96),"park_center_a":Vector3(0,0,65),"park_center_b":Vector3(0,0,96),"park_east_a":Vector3(80,0,66),"park_east_b":Vector3(80,0,96),"shop_counter":Vector3(13.3,0.15,-9.4),"shop_shelf":Vector3(13.3,0.15,-7.7)}
const HEIGHTS := [1.66,1.78,1.61,1.85,1.70,1.74]
const POINTS := {"west_south":Vector3(-4.6,0.15,11.5),"west_north":Vector3(-4.6,0.15,-11.5),"east_south":Vector3(4.5,0.15,11.5),"east_north":Vector3(4.5,0.15,-11.5),"bench":Vector3(4,0.15,2),"crossing":Vector3(0,0,0)}
const SPAWNS := [Vector3(-4.6,0.18,-7),Vector3(4.5,0.18,7),Vector3(-4.5,0.18,2),Vector3(4.5,0.18,-6),Vector3(4.4,0.18,11),Vector3(-4.5,0.18,-12)]
const ACTIONS := ["walk","rest","give_space","acknowledge","complain","inspect","defend"]
signal dialogue(speaker: String,line: String)
signal attacked(actor: Node3D)
var _submitted_ids: Array=[]
var actors := {}
var active_ids: Array=[]
var active_points: Dictionary={}
var bridge: Node
var player: Node3D
var vehicle: Node3D
var _clock: Node
var _next_tick := 0
var _submitted_tick := -1
var _events := {}
var _event_id := 0
var accepted_batches := 0
var failed := false

static func installed(city: bool=false) -> bool:
	if Bridge.paths().is_empty():return false
	for id: String in (IDS+CITY_IDS if city else IDS):
		if not ResourceLoader.exists("res://candidate_assets/npc_"+id+".glb","PackedScene"):return false
	return true

func prepare(hero: Node3D,car: Node3D,city: bool=false) -> bool:
	if not installed(city):return false
	active_ids=IDS+CITY_IDS if city else IDS.duplicate()
	active_points=POINTS.duplicate()
	if city:active_points.merge(CITY_POINTS)
	player=hero
	vehicle=car
	var heights: Array=HEIGHTS+CITY_HEIGHTS if city else HEIGHTS
	var spawns: Array=SPAWNS+CITY_SPAWNS if city else SPAWNS
	for i: int in range(active_ids.size()):
		var id: String=active_ids[i]
		var scene := load("res://candidate_assets/npc_"+id+".glb") as PackedScene
		var actor := Actor.new()
		if not actor.configure(id,scene,heights[i]):
			actor.free()
			return false
		actor.name=id
		actor.position=spawns[i]
		actor.use_crossing=IDS.has(id)
		actor.strike.connect(func(attacker: Node3D):attacked.emit(attacker))
		actor.spoke.connect(func(line: String):
			if is_instance_valid(player) and actor.global_position.distance_to(subject().global_position)<=9.0:dialogue.emit(id.capitalize(),line))
		add_child(actor)
		actors[id]=actor
	return true

func _ready() -> void:
	process_mode=Node.PROCESS_MODE_PAUSABLE
	_clock=get_node("/root/WorldClock")
	bridge=Bridge.new()
	add_child(bridge)
	bridge.received.connect(_accept)
	bridge.unavailable.connect(_halt)
	if not bridge.start():_halt()

func subject() -> Node3D:
	return vehicle if is_instance_valid(vehicle) and vehicle.get("occupied")==true else player

func perceive(kind: String,origin: Vector3,radius: float) -> void:
	_event_id+=1
	for id: String in active_ids:
		var actor: Node3D=actors[id]
		if actor.dead:continue
		var distance := actor.global_position.distance_to(origin)
		if distance>radius:continue
		var query := PhysicsRayQueryParameters3D.create(origin+Vector3.UP*0.8,actor.global_position+Vector3.UP*0.8,1)
		if not get_world_3d().direct_space_state.intersect_ray(query).is_empty():continue
		_events[id]={"id":_event_id,"kind":kind,"distance":distance}

func _physics_process(_delta: float) -> void:
	if failed or _clock.tick<_next_tick or not bridge.pending.is_empty():return
	var tick: int=_clock.tick
	var observations: Array=[]
	var target := subject()
	for id: String in active_ids:
		var actor: CharacterBody3D=actors[id]
		if actor.dead:continue
		var p := actor.global_position
		observations.append({"id":id,"position":[clampf(p.x,-600,600),clampf(p.z,-600,600)],"minute":_clock.minute_of_day(),"tick":tick,"reached":actor.arrived,"player_distance":p.distance_to(target.global_position),"event":_events.get(id)})
	if observations.is_empty():return
	if bridge.submit(observations,tick):
		_submitted_ids=observations.map(func(o):return o["id"])
		_submitted_tick=tick
		_next_tick=tick+30
		_events.clear()
	else:_halt()

func _accept(result: Dictionary) -> void:
	var intents: Variant=result.get("intents")
	if not intents is Array or intents.size()!=_submitted_ids.size():
		_halt()
		return
	var seen := {}
	for intent: Variant in intents:
		if not intent is Dictionary or intent.size()!=5:
			_halt()
			return
		var id: Variant=intent.get("id")
		var rate: Variant=intent.get("speed")
		var expiry: Variant=intent.get("valid_until")
		if not id is String or not _submitted_ids.has(id) or not actors.has(id) or seen.has(id) or not active_points.has(intent.get("destination")) or not intent.get("action") in ACTIONS or not (rate is float or rate is int) or not is_finite(float(rate)) or float(rate)<0 or float(rate)>2 or not (expiry is float or expiry is int) or expiry!=_submitted_tick+120 or expiry<_clock.tick:
			_halt()
			return
		seen[id]=true
	for intent: Dictionary in intents:
		actors[intent["id"]].apply_intent(intent,active_points[intent["destination"]],subject())
	accepted_batches+=1

func _halt() -> void:
	failed=true
	for actor: Node in actors.values():actor.halt()
	if is_instance_valid(bridge) and bridge.pid>0:bridge._stop()
	# Explicitly stop on failure; not a substitute GDScript AI policy.
	print("CODECITY_NPC_WORKER_UNAVAILABLE idle fallback")

func nearest_visible(origin: Vector3,radius: float) -> Node3D:
	var result: Node3D
	var nearest:=radius
	for actor: Node3D in actors.values():
		if actor.get("dead")==true:continue
		var distance:=actor.global_position.distance_to(origin)
		if distance>nearest:continue
		var query:=PhysicsRayQueryParameters3D.create(origin+Vector3.UP*0.8,actor.global_position+Vector3.UP*0.8,1)
		if not get_world_3d().direct_space_state.intersect_ray(query).is_empty():continue
		nearest=distance
		result=actor
	return result

func register_hit(target: Node3D,origin: Vector3) -> void:
	if not is_instance_valid(target) or target.get("dead")==true:return
	perceive("threat",origin,8.0)
	_event_id+=1
	_events[target.npc_id]={"id":_event_id,"kind":"attack","distance":target.global_position.distance_to(origin)}

func strike_target(origin: Vector3,forward: Vector3,radius: float) -> Node3D:
	var nearest:=radius
	var result: Node3D
	for target: Node3D in actors.values():
		if target.get("dead")==true:continue
		var offset:=target.global_position-origin
		offset.y=0
		var distance:=offset.length()
		if distance>nearest or distance<0.001 or offset.normalized().dot(forward)<0.45:continue
		var query:=PhysicsRayQueryParameters3D.create(origin+Vector3.UP*0.9,target.global_position+Vector3.UP*0.9,1)
		if not get_world_3d().direct_space_state.intersect_ray(query).is_empty():continue
		nearest=distance
		result=target
	return result
