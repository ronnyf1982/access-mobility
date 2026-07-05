# Projektstatus

## Aktueller Sprint: Sprint 1 — Grundgerüst ✅

**Abgeschlossen:** 2026-07-05

### Umgesetzt

- [x] Projektstruktur (`backend/`, `frontend/`, `docs/`)
- [x] `docker-compose.dev.yml` mit PostgreSQL auf Port 5440
- [x] `.env.example` und `.gitignore`
- [x] FastAPI-App mit Health-Endpoint `GET /api/v1/health`
- [x] CORS konfiguriert für `http://localhost:5180`
- [x] SQLAlchemy-Datenbankanbindung vorbereitet (`session.py`, `base.py`)
- [x] Alembic vorbereitet (`alembic.ini`, `env.py`, `script.py.mako`)
- [x] Vue 3 + TypeScript + Vite auf Port 5180
- [x] PrimeVue 4 mit Aura-Theme eingerichtet
- [x] Pinia Store (`useAppStore`)
- [x] Vue Router mit Home-Route
- [x] Axios-Client mit `VITE_API_BASE_URL`
- [x] `HomeView.vue` mit Health-Check-Button
- [x] `README.md` mit Startbefehlen

### Designentscheidungen (freigegeben)

- [x] Responsive Webplattform — keine native App (MVP-Scope)
- [x] Öffentlicher Bereich (Landingpage) + geschützter Portalbereich
- [x] Designrichtung: Schwarz/Anthrazit + Gelb als Akzentfarbe
- [x] Stil: modern, premium, barrieregerecht, klar, nicht überladen
- [x] Gelb für Buttons, aktive Navigation, Icons, Status, CTAs

### Noch nicht umgesetzt (bewusst)

- Authentifizierung / JWT
- Rollenmodell
- Benutzer-, Organisations-, Fahrzeug-, Fahrer-, Fahrtenmodule
- Serienfahrten
- Zahlungsintegration
- Krankenkassenabrechnung
- Externe APIs / Live-GPS
- Native Mobile App

## Nächster Sprint: Sprint 2 — Stammdaten
