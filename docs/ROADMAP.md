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

## Sprint 7 — Manuelles Matching & Disposition ✅
Anfrage-Snapshot → Matching-Bewertung → manuelle Zuweisung durch Disponenten.

- Backend: `assigned`-Status + 5 Zuweisungsfelder auf `TransportRequest`, Alembic-Migration
- `manual_matching.py`: Snapshot-basiertes Matching (8 Fahrzeug- + 6 Fahrerregeln), 3 Status: `suitable` / `warning` / `unsuitable`
- 3 neue Endpoints: `GET matching-options`, `POST assign`, `POST unassign`
- Matching ist Entscheidungshilfe — kein Block, Disponent kann immer überschreiben
- **Dual-UI-Modus:** Fahrgast-Ansicht (Wizard, „Meine Fahrten") vs. Dispo-Ansicht (Fahrgastdaten, Matching, kein Wizard)
- Sidebar-Label rollenbasiert: „Fahrten anfragen" (Fahrgäste) / „Disposition" (Provider/Disponent)
- Fahrgast-Kontaktdaten (`passenger_display_name`, email, phone, emergency_contact_*) in API-Responses für Dispo-Rollen
- Frontend: Fahrgastdaten-Infobox + schreibgeschützte Anfragedetails in Dispo-Detailansicht
- Dashboard: `assignedCount` in KPI-Kachel
- Seed: 2 neue Demo-Anfragen (gute Übereinstimmung + Warnungsfall), Fahrer-Qualifikation aktualisiert
- Tests: 26 Pytest-Tests (alle bestanden), TypeScript-Check ✅, Build ✅

## Sprint 8 — Kontakt & Erreichbarkeit
Vollständige Kontaktdaten für Fahrgäste und bessere Erreichbarkeit für Disponenten.

- Telefon-Pflichtfeld oder Alternativtelefon im Benutzerkonto (`User.phone`, Pflicht vs. optional)
- Alternativtelefon / Mobilnummer als zweites Feld
- Abholkontakt (Ansprechperson vor Ort, kann vom Fahrgast abweichen)
- Notfallkontakt direkt im Mobilitätsprofil besser sichtbar / einfacher befüllbar
- Dispatcher-Ansicht: direkte Telefon-Shortcut-Links (tel:) in Listenansicht und Detailansicht

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
