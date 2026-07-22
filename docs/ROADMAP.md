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

## Sprint 8 — Assistant Core & barrierefreies Onboarding-Fundament ✅

Onboarding-Fundament und Sprachassistenz-Wahl nach erstem Login implementiert.

- **User-Modell erweitert:** `voice_mode_enabled`, `onboarding_completed_at`, `first_login_at`, `last_login_at` (Alembic-Migration `b3c4d5e6f7a8`)
- **Login-Verhalten:** `first_login_at` und `last_login_at` werden beim Login gesetzt
- **UserPublic-Schema:** `needs_onboarding` (computed: true wenn `onboarding_completed_at is None`), neue Felder in `/auth/login` + `/auth/me`
- **Neue Backend-Endpunkte:**
  - `GET /onboarding/status` — Onboarding-Status + Profil-Füllstand
  - `POST /onboarding/preferences` — Wahl speichern, `onboarding_completed_at` setzen
  - `GET /assistant/capabilities` — rollenbasierte Sprachassistenz-Fähigkeitenliste
- **OnboardingView** (`/onboarding`): Zwei große Kacheln „Ja, Sprachführung aktivieren" / „Nein, normale Einrichtung". ARIA, Tastatur, WCAG AA.
- **Router-Guard:** Automatische Weiterleitung nach `/onboarding` wenn `needs_onboarding === true`. Nach Abschluss: Fahrgäste → `/mobility-profile`, alle anderen → `/dashboard`.
- **Rollenbasierte Sidebar:** Fahrgäste sehen nur Dashboard/Fahrten/Mobilitätsprofil. Fahrer sehen Dashboard/Aufträge. Dispo/Provider/Admin sehen Disposition/Fahrzeuge/Fahrer/...
- **Frontend-API:** `api/onboarding.ts`, `api/assistant.ts` (Typen, API-Calls)
- Tests: 26 Pytest-Tests ✅, TypeScript-Check ✅, Vite-Build ✅

Referenz: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`, `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

## Sprint 9 — Sprachgeführter Mobilitätscheck (offline-fähig) ✅

Geführter Mobilitätscheck als offline-fähiges Dialogfundament implementiert.

- **Route:** `/mobility-profile/assistant` (unter PortalLayout, requiresAuth)
- **Fragenkatalog:** `frontend/src/data/mobilityAssistantQuestions.ts` — 10 Fragen, zentral konfiguriert
- **Feldmapping:** 10 vorhandene MobilityProfile-Felder + `voice_mode_enabled` (User) — nur tatsächlich vorhandene Felder
- **Keine Speicherung** bis zur expliziten Bestätigung — lokales Draft-Objekt
- **Zusammenfassung** zeigt alle Antworten mit gesetzten Feldern und ggf. fehlenden Feldhinweisen
- **Text-to-Speech (Browser Web Speech API):** optional, Fallback auf visuelle UI wenn nicht verfügbar. Auto-Vorlesen wenn `voice_mode_enabled = true`.
- **Onboarding-Verknüpfung:** Sprachführung Ja → Fahrgäste landen auf `/mobility-profile/assistant`
- **MobilityProfileView:** CTA-Karte „Geführten Check starten" sichtbar für alle Fahrgäste
- **Fehlende Felder (keine Migration):** `may_not_wait_alone`, `needs_screen_reader_optimized_ui`, `prefers_voice_guidance` → Roadmap Sprint 10+
- **Backend-Änderung:** `GET /assistant/capabilities` — `mobility_profile`-Capability um `guided_check: true`, `guided_check_route`, `offline_supported: true`, `online_ai_supported: false` erweitert
- Tests: 26 Pytest-Tests ✅, TypeScript-Check ✅, Vite-Build ✅

Referenz: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`, `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

## Sprint 9B — Verbesserter Sprachassistent: TTS-Flow, STT-Bestätigung, Tastaturkürzel ✅

Erweiterte Sprachinteraktion für den geführten Mobilitätscheck.

