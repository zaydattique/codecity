extends Node
## Notifications only. State mutations belong to authoritative systems.
signal interaction_completed(actor_id: StringName, target_id: StringName, action: StringName)
signal mission_state_changed(mission_id: StringName, state: StringName)
signal chunk_state_changed(chunk_id: StringName, loaded: bool)
