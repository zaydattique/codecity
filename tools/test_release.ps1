param([Parameter(Mandatory=$true)][string]$Revision)
$ErrorActionPreference = "Stop"
$root=(Get-Location).Path
$evidence=Join-Path $root "build\release-evidence"
$zip=Join-Path $root "build\BloomLogic-Windows.zip"
$extract=Join-Path $root "build\clean extraction"
$cwd=Join-Path $root "build\empty working directory"
$profile=Join-Path $evidence "profile"
New-Item -ItemType Directory -Force $evidence,$extract,$cwd,$profile | Out-Null
python -m tools.release_manifest prepare dist/BloomLogic --revision $Revision
if ($LASTEXITCODE -ne 0) { throw "Manifest generation failed" }
Compress-Archive -Path dist/BloomLogic -DestinationPath $zip -CompressionLevel Optimal -Force
Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
$package=Join-Path $extract "BloomLogic"
python -m tools.release_manifest verify "$package"
if ($LASTEXITCODE -ne 0) { throw "Clean extraction integrity failed" }
$exe=Join-Path $package "BloomLogic.exe"
$hash=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
$hardware=[ordered]@{
  cpu=@(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
  ram_bytes=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
  os=Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture
  adapters=@(Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM,CurrentHorizontalResolution,CurrentVerticalResolution)
}
$hardware | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $evidence "hardware.json")
$env:BLOOMLOGIC_PROFILE_DIR=$profile
$env:BLOOMLOGIC_CAPTURE_DIR=$evidence
$env:PATH="$env:SystemRoot\System32;$env:SystemRoot"
Remove-Item Env:PYTHONPATH,Env:PYTHONHOME,Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
$metrics=@()
function Run-Check([string]$name,[string[]]$arguments,[int]$seconds) {
  $watch=[Diagnostics.Stopwatch]::StartNew()
  $p=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $cwd -PassThru
  $peak=0L
  while (-not $p.WaitForExit(250)) {
    $p.Refresh()
    try { $peak=[Math]::Max($peak,$p.PeakWorkingSet64) } catch {}
    if ($watch.Elapsed.TotalSeconds -gt $seconds) { $p.Kill(); throw "$name timed out" }
  }
  $watch.Stop()
  if ($p.ExitCode -ne 0) { Get-Content (Join-Path $profile "*.log") -ErrorAction SilentlyContinue; throw "$name failed: $($p.ExitCode)" }
  $script:metrics+= [pscustomobject]@{name=$name;seconds=[Math]::Round($watch.Elapsed.TotalSeconds,3);sampled_peak_working_set_bytes=$peak;exit_code=$p.ExitCode}
  Write-Host "PASS $name"
}
$rule="BloomLogic isolated release audit $PID"
try {
  $enabled=@(Get-NetFirewallProfile | Where-Object Enabled -eq True)
  if ($enabled.Count -ne 3) { throw "Firewall not enabled on every profile; cannot verify network block" }
  New-NetFirewallRule -DisplayName $rule -Direction Outbound -Program $exe -Action Block -Profile Any -Enabled True | Out-Null
  $active=Get-NetFirewallRule -DisplayName $rule -PolicyStore ActiveStore
  if ($active.Action -ne "Block" -or $active.Enabled -ne "True") { throw "Network block not active" }
  $active | Select-Object DisplayName,Enabled,Direction,Action,Profile | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $evidence "network-policy.json")
  Run-Check "clean-offline-self-test" @("--self-test") 120
  Run-Check "clean-offline-walkthrough" @("--gui-test") 300
  Run-Check "fresh-process-resume" @("--resume-check") 120
  # Reproduce the reported decoder error with both optional normal maps invalid.
  $runtime=Join-Path $package "_internal\runtime"
  $optional=@("soil-normal.png","soil-nor_gl.jpg","soil-gloss.png")
  $env:BLOOMLOGIC_PROFILE_DIR=Join-Path $evidence "texture-fallback-profile"
  $env:BLOOMLOGIC_CAPTURE_DIR=Join-Path $evidence "texture-fallback-review"
  try {
    foreach ($name in $optional) { $p=Join-Path $runtime $name; Move-Item -LiteralPath $p -Destination "$p.backup"; [IO.File]::WriteAllText($p,"invalid texture for regression test") }
    Run-Check "optional-texture-decoder-failure-walkthrough" @("--gui-test","--texture-fallback-test") 300
    $log=Get-Content (Join-Path $env:BLOOMLOGIC_PROFILE_DIR "application.log") -Raw
    if ($log -notmatch "Real optional texture decoder failure handled") { throw "Expected real decoder regression did not run" }
  } finally {
    foreach ($name in $optional) { $p=Join-Path $runtime $name; if (Test-Path "$p.backup") { Remove-Item -LiteralPath $p -Force; Move-Item -LiteralPath "$p.backup" -Destination $p } }
  }
  $env:BLOOMLOGIC_CAPTURE_DIR=$evidence
  # Independent benchmark profile avoids overwriting the saved walkthrough.
  $env:BLOOMLOGIC_PROFILE_DIR=Join-Path $evidence "benchmark-profile"
  Run-Check "benchmark-720p" @("--benchmark") 180
  Run-Check "benchmark-1080p" @("--benchmark","--1080p") 240
  [ordered]@{revision=$Revision;archive_sha256=$hash;archive_bytes=(Get-Item $zip).Length;network="outbound firewall block for extracted executable";external_python_on_path=$false;working_directory="empty separate folder";tests=$metrics} | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 (Join-Path $evidence "release-checks.json")
} finally {
  Remove-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue
}
