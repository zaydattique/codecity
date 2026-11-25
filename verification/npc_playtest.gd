extends SceneTree
const Harbor = preload("res://scenes/harbor_playtest.gd")
const Crowd = preload("res://core/npc_director.gd")

func _initialize() -> void:
	call_deferred("_verify")

func _wait_batch(crowd: Node, previous: int) -> bool:
	var deadline := Time.get_ticks_msec()+5000
	while crowd.accepted_batches<=previous and not crowd.failed and Time.get_ticks_msec()<deadline:
		await create_timer(0.025).timeout
	return crowd.accepted_batches>previous and not crowd.failed

func _verify() -> void:
	if not Crowd.installed():
		_fail("six actual cast assets or Python missing")
		return
	var world=Harbor.new()
	if not world.prepare("adrian"):
		world.free()
		_fail("world preparation")
		return
	root.add_child(world)
	var crowd: Node3D=world.crowd
	if crowd==null or crowd.actors.size()!=6:
		_fail("six actual NPC actors missing")
		return
	if not await _wait_batch(crowd,0):
		_fail("first real Python batch")
		return
	var positions := {}
	for id: String in Crowd.IDS:
		positions[id]=crowd.actors[id].global_position
	var before: int=crowd.accepted_batches
	await create_timer(2.0).timeout
	if crowd.failed or crowd.accepted_batches<=before:
		_fail("persistent Python worker stopped")
		return
	var moved := 0
	for id: String in Crowd.IDS:
		var actor: CharacterBody3D=crowd.actors[id]
		if actor.global_position.distance_to(positions[id])>0.25:moved+=1
		if not actor.is_on_floor() or not actor.global_position.is_finite():
			_fail("NPC physical movement or ground")
			return
	if moved<4:
		_fail("fewer than four independent actors moved")
		return
	# Send the same genuine in-world greeting to two distinct profiles.
	var nora: CharacterBody3D=crowd.actors["nora"]
	var liam: CharacterBody3D=crowd.actors["liam"]
	crowd.perceive("greet",nora.global_position,2.5)
	crowd.perceive("greet",liam.global_position,2.5)
	before=crowd.accepted_batches
	if not await _wait_batch(crowd,before):
		_fail("contextual greeting batch")
		return
	if nora.action!="acknowledge" or liam.action=="acknowledge":
		_fail("personality-specific greeting not observed: "+str([nora.action,liam.action]))
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/npc_street.png")!=OK:
			_fail("NPC street capture")
			return
		# One actual cast view, not generated concept art.
		var camera := Camera3D.new()
		world.add_child(camera)
		camera.global_position=Vector3(0,10,18)
		camera.look_at(Vector3(0,0.7,0))
		camera.current=true
		for i: int in range(3):await process_frame
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/npc_overview.png")!=OK:
			_fail("NPC overview capture")
			return
	# Pause and terminate the real Python worker; require explicit idle fallback.
	world._set_pause(true)
	before=crowd.accepted_batches
	await create_timer(0.2,true).timeout
	if crowd.accepted_batches!=before:
		_fail("NPC decision tick during pause")
		return
	world._set_pause(false)
	# Request real worker termination through its owned mailbox. OS.kill from
	# the fixture would remove Godot's process-map entry behind the bridge.
	var stop := FileAccess.open(crowd.bridge.folder.path_join("stop"),FileAccess.WRITE)
	if stop==null:
		_fail("worker stop request")
		return
	stop.close()
	var stop_deadline := Time.get_ticks_msec()+4000
	while not crowd.failed and Time.get_ticks_msec()<stop_deadline:
		await create_timer(0.025).timeout
	if not crowd.failed:
		_fail("dead worker not detected")
		return
	for actor: Node in crowd.actors.values():
		if actor.action!="idle" or actor.expires!=-1:
			_fail("fallback continued to claim Python decisions")
			return
	print("CODECITY_NPC_PLAYTEST_OK six rigs persistent Python independent movement greeting pause idle fallback")
	world.queue_free()
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
