<#
.SYNOPSIS
    One-time setup for building the workshop on Windows.

.DESCRIPTION
    Installs, if missing: Quarto, the 'mlws2h' conda environment, the Inter
    typeface, and the Quarto countdown extension. Everything lands under your user
    profile — no admin rights needed, nothing installed machine-wide.

    Students need NONE of this. This is only for building the material.

    NOT installed by this script (see docs/INSTALL.md):
      * Miniforge  — install it first; this script needs conda
      * MiKTeX     — needed only to rebuild the 11 TikZ diagrams. The
                     rendered SVG/PNG are committed, so the slides build
                     without any LaTeX at all.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\setup.ps1
#>
[CmdletBinding()]
param(
    [string]$QuartoVersion = '1.10.18',
    [string]$EnvName = 'mlws2h'
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

function Step($m) { Write-Host "`n==> $m" -ForegroundColor White -BackgroundColor DarkBlue }
function Ok($m)   { Write-Host "    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "    $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "`nFAILED: $m" -ForegroundColor Red; exit 1 }

# ------------------------------------------------------------- Quarto ----
if (Get-Command quarto -ErrorAction SilentlyContinue) {
    Ok "Quarto already installed: $(quarto --version)"
} else {
    Step "Installing Quarto $QuartoVersion"
    $dest = Join-Path $env:LOCALAPPDATA "Programs\Quarto"
    $zip  = Join-Path $env:TEMP "quarto-$QuartoVersion-win.zip"
    $url  = "https://github.com/quarto-dev/quarto-cli/releases/download/v$QuartoVersion/quarto-$QuartoVersion-win.zip"

    # The .zip, not the .msi: no installer, no admin rights, and it can live
    # entirely under the user profile.
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $dest -Force
    Remove-Item $zip -Force

    $bin = (Get-ChildItem $dest -Recurse -Filter 'quarto.exe' | Select-Object -First 1).Directory.FullName
    if (-not $bin) { Die "quarto.exe not found under $dest" }

    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$bin*") {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$bin", 'User')
        Ok "added to your user PATH: $bin"
    }
    $env:Path = "$env:Path;$bin"
    Ok "Quarto $(quarto --version)"
    Warn 'Open a NEW terminal for the PATH change to apply everywhere.'
}

# -------------------------------------------------------------- conda ----
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Die @"
conda not found. Install Miniforge first, then re-run this script:
    https://github.com/conda-forge/miniforge#miniforge3
Then, once, so PowerShell can activate environments:
    conda init powershell
and reopen PowerShell.
"@
}

$hook = & conda 'shell.powershell' 'hook' 2>$null
if ($hook) { $hook | Out-String | Invoke-Expression }

$existing = (conda env list) -match "^$EnvName\s"
if ($existing) {
    Step "Updating conda env '$EnvName'"
    conda env update -n $EnvName -f environment-windows.yml --prune
} else {
    Step "Creating conda env '$EnvName' (several minutes)"
    conda env create -f environment-windows.yml
}
if ($LASTEXITCODE -ne 0) { Die 'conda environment build' }
conda activate $EnvName
Ok "environment ready: $(python --version)"

# --------------------------------------------------------------- Inter ----
# The slides and the TikZ diagrams both specify Inter. If it
# is missing everything still builds, but the three stop matching.
Step 'Checking the Inter typeface'
$fontDir = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
$haveInter = (Test-Path $fontDir) -and (Get-ChildItem $fontDir -Filter 'Inter-*.otf' -ErrorAction SilentlyContinue)
if ($haveInter) {
    Ok 'Inter already installed'
} else {
    $zip = Join-Path $env:TEMP 'inter.zip'
    $tmp = Join-Path $env:TEMP 'inter-extract'
    Invoke-WebRequest -Uri 'https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip' -OutFile $zip -UseBasicParsing
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    New-Item -ItemType Directory -Force -Path $fontDir | Out-Null

    # Static upright weights only: some renderers pick weights far
    # more reliably from static faces than from a variable font.
    $faces = Get-ChildItem (Join-Path $tmp 'extras\otf') -Filter 'Inter-*.otf' |
             Where-Object { $_.Name -notmatch 'Italic' }
    foreach ($f in $faces) {
        Copy-Item $f.FullName $fontDir -Force
        # A per-user font must be registered, or nothing will see it.
        New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts' `
            -Name "$($f.BaseName) (TrueType)" -PropertyType String `
            -Value (Join-Path $fontDir $f.Name) -Force | Out-Null
    }
    Remove-Item $zip, $tmp -Recurse -Force
    Ok "installed $($faces.Count) Inter faces"
    Warn 'Some apps only notice new fonts after a sign-out or reboot.'
}

# -------------------------------------------------- Quarto extensions ----
# Committed to git, so this only matters on a clone that dropped them.
Step 'Quarto extensions'
Push-Location slides
if (-not (Test-Path '_extensions\gadenbuie\countdown')) {
    # NB: the extension lives in the repo's quarto/ subdirectory, not its root
    quarto add gadenbuie/countdown/quarto --no-prompt
} else { Ok 'countdown present' }
Pop-Location

# --------------------------------------------------------------- LaTeX ----
if (-not (Get-Command lualatex -ErrorAction SilentlyContinue)) {
    Warn @"
lualatex not found — the 11 TikZ diagrams cannot be REBUILT.
The rendered SVG and PNG are committed, so the slides and notebooks still
build fine. Install MiKTeX only if you need to change a diagram:
    https://miktex.org/download
"@
}

Write-Host "`nDone." -ForegroundColor Green
Write-Host @'
Next:
    conda activate mlws2h
    .\tools\build.ps1              # full pipeline
    .\tools\build.ps1 -Serve       # ...and serve it on :8777
'@
