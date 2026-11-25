extends RefCounted
## Deterministic, square city plan. Geometry, collision and map share these parcels.
## 15 x 15 cells of 80m, centered on Harbor Boulevard.
const Harbor = preload("res://core/harbor_layout.gd")
const CELL := 80.0
const HALF := 600.0
const EXTENT := 1200.0
const RADIUS := 7
const BOUNDS := Rect2(-HALF,-HALF,EXTENT,EXTENT)
const PARK_CELLS := [Vector2i(-1,1),Vector2i(0,1),Vector2i(1,1)]
const TOWER_CELLS := [Vector2i(-2,1),Vector2i(2,1),Vector2i(-1,0),Vector2i(1,0),Vector2i(-2,2),Vector2i(2,2),Vector2i(-1,2),Vector2i(0,2),Vector2i(1,2),Vector2i(0,-1)]
const TOWER_FLOORS := [12,16,14,20,11,18,13,17,15,19]
const DISTRICTS := ["Harbor","Market","Residential","Downtown","Industrial","Waterfront"]
const PALETTE: Array[Color]=[Color(0.88,0.91,0.95),Color(1,0.85,0.70),Color(0.73,0.86,0.78),Color(0.95,0.72,0.65),Color(0.68,0.78,0.91),Color(0.87,0.83,0.74),Color(0.83,0.78,0.90),Color(0.78,0.84,0.84)]
const USES := ["Cafe","Grocer","Apartments","Office","Workshop","Bookshop","Clothing","Pharmacy","Hotel","Restaurant","Gallery","Storage","Studio","Market"]

static func cell_at(p: Vector2) -> Vector2i:
	return Vector2i(floori((p.x+CELL*0.5)/CELL),floori((p.y+CELL*0.5)/CELL))

static func valid(cell: Vector2i) -> bool:
	return absi(cell.x)<=RADIUS and absi(cell.y)<=RADIUS

static func origin(cell: Vector2i) -> Vector2:
	return Vector2(cell)*CELL-Vector2.ONE*CELL*0.5

static func _seed(cell: Vector2i) -> int:
	return (cell.x+RADIUS)*31+(cell.y+RADIUS)*73+13

static func district(cell: Vector2i) -> String:
	if cell==Vector2i.ZERO:return "Harbor Boulevard"
	if PARK_CELLS.has(cell):return "Harbor Park"
	if absi(cell.x)<=2 and absi(cell.y)<=2:return "Downtown"
	if cell.y>=4:return "Waterfront"
	if cell.x>=4:return "Industrial"
	if cell.x<=-4:return "Residential"
	return "Market"

static func paved_lots(cell: Vector2i) -> Array[Rect2]:
	if not valid(cell):return []
	var o:=origin(cell)
	if cell==Vector2i.ZERO or PARK_CELLS.has(cell):
		return [Rect2(o+Vector2(5,5),Vector2(70,70))]
	var s:=_seed(cell)
	var x:=float(28+s%23)
	var z:=float(27+(s*3)%25)
	# Main roads join at cell boundaries; staggered local streets form smaller
	# asymmetric blocks. Every lot has pedestrian clearance on all sides.
	return [
		Rect2(o+Vector2(5,5),Vector2(x-9,z-9)),
		Rect2(o+Vector2(x+4,5),Vector2(71-x,z-9)),
		Rect2(o+Vector2(5,z+4),Vector2(x-9,71-z)),
		Rect2(o+Vector2(x+4,z+4),Vector2(71-x,71-z))
	]

static func parcels(cell: Vector2i) -> Array[Dictionary]:
	var result: Array[Dictionary]=[]
	if not valid(cell) or cell==Vector2i.ZERO or PARK_CELLS.has(cell):return result
	var s:=_seed(cell)
	var lots:=paved_lots(cell)
	var tower_index:=TOWER_CELLS.find(cell)
	for i: int in range(lots.size()):
		var lot:=lots[i]
		var style:=posmod(s+i*13,50)
		var prototype:=style%4
		var desired:=Vector2(9.5+float(style%6)*1.1,11.0+float((style*3)%8)*1.3)
		var footprint:=Vector2(minf(desired.x,lot.size.x-4),minf(desired.y,lot.size.y-4))
		var offset:=Vector2(float((s+i*2)%3)-1,float((s+i*5)%3)-1)
		var rect:=Rect2(lot.get_center()-footprint*0.5+offset,footprint)
		var floors:=2+style%3
		var is_tower:=tower_index>=0 and i==0
		if is_tower:floors=TOWER_FLOORS[tower_index]
		result.append({"rect":rect,"prototype":prototype,"style":style,"floors":floors,"tower":is_tower,"use":USES[style%USES.size()],"finish":PALETTE[floori(float(style)/4.0)%PALETTE.size()]})
	return result

static func walkable(p: Vector2) -> bool:
	if not BOUNDS.has_point(p):return false
	var cell:=cell_at(p)
	if cell==Vector2i.ZERO:
		for footprint: Rect2 in Harbor.BUILDINGS:
			if footprint.has_point(p):return false
	for item: Dictionary in parcels(cell):
		var footprint: Rect2=item["rect"]
		if footprint.has_point(p):return false
	return true

static func _pixel_rect(r: Rect2,side: int) -> Rect2i:
	var scale:=float(side)/EXTENT
	var a: Vector2i=Vector2i((r.position+Vector2.ONE*HALF)*scale)
	var b: Vector2i=Vector2i((r.end+Vector2.ONE*HALF)*scale)
	return Rect2i(a,Vector2i(maxi(1,b.x-a.x),maxi(1,b.y-a.y)))

static func map_image(side: int=1536) -> Image:
	var image:=Image.create_empty(side,side,false,Image.FORMAT_RGB8)
	image.fill(Color(0.12,0.17,0.21))
	for x: int in range(-RADIUS,RADIUS+1):
		for z: int in range(-RADIUS,RADIUS+1):
			var cell:=Vector2i(x,z)
			for lot: Rect2 in paved_lots(cell):
				image.fill_rect(_pixel_rect(lot,side),Color(0.26,0.37,0.28) if PARK_CELLS.has(cell) else Color(0.29,0.33,0.35))
			for item: Dictionary in parcels(cell):
				image.fill_rect(_pixel_rect(item["rect"],side),Color(0.49,0.59,0.63) if item["tower"] else Color(0.40,0.44,0.46))
	image.fill_rect(_pixel_rect(Harbor.BLOCK,side),Color(0.29,0.33,0.35))
	image.fill_rect(_pixel_rect(Harbor.ROAD,side),Color(0.12,0.17,0.21))
	for rect: Rect2 in Harbor.BUILDINGS:image.fill_rect(_pixel_rect(rect,side),Color(0.40,0.44,0.46))
	return image
