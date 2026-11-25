extends Node3D
## A functional ground-floor store inside the existing east building, not a facade.
const Layout=preload("res://core/harbor_layout.gd")
const Style=preload("res://core/ui_style.gd")
const PRICES := [5,10,35]
const HEALS := [5,15,40]
const PRODUCTS := ["Water","Snack","First aid kit"]
const COUNTER := Vector3(11.2,0.15,-9.3)
signal trade_changed(open: bool)
signal purchase_requested(index: int)
var entrance:=Vector3.ZERO
var interior_entry:=Vector3.ZERO
var player_inside:=false
var opened:=false
var _panel: PanelContainer
var _status: Label
var _balance: Label
var _world: Node3D

func setup(world: Node3D,art: Node3D,hud: CanvasLayer) -> bool:
	_world=world
	var footprint: Rect2=Layout.BUILDINGS[1]
	var found:=false
	for node: Node in art.find_children("*","MeshInstance3D",true,false):
		var mesh:=node as MeshInstance3D
		var n:=String(mesh.name).to_lower()
		if n.begins_with(Layout.BUILDING_IDS[1]) and "door_centered_small_01" in n and not "wall_" in n:
			var center: Vector3=(mesh.global_transform*mesh.get_aabb()).get_center()
			if absf(center.x-footprint.position.x)<0.8:
				entrance=Vector3(footprint.position.x-0.8,0.15,center.z)
				interior_entry=Vector3(footprint.position.x+0.85,0.15,center.z)
				found=true
				break
	if not found:return false
	var plaster:=_material(Color(0.74,0.72,0.66),0,0.86)
	var wood:=_material(Color(0.27,0.15,0.08),0,0.68)
	var metal:=_material(Color(0.19,0.23,0.25),0.55,0.48)
	var dark:=_material(Color(0.08,0.12,0.13),0.2,0.55)
	var x0:=footprint.position.x+0.1
	var x1:=footprint.end.x-0.1
	var z0:=footprint.position.y+0.1
	var z1:=footprint.end.y-0.1
	var center:=footprint.get_center()
	# Internal surfaces match the exterior footprint. Door traversal is an
	# explicit interaction transition into this real, furnished 3D room.
	_box("Floor",Vector3(center.x,0.145,center.y),Vector3(footprint.size.x-0.2,0.02,footprint.size.y-0.2),wood,false)
	_box("WestWall",Vector3(x0,1.65,center.y),Vector3(0.18,3,footprint.size.y),plaster,true)
	_box("EastWall",Vector3(x1,1.65,center.y),Vector3(0.18,3,footprint.size.y),plaster,true)
	_box("NorthWall",Vector3(center.x,1.65,z0),Vector3(footprint.size.x,3,0.18),plaster,true)
	_box("SouthWall",Vector3(center.x,1.65,z1),Vector3(footprint.size.x,3,0.18),plaster,true)
	_box("Ceiling",Vector3(center.x,3.20,center.y),Vector3(footprint.size.x,0.1,footprint.size.y),plaster,true)
	_box("Checkout",Vector3(12.2,0.65,-9.3),Vector3(0.75,1.0,2.7),wood,true)
	_box("Register",Vector3(12.05,1.26,-9.3),Vector3(0.45,0.2,0.36),dark,false)
	_box("RegisterScreen",Vector3(12.05,1.46,-9.3),Vector3(0.35,0.22,0.08),metal,false)
	var packages: Array[Material]=[_material(Color(0.14,0.43,0.58),0,0.6),_material(Color(0.67,0.40,0.11),0,0.75),_material(Color(0.72,0.75,0.68),0,0.6)]
	for shelf_z: float in [-14.8,-4.0]:
		_box("ShelfFrame",Vector3(10.1,0.95,shelf_z),Vector3(3.2,1.6,0.48),metal,true)
		for y: float in [0.55,1.0,1.45]:
			_box("Shelf",Vector3(10.1,y,shelf_z-0.28),Vector3(3.3,0.07,0.60),wood,false)
			for i: int in range(9):
				_box("Stock",Vector3(8.7+i*0.34,y+0.15,shelf_z-0.30),Vector3(0.22,0.23,0.22),packages[i%packages.size()],false)
	for z: float in [-13.5,-7.0,-3.0]:
		var light:=OmniLight3D.new()
		light.position=Vector3(center.x,2.8,z)
		light.omni_range=5.5
		light.light_energy=1.3
		light.light_color=Color(1.0,0.91,0.74)
		add_child(light)
		_box("Fixture",Vector3(center.x,3.0,z),Vector3(1.4,0.07,0.25),metal,false)
	_sign("HARBOR MARKET",entrance+Vector3.UP*2.25,0.006,Color(0.94,0.82,0.59))
	_sign("CHECKOUT",Vector3(12.2,2.15,-9.3),0.004,Color(0.86,0.93,0.87))
	_sign("EXIT",interior_entry+Vector3.UP*2.05,0.004,Color(0.75,0.94,0.82))
	_build_menu(hud)
	return true

