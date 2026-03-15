# ============================================================
#  Font Organizer — Windows installer (PowerShell)
# ============================================================
#  Usage (run as Administrator for full PATH + system install):
#    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#    .\install.ps1
#
#  What it does:
#    1. Verifies Python 3.10+
#    2. Verifies git
#    3. Clones (or updates) the repo to %USERPROFILE%\.font-organizer
#    4. Installs the package with pip (editable install)
#    5. Adds the pip Scripts dir to the system/user PATH
# ============================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$RepoUrl    = "https://github.com/ZingerEngineer/font_organizer.git"
$InstallDir = Join-Path $env:USERPROFILE ".font-organizer"

# ── colours ─────────────────────────────────────────────────
function Write-Info    { param($msg) Write-Host "  $([char]0x276F)  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "  $([char]0x2714)  $msg" -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host "  $([char]0x26A0)  $msg" -ForegroundColor Yellow }
function Write-Fail    { param($msg) Write-Host "  $([char]0x2717)  $msg" -ForegroundColor Red; exit 1 }

function Write-Banner {
  $c = [char]27 + "[36m"  # Cyan ANSI
  $r = [char]27 + "[0m"
  $lines = @(
    "  $c" + [char]9608 + [char]9608 + [char]9608 + [char]9608 + [char]9608 + [char]9608 + [char]9608 + [char]9617 + " $r"
    "  " + [char]0x2588
  )
  # Simpler approach — no ANSI block chars in PS host on older Windows
  Write-Host ""
  Write-Host "  ===========================================" -ForegroundColor Cyan
  Write-Host "    FONT ORGANIZER  —  Windows Installer" -ForegroundColor Cyan
  Write-Host "  ===========================================" -ForegroundColor Cyan
  Write-Host ""
}

# ── helpers ──────────────────────────────────────────────────
function Test-IsAdmin {
  $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
  $p  = New-Object System.Security.Principal.WindowsPrincipal($id)
  return $p.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Find-Python {
  $candidates = @("python", "python3", "py")
  foreach ($cmd in $candidates) {
    try {
      $ver = & $cmd -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}'); print(v >= (3,10))" 2>$null
      if ($ver -and $ver[-1] -eq "True") {
        return $cmd
      }
    } catch {}
  }
  return $null
}

# ── 1. Python version check ──────────────────────────────────
function Assert-Python {
  Write-Info "Checking Python..."
  $script:PY = Find-Python
  if (-not $script:PY) {
    Write-Fail "Python 3.10+ is required but was not found.`n  Download it from https://python.org"
  }
  $ver = & $script:PY -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}')"
  Write-Success "Python $ver found  ($script:PY)"
}

# ── 2. Git check ─────────────────────────────────────────────
function Assert-Git {
  Write-Info "Checking git..."
  try {
    $gitVer = & git --version 2>$null
    Write-Success "git found  ($gitVer)"
  } catch {
    Write-Fail "git is required but was not found.`n  Install it from https://git-scm.com"
  }
}

# ── 3. Clone or update repo ──────────────────────────────────
function Invoke-CloneOrUpdate {
  if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Info "Repository already exists — pulling latest changes..."
    & git -C $InstallDir pull --ff-only
    Write-Success "Repository updated  ($InstallDir)"
  } else {
    Write-Info "Cloning repository..."
    & git clone $RepoUrl $InstallDir
    Write-Success "Repository cloned  ($InstallDir)"
  }
}

# ── 4. Install package ───────────────────────────────────────
function Install-Package {
  Write-Info "Installing font-organizer (editable)..."
  & $script:PY -m pip install --quiet --editable $InstallDir
  Write-Success "Package installed"
}

# ── 5. Add pip Scripts dir to PATH ──────────────────────────
function Add-ToPath {
  # Find where pip put the script
  $scriptsDir = & $script:PY -c "import sysconfig; print(sysconfig.get_path('scripts'))"

  if (-not $scriptsDir -or -not (Test-Path $scriptsDir)) {
    Write-Warn "Could not determine pip scripts directory. Add it to PATH manually."
    return
  }

  # Check if already on PATH
  $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
  if ($currentPath -like "*$scriptsDir*") {
    Write-Success "Scripts directory already on PATH  ($scriptsDir)"
    return
  }

  # Prefer Machine scope when running as admin (available to all users + sudo-equiv)
  if (Test-IsAdmin) {
    $scope = "Machine"
    $machinePath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($machinePath -notlike "*$scriptsDir*") {
      [System.Environment]::SetEnvironmentVariable("PATH", "$machinePath;$scriptsDir", "Machine")
      Write-Success "Added to system PATH (Machine scope)  ($scriptsDir)"
    } else {
      Write-Success "Already on system PATH  ($scriptsDir)"
    }
  } else {
    [System.Environment]::SetEnvironmentVariable("PATH", "$currentPath;$scriptsDir", "User")
    Write-Success "Added to user PATH  ($scriptsDir)"
    Write-Warn "Restart your terminal for PATH changes to take effect."
  }

  # Also update current session PATH
  $env:PATH = "$env:PATH;$scriptsDir"
}

# ── 6. Verify binary is callable ────────────────────────────
function Test-BinaryCallable {
  try {
    $null = & font-organizer --help 2>&1
    Write-Success "font-organizer is callable from any directory"
  } catch {
    Write-Warn "font-organizer not yet on PATH in this session."
    Write-Warn "Restart your terminal, then run:  font-organizer --help"
  }
}

# ── main ─────────────────────────────────────────────────────
function Main {
  Write-Banner

  if (-not (Test-IsAdmin)) {
    Write-Warn "Running without Administrator privileges."
    Write-Warn "For system-wide installation (all users), re-run as Administrator."
    Write-Host ""
  }

  Assert-Python
  Assert-Git
  Invoke-CloneOrUpdate
  Install-Package
  Add-ToPath
  Test-BinaryCallable

  Write-Host ""
  Write-Host "  ===========================================" -ForegroundColor Green
  Write-Host "    Font Organizer installed successfully!" -ForegroundColor Green
  Write-Host "  ===========================================" -ForegroundColor Green
  Write-Host ""
  Write-Host "  Usage:" -ForegroundColor Cyan
  Write-Host "    font-organizer C:\path\to\fonts"
  Write-Host "    font-organizer C:\path\to\fonts --dry-run"
  Write-Host "    font-organizer C:\path\to\fonts --theme pick"
  Write-Host ""
  Write-Host "  For protected directories, run PowerShell as Administrator:"
  Write-Host "    font-organizer C:\Windows\Fonts"
  Write-Host ""
}

Main
