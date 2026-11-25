extends VehicleBody3D
## Raycast suspension development candidate, not a high-fidelity tyre/drivetrain model.
const Orbit = preload("res://core/camera_orbit.gd")
const REST := 0.18
const MAX_SPEED := 9.0
const WHEEL_KEYS := ["FL","FR","RL","RR"]
var built := false
var occupied := false
var input_enabled := false
var headlights_on := false
var _art: Node3D
var _wheels: Array[VehicleWheel3D] = []
var _door: Node3D
var _door_basis: Basis
var _door_tween: Tween
var _door_angle := 0.0
var _door_sweep := AABB()
var _camera: Camera3D
var _headlights: Array[SpotLight3D] = []
var _driver_side := -1.0
var _engine_audio: AudioStreamPlayer3D

func configure(model: PackedScene) -> bool:
	if model == null or is_inside_tree():
		return false
	_art=model.instantiate() as Node3D
	if _art == null:
		return false
	add_child(_art)
	mass=1250.0
	collision_layer=4
	collision_mask=11
	linear_damp=0.12
	angular_damp=0.45
	can_sleep=false
	continuous_cd=true
	process_mode=Node.PROCESS_MODE_PAUSABLE
	var shell := CollisionShape3D.new()
	var box := BoxShape3D.new()
	# Body-only proxy; actual wheel suspension carries the body.
	box.size=Vector3(2.12,0.65,4.12)
	shell.shape=box
	shell.position=Vector3(0,0.62,0)
	add_child(shell)
	return true

func _ready() -> void:
	if _art == null:
		return
	# Validate all four real mesh sockets before creating any raycast wheel.
	var sockets: Array[Node3D] = []
	var centers: Array[Vector3] = []
	var radii: Array[float] = []
	for key: String in WHEEL_KEYS:
		var socket := _art.find_child("WheelVisual_"+key,true,false) as Node3D
		if socket == null:
			push_error("Coupe wheel socket missing: "+key)
			return
		var bounds := _local_bounds(socket)
		var radius := bounds.size.y*0.5
		var center := to_local(socket.global_position)
		if not center.is_finite() or radius<0.24 or radius>0.49 or absf(center.x)<0.55 or absf(center.z)<0.8:
			push_error("Coupe wheel dimensions invalid: "+key+" "+str(bounds))
			return
		sockets.append(socket)
		centers.append(center)
		radii.append(radius)
	if centers[0].z<=centers[2].z or centers[1].z<=centers[3].z:
		push_error("Coupe forward axis invalid")
		return
	_door=_art.find_child("DoorPivot_L",true,false) as Node3D
	if _door==null or _art.find_child("DoorPivot_R",true,false)==null:
		push_error("Actual door pivot missing")
		return
	_door_basis=_door.basis
	_driver_side=signf(to_local(_door.global_position).x)
	if is_zero_approx(_driver_side):
		push_error("Driver side invalid")
		return
	# Derive a conservative swept envelope from the actual closed door meshes.
	var closed := _local_bounds(_door)
	var pivot := to_local(_door.global_position)
	_door_sweep=closed
	for sample: int in range(11):
		var angle := deg_to_rad(50.0)*-_driver_side*float(sample)/10.0
		var rotation := Basis(Vector3.UP,angle)
		for corner: int in range(8):
			_door_sweep=_door_sweep.expand(pivot+rotation*(closed.get_endpoint(corner)-pivot))
	for i: int in range(4):
		var wheel := VehicleWheel3D.new()
		wheel.name="Suspension_"+WHEEL_KEYS[i]
		wheel.position=centers[i]+Vector3.UP*REST
		wheel.wheel_radius=radii[i]
		wheel.wheel_rest_length=REST
		wheel.suspension_travel=0.22
		wheel.suspension_stiffness=45.0
		wheel.suspension_max_force=6500.0
		wheel.damping_compression=0.50
		wheel.damping_relaxation=0.65
		wheel.wheel_friction_slip=3.0
		wheel.wheel_roll_influence=0.15
		wheel.use_as_steering=i<2
		wheel.use_as_traction=i>=2
		add_child(wheel)
		var socket: Node3D=sockets[i]
		socket.reparent(wheel,false)
		socket.transform=Transform3D.IDENTITY
		_wheels.append(wheel)
	_camera=Camera3D.new()
	_camera.name="CoupeCamera"
	_camera.fov=66
	_camera.near=0.1
	add_child(_camera)
	_camera.top_level=true
	_camera.current=false
	for x: float in [-0.78,0.78]:
		var light := SpotLight3D.new()
		light.position=Vector3(x,0.63,1.97)
		light.rotation_degrees=Vector3(-4,180,0)
		light.spot_range=24
		light.spot_angle=28
		light.light_energy=2.1
		light.visible=false
		add_child(light)
		_headlights.append(light)
	_engine_audio=AudioStreamPlayer3D.new()
	_engine_audio.stream=_engine_loop()
	_engine_audio.max_distance=20.0
	_engine_audio.unit_size=3.0
	_engine_audio.volume_db=-20.0
	_engine_audio.position=Vector3(0,0.65,1.0)
	add_child(_engine_audio)
	built=true
	brake=45.0
	print("CODECITY_COUPE_WHEEL_SETUP_OK ",centers," radii=",radii)