- **TTS-Flow:** Frage vorlesen → nachfragen, ob Optionen vorgelesen werden sollen → nur auf Anfrage vorlesen
- **STT (optional):** Button-gesteuert, nie dauerhaft — `window.SpeechRecognition` / `webkitSpeechRecognition`
- **STT-Bestätigungsdialog:** Erkannte Antwort anzeigen + Bestätigung vor Übernahme
- **Tastaturkürzel:** J/N/W/S/R/H/ArrowLeft/Escape mit sichtbarer Hinweisleiste
- **Neues Utility:** `frontend/src/utils/speech.ts` (TTS + STT + `normalizeSpokenInput`)
- Browser-Test ✅, TypeScript-Check ✅, Vite-Build ✅

## Sprint 10 — Fahrer-Schichtstart & Fahrzeugwahl ✅

Fahrer startet Schicht, wählt Fahrzeug (Standardfahrzeug oder per Kennzeichen), pausiert/beendet Schicht, sieht Tagesaufträge.

- **Backend:** `DriverShift`-Modell mit `ShiftStatus` (active/paused/ended), Alembic-Migration `driver_shifts`-Tabelle
- **`DriverProfile.default_vehicle_id`:** Nullable FK, Seed setzt AM-BUS-1 für driver@access.test; neuer Endpoint `GET /driver/me` liefert Profil + Standardfahrzeug + aktive Schicht in einem Call
- **API-Endpoints:** `GET /driver/me`, `GET /driver/shift/current`, `POST /shift/start|end|pause|resume`, `GET /vehicles/search`, `GET /assignments`
- **Schicht starten:** vehicle_id > license_plate > default_vehicle_id des Profils (Fallback)
- **Fahrer-App (mobile-first):** Große Statuskarte oben, große Aktions-Buttons (56 px+), kein Verwaltungs-UI
  - Szenario A: Standardfahrzeug direkt sichtbar → ein Button „Schicht mit diesem Fahrzeug beginnen"
  - Szenario B: Kennzeichen-Suche → Fahrzeug wählen → „Schicht beginnen"
  - Schicht beenden: immer mit Bestätigungs-Modal (Bottom-Sheet)
- **Auftragsstruktur:** „Linienfahrten" (Platzhalter, Sprint 15) + „Spontane Fahrten" (TransportRequests)
- **Sidebar:** Fahrer-Nav mit „Meine Schicht" + „Meine Aufträge" → `/driver`
- **Tests:** 20/20 passed, TypeScript-Check ✅, Vite-Build ✅
- **Noch nicht:** STT/Spracheingabe, Live-GPS, Push-Notifications, Statusbuttons zugestiegen/ausgestiegen

## Sprint 11 — Fahrt-Statusereignisse & Benachrichtigungseinstellungen ✅

Fahrten erhalten einen nachvollziehbaren Statusverlauf. Fahrer setzen Statusereignisse. Fahrgäste konfigurieren Benachrichtigungseinstellungen.

- **Neues Modell `RideStatusEvent`:** 7 Ereignistypen (driver_on_way, driver_arrived, passenger_picked_up, ride_started, ride_completed, ride_cancelled, issue_reported), verknüpft mit TransportRequest + auslösendem User
- **TransportRequestStatus** um `completed` erweitert; wird automatisch gesetzt wenn `ride_completed`-Ereignis erstellt wird (`ride_cancelled` → `cancelled`)
- **Neues Modell `PassengerNotificationPreference`:** pro Ereignistyp 4 Flags (notify_trusted_persons, channel_in_app, channel_email, channel_sms); noch kein Versand — nur Einstellungsgrundlage
- **Alembic-Migration `f7a8b9c0d1e2`:** `ridestatuseventtype`- + `notificationeventtype`-Enums, `ride_status_events`- + `passenger_notification_preferences`-Tabellen, `completed` zu `transportrequeststatus` hinzugefügt
- **API-Endpoints:**
  - `POST /driver/transport-requests/{id}/status-events` — Fahrer setzt Status (nur eigene zugewiesene Fahrten)
  - `GET /transport-requests/{id}/status-events` — Fahrer (eigene), Fahrgast (eigene), Staff-Rollen
  - `GET /passenger/notification-preferences` — eigene Einstellungen lesen
  - `PUT /passenger/notification-preferences` — Upsert aller Einstellungen
