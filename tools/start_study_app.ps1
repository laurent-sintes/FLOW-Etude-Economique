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
function Read-Health {try {Invoke-RestMethod -Uri "$url/api/health" -TimeoutSec 2}catch{$null}}
$health=Read-Health
if($health -and $health.id -ne 'flow-study'){throw 'ERR_PORT_IN_USE'}
if($health){
  if($health.mode -ne 'current' -or -not $health.sources_current){$Restart=$true}
  $buildPath=Join-Path $studyRoot 'app/dist/index.html'
  if(Test-Path -LiteralPath $buildPath){
    $buildHash=(Get-FileHash -LiteralPath $buildPath -Algorithm SHA256).Hash.ToLower()
    if($health.client_build_sha256 -ne $buildHash){$Restart=$true}
  }
}
if($health -and $Restart){
  if(-not (Test-Path -LiteralPath $statePath) -and $Port -eq 8766 -and (Test-Path -LiteralPath $legacyStatePath)){$statePath=$legacyStatePath}
  if(-not (Test-Path -LiteralPath $statePath)){throw 'ERR_SERVER_OWNER_UNKNOWN'}
  $owned=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
  $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($owned.pid)"
  if(-not $process -or $process.CommandLine -notmatch 'tools/serve_study_app.py' -or $owned.port -ne $Port){throw 'ERR_SERVER_OWNER_UNKNOWN'}
  Stop-Process -Id $owned.pid
  $health=$null
}
if(-not $health){
  if(-not (Test-Path -LiteralPath (Join-Path $studyRoot 'app/dist/index.html'))){throw 'ERR_APP_BUILD_REQUIRED'}
  $server=Start-Process -FilePath $Python -ArgumentList @('tools/serve_study_app.py','--port',$Port) -WorkingDirectory $studyRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $stateFolder 'server.log') -RedirectStandardError (Join-Path $stateFolder 'server-error.log')
  $deadline=[DateTime]::UtcNow.AddSeconds(120)
  do {Start-Sleep -Milliseconds 300;$health=Read-Health;if($server.HasExited){throw 'ERR_SERVER_START_FAILED'}} until($health -or [DateTime]::UtcNow -gt $deadline)
  if(-not $health){throw 'ERR_SERVER_NOT_READY'}
  if($health.id -ne 'flow-study' -or $health.pid -ne $server.Id){throw 'ERR_SERVER_IDENTITY_MISMATCH'}
  @{pid=$server.Id;port=$Port;root=$studyRoot} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
}
Write-Output $url
if(-not $NoOpen){Start-Process $url}
