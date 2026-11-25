extends CharacterBody3D
## Physics/controller test with actual candidate rig. No licensed motion installed yet.
const Orbit = preload("res://core/camera_orbit.gd")
const WALK := 2.0
const RUN := 4.0
const SPRINT := 6.0
const CROUCH := 1.2
const RADIUS := 0.29
const STEP := 0.20
var height_m := 1.81
var yaw := 0.0
var pitch := -0.18
var sensitivity := 0.0025
var controls_enabled := true
var first_person := false
var _capsule: CapsuleShape3D
var _shape: CollisionShape3D
var _visual: Node3D
var _camera: Camera3D
var _crouched := false
var _animation: AnimationPlayer
var motion_installed := false
var _was_grounded := false
var _ever_grounded := false

func configure(model: PackedScene, height: float) -> bool:
	if model == null or height < 1.5 or height > 2.0 or is_inside_tree():
		return false
	height_m = height
	_visual = model.instantiate() as Node3D
	if _visual == null:
		return false
	add_child(_visual)
	var animation_nodes := _visual.find_children("*","AnimationPlayer",true,false)
	print("MOTION_IMPORT animation_players=",animation_nodes.size())
	if animation_nodes.size()==1:
		_animation=animation_nodes[0] as AnimationPlayer
		print("MOTION_IMPORT clips=",_animation.get_animation_list())
		motion_installed=true
		for clip: String in ["idle","walk","jog","sprint","crouch_idle","crouch_walk","jump_start","jump_air","jump_land"]:
			if not _animation.has_animation(clip):
				motion_installed=false
				break
		if motion_installed:
			for clip: String in ["idle","walk","jog","sprint","crouch_idle","crouch_walk","jump_air"]:
				_animation.get_animation(clip).loop_mode=Animation.LOOP_LINEAR
	_capsule = CapsuleShape3D.new()
	_capsule.radius = RADIUS
	_capsule.height = height_m
	_shape = CollisionShape3D.new()
	_shape.shape = _capsule
	_shape.position.y = height_m * 0.5
	add_child(_shape)
	collision_layer = 2
	collision_mask = 1
	floor_snap_length = 0.22
	floor_max_angle = deg_to_rad(48)
	_camera = Camera3D.new()
	_camera.name = "PlayerCamera"
	_camera.fov = 68
	_camera.near = 0.08
	add_child(_camera)
	_camera.top_level = true
	return true

func _ready() -> void:
	if _camera != null:
		_camera.current = true
		_update_camera(1.0)
		if motion_installed:
			_animation.play("idle")

func _unhandled_input(event: InputEvent) -> void:
	if not controls_enabled:
		return
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		yaw = wrapf(yaw - event.relative.x * sensitivity, -PI, PI)
		pitch = clampf(pitch + event.relative.y * sensitivity, -1.1, 0.5)
	elif event.is_action_pressed("camera_view"):
		first_person = not first_person

func _physics_process(delta: float) -> void:
	if _camera == null or not controls_enabled:
		return
	var input := Input.get_vector("move_left","move_right","move_forward","move_back")
	var direction := (Basis(Vector3.UP,yaw) * Vector3(input.x,0,input.y))
	var speed := RUN
	if Input.is_action_pressed("walk"):
		speed = WALK
	elif Input.is_action_pressed("sprint"):
		speed = SPRINT
	_set_crouch(Input.is_action_pressed("crouch"))
	if _crouched:
		speed = CROUCH
	var target := direction * speed
	velocity.x = move_toward(velocity.x,target.x,16.0*delta)
	velocity.z = move_toward(velocity.z,target.z,16.0*delta)
	if not is_on_floor():
		velocity.y -= 9.81 * delta
	elif Input.is_action_just_pressed("jump") and not _crouched:
		velocity.y = 4.0
	else:
		velocity.y = minf(velocity.y,0.0)
	if is_on_floor() and direction.length_squared() > 0.01 and velocity.y <= 0:
		_try_step(Vector3(velocity.x,0,velocity.z)*delta)
	move_and_slide()
	if direction.length_squared() > 0.01:
		var target_yaw := atan2(direction.x,direction.z)
		_visual.rotation.y = lerp_angle(_visual.rotation.y,target_yaw,Orbit.follow_weight(12.0,delta))
	_update_camera(delta)
	_update_motion()

