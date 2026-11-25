extends Node
## Trusted bounded Python interpreter, one process at a time. No shell.
signal finished(result: Dictionary)
var _pid := -1
var _deadline := 0
var _id := ""
var _request := ""
var _reply := ""

static func paths() -> PackedStringArray:
	if OS.has_feature("editor"):
		var script := ProjectSettings.globalize_path("res://../ai/academy.py")
		var override := OS.get_environment("CODECITY_ACADEMY_SCRIPT")
		if not override.is_empty():
			script=override
		var python := OS.get_environment("CODECITY_PYTHON")
		if python.is_empty():
			python="python" if OS.get_name()=="Windows" else "python3"
		return PackedStringArray([python,script]) if FileAccess.file_exists(script) else PackedStringArray()
	var folder := OS.get_executable_path().get_base_dir()
	var python := folder.path_join("python/python.exe")
	var script := folder.path_join("academy.py")
	return PackedStringArray([python,script]) if FileAccess.file_exists(python) and FileAccess.file_exists(script) else PackedStringArray()

func submit(source: String) -> bool:
	var command := paths()
	if _pid!=-1 or command.size()!=2 or source.is_empty() or source.to_utf8_buffer().size()>4096:
		return false
	_id=Crypto.new().generate_random_bytes(16).hex_encode()
	_request=ProjectSettings.globalize_path("user://academy_"+_id+".json")
	_reply=ProjectSettings.globalize_path("user://academy_"+_id+".result")
	var file := FileAccess.open(_request,FileAccess.WRITE)
	if file==null:
		return false
	file.store_string(JSON.stringify({"id":_id,"version":1,"source":source}))
	file.close()
	_pid=OS.create_process(command[0],PackedStringArray([command[1],_request,_reply]),false)
	if _pid<=0:
		_cleanup()
		return false
	_deadline=Time.get_ticks_msec()+5000
	return true

func _process(_delta: float) -> void:
	if _pid<=0:return
	if Time.get_ticks_msec()>_deadline:
		OS.kill(_pid)
		_finish({"ok":false,"output":"Python lesson timed out."})
		return
	if OS.is_process_running(_pid):return
	var result: Dictionary={"ok":false,"output":"Python runner returned no valid result."}
	if FileAccess.file_exists(_reply):
		var f := FileAccess.open(_reply,FileAccess.READ)
		if f!=null and f.get_length()<=4096:
			var parsed: Variant=JSON.parse_string(f.get_as_text())
			if parsed is Dictionary and parsed.get("id")==_id and parsed.get("version")==1:
				result=parsed
	_finish(result)

func _finish(result: Dictionary) -> void:
	_cleanup()
	finished.emit(result)

func _cleanup() -> void:
	for path: String in [_request,_reply,_reply.get_basename()+".tmp"]:
		if not path.is_empty() and FileAccess.file_exists(path):
			DirAccess.remove_absolute(path)
	_pid=-1
	_id=""
	_request=""
	_reply=""

func _exit_tree() -> void:
	if _pid>0:
		if OS.is_process_running(_pid):OS.kill(_pid)
		_cleanup()
