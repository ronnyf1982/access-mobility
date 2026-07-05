# Roadmap — access-mobility MVP

## Sprint 1 — Grundgerüst ✅
Lauffähiges Fullstack-Grundgerüst: FastAPI + Vue 3 + PostgreSQL via Docker.
Health-Endpoint, Axios-Client, PrimeVue, Pinia, Vue Router.

## Sprint 2 — Stammdaten
Kernobjekte anlegen und verwalten.

- Backend: `Organization`, `Vehicle`, `Driver`, `Qualification`, `MobilityProfile` — SQLAlchemy-Modelle, Alembic-Migrationen, CRUD, REST-Endpoints
- Frontend: Pinia Stores, DataTable-Views, Formulare für Fahrer, Fahrzeuge, Organisationen
- Mobilitätsprofil: GET + PUT für eigenen Nutzer

## Sprint 3 — Fahrtenbuchung
Einzelne Fahrt buchen, disponieren, ausführen.

- Backend: `Ride`-Modell, Statusmaschine, Zuteilungs-Endpoint
- Frontend: Buchungs-Wizard (PrimeVue Stepper), Fahrtenliste, Fahrer-View mit Statuswechsel
- Koordinator-Flow: Fahrt für andere Person buchen

## Sprint 4 — Organisationsansicht & Admin
Org-Kontext vollständig, Admin-Dashboard.

- Fahrtenliste gefiltert nach Organisation
- Kostenstellen-Referenz an Fahrt
- Stornierung mit Bestätigungs-Dialog
- Admin-Dashboard mit Statistik-Karten
- Benutzer-Rollenverwaltung

## Sprint 5 — Serienfahrten & Stabilisierung
Wiederkehrende Fahrten, Fehlerbehandlung, erste Tests.

- Backend: `RecurringRide` + RRULE-Auflösung (`python-dateutil`)
- Frontend: Serienfahrt-Formular, Einzelfahrten-Übersicht
- Globales Error-Handling (401 → Logout, 422 → Feldvalidierung)
- Manuelles Test-Protokoll für Kernflows

---

## Bewusst außerhalb des MVP

- Echte Krankenkassenabrechnung
- Zahlungsintegration
- Externe APIs (GTFS, Maps)
- Live-GPS / Tracking
- Native Mobile App
- Push-Notifications