- **Fahrer-App:** Jede zugewiesene Fahrt zeigt 5 Statusbuttons + „Problem melden" mit optionaler Notiz; letzter Status + Uhrzeit sichtbar; Ladezustand + Fehlermeldung
- **Fahrgastprofil:** Neuer Abschnitt „Benachrichtigungseinstellungen" mit Tabelle aller Ereignistypen × 4 Kanäle als Checkboxen; Speichern-Button mit Erfolg-/Fehlermeldung
- **Seed:** Zugewiesene Demo-Fahrt für driver@access.test + 7 Benachrichtigungseinstellungen für passenger@access.test (idempotent)
- **Tests:** 158/158 passed, TypeScript-Check ✅, Vite-Build ✅
- **Keine echten Notifications:** Kein SMS/E-Mail/Push-Versand in Sprint 11 — nur Einstellungsgrundlage
- **Grundlage für Sprint 12:** Live-Tracking, GPS, echte Notification-Dispatch-Logik

## Sprint FAHRANDO-2 — Gate-Schutzseite & Website-Testzugänge ✅

Separate Passwortschutzseite (`/gate`) mit DB-basierten Testzugängen — vollständig unabhängig vom App-Login.

- **`/gate`:** Neue Schutzseite (GateView), immer öffentlich erreichbar, zwei-spaltiges schwarzes Layout, Fahrando-Logo
- **`PreviewAccessUser`:** Eigenes Modell + Tabelle (getrennt von `User`), bcrypt-gehashte Passwörter, Aktivstatus, Nutzungshistorie (`last_used_at`)
- **Alembic-Migration** `e6f7a8b9c0d1`: Tabelle `preview_access_users` mit Unique-Index auf email
- **`POST /public/test-access/login`:** DB-Lookup, kein Env-Var, gleiche 401-Meldung für alle Fehler
- **Platform-Admin-Modul „Website-Testzugänge":** 7 Endpoints + CRUD-UI (Liste/Suche/Aktivfilter, Anlegen, Bearbeiten, Passwort-Reset, De-/Aktivierung)
- **Gate-Guard im Router:** `/` erfordert `sessionStorage.fahrando_unlocked === '1'`, `/gate` immer frei, `/login` → App-Login (unverändert)
- **`vite.config.ts` Proxy:** `/api` → `http://localhost:8010` — behebt fehlende API-Erreichbarkeit für `fetch`-Module im Vite Dev-Server
- **46 neue Pytest-Tests** (Zugriffskontrolle, CRUD, Login, Aktivierung, Passwort-Reset, Regression), alle passed
- TypeScript-Check ✅, Vite-Build ✅, Proxy ✅

## Sprint FAHRANDO-1 — Fahrando Coming-Soon, Testzugang & Platform-Admin-Benutzerverwaltung ✅

Plattform-Marke sichtbar machen, Testzugang absichern, Platform-Admin kann Nutzer vollständig verwalten.

