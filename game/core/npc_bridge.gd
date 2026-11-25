extends Node
## One trusted persistent Python process, one in-flight bounded batch.
signal received(result: Dictionary)
signal unavailable
const LIMIT := 65536
var pid := -1
var folder := ""
var pending := ""
var deadline := 0
var failed := false

static func paths() -> PackedStringArray:
	if OS.has_feature("editor"):
		var script := OS.get_environment("CODECITY_NPC_SCRIPT")
		if script.is_empty():script=ProjectSettings.globalize_path("res://../ai/worker.py")
		var python := OS.get_environment("CODECITY_PYTHON")
		if python.is_empty():python="python" if OS.get_name()=="Windows" else "python3"
		return PackedStringArray([python,script]) if FileAccess.file_exists(script) else PackedStringArray()
	var base := OS.get_executable_path().get_base_dir()
	var python := base.path_join("python/python.exe")
	var script := base.path_join("worker.py")
	return PackedStringArray([python,script]) if FileAccess.file_exists(python) and FileAccess.file_exists(script) and FileAccess.file_exists(base.path_join("npc_brain.py")) else PackedStringArray()

func start() -> bool:
	var command := paths()
	if command.size()!=2 or pid>0:return false
	folder=ProjectSettings.globalize_path("user://npc_"+Crypto.new().generate_random_bytes(16).hex_encode())
	if DirAccess.make_dir_recursive_absolute(folder)!=OK:return false
	pid=OS.create_process(command[0],PackedStringArray(["-I","-S",command[1],"--mailbox",folder]),false)
	if pid<=0:
		_stop()
		return false
	return true

func submit(observations: Array, tick: int) -> bool:
	if failed or pid<=0 or not pending.is_empty() or observations.size()!=6:return false
	var id := "npc."+str(tick)
	var data := JSON.stringify({"version":1,"id":id,"op":"npc_batch","observations":observations})
	if data.to_utf8_buffer().size()>LIMIT:return false
	var temp := folder.path_join("request.tmp")
	var f := FileAccess.open(temp,FileAccess.WRITE)
	if f==null:return false
	f.store_string(data)
	f.close()
	if DirAccess.rename_absolute(temp,folder.path_join("request.json"))!=OK:return false
	pending=id
	deadline=Time.get_ticks_msec()+2000
	return true

func _process(_delta: float) -> void:
	if pid<=0 or failed:return
	if not OS.is_process_running(pid):
		# Godot has already observed/reaped this child. Never query it twice.
		pid=-1
		_fail()
		return
	if pending.is_empty():return
	var path := folder.path_join("response.json")
	if FileAccess.file_exists(path):
		var file := FileAccess.open(path,FileAccess.READ)
		var result: Variant=null
		if file!=null and file.get_length()<=LIMIT:
			result=JSON.parse_string(file.get_as_text())
			file.close()
		DirAccess.remove_absolute(path)
		if not result is Dictionary or result.get("id")!=pending or result.get("version")!=1 or result.get("op")!="npc_intents":
			_fail()
			return
		pending=""
		received.emit(result)
	elif Time.get_ticks_msec()>deadline:
		_fail()

func _fail() -> void:
	failed=true
	_stop()
	unavailable.emit()

func _stop() -> void:
	var child := pid
	pid=-1
	if child>0 and OS.is_process_running(child):OS.kill(child)
	pending=""
	if not folder.is_empty():
		for name: String in ["request.json","request.tmp","response.json","response.tmp","stop"]:
			var path := folder.path_join(name)
			if FileAccess.file_exists(path):DirAccess.remove_absolute(path)
		DirAccess.remove_absolute(folder)
	folder=""

func _exit_tree() -> void:
	_stop()
