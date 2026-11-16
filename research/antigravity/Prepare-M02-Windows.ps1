<#
.SYNOPSIS
Prepare a PRIVATE Antigravity M02 evidence directory (no tool calls or settings changes).
.EXAMPLE
powershell -File .\research\antigravity\Prepare-M02-Windows.ps1 -PrivateDir 'C:\REA-M02-PRIVATE\session-001'
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$PrivateDir,
  [switch]$InspectRea
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$FullPrivate = [IO.Path]::GetFullPath($PrivateDir)
$Python = Get-Command python -ErrorAction Stop
Push-Location $RepoRoot
try {
    & $Python.Source -m research.antigravity.session init --private-dir $FullPrivate
    if ($LASTEXITCODE -ne 0) { throw 'M02_PRIVATE_INITIALIZATION_FAILED' }

    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    $npmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $npmCmd) { $npmCmd = Get-Command npm -ErrorAction SilentlyContinue }
    $nodeVersion = 'NOT_INSTALLED'
    $npmVersion = 'NOT_INSTALLED'
    if ($nodeCmd) { $nodeVersion = (& $nodeCmd.Source --version | Select-Object -First 1) }
    if ($npmCmd) { $npmVersion = (& $npmCmd.Source --version | Select-Object -First 1) }
    $runtime = [ordered]@{
      record_type = 'WINDOWS_OPERATOR_ENVIRONMENT_DIAGNOSTIC_ONLY'
      node_version = $nodeVersion
      npm_version = $npmVersion
      expected_rea_release = '6.9.0'
      antigravity_client_was_invoked = $false
      mcp_tools_calls_performed = $false
      scientific_P2 = 'HOLD'
      pilot_authorized = $false
    }
    $runtime | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $FullPrivate 'runtime-versions-private.json') -Encoding UTF8

    if ($InspectRea) {
        # Explicit user opt-in. npx may fetch/cache the package; dry-run
        # previews client settings and does NOT connect a real Antigravity agent.
        $Npx = Get-Command npx.cmd -ErrorAction Stop
        & $Npx.Source -y 'rea-agents@6.9.0' --version |
          Out-File -LiteralPath (Join-Path $FullPrivate 'rea-version-private.txt') -Encoding utf8
        if ($LASTEXITCODE -ne 0) { throw 'PINNED_REA_VERSION_CHECK_FAILED' }
        & $Npx.Source -y 'rea-agents@6.9.0' setup --client antigravity --dry-run |
          Out-File -LiteralPath (Join-Path $FullPrivate 'rea-setup-dry-run-private.txt') -Encoding utf8
        if ($LASTEXITCODE -ne 0) { throw 'ANTIGRAVITY_DRY_RUN_FAILED_DO_NOT_APPLY' }
    }
    Write-Output 'M02_PRIVATE_OPERATOR_KIT_CREATED=true'
    Write-Output 'M02_REAL_ANTIGRAVITY_CLIENT_EXECUTED=false'
    Write-Output 'M02_REA_SETUP_APPLIED=false'
    Write-Output 'M02_P2=HOLD'
    Write-Output 'M02_NEXT=Follow private README; capture actual client-native calls and audit them.'
} finally {
    Pop-Location
}
