extends RefCounted
## Original 32m street plus accessible alleys and rear courts within the same block.
## +X east, -Z north. Each building translation matches the imported art group.
const STREET := Rect2(-6.0, -16.0, 12.0, 32.0)
const ROAD := Rect2(-3.4, -16.0, 6.8, 32.0)
const BLOCK := Rect2(-20,-18,40,36)
const SIDEWALKS: Array[Rect2] = [Rect2(-6,-16,2.6,32),Rect2(3.4,-16,2.6,32)]
const COURTS: Array[Rect2] = [Rect2(-20,-18,14,36),Rect2(6,-18,14,36),Rect2(-6,-18,12,2),Rect2(-6,16,12,2)]
const BUILDING_IDS := ["harbor_east_01","harbor_east_02","harbor_west_01","harbor_west_02"]
const BUILDING_OFFSETS: Array[Vector3] = [Vector3(1.25,0,1.5),Vector3(1.25,0,-1.5),Vector3(-1.25,0,1.5),Vector3(-1.25,0,-1.5)]
const BUILDING_DEPTH_SCALE: Array[float] = [1.0,0.8,0.8,1.0]
const BUILDINGS: Array[Rect2] = [
	Rect2(7.25,1.5,9,15), Rect2(7.25,-16.5,7.2,15),
	Rect2(-14.45,-1.5,7.2,18), Rect2(-16.25,-16.5,9,12)
]
const HEIGHTS: Array[float] = [9.0,6.0,6.0,9.0]
const BENCH := Vector2(4.95,2.0)
const SPAWN := Vector3(-4.65,0.18,10.4)
const MAP_EXTENT := 42.0

static func walkable(p: Vector2) -> bool:
	if not BLOCK.has_point(p):return false
	for r: Rect2 in BUILDINGS:
		if r.has_point(p):return false
	return true

static func street_contains(p: Vector3) -> bool:
	return walkable(Vector2(p.x,p.z))

static func map_position(p: Vector3) -> Vector2:
	return Vector2(p.x,p.z)