- **`/` (LandingView):** Fahrando Coming-Soon-Seite (standalone, kein PublicLayout), Zwei-Spalten-Layout (Desktop), FahrandoLogo-Komponente, Login-Formular mit echtem JWT-Auth — kein zweites Auth-System
- **`/login`:** Dauerhafter Redirect zu `/`, Logout kehrt zu `/` zurück
- **`/impressum`, `/datenschutz`:** Placeholder-Seiten (Inhalt folgt vor Launch)
- **FahrandoLogo.vue:** SVG-Komponente, Rollstuhl-Symbol + Bewegungslinien, Gelb, drei Varianten
- **`ensure_platform_admin.py`:** Idempotentes Bootstrap-Script — liest nur aus Env-Vars, setzt `onboarding_completed_at`, gibt niemals Passwort aus
- **Platform-Admin API:** 7 Endpoints `GET|POST /platform-admin/users`, `GET|PATCH /platform-admin/users/{id}`, `POST /reset-password|activate|deactivate`
- **`require_platform_admin`-Dependency:** 403 für alle Nicht-Platform-Admins
- **`PlatformAdminUsersView.vue`:** Liste + Suche/Filter, 4 Modals (Anlegen/Bearbeiten/Passwort-Reset/Aktivierung), Toast-Feedback
- **Router-Guard:** `/platform-admin/*` → 403 ohne `platform_admin`-Rolle → Redirect `/dashboard`
- **Sidebar:** Eigene „Plattform-Admin"-Sektion (gelber Label), getrennt von DISPO_ROLES
- **Sicherheit:** Passwort-Hash nie in API-Response, kein Passwort in Logs/Tests/Doku
- **Tests:** 54 neue Pytest-Tests (alle bestanden), TypeScript-Check ✅, Build ✅

## Sprint FAHRANDO-DEPLOYMENT-1 — Railway-Deployment & Production-Build ✅

Backend auf Railway deployed, statisches Frontend für fahrando.com gebaut und via FileZilla hochgeladen.

- **Railway Backend:** Nixpacks-Deployment, Root-Level `railway.json` + `Procfile`, PostgreSQL auf Railway angebunden
- **Migrationen + Seed:** `alembic upgrade head` + `seed_demo_data` online ausgeführt
- **CORS:** `ALLOWED_ORIGINS=https://fahrando.com,https://www.fahrando.com` als Railway-Umgebungsvariable gesetzt
- **`frontend/.env.production`:** `VITE_API_BASE_URL=https://fahrando-api-production.up.railway.app/api/v1` (nicht committed, in `.gitignore`)
- **API-Base-Fix:** `GateView.vue`, `previewAccess.ts`, `platformAdmin.ts` nutzten relative `/api/v1`-Pfade statt `VITE_API_BASE_URL` — behoben
- **Production-Build:** `npm run build` mit `.env.production` → `dist/` für Webspace
- **Upload-Staging:** `deploy/fahrando-webspace-upload/` (nicht committed, gitignored)
- Website-Testzugänge und Benutzerverwaltung laden online über Railway API

Railway API: `https://fahrando-api-production.up.railway.app` · Frontend: `https://fahrando.com`

## Sprint FAHRANDO-GATE-PROTECTS-LOGIN-DIRECTLINK-1 — Gate schützt /login (Variante B) ✅

Gesamter Teststand liegt hinter dem Preview-Gate — auch `/login` und alle App-Routen sind ohne Gate-Unlock nicht direkt erreichbar.

- **Variante B:** Alle Routen außer `/gate`, `/impressum`, `/datenschutz` erfordern Gate-Unlock
- `/login` ohne Gate-Unlock → Gate-Seite erscheint, Redirect-Parameter (`?redirect=/login`) erhalten
- Nach Gate-Unlock → Weiterleitung zu `/login` → normaler App-Login
- `/platform-admin`, `/dashboard`, `/driver` ohne Gate-Unlock → ebenfalls Gate-Redirect
- Nach Gate-Unlock greifen App-Routen weiterhin normale App-Auth (unverändert)
- Gate erzeugt kein App-JWT — vollständig getrennte Systeme
- `gateExempt`-Flag auf `/impressum` und `/datenschutz` — immer frei erreichbar
- Open-Redirect-Schutz bleibt erhalten (nur interne Pfade, kein `//`)

## Sprint 12A — Live-Status für angefragte/geplante Fahrten ✅

Fahrgast sieht den aktuellen Fahrt-Status und -verlauf für **angefragte und disponierte Fahrten** direkt in der App. Vertrauensperson erhält Backend-Zugriff auf Status-Events.

