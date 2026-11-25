extends SceneTree
const Harbor = preload("res://scenes/harbor_playtest.gd")
func _initialize() -> void:
	call_deferred("_verify")

func ticks(count: int) -> void:
	for i: int in range(count):
		await physics_frame

func _verify() -> void:
	var world=Harbor.new()
	if not world.prepare("adrian"):
		world.free()
		_fail("street prepare")
		return
	root.add_child(world)
	await ticks(120)
	var car: VehicleBody3D=world.vehicle
	if car==null or not car.built or car.contacts()<3 or not car.stopped():
		_fail("four real wheels did not settle: "+str(car.contacts() if car!=null else -1))
		return
	if world.try_toggle_vehicle():
		_fail("remote entry allowed")
		return
	# Establish a repeatable physical approach, not an in-game teleport command.
	var approach: Vector3=car.exit_point(1.0)
	approach.y=0.20
	world.player.global_position=approach
	await ticks(30)
	if not world.try_toggle_vehicle() or not car.occupied or world.player.controls_enabled or world.player.collision_layer!=0 or world._map.actor!=car or not world._status.text.contains("Vehicle controls"):
		_fail("entry or control ownership")
		return
	await ticks(10)
	if absf(car._door_angle)<0.01:
		_fail("actual door pivot did not move")
		return
	await ticks(45)
	var start: Vector3=car.global_position
	var heading: Vector3=car.global_basis.z
	Input.action_press("move_forward")
	await ticks(65)
	Input.action_release("move_forward")
	var travelled: float=(car.global_position-start).dot(heading)
	print("COUPE_ACCEL metres=",travelled," speed=",car.speed_kmh()," contacts=",car.contacts())
	if travelled<0.5 or car.speed_kmh()<2.0:
		_fail("vehicle failed to accelerate forward")
		return
	if world.try_toggle_vehicle():
		_fail("moving exit allowed")
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/coupe_driving.png")!=OK:
			_fail("driving capture")
			return
	Input.action_press("move_left")
	Input.action_press("move_forward")
	await ticks(20)
	Input.action_release("move_left")
	Input.action_release("move_forward")
	if absf(car.steering)<0.08:
		_fail("steering not applied")
		return
	Input.action_press("vehicle_brake")
	await ticks(110)
	Input.action_release("vehicle_brake")
	if not car.stopped():
		_fail("braking failed")
		return
	var reverse_start: Vector3=car.global_position
	var reverse_heading: Vector3=car.global_basis.z
	Input.action_press("move_back")
	await ticks(60)
	Input.action_release("move_back")
	if (car.global_position-reverse_start).dot(reverse_heading)>-0.25:
		_fail("reverse failed")
		return
	Input.action_press("vehicle_brake")
	await ticks(110)
	Input.action_release("vehicle_brake")
	if not car.stopped():
		_fail("reverse braking failed")
		return
	car.toggle_headlights()
	if not car.headlights_on or not car._headlights[0].visible:
		_fail("actual headlight toggle")
		return
	world._toggle_map()
	if car.input_enabled or world.player.controls_enabled:
		_fail("map allowed movement controls")
		return
	world._toggle_map()
	if not car.input_enabled or world.player.controls_enabled:
		_fail("map restored wrong actor")
		return
	world._set_pause(true)
	if not paused or car.input_enabled:
		_fail("driving pause")
		return
	world._set_pause(false)
	if not world.try_toggle_vehicle() or car.occupied or not world.player.controls_enabled or world._map.actor!=world.player or not world._status.text.contains("WASD move"):
		_fail("safe exit and control restoration")
		return
	await ticks(25)
	if not world.player.is_on_floor() or world.player.collision_layer!=2:
		_fail("exit floor or collision")
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/coupe_exit.png")!=OK:
			_fail("exit capture")
			return
	print("CODECITY_VEHICLE_PLAYTEST_OK actual suspension drive reverse steer brake door lights map pause safe exit")
	world.queue_free()
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