func _material(color: Color,metallic: float,roughness: float) -> StandardMaterial3D:
	var material:=StandardMaterial3D.new()
	material.albedo_color=color
	material.metallic=metallic
	material.roughness=roughness
	return material

func _box(label: String,at: Vector3,extent: Vector3,material: Material,solid: bool) -> void:
	var mesh:=BoxMesh.new()
	mesh.size=extent
	mesh.material=material
	var instance:=MeshInstance3D.new()
	instance.name=label
	instance.mesh=mesh
	instance.position=at
	add_child(instance)
	if solid:
		var body:=StaticBody3D.new()
		var shape:=CollisionShape3D.new()
		var volume:=BoxShape3D.new()
		volume.size=extent
		shape.shape=volume
		body.add_child(shape)
		body.position=at
		add_child(body)

func _sign(text: String,at: Vector3,pixel: float,color: Color) -> void:
	var label:=Label3D.new()
	label.text=text
	label.position=at
	label.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	label.pixel_size=pixel
	label.font_size=42
	label.modulate=color
	add_child(label)

func _build_menu(hud: CanvasLayer) -> void:
	_panel=PanelContainer.new()
	_panel.position=Vector2(400,180)
	_panel.custom_minimum_size=Vector2(480,0)
	_panel.theme=Style.theme()
	var layout:=VBoxContainer.new()
	layout.add_theme_constant_override("separation",10)
	_panel.add_child(layout)
	var heading:=Label.new()
	heading.text="HARBOR MARKET"
	heading.add_theme_font_size_override("font_size",26)
	layout.add_child(heading)
	_balance=Label.new()
	layout.add_child(_balance)
	for i: int in range(PRODUCTS.size()):
		var button:=Button.new()
		button.text="%s   $%d   +%d health"%[PRODUCTS[i],PRICES[i],HEALS[i]]
		button.pressed.connect(func():purchase_requested.emit(i))
		layout.add_child(button)
	_status=Label.new()
	_status.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	_status.text="Items are consumed immediately."
	layout.add_child(_status)
	var close:=Button.new()
	close.text="Back"
	close.pressed.connect(close_trade)
	layout.add_child(close)
	hud.add_child(_panel)
	_panel.hide()

func enter(actor: CharacterBody3D) -> bool:
	if player_inside or actor.global_position.distance_to(entrance)>1.8:return false
	actor.global_position=interior_entry+Vector3.UP*0.04
	actor.velocity=Vector3.ZERO
	player_inside=true
	return true

func exit(actor: CharacterBody3D) -> bool:
	if not player_inside or opened or actor.global_position.distance_to(interior_entry)>1.8:return false
	actor.global_position=entrance+Vector3.UP*0.04
	actor.velocity=Vector3.ZERO
	player_inside=false
	return true

func can_trade(actor: CharacterBody3D,seller: Node3D) -> bool:
	return player_inside and is_instance_valid(seller) and not seller.get("dead")==true and actor.global_position.distance_to(COUNTER)<1.6 and seller.global_position.distance_to(COUNTER)<3.2

func open_trade(actor: CharacterBody3D,seller: Node3D,cash: int) -> bool:
	if opened or not can_trade(actor,seller):return false
	opened=true
	_balance.text="Cash: $%d"%cash
	_status.text="Items are consumed immediately."
	_panel.show()
	trade_changed.emit(true)
	return true

func result(message: String,cash: int) -> void:
	_status.text=message
	_balance.text="Cash: $%d"%cash

func close_trade() -> void:
	if not opened:return
	opened=false
	_panel.hide()
	trade_changed.emit(false)