> **Fahrttyp:** Betrifft ausschließlich den Typ „Angefragte/geplante Fahrt" — Fahrten mit Vorlaufzeit, manueller Disposition und Zuweisung. Kein Spontanfahrten-Modus.

- **Backend:** `trusted_person`-Zugriff auf `GET /transport-requests/{id}/status-events` — prüft aktive `TrustedRelationship` mit `can_view_rides=True`
- **Neuer Service:** `backend/app/services/notification_dispatch.py` — Placeholder `collect_notification_targets_for_status_event()` (liest Präferenzen, kein echter Versand)
- **Frontend (`TransportRequestView.vue`):** Fahrgastkarten zeigen Live-Status-Abschnitt für `assigned`/`completed`/`cancelled`-Fahrten — aktueller Status, letzter Zeitstempel, Statusverlauf (neueste zuerst)
- **Polling:** alle 20 Sekunden für aktiv zugewiesene Fahrten (Interval sauber gestoppt on unmount)
- **`frontend/src/api/rides.ts`:** eigenständiges API-Modul `getRideStatusEvents()` für Fahrgast-/Vertrauenspersonen-Kontext
- **`completed`-Status-Badge** + `statusIcon` im Frontend ergänzt
- **Tests:** 156/165 passed, 9 skipped (Seed-abhängig)
- **TypeScript-Check:** ✅ | **Build:** ✅ built in 2.63s | **Alembic:** keine neue Migration
- **Bewusst zurückgestellt:** Vertrauenspersonen-View (folgt 12E), echter Dispatch (folgt 12E), GPS-Tracking (folgt 12D)

## Sprint 12B — Spontane Fahrten: Karten-MVP, Standortfreigabe und Matching ✅

**Fahrttyp:** Spontane Fahrt — Fahrgast bucht jetzt sofort, ohne Vorlaufzeit oder Disposition.

> **Umgesetzt:** Karten-MVP mit Leaflet/OpenStreetMap, Fahrgast-Standortfreigabe per Browser-Geolocation,
> Backend-Matching mit Haversine-ETA, vollständige Verfügbarkeits- und Capability-Prüfung.
> Noch keine finale Buchung — folgt Sprint 12C.

**Kartenlösung:** Leaflet + OpenStreetMap-Tiles (kein API-Key, kein externer kostenpflichtiger Dienst, MVP/Preview-Status).
Für Produktion: OSM-Nutzungsbedingungen, Datenschutz und ggf. eigener Tile-/Routing-Dienst prüfen.

**Backend:**
- `POST /api/v1/spontaneous-rides/matches` — gibt passende freie Fahrzeuge zurück
- Haversine-Luftlinien-ETA: `max(3, int(km / 30 * 60))` Minuten
- Verfügbarkeit: Fahrer mit aktiver Schicht (`status=active`), nicht in Pause, Fahrzeug nicht belegt (`TransportRequest.status=assigned`)
- Mobilitätsprofil-Capability-Check: Rampe, Lift, Rollstuhlplatz, Elektro-Rollstuhl, Liegendtransport etc.
- Berechtigung: passenger (nur für sich selbst), trusted_person (für verknüpften Fahrgast), dispatcher/coordinator/admin
- Fahrerdaten in Response: kein Telefon, keine E-Mail, keine private Adresse
- Migration: `current_latitude / current_longitude` zu `driver_shifts` ergänzt
- Seed: Demo-Schicht AM-VAN-1 (aktiv, passt) + AM-CAR-1 (Pause, gefiltert)
- 13 neue Tests, alle grün

**Frontend:**
- Route `/spontaneous-ride` → `SpontaneousRideView`
- Einstieg „Spontane Fahrt buchen" im Dashboard (Fahrgast/Vertrauensperson)
- Standortfreigabe nur nach Klick, mit verständlichen Fehlerstaaten
- Leaflet-Karte: Fahrgast-Marker + Fahrzeug-Marker mit Popup (Label, Entfernung, ETA, Ausstattung)
- Textliste parallel zur Karte (barrierefrei)
- „Auswählen"-Button deaktiviert mit Hinweis „folgt Sprint 12C"

