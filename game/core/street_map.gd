extends Control
## Both the minimap and expanded map draw the same installed world footprint.
const Layout = preload("res://core/harbor_layout.gd")
var actor: Node3D
var expanded := false
var zoom := 1.0
var pan := Vector2.ZERO
var waypoint := Vector2.INF

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
	return minf((size.x-24.0)/32.0,(size.y-46.0)/34.0)*zoom

func _screen(p: Vector2) -> Vector2:
	return size*0.5+Vector2(0,8)+pan+p*_scale_factor()

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
	draw_rect(Rect2(Vector2.ZERO,size),Color(0.035,0.06,0.085,0.94))
	draw_rect(_map_rect(Layout.STREET),Color(0.31,0.36,0.39))
	draw_rect(_map_rect(Layout.ROAD),Color(0.14,0.18,0.22))
	for r: Rect2 in Layout.BUILDINGS:
		draw_rect(_map_rect(r),Color(0.46,0.40,0.33))
		draw_rect(_map_rect(r),Color(0.62,0.56,0.46),false,1.0)
	draw_line(_screen(Vector2(0,-16)),_screen(Vector2(0,16)),Color(0.7,0.7,0.6),1.0)
	draw_circle(_screen(Layout.BENCH),3,Color(0.78,0.67,0.45))
	if waypoint.is_finite():
		draw_circle(_screen(waypoint),5,Color(0.92,0.68,0.23),false,2.0)
	if is_instance_valid(actor):
		draw_circle(_screen(Layout.map_position(actor.global_position)),5,Color(0.35,0.85,1.0))
	var font := ThemeDB.fallback_font
	draw_string(font,Vector2(10,18),"HARBOR BOULEVARD",HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color.WHITE)
	draw_string(font,Vector2(size.x-21,18),"N",HORIZONTAL_ALIGNMENT_LEFT,-1,12,Color.WHITE)
	if expanded:
		draw_string(font,Vector2(10,size.y-10),"Click street: waypoint | Wheel: zoom | Middle drag: pan",HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color.WHITE)
