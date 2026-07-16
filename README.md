# access-mobility

Barrierefreie Mobilitätsplattform — lokales MVP-Grundgerüst

## Ports

| Dienst              | Adresse                        |
|---------------------|-------------------------------|
| Frontend (Vue/Vite) | http://localhost:5180          |
| Backend (FastAPI)   | http://localhost:8010          |
| Swagger UI          | http://localhost:8010/docs     |
| PostgreSQL (Docker) | localhost:5440                 |

---

## Ersteinrichtung

### 1. Umgebungsdatei anlegen

```bash
cp .env.example backend/.env
```

Werte in `backend/.env` bei Bedarf anpassen.

### 2. Datenbank starten

```bash
docker compose -f docker-compose.dev.yml up -d
```

### 3. Backend starten

```bash
cd backend

# Virtuelle Umgebung erstellen (einmalig)
python -m venv .venv

# Aktivieren — Windows:
.venv\Scripts\activate
# Aktivieren — macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Alle Migrationen ausführen (Sprint 3: users/orgs + Sprint 4: mobility_profiles)
alembic upgrade head

uvicorn app.main:app --reload --port 8010
```

Backend läuft auf http://localhost:8010  
Swagger UI: http://localhost:8010/docs

### 4. Demo-Daten einmalig laden

```bash
cd backend
python -m app.scripts.seed_demo_data
```

### 5. Frontend starten (neues Terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend läuft auf http://localhost:5180

### Schnellstart (Windows — alle Dienste auf einmal)

```powershell
scripts\windows\Start-AccessMobility-Dev.ps1
```

Das Skript startet Docker-DB, führt Migrationen und Seed aus, startet das Backend
in einem neuen Fenster und gibt den Frontend-Startbefehl aus.

---

## Umgebungsprüfung vor Browser-Test (Pflicht)

Vor jedem Login-Test oder Browser-Test müssen alle Dienste laufen:

| # | Dienst | Port | Prüfung |
|---|--------|------|---------|
| 1 | PostgreSQL (Docker) | 5440 | `docker compose -f docker-compose.dev.yml ps` |
| 2 | Alembic-Migrationen | — | `cd backend && alembic current` → zeigt `(head)` |
| 3 | Seed-Daten | — | `cd backend && python -m app.scripts.seed_demo_data` |
| 4 | Backend (FastAPI) | 8010 | `curl http://localhost:8010/api/v1/health` → 200 OK |
| 5 | Frontend (Vue/Vite) | 5180 | http://localhost:5180 erreichbar |

**Alle 5 Punkte müssen ✅ sein.** uvicorn läuft nicht automatisch — es muss
nach jedem Systemneustart neu gestartet werden.

---

## Demo-Zugangsdaten (alle mit Passwort `Access123!`)

| E-Mail                    | Rolle                   |
|---------------------------|-------------------------|
| passenger@access.test     | Fahrgast                |
| relative@access.test      | Vertrauensperson        |
| orgadmin@access.test      | Organisations-Admin     |
| coordinator@access.test   | Koordinator:in          |
| provider@access.test      | Fahrdienst-Admin        |
| dispatcher@access.test    | Disponent:in            |
| driver@access.test        | Fahrer:in               |
| admin@access.test         | Plattform-Admin         |

---

## Entwicklung

### Neue Datenbank-Migration erstellen

```bash
cd backend
alembic revision --autogenerate -m "kurze-beschreibung"
alembic upgrade head
```

### Datenbank zurücksetzen

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
cd backend && alembic upgrade head && python -m app.scripts.seed_demo_data
```

### Docker-Datenbank stoppen

```bash
docker compose -f docker-compose.dev.yml down
```

---

## Projektstruktur

```
access-mobility/
├── backend/          FastAPI + SQLAlchemy + Alembic
├── frontend/         Vue 3 + TypeScript + Vite + PrimeVue
├── docs/             Projektdokumentation
├── docker-compose.dev.yml
├── .env.example
└── README.md
```

Siehe `docs/ROADMAP.md` für die Sprintplanung.
