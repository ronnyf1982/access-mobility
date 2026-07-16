# Start-AccessMobility-Dev.ps1
# Startet die vollstaendige lokale Entwicklungsumgebung fuer access-mobility.
# Reihenfolge: Docker-DB -> Migrationen -> Seed -> Backend (neues Fenster) -> Frontend-Hinweis

param(
    [switch]$SkipSeed,
    [switch]$SkipFrontendHint
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot ".." "..")
$Backend = Join-Path $Root "backend"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"

function Write-Step { param($n, $msg) Write-Host "`n[$n/5] $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host " FAIL $msg" -ForegroundColor Red; exit 1 }

# ── 1. Docker / PostgreSQL ───────────────────────────────────────────────────
Write-Step 1 "Docker-Datenbank starten (Port 5440)"
Push-Location $Root
docker compose -f docker-compose.dev.yml up -d
if ($LASTEXITCODE -ne 0) { Write-Fail "docker compose fehlgeschlagen" }
Write-OK "PostgreSQL laeuft"

# Kurz warten bis DB bereit ist
$retries = 0
do {
    Start-Sleep -Seconds 2
    $pg = & docker compose -f docker-compose.dev.yml ps --format json 2>$null | ConvertFrom-Json | Where-Object { $_.State -eq "running" }
    $retries++
} while (-not $pg -and $retries -lt 10)
if (-not $pg) { Write-Fail "PostgreSQL ist nach 20 Sekunden noch nicht erreichbar" }

# ── 2. Alembic Migrationen ───────────────────────────────────────────────────
Write-Step 2 "Alembic-Migrationen auf aktuellem Stand bringen"
Push-Location $Backend
& $Python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { Write-Fail "alembic upgrade head fehlgeschlagen" }
$current = & $Python -m alembic current 2>&1
Write-OK "Alembic-Stand: $current"

# ── 3. Seed-Daten ────────────────────────────────────────────────────────────
if (-not $SkipSeed) {
    Write-Step 3 "Demo-Daten einlesen (idempotent)"
    & $Python -m app.scripts.seed_demo_data
    if ($LASTEXITCODE -ne 0) { Write-Fail "seed_demo_data fehlgeschlagen" }
    Write-OK "Seed-Daten vorhanden"
} else {
    Write-Host "`n[3/5] Seed uebersprungen (-SkipSeed)" -ForegroundColor Yellow
}

# ── 4. Backend (uvicorn) in neuem Fenster ───────────────────────────────────
Write-Step 4 "Backend starten (Port 8010) — neues Fenster"
$uvicornCmd = "cd `"$Backend`"; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8010"
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $uvicornCmd

# Warten bis Backend antwortet
Write-Host "  Warte auf http://localhost:8010/api/v1/health ..." -ForegroundColor DarkCyan
$retries = 0
$ready = $false
do {
    Start-Sleep -Seconds 2
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8010/api/v1/health" -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) { $ready = $true }
    } catch {}
    $retries++
} while (-not $ready -and $retries -lt 15)

if ($ready) { Write-OK "Backend antwortet auf Port 8010" }
else { Write-Host "  WARNUNG: Backend nach 30 Sekunden noch nicht erreichbar — pruefe das neue Fenster" -ForegroundColor Yellow }

Pop-Location

# ── 5. Frontend-Hinweis ──────────────────────────────────────────────────────
Write-Step 5 "Frontend (Port 5180)"
if (-not $SkipFrontendHint) {
    Write-Host ""
    Write-Host "  Starte das Frontend manuell in einem eigenen Terminal:" -ForegroundColor Yellow
    Write-Host "    cd `"$(Join-Path $Root 'frontend')`"" -ForegroundColor White
    Write-Host "    npm run dev" -ForegroundColor White
    Write-Host ""
    Write-Host "  Oder druecke [F] um das Frontend hier im Hintergrund zu starten." -ForegroundColor DarkYellow
    $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    if ($key.Character -eq 'f' -or $key.Character -eq 'F') {
        $frontendCmd = "cd `"$(Join-Path $Root 'frontend')`"; npm run dev"
        Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCmd
        Write-OK "Frontend-Fenster geoeffnet"
    }
}

# ── Zusammenfassung ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  access-mobility Entwicklungsumgebung" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL  : localhost:5440" -ForegroundColor White
Write-Host "  Backend     : http://localhost:8010" -ForegroundColor White
Write-Host "  Swagger UI  : http://localhost:8010/docs" -ForegroundColor White
Write-Host "  Frontend    : http://localhost:5180" -ForegroundColor White
Write-Host ""
Write-Host "  Demo-Login  : driver@access.test / Access123!" -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor Cyan
