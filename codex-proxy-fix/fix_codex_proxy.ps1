<#
  Feiniao + Codex proxy fix v1.0
  What it does:
    1. Backs up your current User-level proxy env vars (HTTP_PROXY / HTTPS_PROXY / ALL_PROXY / NO_PROXY).
    2. Reads the Windows system proxy that Feiniao sets (HKCU ProxyServer), tests it with curl.
       If it fails, tries the other local "core" ports that answered in diagnostics.
    3. Points the User env vars at the working port (http://127.0.0.1:PORT).
  Nothing else is touched (no registry writes, no firewall, no Machine-level vars).

  Run:      powershell -ExecutionPolicy Bypass -File .\fix_codex_proxy.ps1
  Preview:  powershell -ExecutionPolicy Bypass -File .\fix_codex_proxy.ps1 -DryRun
  Remove:   powershell -ExecutionPolicy Bypass -File .\fix_codex_proxy.ps1 -Clear
            (deletes the 4 User vars so Codex just follows the Windows system proxy)
  Undo:     powershell -ExecutionPolicy Bypass -File .\fix_codex_proxy.ps1 -Restore .\backups\proxy_env_backup_XXXX.txt

  Re-run it whenever Feiniao restarts and Codex stops connecting: Feiniao may pick a new port each launch.
#>
param(
    [switch]$DryRun,
    [switch]$Clear,
    [string]$Restore
)

$ErrorActionPreference = 'Stop'

# When launched by double-click (exe), keep the window open at the end.
$script:PauseAtEnd = -not $env:CODEX_FIX_NOPAUSE
function Exit-Fix([int]$code) {
    if ($script:PauseAtEnd) { Write-Host ""; Read-Host "Press Enter to close" | Out-Null }
    exit $code
}
$Names = 'HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY'
$NoProxyValue = 'localhost,127.0.0.1,::1'
$TestUrl = 'https://example.com/'
$FallbackPorts = @(15405, 15234)   # ports that returned HTTP 200 in diagnosis_20261124_104202

$here = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent ([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName) }
$backupDir = Join-Path $here 'backups'

function Set-UserVar($name, $value) {
    if ($DryRun) { Write-Host "  [DryRun] User $name = $value"; return }
    [Environment]::SetEnvironmentVariable($name, $value, 'User')   # $null deletes
    Set-Item -Path "Env:$name" -Value $value -ErrorAction SilentlyContinue
    if ($null -eq $value) { Remove-Item "Env:$name" -ErrorAction SilentlyContinue }
    Write-Host "  User $name = $(if ($null -eq $value) {'<removed>'} else {$value})"
}

function Test-Proxy($proxyUrl) {
    $out = & curl.exe -s -o NUL -I --max-time 8 -x $proxyUrl -w "%{http_code}" $TestUrl 2>$null
    return ($LASTEXITCODE -eq 0 -and $out -match '^[23]\d\d$')
}

# ---------- Restore ----------
if ($Restore) {
    if (-not (Test-Path $Restore)) { throw "Backup file not found: $Restore" }
    Write-Host "Restoring from $Restore"
    foreach ($line in Get-Content $Restore) {
        if ($line -match '^(HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|NO_PROXY)=(.*)$') {
            $v = $Matches[2]; if ($v -eq '<unset>') { $v = $null }
            Set-UserVar $Matches[1] $v
        }
    }
    Write-Host "Done. Fully quit Codex and reopen it."
    Exit-Fix 0
}

# ---------- Backup ----------
if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backupFile = Join-Path $backupDir "proxy_env_backup_$stamp.txt"
    $Names | ForEach-Object {
        $v = [Environment]::GetEnvironmentVariable($_, 'User'); if ($null -eq $v) { $v = '<unset>' }
        "$_=$v"
    } | Set-Content -Path $backupFile -Encoding UTF8
    Write-Host "Backup saved: $backupFile"
}

# ---------- Clear mode ----------
if ($Clear) {
    Write-Host "Removing User-level proxy vars (Codex will follow the Windows system proxy)..."
    foreach ($n in $Names) { Set-UserVar $n $null }
    Write-Host "Done. Fully quit Codex (tray icon too) and reopen it."
    Exit-Fix 0
}

# ---------- Find a working proxy ----------
Write-Host "Current User HTTPS_PROXY = $([Environment]::GetEnvironmentVariable('HTTPS_PROXY','User'))"

$candidates = New-Object System.Collections.Generic.List[string]
$is = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction SilentlyContinue
if ($is -and $is.ProxyEnable -eq 1 -and $is.ProxyServer) {
    $ps = [string]$is.ProxyServer
    # handles "127.0.0.1:15405" and "http=127.0.0.1:15405;https=..."
    if ($ps -match 'https=([^;]+)') { $hp = $Matches[1] }
    elseif ($ps -match 'http=([^;]+)') { $hp = $Matches[1] }
    else { $hp = ($ps -split ';')[0] }
    $hp = $hp -replace '^[a-z0-9]+://',''
    Write-Host "Windows system proxy (set by Feiniao): $hp"
    $candidates.Add("http://$hp")
} else {
    Write-Host "Windows system proxy is OFF. Is Feiniao connected?"
}
foreach ($p in $FallbackPorts) { $u = "http://127.0.0.1:$p"; if (-not $candidates.Contains($u)) { $candidates.Add($u) } }

$working = $null
foreach ($c in $candidates) {
    Write-Host -NoNewline "Testing $c ... "
    if (Test-Proxy $c) { Write-Host "OK"; $working = $c; break } else { Write-Host "fail" }
}

if (-not $working) {
    Write-Host ""
    Write-Host "No working local proxy found. Make sure Feiniao is connected (node selected), then run this again." -ForegroundColor Yellow
    Write-Host "Env vars were NOT changed."
    Exit-Fix 1
}

Write-Host ""
Write-Host "Setting User proxy vars to $working"
Set-UserVar 'HTTP_PROXY'  $working
Set-UserVar 'HTTPS_PROXY' $working
Set-UserVar 'ALL_PROXY'   $working
Set-UserVar 'NO_PROXY'    $NoProxyValue

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "Next: fully quit Codex (right-click tray icon -> Quit, or end it in Task Manager), close old terminals, then reopen Codex."
Write-Host "Already-open programs keep the old dead value until they are restarted."
Exit-Fix 0
