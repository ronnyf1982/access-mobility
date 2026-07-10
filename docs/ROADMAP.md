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

## Sprint 6 — Fahrt-/Transportanfrage Grundlage ✅
`TransportRequest`-Domänenobjekt als Kern des Buchungsprozesses.

- Backend: `TransportRequest`-Modell (status: draft/requested/cancelled), Alembic-Migration, JSONB-Snapshots
- 6 REST-Endpunkte: list, create, get, update, submit (draft→requested), cancel
- Snapshots: `requirement_snapshot` + `mobility_profile_snapshot` frieren Anforderungen zum Anfragezeit­punkt ein
- Frontend: `TransportRequestView` (Liste + Wizard-light), Pinia Store, API-Modul, Route `/transport-requests`
- Sidebar-Eintrag „Fahrten anfragen", Dashboard-KPI-Kachel mit Count und Direktlink
- Seed-Daten: 1 draft + 1 requested für passenger@access.test (idempotent)
- Kein Matching, keine Disposition, keine Fahrerzuweisung in diesem Sprint

## Sprint 7 — Manuelles Matching & Disposition
Anfrage → Fahrt zuweisen, Fahrdienst bestätigt.

- Backend: `Ride`-Modell (Zuteilung TransportRequest → Fahrzeug + Fahrer), Status-Maschine
- Disponent-Flow: offene Anfragen sehen, Fahrzeug/Fahrer zuweisen, Bestätigung auslösen
- Benachrichtigung: Fahrgast erhält Bestätigung (In-App-Notification)
- Frontend: Dispositions-View (Dispatcher-Rolle), Fahrtbestätigungs-Banner für Fahrgäste

## Sprint 8 — Fahrtstart & Fahreransicht
Fahrer sieht Tagesaufträge, startet Fahrt, markiert Abschluss.

- Backend: Fahrtstart-/Abschluss-Endpoints, Zeitstempel
- Frontend: Fahrer-Dashboard, Auftragsliste, Statuswechsel (unterwegs → abgeschlossen)

## Sprint 9 — KI-Transportberater (Prototyp)
Assistierter Anfrageprozess: KI schlägt Transporttyp und Anforderungen vor.

- Integration Claude API (claude-sonnet-4-6 oder höher)
- Kontext: Mobilitätsprofil + Fahrtdaten → Vorschlag-Text
- Fahrgast kann Vorschlag übernehmen oder manuell anpassen

---

## Bewusst außerhalb des MVP

- Echte Krankenkassenabrechnung
- Zahlungsintegration
- Externe APIs (GTFS, Maps)
- Live-GPS / Tracking
- Native Mobile App
- Push-Notifications