**Matching-Kernregeln:**
- Mobilitätsprofil (Rollstuhl, Rampe, Lift, Einstiegshilfen, med. Bedarf)
- Fahrer im Dienst und nicht in Pause
- Fahrzeug und Fahrer nicht bereits einer aktiven Fahrt zugewiesen
- Sortierung nach Entfernung (Haversine, aufsteigend)
- Kein automatischer Block — Fahrgast wählt aus Vorschlägen

## Sprint 12C — Spontane Fahrten: Buchung & Fahrerannahme ✅

Fahrgast bucht ein Fahrzeug aus dem Matching-Ergebnis, Fahrer nimmt an oder lehnt ab.

**Neue Status-Werte (`TransportRequestStatus`):**
- `spontaneous_requested` — Buchung angefragt, Fahrer hat noch nicht reagiert
- `driver_declined` — Fahrer hat abgelehnt (Fahrzeug wird wieder frei)

**Backend:**
- `POST /api/v1/spontaneous-rides/book` — Buchung anlegen; prüft aktive Schicht, blockiert Doppelbuchung (409)
- `GET /api/v1/driver/spontaneous-ride-requests` — Fahrer sieht offene Anfragen
- `POST /api/v1/driver/spontaneous-ride-requests/{id}/accept` — Status → `assigned`
- `POST /api/v1/driver/spontaneous-ride-requests/{id}/decline` — Status → `driver_declined`
- Neue `TransportRequest`-Felder: `is_spontaneous`, `pickup_latitude/longitude`, `destination_latitude/longitude`
- `_BLOCKING_STATUSES` in `spontaneous_matching.py` um `spontaneous_requested` erweitert
- Alembic-Migration `b9c0d1e2f3a4`: Enum-Werte + 5 neue Spalten
- 12 neue Tests, alle grün (gesamt: 190 passed)

**Frontend:**
- Passenger-App: „Auswählen"-Button jetzt aktiv → `POST /spontaneous-rides/book`
- Buchung per Fahrzeug-Button; Loading-State pro Fahrzeug
- Nach erfolgreicher Buchung: Bestätigungs-Screen mit Fahrzeug, Fahrer, ETA
- 409-Fehler (Fahrzeug weg) wird mit Klartext angezeigt
- Fahrer-App (`DriverDashboardView`): neue Sektion „Spontane Fahrtanfragen"
- Annehmen/Ablehnen-Buttons mit Loading-State; nach Annahme erscheint Fahrt in Aufträgen

**Bewusst zurückgestellt:**
- Kein echtes Live-Tracking nach Annahme (folgt 12D)
- Keine Zahlungs- oder Abrechnungslogik
- Keine SMS/E-Mail/Push (Grundlage Sprint 11)
- Keine externe Routing-API
- Bestehende geplante Fahrten unverändert

**GPS-Datenschutz-Grundregeln (verbindlich):**
- GPS nur nach ausdrücklicher, informierter Zustimmung
- Standort nur für die konkrete Sofortfahrt — kein Dauertracking
- Keine Hintergrundüberwachung im MVP
- Vertrauenspersonen nur gemäß Benachrichtigungseinstellungen (Sprint 11) informiert

## Sprint 12D — Spontane Fahrten: Live-Tracking Fahrer → Fahrgast ✅

Nach Fahrerannahme sieht der Fahrgast den Fahrer auf der Karte. Kein WebSocket, kein externe Routing-API — Polling-MVP.

