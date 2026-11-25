extends SceneTree
## Test-only: runs on an isolated copy of game containing the licensed GLB.
## Does not make an asset approved or create gameplay geometry.

func _initialize() -> void:
	call_deferred("_verify")

func _verify() -> void:
	var scene: PackedScene = load("res://_qa/bench.glb") as PackedScene
	if scene == null:
		_fail("GLB did not import as PackedScene")
		return
	var instance: Node = scene.instantiate()
	root.add_child(instance)
	var meshes: Array[Node] = instance.find_children("*", "MeshInstance3D", true, false)
	if instance is MeshInstance3D:
		meshes.push_front(instance)
	if meshes.is_empty():
		_fail("Imported scene contains no mesh")
		return
	var bounds := AABB()
	var first := true
	var textured := false
	var triangle_count := 0
	for node: Node in meshes:
		var mesh_node := node as MeshInstance3D
		if mesh_node.mesh == null:
			_fail("Missing mesh resource")
			return
		var box: AABB = mesh_node.global_transform * mesh_node.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
		for i: int in range(mesh_node.mesh.get_surface_count()):
			var material := mesh_node.get_active_material(i)
			if material is BaseMaterial3D and material.albedo_texture != null:
				textured = true
			var arrays: Array = mesh_node.mesh.surface_get_arrays(i)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			@warning_ignore("integer_division")
			triangle_count += (indices.size() if not indices.is_empty() else vertices.size()) / 3
	if not textured or triangle_count != 630:
		_fail("Unexpected texture or triangle count")
		return
	var size_values: Array[float] = [bounds.size.x, bounds.size.y, bounds.size.z]
	size_values.sort()
	var expected: Array[float] = [0.49654, 0.88929, 1.16494]
	for i: int in range(3):
		if absf(size_values[i] - expected[i]) > 0.03:
			_fail("Unexpected imported dimensions")
			return
	print("CODECITY_BENCH_IMPORT_OK triangles=", triangle_count, " dimensions=", bounds.size)
	instance.queue_free()
	quit(0)

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
