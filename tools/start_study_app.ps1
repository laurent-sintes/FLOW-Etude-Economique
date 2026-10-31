param([int]$Port=8766,[switch]$NoOpen,[switch]$Restart,[string]$Python)
$ErrorActionPreference='Stop'
$studyRoot=Split-Path $PSScriptRoot -Parent
$runtimePython=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if(-not $Python){
  $venvPython=Join-Path $studyRoot '.venv/Scripts/python.exe'
  if(Test-Path -LiteralPath $venvPython){$Python=$venvPython}
  elseif(Test-Path -LiteralPath $runtimePython){$Python=$runtimePython}
  else{$Python=(Get-Command python -ErrorAction Stop).Source}
}
$deps=Join-Path $studyRoot 'tmp/yaml-stacks/deps'
$modelDeps=Join-Path $studyRoot 'tmp/model-deps'
if(Test-Path -LiteralPath $modelDeps){$env:PYTHONPATH=$modelDeps}
elseif(Test-Path -LiteralPath $deps){$env:PYTHONPATH=$deps}
$stateFolder=Join-Path $studyRoot 'tmp/study-app'
New-Item -ItemType Directory -Path $stateFolder -Force | Out-Null
$statePath=Join-Path $stateFolder "server-$Port.json"
$legacyStatePath=Join-Path $stateFolder 'server.json'
$url="http://127.0.0.1:$Port"
# Generate the delivery only when source or output hashes changed.
& $Python -m tools.prepare_static_app
if($LASTEXITCODE){throw 'ERR_STATIC_BUILD_FAILED'}
function Read-Manifest {try {Invoke-RestMethod -Uri "$url/site-manifest.json" -TimeoutSec 2}catch{$null}}
function Read-LegacyHealth {try {Invoke-RestMethod -Uri "$url/api/health" -TimeoutSec 2}catch{$null}}
$manifest=Read-Manifest
$legacy=$null
if(-not $manifest){$legacy=Read-LegacyHealth}
if(($manifest -and $manifest.id -ne 'flow-study') -or ($legacy -and $legacy.id -ne 'flow-study')){throw 'ERR_PORT_IN_USE'}
if(-not (Test-Path -LiteralPath $statePath) -and $Port -eq 8766 -and (Test-Path -LiteralPath $legacyStatePath)){$statePath=$legacyStatePath}
$owned=$null
$process=$null
if(Test-Path -LiteralPath $statePath){
  $owned=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
  $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($owned.pid)"
}
if($manifest -or $legacy){
  $validOwner=$owned -and $owned.port -eq $Port -and $process -and ($process.CommandLine -match 'tools/serve_study_app.py' -or $process.CommandLine -match '-m http.server')
  if(-not $validOwner){throw 'ERR_SERVER_OWNER_UNKNOWN'}
  if($legacy -or $Restart -or $process.CommandLine -match 'tools/serve_study_app.py'){
    Stop-Process -Id $owned.pid
    $manifest=$null
  }
}
if(-not $manifest){
  $server=Start-Process -FilePath $Python -ArgumentList @('-m','http.server',"$Port",'--bind','127.0.0.1','--directory','app/dist') -WorkingDirectory $studyRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $stateFolder 'server.log') -RedirectStandardError (Join-Path $stateFolder 'server-error.log')
  $deadline=[DateTime]::UtcNow.AddSeconds(15)
  do {Start-Sleep -Milliseconds 200;$manifest=Read-Manifest;if($server.HasExited){throw 'ERR_SERVER_START_FAILED'}} until($manifest -or [DateTime]::UtcNow -gt $deadline)
  if(-not $manifest){throw 'ERR_SERVER_NOT_READY'}
  if($manifest.id -ne 'flow-study'){throw 'ERR_SERVER_IDENTITY_MISMATCH'}
  @{pid=$server.Id;port=$Port;root=$studyRoot;mode='static'} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
}
Write-Output $url
if(-not $NoOpen){Start-Process $url}