**Backend:**
- `POST /api/v1/driver/location` — Fahrer aktualisiert Schichtstandort (nur eigene aktive Schicht); optional mit `transport_request_id` für Fahrtvalidierung
- `GET /api/v1/spontaneous-rides/{id}/tracking` — Fahrgast/Fahrer liest Tracking-Status; Zugriffskontrolle (eigene Fahrt), keine sensiblen Daten (kein Telefon, keine E-Mail)
- `TransportRequestListItem` um `is_spontaneous`, `pickup_latitude`, `pickup_longitude` erweitert
- Kein Schema-Change: `DriverShift.current_latitude/longitude` aus Sprint 12B bereits vorhanden
- Keine neue Migration
- Zustandslabels: `spontaneous_requested → „Warte auf Fahrerannahme"`, `assigned → „Fahrer angenommen — unterwegs zu Ihnen"`

**Frontend:**
- `SpontaneousRideView.vue`: Phase `booked` mit Live-Polling (alle 15 Sek.)
  - Status-Badge (Waiting/Active/Error) mit Icon und Farbe
  - Karte zeigt Fahrer-Marker + Abhol-Marker wenn `can_track=True`
  - Textliste: Fahrer, Fahrzeug, Entfernung, ETA, letzter Standortzeitpunkt
  - Bei Ablehnung: Fehlermeldung + „Erneut suchen"
  - Polling stoppt bei Terminal-Status (declined/completed/cancelled) und bei unmount
- `SpontaneousRideMap.vue`: neuer Fahrer-Marker (🚗), fitBounds für Fahrer + Abholpunkt
- `DriverDashboardView.vue`: Standort-Teilen-Sektion für spontane Fahrten
  - Button „Standort teilen" → Browser-Geolocation → sendet an Backend
  - Auto-Update alle 15 Sek.
  - „Standort stoppen"-Button, grüner Puls-Indikator
  - Datenschutz-Hinweis: nur während dieser Fahrt, kein Hintergrundtracking

**Datenschutzgrenzen (verbindlich):**
- Standort wird NUR in `DriverShift.current_latitude/longitude` gespeichert — kein Verlauf, kein Log
- Tracking-Response enthält nur Anzeigename, keine Kontaktdaten
- Fahrgast sieht nur eigene Fahrt; Fahrer sieht nur eigene zugewiesene Fahrt
- Standortfreigabe nur nach explizitem Klick (kein Auto-Start), Stopp jederzeit möglich

**Tests:** 16 neue Tests (206 gesamt, alle grün) · TypeScript ✅ · Build ✅ (404 Module, 793 kB, 5.10s) · Alembic ✅ (keine Migration)

**Bewusst zurückgestellt:**
- Kein WebSocket (Polling reicht für MVP)
- Keine externe Routing-API
- Kein dauerhafter Standortverlauf
- Keine Zahlungs-/Abrechnungslogik
- Vertrauensperson-Tracking folgt Sprint 12E

## Sprint 12K — Automatische Weiterleitung nach Ablehnung oder Timeout ✅

Wenn ein Fahrer ablehnt oder die 2-Minuten-Wartezeit abläuft, sucht das System automatisch den nächsten freien Fahrer.

- **`rematch_group_id` + `rematch_attempt`** auf `TransportRequest` — verbinden alle Versuche einer Rematch-Kette, Alembic-Migration `e2f3a4b5c6d7`
- **`do_rematch()`** in `spontaneous_matching.py`: setzt alten TR auf `driver_declined`, sucht Ersatzfahrer (alle bisherigen Fahrer der Gruppe ausgeschlossen), erstellt neuen TR mit `rematch_attempt+1`; max. 3 Versuche
- **Tracking-Response** liefert `next_request_id` (nächste TR-ID bei Rematch) und `request_expires_at` (Buchungszeit + 120s)
- **`POST /{id}/timeout`**: Frontend ruft diesen Endpoint auf wenn `request_expires_at` in der Vergangenheit — löst Rematch aus; nur Fahrgast der Fahrt, nur bei `spontaneous_requested`-Status
- **Decline-Endpoint** ruft `do_rematch()` statt direkten Status-Set
- **Fahrgast-App**: blaues Rematch-Banner; kein UI-Reset; `driver_declined`-Fehler nur noch bei endgültiger Ablehnung; Polling wechselt `activeRequestId` bei Rematch automatisch
- **Manuelle Stornierung** → kein Rematch (unveränderte Logik aus 12J)
- **14 Tests**, alle grün (352 gesamt); TypeScript ✅; Build ✅; Alembic ✅

