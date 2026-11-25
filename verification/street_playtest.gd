extends SceneTree
const Harbor = preload("res://scenes/harbor_playtest.gd")
const Layout = preload("res://core/harbor_layout.gd")

func _initialize() -> void:
	call_deferred("_verify")

func ticks(count: int) -> void:
	for i: int in range(count):
		await physics_frame

func _verify() -> void:
	if not Harbor.installed():
		_fail("missing actual asset pack")
		return
	var world=Harbor.new()
	if not world.prepare("adrian"):
		_fail("Adrian spawn preparation")
		return
	root.add_child(world)
	await ticks(15)
	var actor: CharacterBody3D=world.player
	if not actor.is_on_floor() or absf(actor.position.y-0.15)>0.05:
		_fail("spawn did not settle on actual sidewalk proxy")
		return
	var require_motion := "--motion" in OS.get_cmdline_user_args()
	if require_motion and (not actor.motion_installed or actor.motion_clip()!="idle"):
		_fail("licensed idle clip missing; installed=%s clip=%s"%[actor.motion_installed,actor.motion_clip()])
		return
	var start: Vector3=actor.position
	Input.action_press("move_forward")
	await ticks(90)
	if require_motion and actor.motion_clip()!="jog":
		_fail("licensed locomotion clip not playing")
		return
	Input.action_release("move_forward")
	await ticks(12)
	if actor.position.z>start.z-3.0 or not Layout.street_contains(actor.position):
		_fail("walking movement")
		return
	var before: float=actor.position.y
	Input.action_press("jump")
	await ticks(10)
	Input.action_release("jump")
	if actor.position.y<before+0.20:
		_fail("jump")
		return
	await ticks(65)
	if not actor.is_on_floor():
		_fail("jump landing")
		return
	Input.action_press("move_left")
	await ticks(110)
	Input.action_release("move_left")
	await ticks(12)
	if actor.position.x < -5.78 or actor.position.x > -5.4:
		_fail("building wall collision")
		return
	world._toggle_map()
	var paused_pos: Vector3=actor.position
	Input.action_press("move_forward")
	await ticks(30)
	Input.action_release("move_forward")
	if actor.position.distance_to(paused_pos)>0.03 or not world._map.expanded:
		_fail("map control ownership")
		return
	world._toggle_map()
	world._set_pause(true)
	if actor.controls_enabled or not paused:
		_fail("pause ownership")
		return
	world._set_pause(false)
	if not actor.controls_enabled or paused:
		_fail("resume")
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/street_playtest.png")!=OK:
			_fail("capture failed")
			return
		world._toggle_map()
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/full_map.png")!=OK:
			_fail("map capture failed")
			return
		world._toggle_map()
	world.queue_free()
	await process_frame
	var other=Harbor.new()
	if not other.prepare("maya"):
		_fail("Maya spawn preparation")
		return
	root.add_child(other)
	await ticks(15)
	if not other.player.is_on_floor() or not is_equal_approx(other.player.height_m,1.69) or (require_motion and not other.player.motion_installed):
		_fail("second protagonist spawn")
		return
	print("CODECITY_STREET_PLAYTEST_OK walking jump wall map pause both protagonists")
	other.queue_free()
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
