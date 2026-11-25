extends Node3D
## Streams the actual imported modular facades. No stand-in human or building meshes.
const City = preload("res://core/city_layout.gd")
const Harbor = preload("res://core/harbor_layout.gd")
const STREAM_RADIUS := 1
var _templates: Array[Array]=[[],[],[],[]]
var _mesh_cache: Dictionary={}
var _chunks: Dictionary={}
var _pending: Array[Vector2i]=[]
var _focus: Node3D
var _center:=Vector2i(999,999)
var _paving: Material
var _asphalt: Material
var _grass: StandardMaterial3D
var _bench: Array[Dictionary]=[]
var built_parcels:=0

func configure(art: Node3D,paving: Material,actor: Node3D) -> bool:
	_focus=actor
	_paving=paving
	for node: Node in art.find_children("*","MeshInstance3D",true,false):
		var source:=node as MeshInstance3D
		if source.mesh==null:continue
		var lower:=String(source.name).to_lower()
		if lower.begins_with("carriageway"):_asphalt=source.get_active_material(0)
		if "bench" in lower:
			_bench.append({"mesh":source.mesh,"transform":source.global_transform,"material":source.get_active_material(0)})
		for i: int in range(Harbor.BUILDING_IDS.size()):
			if not lower.begins_with(Harbor.BUILDING_IDS[i]):continue
			var center:=Harbor.BUILDINGS[i].get_center()
			var t:=source.global_transform
			t.origin-=Vector3(center.x,0.15,center.y)
			var bounds: AABB=t*source.get_aabb()
			var middle:=bounds.get_center().y
			var top: bool="roof" in lower or "crown_" in lower
			var floor_index:=clampi(floori(middle/3.0),0,int(Harbor.HEIGHTS[i]/3.0)-1)
			var materials: Array[Material]=[]
			for surface: int in range(source.mesh.get_surface_count()):
				materials.append(source.get_active_material(surface))
			_templates[i].append({"mesh":source.mesh,"transform":t,"floor":floor_index,"top":top,"wall":"wall_" in lower or "crown_" in lower,"materials":materials})
			break
	if _asphalt==null or _paving==null:return false
	for group: Array in _templates:
		if group.size()<5:return false
	_grass=StandardMaterial3D.new()
	_grass.albedo_color=Color(0.19,0.29,0.15)
	_grass.roughness=1.0
	return true

func _ready() -> void:
	process_mode=Node.PROCESS_MODE_PAUSABLE
	_surface(self,City.BOUNDS,-0.012,_asphalt,2.1)
	_collider(self,"CityFloor",Vector3(0,-0.15,0),Vector3(City.EXTENT,0.30,City.EXTENT))
	_boundary()
	_recenter()
	# Central tile and nearest neighbors first, before the player can arrive.
	for i: int in range(mini(3,_pending.size())):_build_next()

func set_focus(actor: Node3D) -> void:
	_focus=actor

func _physics_process(_delta: float) -> void:
	_recenter()
	if not _pending.is_empty():_build_next()

func _recenter() -> void:
	if not is_instance_valid(_focus):return
	var cell:=City.cell_at(Vector2(_focus.global_position.x,_focus.global_position.z))
	if cell==_center:return
	_center=cell
	var wanted: Array[Vector2i]=[]
	for dx: int in range(-STREAM_RADIUS,STREAM_RADIUS+1):
		for dz: int in range(-STREAM_RADIUS,STREAM_RADIUS+1):
			var target:=cell+Vector2i(dx,dz)
			if City.valid(target):wanted.append(target)
	for key: Vector2i in _chunks.keys():
		if not wanted.has(key):
			built_parcels-=City.parcels(key).size()
			_chunks[key].queue_free()
			_chunks.erase(key)
	_pending.clear()
	for key: Vector2i in wanted:
		if not _chunks.has(key):_pending.append(key)
	_pending.sort_custom(func(a: Vector2i,b: Vector2i):return (a-_center).length_squared()<(b-_center).length_squared())

func _build_next() -> void:
	if _pending.is_empty():return
	var cell: Vector2i=_pending.pop_front()
	if _chunks.has(cell):return
	var chunk:=Node3D.new()
	chunk.name="Block_%d_%d"%[cell.x,cell.y]
	add_child(chunk)
	_chunks[cell]=chunk
	var lots:=City.paved_lots(cell)
	if cell==Vector2i.ZERO:
		# Keep the imported center street and its courtyard intact. Fill only
		# the surrounding ground, leaving the north/south route continuous.
		var o:=City.origin(cell)
		for rect: Rect2 in [Rect2(o+Vector2(5,5),Vector2(14.9,70)),Rect2(20.1,-35,14.9,70),Rect2(-20,-35,14,16.9),Rect2(6,-35,14,16.9),Rect2(-20,18.1,14,16.9),Rect2(6,18.1,14,16.9)]:
			_surface(chunk,rect,0.005,_paving,1.8)
		return
	if City.PARK_CELLS.has(cell):
		for lot: Rect2 in lots:
			_surface(chunk,lot,0.004,_grass,4.0)
			_park_path(chunk,lot)
		return
	for lot: Rect2 in lots:_surface(chunk,lot,0.004,_paving,1.8)
	var groups: Dictionary={}
	for item: Dictionary in City.parcels(cell):
		_add_parcel(chunk,item,groups)
		built_parcels+=1
	for key: String in groups:
		var entry: Dictionary=groups[key]
		var transforms: Array=entry["transforms"]
		var instances:=MultiMesh.new()
		instances.transform_format=MultiMesh.TRANSFORM_3D
		instances.mesh=entry["mesh"]
		instances.instance_count=transforms.size()
		for i: int in range(transforms.size()):instances.set_instance_transform(i,transforms[i])
		var draw:=MultiMeshInstance3D.new()
		draw.multimesh=instances
		chunk.add_child(draw)

