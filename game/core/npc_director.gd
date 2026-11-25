extends Node3D
## Six real rigs, one batch per 30 simulation ticks; no player-facing AI data.
const Bridge = preload("res://core/npc_bridge.gd")
const Actor = preload("res://core/street_npc.gd")
const IDS := ["nora","omar","elena","marcus","sana","liam"]
const HEIGHTS := [1.66,1.78,1.61,1.85,1.70,1.74]
const POINTS := {"west_south":Vector3(-4.6,0.15,11.5),"west_north":Vector3(-4.6,0.15,-11.5),"east_south":Vector3(4.5,0.15,11.5),"east_north":Vector3(4.5,0.15,-11.5),"bench":Vector3(4,0.15,2),"crossing":Vector3(0,0,0)}
const SPAWNS := [Vector3(-4.6,0.18,-7),Vector3(4.5,0.18,7),Vector3(-4.5,0.18,2),Vector3(4.5,0.18,-6),Vector3(4.4,0.18,11),Vector3(-4.5,0.18,-12)]
const ACTIONS := ["walk","rest","give_space","acknowledge","complain","inspect"]
var actors := {}
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

static func installed() -> bool:
	if Bridge.paths().is_empty():return false
	for id: String in IDS:
		if not ResourceLoader.exists("res://candidate_assets/npc_"+id+".glb","PackedScene"):return false
	return true

func prepare(hero: Node3D,car: Node3D) -> bool:
	if not installed():return false
	player=hero
	vehicle=car
	for i: int in range(IDS.size()):
		var id: String=IDS[i]
		var scene := load("res://candidate_assets/npc_"+id+".glb") as PackedScene
		var actor := Actor.new()
		if not actor.configure(id,scene,HEIGHTS[i]):
			actor.free()
			return false
		actor.name=id
		actor.position=SPAWNS[i]
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
	for id: String in IDS:
		var actor: Node3D=actors[id]
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
	for id: String in IDS:
		var actor: CharacterBody3D=actors[id]
		var p := actor.global_position
		observations.append({"id":id,"position":[clampf(p.x,-6,6),clampf(p.z,-16,16)],"minute":_clock.minute_of_day(),"tick":tick,"reached":actor.arrived,"player_distance":p.distance_to(target.global_position),"event":_events.get(id)})
	if bridge.submit(observations,tick):
		_submitted_tick=tick
		_next_tick=tick+30
		_events.clear()
	else:_halt()

func _accept(result: Dictionary) -> void:
	var intents: Variant=result.get("intents")
	if not intents is Array or intents.size()!=6:
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
		if not id is String or not actors.has(id) or seen.has(id) or not POINTS.has(intent.get("destination")) or not intent.get("action") in ACTIONS or not (rate is float or rate is int) or not is_finite(float(rate)) or float(rate)<0 or float(rate)>2 or not (expiry is float or expiry is int) or expiry!=_submitted_tick+120 or expiry<_clock.tick:
			_halt()
			return
		seen[id]=true
	for intent: Dictionary in intents:
		actors[intent["id"]].apply_intent(intent,POINTS[intent["destination"]],subject())
	accepted_batches+=1

func _halt() -> void:
	failed=true
	for actor: Node in actors.values():actor.halt()
	if is_instance_valid(bridge) and bridge.pid>0:bridge._stop()
	# Explicitly stop on failure; not a substitute GDScript AI policy.
	print("CODECITY_NPC_WORKER_UNAVAILABLE idle fallback")
