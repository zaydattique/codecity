extends RefCounted
## Spherical orbit adapted from OpenCity scripts/follow_camera.gd.
## Copyright (c) 2026 Charan Raj Kandula; MIT, see THIRD_PARTY_NOTICES.md.
## Decoupled from demo groups, globals and input; pure geometry for both modes.
## A future camera rig must handle world collisions, input and target validity.

static func offset(yaw: float, pitch: float, distance: float) -> Vector3:
	if not is_finite(yaw) or not is_finite(pitch) or not is_finite(distance) or distance < 0.0:
		return Vector3.ZERO
	var p := clampf(pitch, -1.1, 0.5)
	return Vector3(sin(yaw) * cos(p), -sin(p), cos(yaw) * cos(p)) * distance

static func follow_weight(speed: float, delta: float) -> float:
	if not is_finite(speed) or not is_finite(delta) or speed <= 0.0 or delta <= 0.0:
		return 0.0
	return 1.0 - exp(-speed * delta)
