param(
    [string]$Godot = "godot",
    [string]$Python = "python",
    [string]$Blender = "blender",
    [switch]$AssetPilot,
    [ValidateSet("adrian","maya")][string]$Character,
    [string]$SystemPack = "art/raw/system-assets.zip"
)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
function Invoke-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Exe failed with exit $LASTEXITCODE" }
}
Invoke-Checked $Python @("--version")
Invoke-Checked $Python @("-m","pytest","-q")
Invoke-Checked $Python @("tools/check_foundation.py")
Invoke-Checked $Godot @("--version")
$qa = "build/local-verification"
if (Test-Path $qa) { throw "Use a fresh local verification directory; preserve previous evidence." }
New-Item -ItemType Directory $qa | Out-Null
Copy-Item game "$qa/game" -Recurse
New-Item -ItemType Directory "$qa/game/_qa" | Out-Null
Copy-Item verification/session_contract.gd "$qa/game/_qa/"
function Run-Engine([string]$Name,[string[]]$Arguments,[string]$Marker = "") {
    & $Godot @Arguments 2>&1 | Tee-Object "$qa/$Name.log"
    if ($LASTEXITCODE -ne 0) { throw "$Name failed" }
    if (Select-String -Path "$qa/$Name.log" -Pattern "SCRIPT ERROR:|ERROR:") { throw "$Name reported errors" }
    if ($Marker -and !(Select-String -Path "$qa/$Name.log" -SimpleMatch $Marker)) { throw "$Name marker missing" }
}
Run-Engine "import" @("--headless","--path","$qa/game","--editor","--import")
Run-Engine "smoke" @("--headless","--path","$qa/game","--quit-after","180","--","--smoke") "CODECITY_FOUNDATION_SMOKE_OK"
Run-Engine "session" @("--headless","--path","$qa/game","--script","res://_qa/session_contract.gd") "CODECITY_SESSION_CONTRACT_OK"
if ($AssetPilot) {
    Invoke-Checked $Python @("tools/fetch_pilot_asset.py")
    Invoke-Checked $Blender @("--background","--factory-startup","--disable-autoexec","--python-exit-code","1","--python","tools/render_pilot_asset.py")
}
if ($Character) {
    if (!(Test-Path $SystemPack)) { Invoke-Checked $Python @("tools/fetch_system_pack.py",$SystemPack) }
    Invoke-Checked $Blender @("--background","--disable-autoexec","--python-exit-code","1","--python","tools/build_character.py","--","--id",$Character,"--pack",$SystemPack)
}
Write-Output "Functional checks only; visual review, actual game export and hardware profiling remain separate."
