extends SceneTree
## Candidate-only Godot import and render review. Not gameplay or asset approval.
## Run in a staged project with exact GLBs, not the shipping game.
var _stage: Node3D
var _camera: Camera3D

func _initialize() -> void:
	call_deferred("_review")

func _review() -> void:
	_stage = Node3D.new()
	root.add_child(_stage)
	var street := _load_asset("res://_qa/street.glb", Vector3.ZERO)
	if street == null:
		_fail("street import failed")
		return
	var adrian := _load_asset("res://_qa/adrian.glb", Vector3(-4.6, 0.15, 10.4))
	var maya := _load_asset("res://_qa/maya.glb", Vector3(-3.8, 0.15, 10.4))
	if adrian == null or maya == null:
		_fail("character import failed")
		return
	if not _check_character(adrian, 1.81) or not _check_character(maya, 1.69):
		_fail("character mesh, skin or height invalid")
		return
	var road_meshes: Array[Node] = street.find_children("*", "MeshInstance3D", true, false)
	if road_meshes.size() < 100:
		_fail("street assembly geometry missing")
		return
	var textured := false
	for mesh: Node in road_meshes:
		var visual := mesh as MeshInstance3D
		if visual.mesh == null:
			_fail("null street mesh")
			return
		for i: int in range(visual.mesh.get_surface_count()):
			var mat := visual.get_active_material(i)
			if mat is BaseMaterial3D and mat.albedo_texture != null:
				textured = true
	if not textured:
		_fail("street lacks imported textures")
		return
	print("CODECITY_REAL_ASSET_IMPORT_OK street_meshes=", road_meshes.size())
	if "--render-review" not in OS.get_cmdline_user_args():
		quit(0)
		return
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	var sky := Sky.new()
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color(0.22, 0.40, 0.66)
	sky_mat.sky_horizon_color = Color(0.74, 0.81, 0.89)
	sky.sky_material = sky_mat
	environment.environment.sky = sky
	environment.environment.background_mode = Environment.BG_SKY
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color(0.75, 0.81, 0.9)
	environment.environment.ambient_light_energy = 0.65
	_stage.add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -32, 0)
	sun.light_energy = 1.35
	sun.shadow_enabled = true
	_stage.add_child(sun)
	_camera = Camera3D.new()
	_camera.fov = 65
	_camera.position = Vector3(-0.8, 1.9, 15.0)
	_stage.add_child(_camera)
	_camera.look_at(Vector3(-3.4, 1.3, 9.0))
	_camera.current = true
	for i: int in range(12):
		await process_frame
	await RenderingServer.frame_post_draw
	if not _capture("res://_qa/character_review.png"):
		_fail("character screenshot failed")
		return
	_camera.position = Vector3(1.2, 1.7, 14.5)
	_camera.look_at(Vector3(0, 2.8, -8))
	for i: int in range(12):
		await process_frame
	await RenderingServer.frame_post_draw
	if not _capture("res://_qa/street_review.png"):
		_fail("street screenshot failed")
		return
	print("CODECITY_REAL_RENDER_REVIEW_OK")
	quit(0)

func _capture(path: String) -> bool:
	var img: Image = root.get_texture().get_image()
	return img != null and not img.is_empty() and img.save_png(path) == OK

func _load_asset(path: String, location: Vector3) -> Node3D:
	var packed := load(path) as PackedScene
	if packed == null:
		return null
	var instance := packed.instantiate() as Node3D
	if instance == null:
		return null
	_stage.add_child(instance)
	instance.position = location
	return instance

func _check_character(actor: Node3D, height: float) -> bool:
	var skins := actor.find_children("*", "Skeleton3D", true, false)
	if skins.size() != 1 or (skins[0] as Skeleton3D).get_bone_count() != 53:
		return false
	var skeleton := skins[0] as Skeleton3D
	skeleton.force_update_all_bone_transforms()
	var low := INF
	var high := -INF
	var raw_low := INF
	var raw_high := -INF
	var textured := false
	var mesh_count := 0
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if mesh.mesh == null:
			return false
		mesh_count += 1
		var box: AABB = mesh.global_transform * mesh.get_aabb()
		raw_low = minf(raw_low, box.position.y)
		raw_high = maxf(raw_high, box.end.y)
		var skin := mesh.skin
		if skin == null or mesh.get_node_or_null(mesh.skeleton) != skeleton:
			return false
		var transforms: Array[Transform3D] = []
		for bind: int in range(skin.get_bind_count()):
			var bone := skin.get_bind_bone(bind)
			if skin.get_bind_name(bind) != &"":
				bone = skeleton.find_bone(skin.get_bind_name(bind))
			if bone < 0 or bone >= skeleton.get_bone_count():
				return false
			transforms.append(skeleton.get_bone_global_pose(bone) * skin.get_bind_pose(bind))
		for i: int in range(mesh.mesh.get_surface_count()):
			var arrays: Array = mesh.mesh.surface_get_arrays(i)
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			# glTF importer uses normalized shape arrays (absolute target positions).
			# Reconstruct the actual visible mesh, including the MPFB active body morph.
			var shapes := mesh.mesh.surface_get_blend_shape_arrays(i)
			if shapes.size() != mesh.get_blend_shape_count():
				return false
			var source_vertices: PackedVector3Array = verts.duplicate()
			var normalized := (mesh.mesh as ArrayMesh).blend_shape_mode == Mesh.BLEND_SHAPE_MODE_NORMALIZED
			for shape: int in range(shapes.size()):
				var values: PackedVector3Array = shapes[shape][Mesh.ARRAY_VERTEX]
				var weight: float = mesh.get_blend_shape_value(shape)
				if values.size() != verts.size() or not is_finite(weight):
					return false
				if absf(weight) < 0.000001:
					continue
				for v: int in range(verts.size()):
					var delta: Vector3 = values[v] - source_vertices[v] if normalized else values[v]
					verts[v] += delta * weight
			var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
			var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
			if verts.is_empty() or weights.size() != bones.size() or bones.size() % verts.size() != 0:
				return false
			@warning_ignore("integer_division")
			var influences: int = bones.size() / verts.size()
			if influences != 4 and influences != 8:
				return false
			for v: int in range(verts.size()):
				var pos := Vector3.ZERO
				var total := 0.0
				for j: int in range(influences):
					var index: int = v * influences + j
					var w: float = weights[index]
					if w <= 0.0:
						continue
					var bind: int = bones[index]
					if bind < 0 or bind >= transforms.size():
						return false
					pos += (transforms[bind] * verts[v]) * w
					total += w
				if absf(total - 1.0) > 0.02:
					return false
				var world_pos: Vector3 = skeleton.global_transform * pos
				low = minf(low, world_pos.y)
				high = maxf(high, world_pos.y)
			var mat := mesh.get_active_material(i)
			if mat is BaseMaterial3D and mat.albedo_texture != null:
				textured = true
	print("CHARACTER_IMPORT meshes=",mesh_count," bones=53 skinned_height=",high-low," raw_aabb_height=",raw_high-raw_low)
	return textured and mesh_count >= 7 and absf(high-low-height) <= 0.08

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
