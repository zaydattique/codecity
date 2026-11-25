extends RefCounted
## Single in-flight, allowlisted threaded scene request.
## Progress is the engine-reported resource load, never a synthetic timer.
enum Status { IDLE, LOADING, READY, FAILED }
var status: Status = Status.IDLE
var progress: float = 0.0
var _path: String = ""
var _scene: PackedScene

func request(path: String, approved_paths: PackedStringArray) -> bool:
	if status == Status.LOADING or not approved_paths.has(path) or not path.begins_with("res://") or not ResourceLoader.exists(path, "PackedScene"):
		return false
	_scene = null
	progress = 0.0
	_path = path
	if ResourceLoader.load_threaded_request(_path, "PackedScene") != OK:
		status = Status.FAILED
		return false
	status = Status.LOADING
	return true

func poll() -> Status:
	if status != Status.LOADING:
		return status
	var measured: Array = []
	var current := ResourceLoader.load_threaded_get_status(_path, measured)
	if not measured.is_empty():
		progress = clampf(float(measured[0]), 0.0, 1.0)
	match current:
		ResourceLoader.THREAD_LOAD_LOADED:
			_scene = ResourceLoader.load_threaded_get(_path) as PackedScene
			status = Status.READY if _scene != null else Status.FAILED
			if status == Status.READY:
				progress = 1.0
		ResourceLoader.THREAD_LOAD_FAILED, ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
			status = Status.FAILED
	return status

func take_scene() -> PackedScene:
	if status != Status.READY:
		return null
	var result := _scene
	_scene = null
	_path = ""
	status = Status.IDLE
	progress = 0.0
	return result
