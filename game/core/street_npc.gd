extends CharacterBody3D
## Executes validated Python intents; no autonomous decision fallback.
signal spoke(line: String)
signal strike(actor: Node3D)
var health:=40
var dead:=false
var combat_installed:=false
var _combat_lock:=0.0
var _strike_delay:=-1.0
var _cooldown:=0.0
var _dead_elapsed:=0.0
var _fade_materials: Array[Dictionary]=[]
var _spawn:=Vector3.ZERO
var _shape: CollisionShape3D
var use_crossing := true
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
	combat_installed=true
	for clip: String in ["punch_jab","hit_chest","death"]:
		if not _anim.has_animation(clip):combat_installed=false
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
	_shape=shape
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
	_spawn=global_position
	_clock=get_node("/root/WorldClock")
	_anim.play("idle")

func apply_intent(intent: Dictionary, point: Vector3, subject: Node3D) -> void:
	if dead:return
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
		spoke.emit(_reaction.text)

func halt() -> void:
	expires=-1
	action="idle"
	speed=0
	_reaction.hide()
	_reaction_seconds=0


func _physics_process(delta: float) -> void:
	if dead:
		_tick_body(delta)
		return
	_cooldown=maxf(0,_cooldown-delta)
	if _combat_lock>0:
		_combat_lock=maxf(0,_combat_lock-delta)
		if _strike_delay>=0:
			_strike_delay-=delta
			if _strike_delay<=0:
				_strike_delay=-1
				strike.emit(self)
		velocity=Vector3.ZERO
		if not is_on_floor():velocity.y-=9.81*delta
		move_and_slide()
		return
	var direction := Vector3.ZERO
	if action=="defend" and is_instance_valid(_subject) and _clock.tick<=expires:
		var offset:=_subject.global_position-global_position
		offset.y=0
		if offset.length()<=2.5:
			_face(offset,delta)
			if offset.length()<1.55 and _cooldown<=0 and combat_installed:
				_combat_lock=clampf(_anim.get_animation("punch_jab").length,0.35,2.0)
				_strike_delay=_combat_lock*0.42
				_cooldown=1.5
				_anim.play("punch_jab",0.08)
				return
			if offset.length()>1.1:direction=offset.normalized()
			velocity.x=direction.x*1.5
			velocity.z=direction.z*1.5
			if not is_on_floor():velocity.y-=9.81*delta
			move_and_slide()
			var clip: String="walk" if direction.length()>0.1 else "idle"
			if _anim.current_animation!=clip:_anim.play(clip,0.15)
			return
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
		if use_crossing and absf(goal.x)>3.4 and absf(global_position.x)>3.4 and signf(goal.x)!=signf(global_position.x):
			if absf(global_position.z)>0.45:target=Vector3(global_position.x,0,0)
			else:target=Vector3(goal.x,0,0)
		elif use_crossing and absf(global_position.x)<=3.4 and absf(goal.x)>3.4:
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
	var leading:=global_position+motion.normalized()*(0.27+motion.length()+0.04)
	var ray:=PhysicsRayQueryParameters3D.create(leading+Vector3.UP*0.26,leading-Vector3.UP*0.04,1,[get_rid()])
	var surface:=get_world_3d().direct_space_state.intersect_ray(ray)
	if surface.is_empty() or surface.normal.y<0.7:return
	var rise: float=surface.position.y-global_position.y
	if rise>=0.025 and rise<=0.21:
		global_position.y+=rise+0.015
		velocity.y=0.0

func take_damage(amount: int) -> bool:
	if dead or amount<=0 or not combat_installed:return false
	health=maxi(0,health-amount)
	_strike_delay=-1
	_reaction_seconds=0
	dead=health==0
	if dead:
		halt()
		_dead_elapsed=0
		collision_layer=0
		collision_mask=0
		_shape.set_deferred("disabled",true)
		_anim.play("death",0.08)
	else:
		_combat_lock=clampf(_anim.get_animation("hit_chest").length,0.25,2.5)
		_anim.play("hit_chest",0.07)
	return true

func _tick_body(delta: float) -> void:
	_dead_elapsed+=delta
	var death_length:=clampf(_anim.get_animation("death").length,0.4,6.0)
	if _dead_elapsed>=death_length+2.5 and _fade_materials.is_empty() and _art.visible:
		for node: Node in _art.find_children("*","MeshInstance3D",true,false):
			var mesh:=node as MeshInstance3D
			for i: int in range(mesh.mesh.get_surface_count()):
				var active:=mesh.get_active_material(i)
				if not active is StandardMaterial3D:continue
				var fading:=active.duplicate() as StandardMaterial3D
				fading.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
				_fade_materials.append({"node":mesh,"surface":i,"old":mesh.get_surface_override_material(i),"fade":fading})
				mesh.set_surface_override_material(i,fading)
	if _dead_elapsed>=death_length+2.5:
		var alpha:=clampf(1.0-(_dead_elapsed-death_length-2.5)/1.2,0,1)
		for entry: Dictionary in _fade_materials:
			var material: StandardMaterial3D=entry["fade"]
			var color:=material.albedo_color
			color.a=alpha
			material.albedo_color=color
		if alpha<=0:_art.hide()
	if _dead_elapsed>=death_length+12:
		for entry: Dictionary in _fade_materials:
			entry["node"].set_surface_override_material(entry["surface"],entry["old"])
		_fade_materials.clear()
		global_position=_spawn+Vector3.UP*0.02
		health=40
		dead=false
		_combat_lock=0
		velocity=Vector3.ZERO
		collision_layer=8
		collision_mask=15
		_shape.set_deferred("disabled",false)
		_art.show()
		_anim.play("idle")