func _local_bounds(root: Node3D) -> AABB:
	var merged := AABB()
	var first := true
	var meshes := root.find_children("*","MeshInstance3D",true,false)
	if root is MeshInstance3D:
		meshes.push_front(root)
	for node: Node in meshes:
		var m := node as MeshInstance3D
		if m.mesh==null:
			continue
		var box: AABB=global_transform.affine_inverse()*m.global_transform*m.get_aabb()
		merged=box if first else merged.merge(box)
		first=false
	return merged

func _physics_process(delta: float) -> void:
	if not built:
		return
	var speed := linear_velocity.dot(global_basis.z.normalized())
	engine_force=0.0
	brake=0.0
	var steer_target := 0.0
	if occupied and input_enabled:
		var throttle := Input.get_axis("move_back","move_forward")
		steer_target=Input.get_axis("move_right","move_left")*lerpf(0.40,0.24,clampf(absf(speed)/MAX_SPEED,0,1))
		if Input.is_action_pressed("vehicle_brake"):
			brake=65.0
		elif throttle*speed< -0.6:
			brake=40.0
		elif absf(throttle)>0.05 and absf(speed)<MAX_SPEED:
			engine_force=throttle*(2300.0 if throttle>0 else 1150.0)
		else:
			brake=3.0
	else:
		brake=45.0
	steering=move_toward(steering,steer_target,1.5*delta)
	if occupied:
		_update_camera(delta)
		var load_amount:=clampf(absf(engine_force)/2300.0,0.0,1.0)
		var rate:=clampf(absf(speed)/MAX_SPEED,0.0,1.0)
		_engine_audio.pitch_scale=lerpf(_engine_audio.pitch_scale,0.85+rate*0.75+load_amount*0.3,minf(1.0,delta*6.0))
		_engine_audio.volume_db=lerpf(_engine_audio.volume_db,-22.0+load_amount*8.0+rate*4.0,minf(1.0,delta*6.0))

func contacts() -> int:
	var count := 0
	for wheel: VehicleWheel3D in _wheels:
		if wheel.is_in_contact():
			count+=1
	return count

func speed_kmh() -> float:
	return Vector2(linear_velocity.x,linear_velocity.z).length()*3.6

func stopped() -> bool:
	return built and linear_velocity.length()<0.55 and angular_velocity.length()<0.35 and contacts()>=3

func entry_point() -> Vector3:
	return to_global(Vector3(_driver_side*1.35,0.55,0.05))

func exit_point(side: float) -> Vector3:
	return to_global(Vector3(_driver_side*side*1.75,0.55,0.05))

