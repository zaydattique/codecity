# Academy curriculum and execution gate

Primary curriculum: [master directive](MASTER_PRODUCTION_DIRECTIVE.md), section 03. Living World never requires programming. Shared city, separate mission progression; three assistance levels (Guided, Independent, Challenge). Every mission must be physically playable and observe validated results, not merely accept an answer.

| Mission | Python topic | Physical objective |
|---|---|---|
| 01 Control Room | print, comments, syntax | Send actual stdout to assigned electronic display |
| 02 Resource Manager | variables/types | Allocate warehouse stock/fuel/money |
| 03 Traffic Controller | comparisons/Boolean/conditions | Set safe signal timing |
| 04 Construction Automation | for/range | Repeat real equipment operations |
| 05 Water Management | while | Pump until tank condition met |
| 06 Warehouse Intelligence | lists/dicts/indexing | Assign packages and deliveries |
| 07 Power Grid | functions/returns | Restore building lights |
| 08 Smart Security | strings/validation/errors | Fictional access controller only |
| 09 Emergency Routing | graphs/BFS/A* | Compare actual emergency routes |
| 10 Transport Optimization | sorting/searching/data | Improve schedules |
| 11 Object-Oriented City | classes/objects/methods | Controlled simulated entities |
| 12 City Intelligence | decision-making/prediction | Optimize supported NPC behavior |
| Final City Systems Failure | combined | Restore multiple systems |

## Security boundary

No player code execution is enabled. Never call eval, exec, shell, or a native CPython subprocess as the security boundary. Evaluate offline WASM/WASI CPython in a reviewed sandbox runtime (e.g. Wasmtime); require no host preopened paths/network, fixed memory and output limits, instruction fuel/epoch interruption, hard wall-clock timeout, no child processes, cancellation and denial tests on Windows before enabling input. Python NPC worker stays separate, trusted and unchanged. No sandbox runtime selected or integrated yet. The broker must authenticate correlation and terminal ownership out of band; stdout alone proves nothing. World command validator and Godot state authority must reject replay, invalid target and stale session at commit. The trusted Python result contract now validates only successful, bounded stdout for mission 01 and produces one allowed display intent; not a terminal, sandbox, or completed mission. Godot physical display and mission completion remain blocked until an actual control room, terminal and isolated runner exist. Syntax errors/timeout must never update the world.

## University demo scope update
First accessible Academy mission: outdoor street lighting control, two actual fixtures, variables, for/range, if, print and set_lamp. This pilot uses a Python-written AST interpreter of a deliberately restricted subset, never eval/exec, no arbitrary bytecode, imports, files or network. Bounded source/nodes/steps/values/output and atomic commands; Godot validates batch and updates physical lights. Not the general WASM sandbox, not full Python compatibility, and not all thirteen missions. Native interpreter process is trusted implementation, not the security boundary for arbitrary code. Requires denial tests, actual engine integration and packaged runtime verification before release.
