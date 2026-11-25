extends CharacterBody3D
## Executes validated Python intents; no autonomous decision fallback.
var npc_id := ""
var _art: Node3D
var _anim: AnimationPlayer
var goal := Vector3.ZERO
var destination := ""
var action := "idle"
var speed := 0.0
var expires := -1
var arrived := false
var _clock: Node
var _reaction_seconds := 0.0
var _reaction: Label3D
var _subject: Node3D

func configure(id: String, model: PackedScene, height: float) -> bool:
	if model==null:return false
	npc_id=id
	_art=model.instantiate() as Node3D
	if _art==null:return false
	var rigs := _art.find_children("*","Skeleton3D",true,false)
	var anims := _art.find_children("*","AnimationPlayer",true,false)
	if rigs.size()!=1 or anims.size()!=1 or (rigs[0] as Skeleton3D).get_bone_count()!=53:
		_art.free()
		return false
	_anim=anims[0] as AnimationPlayer
	if not _anim.has_animation("idle") or not _anim.has_animation("walk"):
		_art.free()
		return false
	add_child(_art)
	for node: Node in _art.find_children("*","MeshInstance3D",true,false):
		(node as MeshInstance3D).layers=2
	for clip: String in ["idle","walk"]:_anim.get_animation(clip).loop_mode=Animation.LOOP_LINEAR
	var capsule := CapsuleShape3D.new()
	capsule.radius=0.27
	capsule.height=height
	var shape := CollisionShape3D.new()
	shape.shape=capsule
	shape.position.y=height*0.5
	add_child(shape)
	collision_layer=8
	collision_mask=15
	floor_snap_length=0.22
	process_mode=Node.PROCESS_MODE_PAUSABLE
	_reaction=Label3D.new()
	_reaction.position=Vector3.UP*(height+0.25)
	_reaction.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	_reaction.font_size=38
	_reaction.pixel_size=0.003
	_reaction.hide()
	add_child(_reaction)
	return true

func _ready() -> void:
	_clock=get_node("/root/WorldClock")
	_anim.play("idle")

func apply_intent(intent: Dictionary, point: Vector3, subject: Node3D) -> void:
	destination=intent["destination"]
	action=intent["action"]
	goal=point
	speed=float(intent["speed"])
	expires=int(intent["valid_until"])
	arrived=false
	_subject=subject
	if action in ["acknowledge","complain","inspect"]:
		_reaction_seconds=1.3
		_reaction.text={"acknowledge":"Hey.","complain":"Watch out!","inspect":"I'll check it."}[action]
		_reaction.show()

func halt() -> void:
	expires=-1
	action="idle"
	speed=0
	_reaction.hide()
	_reaction_seconds=0

func _physics_process(delta: float) -> void:
	var direction := Vector3.ZERO
	if _reaction_seconds>0:
		_reaction_seconds-=delta
		if is_instance_valid(_subject):
			direction=_subject.global_position-global_position
			direction.y=0
			_face(direction,delta)
		direction=Vector3.ZERO
		if _reaction_seconds<=0:_reaction.hide()
	elif _clock.tick<=expires and action!="rest":
		var target := goal
		# Use the crossing corridor for opposite sidewalk destinations, not
		# diagonal shortcuts through the parked car or facade.
		if absf(goal.x)>3.4 and absf(global_position.x)>3.4 and signf(goal.x)!=signf(global_position.x):
			if absf(global_position.z)>0.45:target=Vector3(global_position.x,0,0)
			else:target=Vector3(goal.x,0,0)
		elif absf(global_position.x)<=3.4 and absf(goal.x)>3.4:
			target=Vector3(goal.x,0,0)
		var offset := target-global_position
		offset.y=0
		arrived=Vector2(goal.x-global_position.x,goal.z-global_position.z).length()<0.55
		if not arrived and offset.length()>0.25:
			direction=offset.normalized()
			# Local physical separation only, independent of decision policy.
			for other: Node in get_parent().get_children():
				if other==self or not other is CharacterBody3D:continue
				var away: Vector3=global_position-other.global_position
				away.y=0
				if away.length()>0.01 and away.length()<0.85:
					direction+=away.normalized()*0.65
			direction=direction.normalized()
			_face(direction,delta)
	velocity.x=move_toward(velocity.x,direction.x*speed,8*delta)
	velocity.z=move_toward(velocity.z,direction.z*speed,8*delta)
	if not is_on_floor():velocity.y-=9.81*delta
	else:
		velocity.y=0
		_step(Vector3(velocity.x,0,velocity.z)*delta)
	move_and_slide()
	var clip := "walk" if Vector2(velocity.x,velocity.z).length()>0.2 else "idle"
	if _anim.current_animation!=clip:_anim.play(clip,0.18)

func _face(direction: Vector3,delta: float) -> void:
	if direction.length_squared()>0.01:
		_art.rotation.y=lerp_angle(_art.rotation.y,atan2(direction.x,direction.z),clampf(delta*10,0,1))

func _step(motion: Vector3) -> void:
	if motion.length_squared()<0.000001 or not test_move(global_transform,motion):return
	if test_move(global_transform,Vector3.UP*0.20):return
	var raised := global_transform.translated(Vector3.UP*0.20)
	if test_move(raised,motion):return
	var hit := KinematicCollision3D.new()
	if test_move(raised.translated(motion),Vector3.DOWN*0.23,hit) and hit.get_normal().y>0.7:
		global_position.y+=0.20
		apply_floor_snap()