func _add_parcel(chunk: Node3D,item: Dictionary,groups: Dictionary) -> void:
	var index: int=item["prototype"]
	var rect: Rect2=item["rect"]
	var floors: int=item["floors"]
	var style: int=item["style"]
	var center:=rect.get_center()
	var footprint: Rect2=Harbor.BUILDINGS[index]
	var scale:=Vector3(rect.size.x/footprint.size.x,1.0,rect.size.y/footprint.size.y)
	var base:=Transform3D(Basis.from_scale(scale),Vector3(center.x,0.005,center.y))
	var source_floors:=int(Harbor.HEIGHTS[index]/3.0)
	for entry: Dictionary in _templates[index]:
		var t: Transform3D=entry["transform"]
		var mesh: Mesh=entry["mesh"]
		var finish_index:=floori(float(style)/4.0)%City.PALETTE.size()
		var key: String="%d:%d:%d:%s"%[mesh.get_instance_id(),index,finish_index,str(entry["wall"])]
		if not _mesh_cache.has(key):
			var copy:=mesh.duplicate() as Mesh
			var materials: Array=entry["materials"]
			for s: int in range(materials.size()):
				var mat: Material=materials[s]
				if entry["wall"] and mat is StandardMaterial3D:
					var finish:=mat.duplicate() as StandardMaterial3D
					finish.albedo_color*=item["finish"]
					mat=finish
				copy.surface_set_material(s,mat)
			_mesh_cache[key]=copy
		if not groups.has(key):groups[key]={"mesh":_mesh_cache[key],"transforms":[]}
		var transforms: Array=groups[key]["transforms"]
		if entry["top"]:
			t.origin.y+=float(floors-source_floors)*3.0
			transforms.append(base*t)
		elif entry["floor"]==0:
			transforms.append(base*t)
		elif entry["floor"]==1:
			for floor_index: int in range(1,floors):
				var repeated:=t
				repeated.origin.y+=float(floor_index-1)*3.0
				transforms.append(base*repeated)
	# Collision is authoritative and identical to the map parcel footprint.
	_collider(chunk,"ClosedBuilding",Vector3(center.x,float(floors)*1.5,center.y),Vector3(rect.size.x,float(floors)*3.0,rect.size.y))

func _surface(parent: Node3D,rect: Rect2,y: float,material: Material,tile: float) -> void:
	var plane:=PlaneMesh.new()
	plane.size=rect.size
	if material is StandardMaterial3D:
		var mat:=material.duplicate() as StandardMaterial3D
		mat.uv1_scale=Vector3(rect.size.x/tile,rect.size.y/tile,1)
		plane.material=mat
	else:plane.material=material
	var node:=MeshInstance3D.new()
	node.mesh=plane
	node.position=Vector3(rect.get_center().x,y,rect.get_center().y)
	parent.add_child(node)

func _park_path(chunk: Node3D,lot: Rect2) -> void:
	var center:=lot.get_center()
	_surface(chunk,Rect2(center-Vector2(2,lot.size.y*0.5),Vector2(4,lot.size.y)),0.009,_paving,1.8)
	_surface(chunk,Rect2(center-Vector2(lot.size.x*0.5,2),Vector2(lot.size.x,4)),0.009,_paving,1.8)
	# A diagonal pedestrian path through the central green, using actual paving.
	var path:=MeshInstance3D.new()
	var mesh:=PlaneMesh.new()
	mesh.size=Vector2(3,lot.size.length()-5)
	mesh.material=_paving
	path.mesh=mesh
	path.position=Vector3(center.x,0.010,center.y)
	path.rotation.y=PI/4.0
	chunk.add_child(path)
	for entry: Dictionary in _bench:
		var node:=MeshInstance3D.new()
		node.mesh=entry["mesh"]
		var t: Transform3D=entry["transform"]
		t.origin+=Vector3(center.x-8.0,0,center.y-5.0)-Vector3(4.95,0.15,2.0)
		node.transform=t
		node.material_override=entry["material"]
		chunk.add_child(node)
		node.create_trimesh_collision()

func _collider(parent: Node3D,label: String,center: Vector3,extent: Vector3) -> void:
	var body:=StaticBody3D.new()
	body.name=label
	body.collision_layer=1
	body.collision_mask=0
	var shape:=CollisionShape3D.new()
	var volume:=BoxShape3D.new()
	volume.size=extent
	shape.shape=volume
	body.add_child(shape)
	body.position=center
	parent.add_child(body)

func _boundary() -> void:
	var material:=StandardMaterial3D.new()
	material.albedo_color=Color(0.24,0.29,0.30)
	material.roughness=0.8
	for x: float in [-City.HALF,City.HALF]:
		_boundary_wall(Vector3(x,1,0),Vector3(0.20,2,City.EXTENT),material)
	for z: float in [-City.HALF,City.HALF]:
		_boundary_wall(Vector3(0,1,z),Vector3(City.EXTENT,2,0.20),material)

func _boundary_wall(center: Vector3,extent: Vector3,material: Material) -> void:
	_collider(self,"CityLimit",center,extent)
	var node:=MeshInstance3D.new()
	var mesh:=BoxMesh.new()
	mesh.size=extent
	mesh.material=material
	node.mesh=mesh
	node.position=center
	add_child(node)
