# Roadmap — access-mobility MVP

## Sprint 1 — Grundgerüst ✅
Lauffähiges Fullstack-Grundgerüst: FastAPI + Vue 3 + PostgreSQL via Docker.
Health-Endpoint, Axios-Client, PrimeVue, Pinia, Vue Router.

## Sprint 2 — Designbasis, Landingpage & Portal-Layout ✅
Globale CSS-Designbasis, Layouts (PublicLayout / PortalLayout), Komponenten (Sidebar, Topbar, Header, Footer),
LandingView, DashboardView (Dummy-Daten).

## Sprint 3 — Auth, Rollen & Benutzerstammdaten ✅
JWT-Authentifizierung (bcrypt + PyJWT), 8 Benutzerrollen, Login-View, Route-Guard,
Auth-Pinia-Store, 8 Demo-Nutzer + 2 Demo-Orgs.

## Sprint 4 — Fahrgastprofil & Mobilitätsbedarf ✅
MobilityProfile-Modell (22 Felder, 11 Bedarfstypen), GET/PUT-Endpunkte (Auto-Create, Partial-Update),
MobilityProfileView (Accessibility-first, 5 Sektionen), Pinia Store, Sidebar-Eintrag, Dashboard-Profilkarte.

## Sprint 5 — Fahrdienst, Fahrzeuge und Fahrerprofile ✅
Vehicle-Modell (7 Typen, 8 Ausstattungsmerkmale), DriverProfile-Modell (8 Qualifikationsflags),
CRUD-Endpoints, Fahrzeug- und Fahrerverwaltung im Portal, Dashboard-Flottenkachel.

## Sprint 5B — Konfigurierbare Schnellauswahl-Vorlagen ✅
Zentrale Preset-Konfiguration (`backend/app/core/transport_presets.py`), fachlich konservative
Presets (kein Auto-Setzen med. Felder außer was eindeutig zutrifft), Backend liefert
`preset_controlled_profile_fields` + `suggested_field_values`, Frontend-Reset dynamisch
aus Backend-Daten statt lokal hart kodiert.

## Sprint 6 — Fahrtenbuchung
Einzelne Fahrt buchen, disponieren, ausführen.

- Backend: `Ride`-Modell, Statusmaschine, Zuteilungs-Endpoint
- Frontend: Buchungs-Wizard (PrimeVue Stepper), Fahrtenliste (reale Daten), Fahrer-View mit Statuswechsel
- Koordinator-Flow: Fahrt für andere Person buchen

## Sprint 6 — Organisationsansicht, RBAC & Admin
Org-Kontext vollständig, rollenbasierte UI-Einschränkungen, Admin-Dashboard.

- Fahrtenliste gefiltert nach Organisation
- Kostenstellen-Referenz an Fahrt
- Stornierung mit Bestätigungs-Dialog
- Admin-Dashboard mit Statistik-Karten
- Benutzer-Rollenverwaltung

## Sprint 7 — Serienfahrten & Stabilisierung
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
