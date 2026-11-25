extends RefCounted
## Coordinates derived from the actual 32m optimized Harbor Boulevard art assembly.
## Godot +X east, -Z north. Closed exteriors are not enterable destinations.
const STREET := Rect2(-6.0, -16.0, 12.0, 32.0)
const ROAD := Rect2(-3.4, -16.0, 6.8, 32.0)
const SIDEWALKS: Array[Rect2] = [Rect2(-6,-16,2.6,32),Rect2(3.4,-16,2.6,32)]
const BUILDINGS: Array[Rect2] = [
	Rect2(6,0,9,15), Rect2(6,-15,9,15),
	Rect2(-15,-3,9,18), Rect2(-15,-15,9,12)
]
const HEIGHTS: Array[float] = [9.0,6.0,6.0,9.0]
const BENCH := Vector2(4.95,2.0)
const SPAWN := Vector3(-4.65,0.18,10.4)

static func street_contains(p: Vector3) -> bool:
	return STREET.has_point(Vector2(p.x,p.z))

static func map_position(p: Vector3) -> Vector2:
	return Vector2(p.x,p.z)