## Exit behind the driver's actual swept door envelope. If blocked, do not
## teleport to the opposite door or overlap world geometry.
func exit_candidates() -> Array[Vector3]:
	var candidates: Array[Vector3]=[]
	for offset: float in [0.62,0.88,1.1]:
		for lateral: float in [1.75,2.05]:
			candidates.append(to_global(Vector3(_driver_side*lateral,0.55,_door_sweep.position.z-offset)))
	return candidates

func clear_of_door(where: Vector3) -> bool:
	var p := to_local(where)
	var margin := 0.38
	var inside_x := p.x>=_door_sweep.position.x-margin and p.x<=_door_sweep.end.x+margin
	var inside_z := p.z>=_door_sweep.position.z-margin and p.z<=_door_sweep.end.z+margin
	return not (inside_x and inside_z)

func set_occupied(value: bool) -> void:
	occupied=value
	input_enabled=value
	if value:
		_engine_audio.play()
		_camera.current=true
		_update_camera(1.0)
	else:
		_engine_audio.stop()
		engine_force=0
		brake=45
		_camera.current=false
	_animate_door()

func _animate_door() -> void:
	if _door_tween!=null and _door_tween.is_valid():
		_door_tween.kill()
	_door_tween=create_tween()
	_door_tween.tween_method(_set_door_angle,_door_angle,deg_to_rad(50.0)*-_driver_side,0.24)
	_door_tween.tween_interval(0.25)
	_door_tween.tween_method(_set_door_angle,deg_to_rad(50.0)*-_driver_side,0.0,0.24)

func _set_door_angle(angle: float) -> void:
	_door_angle=angle
	var parent := _door.get_parent_node_3d()
	var axis := (parent.global_basis.inverse()*global_basis.y).normalized()
	_door.basis=Basis(axis,angle)*_door_basis

func toggle_headlights() -> void:
	headlights_on=not headlights_on
	for light: SpotLight3D in _headlights:
		light.visible=headlights_on

func _update_camera(delta: float) -> void:
	var focus := global_position+Vector3.UP*1.05
	var ideal := focus-global_basis.z.normalized()*5.8+Vector3.UP*2.2
	var ray := PhysicsRayQueryParameters3D.create(focus,ideal,1,[get_rid()])
	var hit := get_world_3d().direct_space_state.intersect_ray(ray)
	if not hit.is_empty():
		ideal=focus+(ideal-focus).normalized()*maxf(0.2,focus.distance_to(hit.position)-0.22)
	var p := _camera.global_position.lerp(ideal,Orbit.follow_weight(9.0,delta))
	ray=PhysicsRayQueryParameters3D.create(focus,p,1,[get_rid()])
	hit=get_world_3d().direct_space_state.intersect_ray(ray)
	if not hit.is_empty():
		p=focus+(p-focus).normalized()*maxf(0.2,focus.distance_to(hit.position)-0.22)
	_camera.global_position=p
	if p.distance_squared_to(focus)>0.001:
		_camera.look_at(focus)

# Original seamless periodic prototype engine bed. Not a recorded car sound.
func _engine_loop() -> AudioStreamWAV:
	var rate:=22050
	var count:=rate
	var samples:=PackedByteArray()
	samples.resize(count*2)
	for i: int in range(count):
		var t:=float(i)/float(rate)
		var pulse:=0.65+0.35*sin(TAU*24.0*t)
		var wave:=sin(TAU*48.0*t)+0.35*sin(TAU*96.0*t)+0.18*sin(TAU*144.0*t)
		samples.encode_s16(i*2,int(wave*pulse*6000.0))
	var clip:=AudioStreamWAV.new()
	clip.format=AudioStreamWAV.FORMAT_16_BITS
	clip.mix_rate=rate
	clip.data=samples
	clip.loop_mode=AudioStreamWAV.LOOP_FORWARD
	clip.loop_begin=0
	clip.loop_end=count
	return clip
