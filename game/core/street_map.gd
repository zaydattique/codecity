extends Control
## Both the minimap and expanded map draw the same installed world footprint.
const Layout = preload("res://core/harbor_layout.gd")
var actor: Node3D
var expanded := false
var zoom := 1.0
var pan := Vector2.ZERO
var waypoint := Vector2.INF
var academy := false
var story_target := Vector2.INF
var aerial: Texture2D

func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_IGNORE

func _process(_delta: float) -> void:
	queue_redraw()

func toggle_full() -> void:
	expanded=not expanded
	mouse_filter=Control.MOUSE_FILTER_STOP if expanded else Control.MOUSE_FILTER_IGNORE
	zoom=1.0
	pan=Vector2.ZERO
	queue_redraw()

func _scale_factor() -> float:
	return minf((size.x-48.0)/32.0,(size.y-72.0)/34.0)*zoom if expanded else 9.0

func _screen(p: Vector2) -> Vector2:
	var center := Vector2.ZERO if expanded or not is_instance_valid(actor) else Layout.map_position(actor.global_position)
	return size*0.5+Vector2(0,8)+pan+(p-center)*_scale_factor()

func _map_rect(r: Rect2) -> Rect2:
	return Rect2(_screen(r.position),r.size*_scale_factor())

func _gui_input(event: InputEvent) -> void:
	if not expanded:
		return
	if event is InputEventMouseButton and event.pressed:
		if event.button_index==MOUSE_BUTTON_WHEEL_UP:
			zoom=clampf(zoom*1.15,1.0,3.0)
		elif event.button_index==MOUSE_BUTTON_WHEEL_DOWN:
			zoom=clampf(zoom/1.15,1.0,3.0)
		elif event.button_index==MOUSE_BUTTON_LEFT:
			var p: Vector2=(event.position-size*0.5-Vector2(0,8)-pan)/_scale_factor()
			if Layout.STREET.has_point(p):
				waypoint=p
		elif event.button_index==MOUSE_BUTTON_RIGHT:
			waypoint=Vector2.INF
		accept_event()
	elif event is InputEventMouseMotion and event.button_mask&MOUSE_BUTTON_MASK_MIDDLE:
		pan=(pan+event.relative).clamp(-size,size)
		accept_event()

func _draw() -> void:
	var ink := Color(0.78,0.85,0.88)
	var font := ThemeDB.fallback_font
	draw_rect(Rect2(Vector2.ZERO,size),Color(0.035,0.055,0.075,0.97))
	# All shapes use the real playable extent; no invented city districts.
	if aerial!=null:
		draw_texture_rect(aerial,_map_rect(Rect2(-18,-18,36,36)),false,Color(0.74,0.82,0.86))
	draw_rect(_map_rect(Layout.STREET),Color(0.24,0.30,0.33,0.22 if aerial!=null else 1.0))
	draw_rect(_map_rect(Layout.ROAD),Color(0.10,0.14,0.18,0.26 if aerial!=null else 1.0))
	for x: float in [-3.4,3.4]:
		draw_line(_screen(Vector2(x,-16)),_screen(Vector2(x,16)),Color(0.53,0.60,0.61),1.4,true)
	for r: Rect2 in Layout.BUILDINGS:
		draw_rect(_map_rect(r),Color(0.18,0.25,0.29,0.20 if aerial!=null else 1.0))
		draw_rect(_map_rect(r),Color(0.39,0.49,0.52),false,1.5)
		for y: int in range(int(r.position.y)+3,int(r.end.y),3) if aerial==null else []:
			draw_line(_screen(Vector2(r.position.x,y)),_screen(Vector2(r.end.x,y)),Color(0.27,0.34,0.37),1)
	for y: int in range(-15,16,3):
		draw_line(_screen(Vector2(0,y)),_screen(Vector2(0,y+1.4)),Color(0.55,0.61,0.63),1.5,true)
	draw_rect(_map_rect(Layout.STREET),Color(0.40,0.53,0.56),false,1.2)
	if academy:
		var pos := _screen(Vector2(-5.25,5))
		draw_circle(pos,6,Color(0.97,0.71,0.34))
		if expanded:draw_string(font,pos+Vector2(13,4),"Harbor utilities",HORIZONTAL_ALIGNMENT_LEFT,-1,15,ink)
	if story_target.is_finite():
		var target := _screen(story_target)
		draw_circle(target,8,Color(0.97,0.71,0.34),false,2.5)
		if expanded:draw_string(font,target+Vector2(12,4),"Nora",HORIZONTAL_ALIGNMENT_LEFT,-1,15,ink)
	if waypoint.is_finite():
		draw_circle(_screen(waypoint),6,Color(0.92,0.68,0.23),false,2.0)
	if is_instance_valid(actor):
		var pos := _screen(Layout.map_position(actor.global_position))
		var heading: Vector3 = actor.global_basis.z if actor is VehicleBody3D else -Basis(Vector3.UP,float(actor.get("yaw"))).z
		var direction := Vector2(heading.x,heading.z).normalized()
		var side := Vector2(-direction.y,direction.x)
		draw_circle(pos,10,Color(0.08,0.12,0.15))
		draw_colored_polygon(PackedVector2Array([pos+direction*10,pos-direction*6+side*5,pos-direction*6-side*5]),Color(0.52,0.91,0.98))
	# Opaque header and footer keep the viewport legible when panned/zoomed.
	draw_rect(Rect2(0,0,size.x,34),Color(0.045,0.075,0.095))
	draw_string(font,Vector2(12,23),"HARBOR BOULEVARD",HORIZONTAL_ALIGNMENT_LEFT,-1,14,ink)
	draw_string(font,Vector2(size.x-24,23),"N",HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color(0.52,0.91,0.98))
	draw_rect(Rect2(0,size.y-28,size.x,28),Color(0.045,0.075,0.095))
	draw_string(font,Vector2(12,size.y-9),"M  Close  |  Scroll to zoom  |  Click to mark" if expanded else "M  Expand map",HORIZONTAL_ALIGNMENT_LEFT,-1,12,ink)
	if expanded:
		draw_string(font,Vector2(24,65),"Current district",HORIZONTAL_ALIGNMENT_LEFT,-1,18,ink)
		draw_string(font,Vector2(24,86),"32 m playable street",HORIZONTAL_ALIGNMENT_LEFT,-1,13,ink)
		draw_string(font,Vector2(size.x-210,65),"MAP LEGEND",HORIZONTAL_ALIGNMENT_LEFT,-1,14,ink)
		draw_string(font,Vector2(size.x-210,88),"Cyan  /  Player or vehicle",HORIZONTAL_ALIGNMENT_LEFT,-1,13,ink)
		draw_string(font,Vector2(size.x-210,109),"Grey  /  Closed buildings",HORIZONTAL_ALIGNMENT_LEFT,-1,13,ink)
