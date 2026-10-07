$ErrorActionPreference='Stop'
$taskDir=Split-Path -Parent $MyInvocation.MyCommand.Path
$remoteDir='/home/e20241515/vblhwl_3d_dram/codex_validation/fin3_factorial_20261007'
$destination='C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\results_vbl_hwl_1t1c_3ddram\Codex_독립검증_2026-10-07\fin3_720_개선실험\raw'
$archiveDir=Join-Path $taskDir 'mirror_local'
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
while ($true) {
 try {
  $reply=(& ssh sogangic1 "source ~/.bash_profile; python3 $remoteDir/mirror_remote.py export") -join "`n"
  if ($LASTEXITCODE -ne 0) { throw 'SSH export failed' }
  $inventory=$reply | ConvertFrom-Json
  if ($inventory.empty) {
   if ($inventory.queue_complete) { break }
   Start-Sleep -Seconds 30
   continue
  }
  $meta=Join-Path $archiveDir ($inventory.batch+'.json')
  scp "sogangic1:$remoteDir/mirror/$($inventory.batch).json" $meta
  if ($LASTEXITCODE -ne 0) { throw 'SCP inventory failed' }
  scp "sogangic1:$remoteDir/mirror/$($inventory.batch).tar" (Join-Path $archiveDir ($inventory.batch+'.tar'))
  if ($LASTEXITCODE -ne 0) { throw 'SCP raw data failed' }
  python (Join-Path $taskDir 'mirror_local.py') $meta $destination
  if ($LASTEXITCODE -ne 0) { throw 'Local verification failed' }
  scp (Join-Path $archiveDir ($inventory.batch+'.receipt.json')) "sogangic1:$remoteDir/mirror/receipt.json"
  if ($LASTEXITCODE -ne 0) { throw 'SCP receipt failed' }
  ssh sogangic1 "source ~/.bash_profile; python3 $remoteDir/mirror_remote.py retire"
  if ($LASTEXITCODE -ne 0) { throw 'Remote retirement failed' }
  [DateTime]::Now.ToString('o') | Set-Content -LiteralPath (Join-Path $taskDir 'collector_heartbeat.txt')
 } catch {
  Write-Output $_
  Start-Sleep -Seconds 30
 }
}
Write-Output 'COLLECTOR COMPLETE'
