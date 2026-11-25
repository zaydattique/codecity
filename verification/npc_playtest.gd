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
	var packed := load("res://scenes/foundation.tscn") as PackedScene
	var menu := packed.instantiate()
	menu._enable_city=false
	root.add_child(menu)
	menu._name.text="Living World QA"
	menu._mode.select(0)
	menu._character.select(0)
	menu._on_apply_pressed()
	menu._open_street()
	var world: Node3D=menu._world
	if world==null:
		_fail("world preparation")
		return
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
	# Story progress must follow actual vehicle ownership, displacement and contact.
	if world._story_stage!=0 or world._try_story_contact():
		_fail("story starts completed or accepts premature contact")
		return
	var car: VehicleBody3D=world.vehicle
	if car==null:
		_fail("story car missing")
		return
	var approach: Vector3=car.exit_point(1.0)
	approach.y=0.20
	world.player.global_position=approach
	for i: int in range(45):await physics_frame
	if not world.try_toggle_vehicle() or world._story_stage!=1:
		_fail("story vehicle entry")
		return
	Input.action_press("move_forward")
	for i: int in range(120):
		await physics_frame
		if world._story_stage==2:break
	Input.action_release("move_forward")
	if world._story_stage!=2:
		_fail("story actual drive did not reach goal")
		return
	Input.action_press("vehicle_brake")
	for i: int in range(120):await physics_frame
	Input.action_release("vehicle_brake")
	if not world.try_toggle_vehicle() or world._story_stage!=3:
		_fail("story safe exit")
		return
	# Fixture positioning only: production still requires range and line of sight.
	var contact: Vector3=nora.global_position
	var remote: Vector3=Vector3(-4.6,0.18,12.0) if contact.z<0 else Vector3(-4.6,0.18,-12.0)
	world.player.global_position=remote
	if world._try_story_contact():
		_fail("remote story contact")
		return
	world.player.global_position=contact+Vector3(0.0,0.0,1.0)
	if not world._try_story_contact() or world._story_stage!=4 or world._try_story_contact():
		_fail("story contact or duplicate completion")
		return
	var active: Dictionary=menu.active_snapshot()
	var progress: Dictionary=menu._sessions.snapshot(active["profile_id"])["progress"]
	if progress["living_world"]!=["a_new_beginning"] or not progress["academy"].is_empty() or world.cash!=650 or menu._sessions.cash_balance()!=650:
		_fail("story profile progression separation")
		return
	if "--capture" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/story_complete.png")!=OK:
			_fail("story capture")
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
	world.queue_free()
	await process_frame
	if not Crowd.installed(true):
		_fail("twelve distinct city rig outputs missing")
		return
	var city:=Harbor.new()
	if not city.prepare("maya",false,true,true):
		_fail("city crowd preparation")
		return
	root.add_child(city)
	var city_crowd: Node3D=city.crowd
	if city_crowd==null or city_crowd.actors.size()!=12 or not await _wait_batch(city_crowd,0):
		_fail("twelve actual city actors and first Python batch")
		return
	var city_positions: Dictionary={}
	for id: String in Crowd.CITY_IDS:city_positions[id]=city_crowd.actors[id].global_position
	await create_timer(2.0).timeout
	var moved_city:=0
	for id: String in Crowd.CITY_IDS:
		var resident: CharacterBody3D=city_crowd.actors[id]
		if resident.global_position.distance_to(city_positions[id])>0.25:moved_city+=1
		if not resident.is_on_floor() or (id!="rhea" and resident.global_position.z<60):
			_fail("actual park actor floor or route")
			return
	if moved_city<4 or city_crowd.failed:
		_fail("six additional independent city residents")
		return
	var rhea: CharacterBody3D=city_crowd.actors["iris"]
	city.player.global_position=rhea.global_position+Vector3(1,0,0)
	city_crowd.perceive("greet",rhea.global_position,2.5)
	if not await _wait_batch(city_crowd,city_crowd.accepted_batches) or rhea.action!="acknowledge" or city._subtitle_queue.is_empty() and not city._subtitle.text.contains("Iris"):
		_fail("actual contextual subtitle")
		return
	if "--capture" in OS.get_cmdline_user_args():
		var camera:=Camera3D.new()
		city.add_child(camera)
		camera.global_position=rhea.global_position+Vector3(6,4,9)
		camera.look_at(rhea.global_position+Vector3.UP*0.9)
		camera.current=true
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/city_park_npcs.png")!=OK:
			_fail("park actor capture")
			return
	# Physical shop access and actual transaction with the installed shopkeeper.
	if not is_instance_valid(city.shop) or not city.player.combat_installed:
		_fail("actual market or licensed protagonist combat motions missing")
		return
	city.player.global_position=city.shop.entrance+Vector3.UP*0.04
	for i: int in range(15):await physics_frame
	if not city._try_shop() or not city.shop.player_inside:
		_fail("market entrance")
		return
	city.player.global_position=city.shop.COUNTER+Vector3.UP*0.04
	for i: int in range(15):await physics_frame
	if not city.player.take_damage(25):
		_fail("player health damage")
		return
	await create_timer(1.5).timeout
	if not city._try_shop() or not city.shop.opened:
		_fail("actual seller checkout")
		return
	city._buy(2)
	if city.cash!=465 or city.player.health!=100:
		_fail("health item actual cash debit and heal")
		return
	city._buy(0)
	if city.cash!=465:
		_fail("full health purchase should not charge")
		return
	city.shop.close_trade()
	if "--capture" in OS.get_cmdline_user_args():
		city.player._camera.current=true
		await RenderingServer.frame_post_draw
		if root.get_texture().get_image().save_png("res://_qa/market_interior.png")!=OK:
			_fail("market interior capture")
			return
	city.player.global_position=city.shop.interior_entry+Vector3.UP*0.04
	for i: int in range(10):await physics_frame
	if not city._try_shop() or city.shop.player_inside:
		_fail("market exit")
		return
	# Use actual licensed punch timing, physical range and NPC HP.
	var victim: CharacterBody3D=city_crowd.actors["jules"]
	if not victim.combat_installed:
		_fail("actual NPC combat motion missing")
		return
	city.player.global_position=victim.global_position+Vector3(1.1,0,0)
	city.player._visual.rotation.y=-PI/2
	city.player.velocity=Vector3.ZERO
	for i: int in range(12):await physics_frame
	if not city.player.start_punch():
		_fail("player punch animation start")
		return
	await create_timer(1.2).timeout
	if victim.health!=20:
		_fail("actual hit HP: %d"%victim.health)
		return
	var deadline:=Time.get_ticks_msec()+4000
	while city.player._combat_lock>0 and Time.get_ticks_msec()<deadline:await physics_frame
	city.player.global_position=victim.global_position+Vector3(1.1,0,0)
	city.player._visual.rotation.y=-PI/2
	for i: int in range(12):await physics_frame
	if not city.player.start_punch():
		_fail("second punch animation")
		return
	await create_timer(1.4).timeout
	if not victim.dead or victim.health!=0 or victim.collision_layer!=0:
		_fail("actual death state and collision ownership")
		return
	var fade_deadline:=Time.get_ticks_msec()+10000
	while victim._art.visible and Time.get_ticks_msec()<fade_deadline:await physics_frame
	if victim._art.visible:
		_fail("body fade did not complete")
		return
	print("CODECITY_COMMERCE_COMBAT_OK physical store purchase and melee damage fade")
	print("CODECITY_CITY_NPC_OK twelve distinct rigs")
	print("CODECITY_NPC_PLAYTEST_OK core and city rigs persistent Python movement dialogue pause fallback")
	city.queue_free()
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