func _update_motion() -> void:
	if not motion_installed:
		return
	var speed := Vector2(velocity.x,velocity.z).length()
	var grounded := is_on_floor()
	var current := _animation.current_animation
	# The spawn begins just above the sidewalk; do not animate an uncommanded jump.
	if not _ever_grounded:
		if grounded:
			_ever_grounded=true
			_was_grounded=true
		return
	var target := "idle"
	if not grounded:
		if _was_grounded:
			target="jump_start"
		elif current=="jump_start" and _animation.is_playing():
			target="jump_start"
		else:
			target="jump_air"
	elif not _was_grounded:
		target="jump_land"
	elif current=="jump_land" and _animation.is_playing():
		target="jump_land"
	elif _crouched:
		target="crouch_walk" if speed>0.18 else "crouch_idle"
	elif speed>4.6:
		target="sprint"
	elif speed>2.6:
		target="jog"
	elif speed>0.18:
		target="walk"
	_was_grounded=grounded
	if current!=target:
		_animation.play(target,0.15)

func motion_clip() -> String:
	return _animation.current_animation if motion_installed else ""

func _try_step(motion: Vector3) -> void:
	if motion.length_squared() < 0.000001 or not test_move(global_transform,motion):
		return
	if test_move(global_transform,Vector3.UP*STEP):
		return
	var raised := global_transform.translated(Vector3.UP*STEP)
	if test_move(raised,motion):
		return
	var forward := raised.translated(motion)
	var hit := KinematicCollision3D.new()
	if test_move(forward,Vector3.DOWN*(STEP+0.03),hit) and hit.get_normal().y > 0.7:
		global_position.y += STEP
		apply_floor_snap()

func _set_crouch(wanted: bool) -> void:
	if wanted == _crouched:
		return
	var crouch_height := height_m*0.65
	if not wanted:
		var query := PhysicsShapeQueryParameters3D.new()
		var full := CapsuleShape3D.new()
		full.radius=RADIUS
		full.height=height_m
		query.shape=full
		query.transform=Transform3D(Basis.IDENTITY,global_position+Vector3.UP*(height_m*0.5+0.025))
		query.collision_mask=1
		query.exclude=[get_rid()]
		if not get_world_3d().direct_space_state.intersect_shape(query,1).is_empty():
			return
	_crouched=wanted
	_capsule.height=crouch_height if wanted else height_m
	_shape.position.y=_capsule.height*0.5
	# Candidate-only collision pose; do not squash the real visual mesh.

func _update_camera(delta: float) -> void:
	var focus := global_position+Vector3.UP*(height_m*(0.58 if _crouched else 0.86))
	var offset := Orbit.offset(yaw,pitch,3.7)
	var ideal := focus+offset
	if first_person:
		_visual.visible=false
		_camera.global_position=focus
		_camera.look_at(focus-Basis(Vector3.UP,yaw)*Vector3(0,sin(pitch),cos(pitch)))
		return
	_visual.visible=true
	var ray := PhysicsRayQueryParameters3D.create(focus,ideal,1,[get_rid()])
	var hit := get_world_3d().direct_space_state.intersect_ray(ray)
	if not hit.is_empty():
		ideal=focus+offset.normalized()*maxf(0.15,focus.distance_to(hit.position)-0.20)
	var smoothed := _camera.global_position.lerp(ideal,Orbit.follow_weight(14.0,delta))
	# Check the smoothed point too; interpolation may otherwise cut through a wall.
	ray=PhysicsRayQueryParameters3D.create(focus,smoothed,1,[get_rid()])
	hit=get_world_3d().direct_space_state.intersect_ray(ray)
	if not hit.is_empty():
		smoothed=focus+(smoothed-focus).normalized()*maxf(0.15,focus.distance_to(hit.position)-0.20)
	_camera.global_position=smoothed
	if _camera.global_position.distance_squared_to(focus)>0.0001:
		_camera.look_at(focus)

func stop_controls() -> void:
	controls_enabled=false
	velocity=Vector3.ZERO
	if motion_installed:
		_animation.play("idle",0.15)

func camera_position() -> Vector3:
	return _camera.global_position
