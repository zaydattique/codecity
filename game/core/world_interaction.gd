extends RefCounted
## Shared world interaction precondition, before the authoritative system commits a fact.
## Domain handlers must additionally check reservations, visibility, state and permissions.

static func within_range(actor: Node3D, target: Node3D, max_metres: float) -> bool:
	if not is_instance_valid(actor) or not is_instance_valid(target) or actor == target:
		return false
	if not actor.is_inside_tree() or not target.is_inside_tree() or actor.get_tree() != target.get_tree():
		return false
	if not is_finite(max_metres) or max_metres <= 0.0 or max_metres > 20.0:
		return false
	var distance_sq := actor.global_position.distance_squared_to(target.global_position)
	return is_finite(distance_sq) and distance_sq <= max_metres * max_metres
