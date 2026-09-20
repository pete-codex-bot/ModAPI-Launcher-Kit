param(
    [string]$LauncherKitPath = "$env:ProgramData\Spore ModAPI Launcher Kit",
    [string]$HashFile = (Join-Path $PSScriptRoot "SHA256SUMS.txt")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $HashFile -PathType Leaf)) {
    throw "Reference hash file not found: $HashFile"
}

$failed = $false
Get-Content -LiteralPath $HashFile | ForEach-Object {
    if ($_ -match '^([0-9a-fA-F]{64})\s{2}(.+\.exe)$') {
        $expected = $Matches[1]
        $name = $Matches[2]
        $installed = Join-Path $LauncherKitPath $name
        if (-not (Test-Path -LiteralPath $installed -PathType Leaf)) {
            Write-Error "Missing installed binary: $installed"
            $failed = $true
        }
        elseif ((Get-FileHash -LiteralPath $installed -Algorithm SHA256).Hash -ne $expected) {
            Write-Error "Custom binary was changed or overwritten: $installed"
            $failed = $true
        }
        else {
            Write-Host "OK: $installed"
        }
    }
}

if ($failed) {
    exit 1
}

Write-Host "Both installed standard-user binaries match this artifact set."
