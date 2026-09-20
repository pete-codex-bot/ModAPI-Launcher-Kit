$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $repositoryRoot "artifacts/standard-user"

foreach ($tool in @("nuget", "msbuild", "python")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Required build tool was not found: $tool"
    }
}

Push-Location $repositoryRoot
try {
    python scripts/verify-standard-user.py --source-only
    if ($LASTEXITCODE -ne 0) { throw "Source verification failed." }

    nuget restore "Spore ModAPI Launcher.sln" -NonInteractive
    if ($LASTEXITCODE -ne 0) { throw "NuGet restore failed." }

    msbuild "Spore ModAPI Easy Installer\Spore ModAPI Easy Installer.csproj" /m /p:Configuration=Release /p:Platform=AnyCPU
    if ($LASTEXITCODE -ne 0) { throw "Easy Installer build failed." }

    msbuild "Spore ModAPI Easy Uninstaller\Spore ModAPI Easy Uninstaller.csproj" /m /p:Configuration=Release /p:Platform=AnyCPU
    if ($LASTEXITCODE -ne 0) { throw "Easy Uninstaller build failed." }

    New-Item -ItemType Directory -Force $artifactDir | Out-Null
    Get-ChildItem $artifactDir -File | Where-Object Extension -in ".exe", ".dll" | Remove-Item -Force
    Remove-Item (Join-Path $artifactDir "SHA256SUMS.txt") -Force -ErrorAction SilentlyContinue

    foreach ($name in @(
        "Spore ModAPI Easy Installer.exe",
        "Spore ModAPI Easy Uninstaller.exe",
        "ModAPI.Common.dll",
        "Newtonsoft.Json.dll"
    )) {
        $source = Join-Path $repositoryRoot "Output/$name"
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
            throw "Expected build output was not generated: $source"
        }
        Copy-Item -LiteralPath $source -Destination $artifactDir -Force
    }

    Get-ChildItem $artifactDir -File | Where-Object Extension -in ".exe", ".dll" |
        Sort-Object Name | ForEach-Object {
            $hash = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLowerInvariant()
            "$hash  $($_.Name)"
        } | Set-Content (Join-Path $artifactDir "SHA256SUMS.txt")

    python scripts/verify-standard-user.py $artifactDir
    if ($LASTEXITCODE -ne 0) { throw "Built artifact verification failed." }

    Write-Host "Standard-user binaries are ready in: $artifactDir"
}
finally {
    Pop-Location
}
