<#
.SYNOPSIS
    Run the whole workshop pipeline on Windows.

.DESCRIPTION
    Same steps, same order as tools/build.sh:
      assets -> asset budget check -> notebooks -> notebook execution -> site

.EXAMPLE
    .\tools\build.ps1
    .\tools\build.ps1 -Serve
    .\tools\build.ps1 -SkipAssets -Serve
    .\tools\build.ps1 -Force
    .\tools\build.ps1 -Quick

.NOTES
    If PowerShell refuses to run this, the execution policy is blocking it.
    Either run it once as:
        powershell -ExecutionPolicy Bypass -File .\tools\build.ps1
    or allow local scripts for your user:
        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#>
[CmdletBinding()]
param(
    [switch]$Serve,
    [switch]$SkipAssets,
    [switch]$Force,
    [switch]$Quick,
    [int]$Port = 8777,
    [string]$EnvName = 'mlws2h'
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

function Step($m) { Write-Host "`n==> $m" -ForegroundColor White -BackgroundColor DarkBlue }
function Ok($m)   { Write-Host "    $m" -ForegroundColor Green }
function Die($m)  { Write-Host "`nFAILED: $m" -ForegroundColor Red; exit 1 }

# Run a command and stop the pipeline if it returns non-zero. PowerShell does
# NOT do this for native executables, which is the classic way a build script
# "succeeds" while every step inside it failed.
# NB: the parameter is NOT called $Args. $Args is a PowerShell automatic
# variable, so a parameter of that name never binds — `& $Exe @Args` then
# splats an empty list and silently runs the executable with no arguments
# at all. That failure is near-invisible: python with no args just opens a
# REPL, reads EOF, and exits 0, so the build "passes" having done nothing.
function Invoke-Checked {
    param([string]$Exe, [string[]]$ArgList, [string]$What)
    & $Exe @ArgList
    if ($LASTEXITCODE -ne 0) { Die $What }
}

# ------------------------------------------------------------------ env --
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Die "conda not found on PATH. Install Miniforge — see docs/INSTALL.md"
}

# `conda activate` needs the shell hook; it is not available in a bare
# PowerShell session unless `conda init powershell` has been run.
if ($env:CONDA_DEFAULT_ENV -ne $EnvName) {
    $hook = & conda 'shell.powershell' 'hook' 2>$null
    if ($hook) { $hook | Out-String | Invoke-Expression }
    try { conda activate $EnvName }
    catch { Die "conda env '$EnvName' not found. Run: .\tools\setup.ps1" }
}
if ($env:CONDA_DEFAULT_ENV -ne $EnvName) {
    Die "could not activate '$EnvName'. Try `conda init powershell`, reopen PowerShell, then re-run."
}
Ok "environment: $EnvName ($(python --version))"

if (-not (Get-Command quarto -ErrorAction SilentlyContinue)) {
    Die "quarto not on PATH. Run: .\tools\setup.ps1"
}

# --------------------------------------------------------------- assets --
if (-not $SkipAssets) {
    Step 'Building visual assets'
    $forceArg = if ($Force) { @('--force') } else { @() }
    if ($Quick) {
        Invoke-Checked python (@('tools/build_assets.py', '--tikz') + $forceArg) 'diagram build'
        Ok 'diagrams built'
    } else {
        Invoke-Checked python (@('tools/build_assets.py') + $forceArg) 'asset build'
        Step 'Checking asset sizes and durations'
        Invoke-Checked python @('tools/check_assets.py') 'an asset is outside the spec'
    }
} else {
    Ok 'skipping assets'
}

# ------------------------------------------------------------ notebooks --
Step 'Generating notebooks'
Invoke-Checked python @('tools/build_notebooks.py') 'notebook generation'

if (-not $Quick) {
    Step 'Executing notebooks (catches a dead dataset URL)'
    Invoke-Checked python @('tools/check_notebooks.py') 'a notebook cell raised'
}

# ----------------------------------------------------------------- site --
Step 'Rendering the site'
Invoke-Checked quarto @('render') 'quarto render'
Ok 'site written to _site/'

# ---------------------------------------------------------------- serve --
if ($Serve) {
    Step "Serving on http://127.0.0.1:$Port"
    Write-Host "    slides:  http://127.0.0.1:$Port/slides/index.html"
    Write-Host '    Ctrl-C to stop'
    python -m http.server $Port --bind 127.0.0.1 -d _site
    exit 0
}

Write-Host "`nDone." -ForegroundColor Green
Write-Host '    .\tools\build.ps1 -SkipAssets -Serve'
Write-Host '    quarto preview slides/index.qmd     # hot reload while editing'