## Sprint 12E — Vertrauenspersonen-View & echter Notification-Dispatch
_geplant_

Dedizierte Ansicht für Vertrauenspersonen. Echter Benachrichtigungs-Dispatch.

- Vertrauenspersonen-View: Fahrten des verknüpften Fahrgastes sehen und Status lesen
- Echter E-Mail/In-App-Dispatch basierend auf `PassengerNotificationPreference` (Sprint 11 Grundlage)
- Backend-Service `notification_dispatch.py` zu echtem Dispatcher ausbauen

## Sprint 13 — Online-KI-Berater / ChatGPT-Anbindung

Assistierter Anfrageprozess: KI schlägt Transporttyp und Anforderungen vor.

- Backend-Endpoint `/api/v1/assistant/interpret` (API-Key nur im Backend)
- Integration Claude API (claude-sonnet-4-6 oder höher) oder ChatGPT
- Kontext: Mobilitätsprofil + Fahrtdaten → Vorschlag-Text + strukturierte Feldvorschläge
- Fahrgast kann Vorschlag übernehmen oder manuell anpassen
- Datenschutz: Zustimmung erforderlich, keine unnötige Weitergabe med. Daten

## Sprint 14 — Fahrt per Sprache anfragen

Vollständige Fahrtbuchung per Sprachführung.

- Sprachgeführter Buchungs-Wizard: Abholort → Ziel → Datum/Zeit → Anforderungen → Bestätigung
- Adresseingabe per Sprache (Online-KI-Interpretation)
- Datum/Zeit-Erkennung aus natürlicher Sprache
- Bestätigungs-Dialog vor Absenden (kein automatisches Absenden)

## Sprint 15 — Regelmäßige Touren / Linienverkehr

Fahrgäste können regelmäßige Fahrten (täglich, wöchentlich) als Serienfahrten anlegen.
Disponenten können Touren mit festen Reihenfolgen und Zeitplänen konfigurieren (Linienverkehr).

## Sprint 16 — Ausfallmanagement

Ersatzfahrzeug, Fahrerausfall, Stornierung mit Neuzuweisung.

## Sprint 17 — Tourenoptimierung

KI-gestützte Routenoptimierung für Disponenten.

---

## Drei Fahrtarten — fachliche Unterscheidung

| Typ | Beschreibung | Status |
|---|---|---|
| **Angefragte/geplante Fahrt** | Fahrgast oder Org stellt Anfrage mit Vorlaufzeit; Disponent weist Fahrzeug + Fahrer zu | ✅ Sprint 6–12A |
| **Linienfahrt** | Wiederkehrende oder fest geplante Fahrten nach Fahrplan/Route | geplant Sprint 15+ |
| **Spontane Fahrt** | Sofortfahrt-Modus (Uber-artig): Fahrgast bucht jetzt, GPS-Standort als Abholort, nächstes freies Fahrzeug, Auto-Rematch bei Ablehnung/Timeout | ✅ Sprint 12B–12K |

## Bewusst außerhalb des MVP

- Echte Krankenkassenabrechnung
- Zahlungsintegration
- Externe Maps-/Routing-API (GTFS, Google Maps, OSM) — Crow-fly-Distanz als MVP-Ersatz
- Echtzeit-GPS-Tracking (Live-Positionsdaten vom Fahrzeug) — Grundlage Sprint 12D
- Native Mobile App
- Push-Notifications (Web-Push)
- Automatisches Matching ohne Disponent (Spontanfahrten: halbautomatisch via Sprint 12B)
