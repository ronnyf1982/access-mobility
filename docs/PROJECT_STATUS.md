# Projektstatus

## Sprint 1 — Grundgerüst ✅

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
- [x] Vue Router, Axios-Client mit `VITE_API_BASE_URL`
- [x] `README.md` mit Startbefehlen

### Designentscheidungen (freigegeben)

- [x] Responsive Webplattform — keine native App (MVP-Scope)
- [x] Öffentlicher Bereich (Landingpage) + geschützter Portalbereich
- [x] Designrichtung: Schwarz/Anthrazit + Gelb als Akzentfarbe
- [x] Designreferenzen abgelegt: `docs/Design/Landingpage.png`, `docs/Design/dashboard.png`
- [x] Verbindlicher Design Guide erstellt: `docs/Design/DESIGN_GUIDE.md`

---

## Sprint 2 — Designbasis, Landingpage & Portal-Layout ✅

**Abgeschlossen:** 2026-07-10

### Umgesetzt

**Globale Designbasis**
- [x] `src/assets/styles/variables.css` — CSS Custom Properties gemäß DESIGN_GUIDE.md
- [x] `src/assets/styles/base.css` — Reset, Typografie, Utility-Klassen (`.am-btn`, `.am-card`, `.am-badge`)
- [x] PrimeVue Dark Mode via `class="dark"` auf `<html>`
- [x] WCAG-AA-konforme Fokus-Styles (gelber Outline-Ring)

**Layouts**
- [x] `src/layouts/PublicLayout.vue` — Header + RouterView + Footer
- [x] `src/layouts/PortalLayout.vue` — Sidebar + Topbar + RouterView

**Komponenten**
- [x] `PublicHeader.vue` — Logo, Nav (Für Fahrgäste / Fahrdienste / Organisationen / Kontakt), CTA-Button, Scroll-Effekt
- [x] `PublicFooter.vue` — 4-spaltiges Link-Grid, Markenblock, Copyright
- [x] `AppSidebar.vue` — fixierte Sidebar, 9 Nav-Einträge (nur Dashboard aktiv, Rest als „bald"-Chips), Support-Block
- [x] `AppTopbar.vue` — Suche, Benachrichtigungs-Badge, User-Avatar (Dummy)

**Views**
- [x] `LandingView.vue` (Route `/`) — Hero mit Stat-Card, Feature Strip, Zielgruppen-Kacheln, Vorteile-Grid, CTA-Banner
- [x] `DashboardView.vue` (Route `/dashboard`) — 4 KPI-Kacheln, Fahrtentabelle (5 Dummy-Zeilen), Buchungsübersicht, Karten-Platzhalter, Schnellaktionen

**Routing**
- [x] Nested Routes: `/` → PublicLayout, `/dashboard` → PortalLayout
- [x] Catch-all → `/dashboard` (für noch nicht implementierte Portal-Routen)
- [x] „Anmelden / Registrieren" führte zu `/dashboard` (kein echter Login)

**Backend**
- [x] Unverändert — Health-Endpoint bleibt, keine neuen Modelle

---

## Produktgrundsätze (freigegeben 2026-07-10)

- [x] **Accessibility-first:** Barrierefreiheit ist Grundlage, kein nachträgliches Feature
- [x] **Fahrgast-Oberfläche:** Wizard-Prinzip, große Buttons, Icon + Text, eine Entscheidung pro Schritt
- [x] **Technische Barrierefreiheit:** ARIA, Tastaturbedienung, Fokuszustände, WCAG AA/AAA, vorlesbare Fehlermeldungen
- [x] **Sprachführung** als späteres Kernfeature vorgesehen (nicht im MVP)
- [x] **Remote-Buchung:** Angehörige/Betreuer/Org können für Fahrgäste buchen — erweitertes Vertrauenspersonen-Modell später
- [x] **Mobilitätsprofil:** 11 Bedarfstypen definiert (Rollstuhl, E-Rollstuhl, Rollator, Krücken, blind, gehörlos, Begleitperson, Einstiegshilfe, Rampe, Lift, Liegendtransport)
- [x] **Fahrzeugausstattung:** 10 Merkmale definiert — Grundlage für späteres Matching
- [x] **Matching-Grundsatz:** Fahrgastbedarf + Fahrzeugausstattung + Fahrerqualifikation müssen gemeinsam passen
- [x] Anforderungsdokument erstellt: `docs/Product/ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md`

---

## Sprint 3 — Auth, Rollen & Benutzerstammdaten ✅

**Abgeschlossen:** 2026-07-10

### Backend

- [x] `bcrypt==4.2.1` + `PyJWT==2.9.0` (Python 3.13 kompatibel) zu `requirements.txt`
- [x] `app/core/config.py` — `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` ergänzt
- [x] `app/core/security.py` — `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`
- [x] `app/models/user.py` — `UserRole` (8 Rollen als Enum), `User`-Modell
- [x] `app/models/organization.py` — `OrganizationType` (7 Typen), `Organization`-Modell
- [x] `app/models/membership.py` — `OrganizationMembership`-Modell
- [x] `app/models/trusted_relationship.py` — `TrustStatus` (3 Zustände), `TrustedRelationship`-Modell
- [x] `app/db/base.py` — alle Modelle für Alembic importiert
- [x] `app/schemas/user.py` — `UserPublic`, `LoginRequest`
- [x] `app/schemas/token.py` — `Token`
- [x] `app/crud/crud_user.py` — `get_by_email`, `get_by_id`
- [x] `app/api/deps.py` — `get_current_user` (OAuth2 Bearer)
- [x] `app/api/v1/endpoints/auth.py` — `POST /auth/login`, `GET /auth/me`, `POST /auth/logout`
- [x] `app/api/v1/router.py` — Auth-Router eingebunden
- [x] Alembic-Migration `20260710_0000-a1b2c3d4e5f6_sprint3_auth_user_org.py`
- [x] `app/scripts/seed_demo_data.py` — 7 Demo-Nutzer, 2 Orgs, 4 Memberships, 1 TrustedRelationship

### Frontend

- [x] `src/types/index.ts` — `UserPublic`, `TokenResponse`, `UserRole`, `ROLE_LABELS`, `ROLE_CONTEXT`
- [x] `src/api/auth.ts` — `login`, `fetchMe`, `logout`
- [x] `src/api/client.ts` — Bearer-Interceptor, 401-Handler (Redirect zu `/login`)
- [x] `src/stores/auth.ts` — Pinia Auth-Store (token, user, isAuthenticated, role, fullName, initials, login, loadUser, logout)
- [x] `src/views/auth/LoginView.vue` — Barrierefreies Login (ARIA, aria-live Fehler, Passwort anzeigen/verbergen, Demo-Auswahl)
- [x] `src/router/index.ts` — `/login`-Route + `beforeEach`-Guard (unauthentifiziert → /login)
- [x] `PublicHeader.vue` — CTA geändert: „Anmelden" → `/login`
- [x] `AppTopbar.vue` — echter Nutzername/Rolle aus Store, Abmelden-Button
- [x] `AppSidebar.vue` — Abmelden-Button im Support-Bereich
- [x] `DashboardView.vue` — Rollen-Kontext-Box mit Willkommensnachricht

### Docs

- [x] `README.md` — Demo-Logins + Seed-Befehl ergänzt
- [x] `docs/PROJECT_STATUS.md` — Sprint 3 dokumentiert
- [x] `docs/DECISIONS.md` — Auth-Entscheidungen dokumentiert
- [x] `.env.example` — `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` ergänzt

### Bewusst nicht umgesetzt (Sprint 3)

- Keine öffentliche Registrierung
- Kein Passwort-Reset / E-Mail-Verifikation
- Kein SSO / OAuth / externe Identitätsprovider
- Kein RBAC (rollenbasierte UI-Einschränkungen) — folgt Sprint 6
- TrustedRelationship nur als Datenmodell — keine eigene UI
- Kein Refresh-Token (localStorage ist MVP/Dev-only; Entscheidung in DECISIONS.md)

---

---

## Sprint 4 — Fahrgastprofil & Mobilitätsbedarf ✅

**Abgeschlossen:** 2026-07-10

### Backend

- [x] `app/models/mobility_profile.py` — `WheelchairType`-Enum (manual/electric/unknown), `MobilityProfile`-Modell (22 Felder inkl. alle Bedarfs-Flags, Notfallkontakt, Hinweise); `unique=True` auf `user_id`
- [x] `app/db/base.py` — `mobility_profile`-Import für Alembic ergänzt
- [x] `app/schemas/mobility_profile.py` — `MobilityProfileBase`, `MobilityProfileCreate`, `MobilityProfileUpdate` (alle Felder `Optional` für Partial-Update), `MobilityProfilePublic`
- [x] `app/crud/crud_mobility_profile.py` — `get_by_user_id`, `get_or_create` (gibt `tuple[MobilityProfile, bool]` zurück), `upsert` (Partial-Update via `exclude_unset=True`)
- [x] `app/api/v1/endpoints/mobility_profile.py` — `GET /mobility-profile/options` (ohne Auth), `GET /mobility-profile/me` (Auto-Create), `PUT /mobility-profile/me` (Partial-Update)
- [x] `app/api/v1/router.py` — `mobility_profile`-Router eingebunden
- [x] Alembic-Migration `20260710_0001-b2c3d4e5f6a1_sprint4_mobility_profile.py`
- [x] `app/scripts/seed_demo_data.py` — Demo-Profil für `passenger@access.test` (Rollstuhl manuell, Rampe, Einstiegshilfe, Notfallkontakt Anna Muster)

### Frontend

- [x] `src/types/index.ts` — `WheelchairType`, `MobilityProfile`, `MobilityProfileUpdate`, `MobilityNeedOption`, `MOBILITY_NEED_KEYS` ergänzt
- [x] `src/api/mobilityProfile.ts` — `getMyProfile()`, `updateMyProfile()`, `getOptions()`
- [x] `src/stores/mobilityProfile.ts` — Pinia Store mit `profile`, `loading`, `saving`, `hasProfile`, `isProfileFilled`, `mobilityNeedItems`, `load()`, `save()`; statische `NEED_DEFINITIONS` (11 Bedarfstypen mit Icon + Beschreibung)
- [x] `src/views/MobilityProfileView.vue` — Accessibility-first Profil-Seite (5 Abschnitte: Notfallkontakt, 11 Bedarf-Toggle-Karten, Fahrzeughinweise, Freitextfelder, Speichern); ARIA-Rollen (`role="checkbox"`, `role="switch"`, `aria-checked`), `aria-live` für Erfolg/Fehler
- [x] `src/router/index.ts` — Route `/mobility-profile` unter `PortalLayout` als Kind von `/dashboard` ergänzt
- [x] `src/components/layout/AppSidebar.vue` — „Mobilitätsprofil"-Eintrag als aktive Route nach Dashboard eingefügt
- [x] `src/views/dashboard/DashboardView.vue` — Profilstatus-Karte in rechter Sidebar (nur für Fahrgäste/Vertrauenspersonen), lädt Profil on mount

### Docs

- [x] `README.md` — Sprint-4-Migrationsschritt dokumentiert
- [x] `docs/PROJECT_STATUS.md` — Sprint 4 dokumentiert
- [x] `docs/DECISIONS.md` — Auto-Create-Profil, Partial-Update, medizinische Freiwilligkeit dokumentiert
- [x] `docs/ROADMAP.md` — Sprints 1–4 als abgeschlossen markiert

### Bewusst nicht umgesetzt (Sprint 4)

- Kein echtes Fahrzeugmatching / Fahrtenbuchung
- Kein Vehicle- oder Driver-Stammdatenmodell (folgt Sprint 5+)
- Medizinische Felder sind freiwillig — kein Pflichtfeld, kein serverseitiger Zwang
- Kein Datumsfeld `date_of_birth` in der UI sichtbar (Datenfeld im Modell vorhanden, aber Sprint 4 setzt es nicht ein)
- Kein Rollenwechsel in der UI — Rollensperren folgen Sprint 6

---

---

## Sprint 5 — Fahrdienst, Fahrzeuge und Fahrerprofile ✅

**Abgeschlossen:** 2026-07-10

### Backend

- [x] `app/models/organization.py` — 8 optionale Felder ergänzt: `address_line`, `postal_code`, `city`, `country`, `dispatch_phone`, `dispatch_email`, `operating_area_notes`, `notes`
- [x] `app/models/vehicle.py` — `VehicleType`-Enum (7 Typen), `Vehicle`-Modell (24 Felder: Kapazität, 8 Ausstattungsmerkmale, Betrieb)
- [x] `app/models/driver_profile.py` — `DriverProfile`-Modell (20 Felder: 8 Qualifikationsflags, Betrieb)
- [x] `app/db/base.py` — `vehicle` + `driver_profile` Imports ergänzt
- [x] `app/schemas/vehicle.py` — `VehicleBase`, `VehicleCreate`, `VehicleUpdate`, `VehiclePublic`
- [x] `app/schemas/driver_profile.py` — `DriverProfileBase`, `DriverProfileCreate`, `DriverProfileUpdate`, `DriverProfilePublic`
- [x] `app/crud/crud_vehicle.py` — `get_all`, `get_by_org`, `get_by_id`, `create`, `update`, `soft_delete`
- [x] `app/crud/crud_driver_profile.py` — `get_all`, `get_by_org`, `get_by_id`, `get_by_user_id`, `create`, `update`, `soft_delete`
- [x] `app/crud/__init__.py` — alle CRUDs importiert
- [x] `app/api/v1/endpoints/vehicles.py` — 5 Endpunkte + GET /options (Typen + Ausstattungsoptionen)
- [x] `app/api/v1/endpoints/drivers.py` — 5 Endpunkte + GET /options (Qualifikationsliste)
- [x] `app/api/v1/router.py` — `vehicles`- und `drivers`-Router eingebunden
- [x] Alembic-Migration `20260710_0002-c3d4e5f6a1b2_sprint5_vehicle_driver.py`
- [x] `app/scripts/seed_demo_data.py` — 3 Demo-Fahrzeuge + 1 Fahrerprofil für WB Fahrdienste GmbH

### Frontend

- [x] `src/types/index.ts` — `VehicleTypeName`, `VEHICLE_TYPE_LABELS`, `Vehicle`, `VehicleUpdate`, `VehicleCreate`, `DriverProfile`, `DriverProfileUpdate`, `DriverProfileCreate` ergänzt
- [x] `src/api/vehicle.ts` — `getVehicles`, `getVehicle`, `createVehicle`, `updateVehicle`, `deactivateVehicle`, `getVehicleOptions`
- [x] `src/api/driverProfile.ts` — `getDrivers`, `getDriver`, `createDriver`, `updateDriver`, `deactivateDriver`, `getDriverOptions`
- [x] `src/stores/vehicle.ts` — Pinia Store (`vehicles`, `loading`, `saving`, `activeCount`, `totalCount`, `load`, `create`, `update`, `deactivate`)
- [x] `src/stores/driverProfile.ts` — Pinia Store analog
- [x] `src/views/VehiclesView.vue` — Accessibility-first (Liste + Formular inline), Ausstattungs-Toggle-Karten, Soft-Delete, ARIA-Rollen
- [x] `src/views/DriversView.vue` — Accessibility-first, Qualifikations-Toggle-Karten, Avatar-Initialen, Qualifikations-Badges
- [x] `src/router/index.ts` — `/vehicles` und `/drivers` unter PortalLayout ergänzt
- [x] `src/components/layout/AppSidebar.vue` — „Fahrzeuge" und „Fahrer" als aktive Routen (kein „bald"-Chip mehr)
- [x] `src/views/dashboard/DashboardView.vue` — „Flotte & Fahrer"-Karte mit Zählern + Links

### Docs

- [x] `docs/PROJECT_STATUS.md` — Sprint 5 dokumentiert
- [x] `docs/ROADMAP.md` — Sprint 5 als abgeschlossen, Sprints 6+7 umnummeriert
- [x] `docs/DECISIONS.md` — Fahrzeugausstattung als Matching-Grundlage, Qualifikationen, Soft-Delete dokumentiert

### Bewusst nicht umgesetzt (Sprint 5)

- Kein Fahrtenbuchungs-Modell (`Ride`)
- Kein echtes Matching
- Keine Tourenoptimierung
- Keine GPS-Position oder Live-Verfügbarkeit
- Vollständige Mandantentrennung (RBAC) folgt Sprint 7
- Kein Dokumentenupload (Führerschein, Zertifikate)

---

## Sprint 10 — Fahrer-Schichtstart & Fahrzeugwahl ✅

**Abgeschlossen:** 2026-07-16

### Backend

- [x] `backend/app/models/driver_shift.py` — `ShiftStatus` (active/paused/ended), `DriverShift`
- [x] `backend/app/models/driver_profile.py` — `default_vehicle_id` (nullable FK → vehicles.id)
- [x] `backend/app/db/base.py` — Import `driver_shift` für Alembic
- [x] `backend/alembic/versions/20260716_0008-c4d5e6f7a8b9_sprint10_driver_shift.py` — Tabelle `driver_shifts`
- [x] `backend/alembic/versions/20260716_0009-d5e6f7a8b9c0_sprint10b_driver_profile_default_vehicle.py` — Spalte `default_vehicle_id`
- [x] `backend/app/schemas/driver_shift.py` — `VehicleBrief`, `DriverShiftPublic`, `DriverShiftWithVehicle`, `DriverShiftStartRequest`, `DriverProfileBrief`, `DriverDashboardContext`
- [x] `backend/app/crud/crud_driver_shift.py` — `start_shift`, `end_shift`, `pause_shift`, `resume_shift`, `find_vehicles_by_license_plate`
- [x] `backend/app/api/v1/endpoints/driver.py` — 7 Endpoints: `GET /me`, `GET /shift/current`, `POST /shift/start|end|pause|resume`, `GET /vehicles/search`, `GET /assignments`; Schichtstart: vehicle_id > license_plate > default_vehicle_id
- [x] `backend/app/api/v1/router.py` — `driver.router` registriert
- [x] `backend/app/api/v1/endpoints/assistant.py` — `_DRIVER_CAPABILITIES` auf Sprint 10 aktualisiert
- [x] `backend/app/scripts/seed_demo_data.py` — Onboarding-Backfill (Staff-Rollen) + default_vehicle_id für driver@access.test (AM-BUS-1)

### Tests

- [x] `backend/tests/api/test_sprint10_driver_shift.py` — **20/20 passed**: /driver/me, default vehicle, start mit Standardfahrzeug, duplicate block, pause/resume, end active/paused, assignments

### Frontend

- [x] `frontend/src/types/index.ts` — `ShiftStatus`, `SHIFT_STATUS_LABELS`, `VehicleBrief`, `DriverShift`, `DriverShiftWithVehicle`, `DriverShiftStartRequest`, `DriverProfileBrief`, `DriverDashboardContext`
- [x] `frontend/src/api/driver.ts` — `getDriverContext`, `startShift`, `endShift`, `pauseShift`, `resumeShift`, `searchVehicles`, `getDriverAssignments`
- [x] `frontend/src/views/DriverDashboardView.vue` — **Mobile-first, große Buttons (56 px+)**:
  - Große Statuskarte (idle / active / paused) mit Status-Icon
  - Szenario A: Standardfahrzeug direkt + ein Button „Schicht mit diesem Fahrzeug beginnen"
  - Szenario B: Kennzeichen-Suche → Fahrzeugliste → „Schicht beginnen"
  - Aktive Schicht: „Pause beginnen" / „Pause beenden" / „Schicht beenden" (mit Bestätigungs-Modal)
  - Abschnitt „Linienfahrten" (Platzhalter) + „Spontane Fahrten" (aus assignments)
- [x] `frontend/src/router/index.ts` — Route `/driver`
- [x] `frontend/src/components/layout/AppSidebar.vue` — Fahrer-Nav: „Meine Schicht" + „Meine Aufträge"

### Docs

- [x] `docs/ROADMAP.md`, `docs/SOURCE_OF_TRUTH.md`, `docs/PROJECT_STATUS.md`
- [x] `docs/Product/APP_CONCEPT.md` — Fahrer-Abschnitt aktualisiert
- [x] `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md` — implementierter Stand Sprint 10
- [x] `docs/Product/DESIGN_AND_ACCESSIBILITY_GUIDE.md` — Abschnitt 5a Fahreroberfläche ergänzt

### Checks

- [x] TypeScript-Check (`vue-tsc --noEmit`): keine Fehler
- [x] Vite-Build: ✅ erfolgreich
- [x] Backend pytest: 20/20 passed

### Bewusst nicht umgesetzt (Sprint 10)

- Kein STT / Spracheingabe für Fahrer-App (voice_mode: "voice_later")
- Kein Live-GPS
- Keine Push-Notifications
- Keine Lohnabrechnung / Zeiterfassung
- Kein Tourenoptimierer / Linienverkehr-Datenmodell
- Keine Statusbuttons „Fahrgast zugestiegen / ausgestiegen" (Sprint 11)
- Kein OpenAI/KI

---

## Sprint FAHRANDO-1 — Fahrando Coming-Soon, Testzugang & Platform-Admin-Benutzerverwaltung ✅

**Abgeschlossen:** 2026-07-16

### Backend

- [x] `backend/app/scripts/ensure_platform_admin.py` — Idempotentes Bootstrap-Script via 4 Env-Vars; Passwort nie in Ausgabe, nie in Dateien
- [x] `backend/app/schemas/platform_admin.py` — `PlatformAdminUserPublic`, `PlatformAdminUserCreate`, `PlatformAdminUserUpdate`, `PlatformAdminPasswordReset`
- [x] `backend/app/crud/crud_platform_admin.py` — `list_users` (ilike-Suche), `create_user`, `update_user` (Self-Protect), `reset_password`, `set_active`, `_to_public` (inkl. Org-Name), `_upsert_membership`
- [x] `backend/app/api/deps.py` — `require_platform_admin`-Dependency (403 für alle anderen Rollen)
- [x] `backend/app/api/v1/endpoints/platform_admin.py` — 7 Endpoints (GET/POST users, GET/PATCH user, reset-password, activate, deactivate)
- [x] `backend/app/api/v1/router.py` — `platform_admin.router` registriert

### Tests

- [x] `backend/tests/api/test_platform_admin.py` — **54 Tests, alle passed**:
  - TestBootstrapScript (6), TestAccessControl (20, parametriert), TestUnauthenticated (2)
  - TestListUsers (5), TestCreateUser (6), TestUpdateUser (4)
  - TestActivation (4), TestPasswordReset (5), TestRegressionAuth (2)
- [x] `backend/tests/conftest.py` — `admin_token`, `admin_headers`, `driver_token`, `driver_headers` ergänzt

### Frontend

- [x] `frontend/src/components/branding/FahrandoLogo.vue` — SVG-Komponente, Rollstuhl + Bewegungslinien, Gelb, Varianten small/default/large, aria-hidden auf SVG
- [x] `frontend/src/views/LandingView.vue` — **Fahrando Coming-Soon-Seite** (standalone, kein PublicLayout): Zwei-Spalten-Layout Desktop, Einspaltung Mobile; Login-Formular mit echtem JWT-Auth, eingeloggt: Dashboard-Button + Logout; Footer mit Impressum/Datenschutz
- [x] `frontend/src/views/platform_admin/PlatformAdminUsersView.vue` — Benutzerverwaltung für Platform-Admin: Tabelle mit Avatar/Rolle/Status, Suche/Filter (Rolle/Aktivstatus), 4 Modals (Anlegen, Bearbeiten, Passwort-Reset, Deaktivierung via Tabellen-Button), Toast-Benachrichtigungen
- [x] `frontend/src/views/ImpressumView.vue` — Placeholder mit "Diese Seite wird derzeit vorbereitet."
- [x] `frontend/src/views/DatenschutzView.vue` — Placeholder analog
- [x] `frontend/src/api/platformAdmin.ts` — API-Client: `listUsers`, `getUser`, `createUser`, `updateUser`, `resetPassword`, `activateUser`, `deactivateUser`
- [x] `frontend/src/router/index.ts` — `/` standalone, `/login` → redirect `/`, `/impressum`, `/datenschutz`, `/platform-admin/users` (requiresPlatformAdmin), Logout → `/`, 404 → `/`
- [x] `frontend/src/components/layout/AppSidebar.vue` — `platform_admin` aus DISPO_ROLES entfernt; eigene "Plattform-Admin"-Sektion (gelber Label); Logout → `/`

### Docs

- [x] `docs/SOURCE_OF_TRUTH.md` — Sprint-Stand, Fahrando-Brand-Entscheidungen, Passwort-Sicherheitsregel, DEPLOYMENT_FAHRANDO_TEST.md als Referenz
- [x] `docs/ROADMAP.md` — Sprint FAHRANDO-1 als abgeschlossen, Sprint 11 vorbereitet
- [x] `docs/PROJECT_STATUS.md` — dieser Abschnitt
- [x] `docs/DEPLOYMENT_FAHRANDO_TEST.md` — Deployment-Anleitung für Fahrando-Testzugang (neu)

### Checks

- [x] TypeScript-Check (`vue-tsc --noEmit`): keine Fehler
- [x] Vite-Build: ✅ erfolgreich
- [x] Backend pytest: 54/54 neue Tests passed (alle 100+ Gesamttests passed)

### Sicherheitsregeln (unverhandelbar)

- Kein Bootstrap-Passwort in Dateien, Logs, Tests, Seed-Daten, Migrationen, Doku oder API-Responses
- Nur der bcrypt-Hash wird in der DB gespeichert
- Kein zweites JWT-System, kein zweites Auth-System — Login auf `/` nutzt dasselbe System wie das Portal
- Platform-Admin-Seiten: 403 für alle Nicht-Platform-Admins, 401 ohne Token

### Bewusst nicht umgesetzt (Sprint FAHRANDO-1)

- Keine Impressum/Datenschutz-Inhalte (folgen vor Launch)
- Keine Organisations-Dropdown im Create-Modal (Org-IDs noch manuell via API/Bootstrap)
- Kein E-Mail-Versand (Willkommens-Mail, Passwort-Reset-Mail)
- Kein Audit-Log für Admin-Aktionen

---

---

## Sprint FAHRANDO-2 — Gate-Schutzseite & Website-Testzugänge ✅

**Abgeschlossen:** 2026-07-16

### Backend

- [x] `backend/app/models/preview_access.py` — `PreviewAccessUser`-Modell (email, password_hash, first_name, last_name, is_active, note, last_used_at, created_at, updated_at)
- [x] `backend/app/db/base.py` — `preview_access`-Import für Alembic ergänzt
- [x] `backend/alembic/versions/20260716_0010-e6f7a8b9c0d1_preview_access_users.py` — Tabelle `preview_access_users`, Unique-Index auf email
- [x] `backend/app/schemas/preview_access.py` — `PublicGateLoginRequest`, `PreviewAccessUserPublic` (ohne password_hash), `PreviewAccessUserCreate` (email normalisiert, Passwort min. 10 Zeichen), `PreviewAccessUserUpdate`, `PreviewAccessPasswordReset`
- [x] `backend/app/crud/crud_preview_access.py` — `get_by_email`, `get_by_id`, `list_users` (Suche/Aktivfilter), `create_user`, `update_user`, `reset_password`, `set_active`, `validate_login` (aktualisiert last_used_at)
- [x] `backend/app/api/v1/endpoints/public_gate.py` — `POST /public/test-access/login` DB-basiert (kein Env-Var), 401 bei ungültigen Daten
- [x] `backend/app/api/v1/endpoints/preview_access_admin.py` — 7 Endpoints unter `/platform-admin/test-access-users`: GET (Liste), POST (Anlegen, 409 bei Duplikat), GET /{id}, PATCH /{id}, POST /{id}/activate, POST /{id}/deactivate, POST /{id}/reset-password (400 bei Mismatch); alle `require_platform_admin`
- [x] `backend/app/api/v1/router.py` — `preview_access_admin.router` + `public_gate.router` registriert

### Tests

- [x] `backend/tests/api/test_preview_access.py` — **46 Tests, alle passed**:
  - TestAccessControl (11), TestListUsers (4, inkl. kein password_hash in Response)
  - TestCreateUser (8, inkl. E-Mail-Normalisierung, 409 Duplikat, 422 kurzes Passwort)
  - TestPublicGateLogin (6, inkl. last_used_at-Update, gleiche 401 für alle Fehler)
  - TestActivation (6), TestPasswordReset (7), TestRegression (4, App-Login unverändert)

### Frontend

- [x] `frontend/src/api/previewAccess.ts` — `listPreviewUsers`, `createPreviewUser`, `getPreviewUser`, `updatePreviewUser`, `activatePreviewUser`, `deactivatePreviewUser`, `resetPreviewUserPassword`
- [x] `frontend/src/views/platform_admin/PlatformAdminTestAccessView.vue` — CRUD-Tabelle mit Suche/Aktivfilter, 3 Modals (Anlegen, Bearbeiten, Passwort-Reset), Toast-Benachrichtigungen, Hinweis: „kein App-Benutzerkonto"
- [x] `frontend/src/views/GateView.vue` — Neubau: Zwei-Spalten-Layout (schwarz/gelb), Fahrando-Logo, H1 „Hier entsteht etwas Großes.", 3 horizontale Nutzen-Punkte, Hinweis-Box, Login-Card (Shield-Icon, E-Mail/Passwort, Passwort-Sichtbarkeit-Toggle, gelber Button), dekorative SVG-Ellipsen. Unlock per `sessionStorage.setItem('fahrando_preview_unlocked', '1')`.
- [x] `frontend/public/Logo1.png` — Fahrando-Marken-Logo (RGBA-PNG, transparent) als statisches Asset
- [x] `frontend/src/router/index.ts` — `/gate` öffentlich (`meta: { public: true }`), `/` erfordert `fahrando_preview_unlocked` in sessionStorage (Gate-Guard), `/login` → LoginView (App-Login, unverändert)
- [x] `frontend/src/components/layout/AppSidebar.vue` — „Website-Testzugänge" unter Plattform-Admin-Sektion ergänzt
- [x] `frontend/vite.config.ts` — **Proxy-Eintrag** `/api` → `http://localhost:8010` (behebt fehlende API-Erreichbarkeit im Vite Dev-Server für `fetch`-basierte API-Module)
- [x] `.env.example` — `TEST_ACCESS_CODE`-Variable entfernt, Hinweis auf DB-basierten Ansatz

### Checks

- [x] TypeScript-Check (`vue-tsc --noEmit`): keine Fehler
- [x] Vite-Build: ✅ erfolgreich
- [x] Backend pytest: 46/46 neue Tests passed (alle 192+ Gesamttests passed)
- [x] Vite-Proxy verifiziert: `GET http://localhost:5180/api/v1/health → 200 OK`

### Sicherheitsregeln (unverhandelbar)

- `PreviewAccessUser` ist vollständig getrennt von der `User`-Tabelle — kein JWT, kein App-Login
- `password_hash` nie in API-Responses
- Login-Fehler geben immer dieselbe 401-Meldung zurück (kein Enumeration-Angriff)
- Gate-Unlock nur per `sessionStorage` (`fahrando_preview_unlocked=1`) — kein Token, kein Cookie
- Kein Passwort in Dateien, Logs, Tests, Doku oder Abschlussbericht

### Bewusst nicht umgesetzt (Sprint FAHRANDO-2)

- Kein E-Mail-Versand bei Zugangserstellung
- Kein Ablaufdatum / zeitlich begrenzte Testzugänge (folgt bei Bedarf)
- Kein Audit-Log für Gate-Logins (last_used_at reicht für MVP)
- Keine Rate-Limiting auf dem Gate-Endpoint (folgt vor Produktivbetrieb)

---

## Sprint FAHRANDO-PREVIEW-GATE-DIREKTLINK-SCHUTZ-1 — Gate-Direktlink-Schutz ✅

**Abgeschlossen:** 2026-07-16

### Problem

Der Gate-Guard prüfte ausschließlich `to.path === '/'`. Direktlinks zu beliebigen öffentlichen Website-Routen umgingen das Gate vollständig.

### Umgesetzt

- [x] `frontend/src/router/index.ts`:
  - `/`-Route: `meta: { requiresPreviewAccess: true }` ergänzt
  - Gate-Guard: Prüft `to.matched.some(r => r.meta.requiresPreviewAccess)` statt `to.path === '/'`
  - Redirect zu `/gate?redirect={to.fullPath}` bei nicht freigeschalteten Gate-Routen
  - Bereits freigeschaltet + auf `/gate`: validierter Redirect zum `?redirect`-Parameter (Open-Redirect-Schutz: nur interne `/`-Pfade erlaubt)
  - sessionStorage-Key: `fahrando_unlocked` → `fahrando_preview_unlocked`
- [x] `frontend/src/views/GateView.vue`:
  - `useRoute` importiert
  - Nach erfolgreichem Login: liest `route.query.redirect`, validiert (muss mit `/` beginnen, kein `//`), leitet dorthin weiter (Fallback: `/`)
  - sessionStorage-Key: `fahrando_unlocked` → `fahrando_preview_unlocked`
- [x] `docs/DEPLOYMENT_FAHRANDO_TEST.md` — Abschnitt 17 und 18 auf neuen Key + Direktlink-Verhalten aktualisiert

### Sicherheitsregeln

- Open-Redirect-Schutz: Redirect-Parameter wird validiert (`startsWith('/') && !startsWith('//')`)
- `/impressum` und `/datenschutz` bleiben ohne Gate-Freigabe zugänglich
- App-Routen (`/dashboard`, `/login` usw.) unterliegen ausschließlich dem App-Auth-Guard, nie dem Gate

### Checks

- [x] TypeScript-Check (`vue-tsc --noEmit`): keine Fehler
- [x] Vite-Build: ✅ erfolgreich

### Bewusst nicht umgesetzt

- Kein serverseitiger Redirect-State — ausschließlich Query-Parameter (stateless, kein Session-Overhead)
- Kein Ablaufdatum für den Gate-Unlock (sessionStorage endet beim Tab-Schließen)

---

## Sprint FAHRANDO-DEPLOYMENT-1 — Railway-Deployment & Production-Build ✅

**Abgeschlossen:** 2026-07-20

### Backend (Railway)

- [x] `railway.json` + `Procfile` für Nixpacks-Deployment auf Root-Ebene
- [x] `requirements.txt` auf Root-Ebene für Nixpacks (Backend-Abhängigkeiten)
- [x] Railway PostgreSQL als `DATABASE_URL`-Umgebungsvariable in Railway-Dashboard
- [x] `alembic upgrade head` auf Railway-Datenbank ausgeführt
- [x] `seed_demo_data` auf Railway-Datenbank ausgeführt
- [x] `ALLOWED_ORIGINS=https://fahrando.com,https://www.fahrando.com` in Railway-Umgebungsvariablen gesetzt
- [x] CORS-Fehler behoben: Frontend auf fahrando.com kann Railway API erreichen

### Frontend (Production-Build & Webspace)

- [x] `frontend/.env.production` mit `VITE_API_BASE_URL=https://fahrando-api-production.up.railway.app/api/v1` angelegt
- [x] `frontend/.env.production` in `.gitignore` eingetragen (`frontend/.env.production`)
- [x] **API-Base-Fix:** alle Frontend-API-Aufrufe auf `VITE_API_BASE_URL` umgestellt:
  - `frontend/src/views/GateView.vue` — Gate-Login-Request nutzte relativen Pfad `/api/v1/public/test-access/login`
  - `frontend/src/api/previewAccess.ts` — `BASE` + `new URL(BASE, window.location.origin)` → absolut
  - `frontend/src/api/platformAdmin.ts` — `BASE` + `new URL(BASE + '/users', window.location.origin)` → absolut
- [x] Production-Build (`npm run build`) mit `.env.production` erfolgreich
- [x] `localhost:8010` nicht im dist-Build vorhanden, Railway-URL korrekt eingebaut
- [x] `deploy/fahrando-webspace-upload/` als Upload-Staging-Ordner (nicht committed, gitignored)
- [x] `deploy/fahrando-webspace-upload/` enthält: `index.html`, `assets/`, `Logo1.png`, `.htaccess`
- [x] Upload via FileZilla auf fahrando.com Webspace ausgeführt

### Verifikation online

- [x] App-Login `https://fahrando.com/login` → Gate erscheint (da noch kein Gate-Unlock)
- [x] Railway Backend antwortet auf `https://fahrando-api-production.up.railway.app/api/v1/health`
- [x] Website-Testzugänge (Platform-Admin) laden über Railway API
- [x] Benutzerverwaltung (Platform-Admin) lädt über Railway API

### Relevante Commits

- `a7894cc` chore: prepare backend for Railway deployment
- `e2da4f9` chore: add root-level Railway config for monorepo deployment
- `7bc8579` chore: use python module pip in Railway build
- `d020192` fix: let Nixpacks manage Python env via root requirements.txt
- `be6c08e` fix: route frontend API calls through configured base URL

### Checks

- [x] TypeScript-Check (`vue-tsc --noEmit`): keine Fehler
- [x] Vite-Build: ✅ erfolgreich
- [x] `localhost:8010` nicht im dist vorhanden
- [x] Railway-URL im dist vorhanden

### Sicherheitsregeln

- `DATABASE_URL` und `SECRET_KEY` nur in Railway-Umgebungsvariablen — nicht in Dateien, Logs oder Doku
- `frontend/.env.production` nicht committed — enthält nur öffentliche API-Base-URL (kein Secret)
- `deploy/`-Ordner nicht committed — enthält fertigen Upload-Build

### Bewusst nicht umgesetzt

- Kein Railway-CLI-Deployment-Script (manuell über Railway-Dashboard)
- Kein automatisches CI/CD (manueller Build + FileZilla-Upload)
- Keine SSL/TLS-Konfiguration auf Webspace (liegt bei united-domains)

---

## Sprint FAHRANDO-GATE-PROTECTS-LOGIN-DIRECTLINK-1 — Gate schützt /login (Variante B) ✅

**Abgeschlossen:** 2026-07-20

### Problem

`/login` war mit `meta: { public: true }` markiert und umging den Gate-Check vollständig. Ein Direktlink zu `https://fahrando.com/login` zeigte den App-Login ohne Gate.

### Umgesetzt

- [x] `frontend/src/router/index.ts` — `beforeEach`-Guard komplett neu strukturiert:
  - **Variante B:** Alle Routen außer `/gate`, `/impressum`, `/datenschutz` erfordern Gate-Unlock
  - `/gate`: immer erreichbar; bei bereits freigeschaltetem Gate → Redirect zu `?redirect`-Ziel
  - `gateExempt: true` auf `/impressum` und `/datenschutz` — immer frei
  - Alle anderen Routen: `!unlocked` → `next({ path: '/gate', query: { redirect: to.fullPath } })`
  - Nach Gate-Unlock: `/login`-Branch prüft App-Auth; nicht-auth-pflichtige Routen (`/`) passieren direkt; `requiresAuth`-Routen → normale App-Auth-Prüfung
- [x] `/impressum` und `/datenschutz`: `meta: { public: true }` → `meta: { gateExempt: true }`
- [x] Open-Redirect-Schutz bleibt erhalten (`startsWith('/') && !startsWith('//')`)

### Verhalten nach Fix

| Route | ohne Gate-Unlock | nach Gate-Unlock |
|---|---|---|
| `/` | → Gate | → Landingpage |
| `/login` | → Gate | → App-Login |
| `/platform-admin` | → Gate | → App-Auth → App-Login |
| `/dashboard` | → Gate | → App-Auth → App-Login |
| `/impressum` | direkt | direkt |
| `/datenschutz` | direkt | direkt |

### Relevanter Commit

- `e937702` fix: require preview gate before app login direct links

### Checks

- [x] TypeScript-Check (`vue-tsc --noEmit`): keine Fehler
- [x] Vite-Build: ✅ erfolgreich

### Bewusst nicht umgesetzt

- Kein serverseitiger Gate-State — ausschließlich `sessionStorage` (stateless, kein Session-Overhead)
- Kein Ablaufdatum für Gate-Unlock (sessionStorage endet beim Tab-Schließen)

---

## Sprint 11 — Fahrt-Statusereignisse & Benachrichtigungseinstellungen ✅

**Abgeschlossen:** 2026-07-20

### Backend

- [x] `backend/app/models/ride_status_event.py` — `RideStatusEvent`-Modell (7 Ereignistypen: driver_on_way, driver_arrived, passenger_picked_up, ride_started, ride_completed, ride_cancelled, issue_reported)
- [x] `backend/app/models/notification_preference.py` — `PassengerNotificationPreference`-Modell (4 Kanal-Flags pro Ereignistyp)
- [x] `backend/app/models/transport_request.py` — `TransportRequestStatus` um `completed` erweitert
- [x] `backend/app/db/base.py` — neue Modelle registriert
- [x] `backend/app/schemas/ride_status_event.py` — `RideStatusEventCreate`, `RideStatusEventRead`
- [x] `backend/app/schemas/notification_preference.py` — `NotificationPreferenceRead`, `NotificationPreferenceUpsert`
- [x] `backend/app/crud/crud_ride_status_event.py` — `create_event` (mit Status-Spiegel auf TransportRequest), `list_events`
- [x] `backend/app/crud/crud_notification_preference.py` — `get_preferences`, `upsert_preference`
- [x] `backend/app/api/v1/endpoints/ride_status_events.py` — `POST /driver/transport-requests/{id}/status-events`, `GET /transport-requests/{id}/status-events`
- [x] `backend/app/api/v1/endpoints/notification_preferences.py` — `GET/PUT /passenger/notification-preferences`
- [x] `backend/app/api/v1/router.py` — neue Endpoints registriert
- [x] `backend/alembic/versions/20260720_0011-f7a8b9c0d1e2_sprint11_ride_status_events.py` — Migration für beide neuen Tabellen + completed-Enum-Wert

### Frontend

- [x] `frontend/src/types/index.ts` — `RideStatusEvent`, `RideStatusEventCreate`, `NotificationPreference`, `NotificationPreferenceUpsert`, Labels + Konstanten
- [x] `frontend/src/api/driver.ts` — `createRideStatusEvent`, `getRideStatusEvents`
- [x] `frontend/src/api/notificationPreferences.ts` — `getNotificationPreferences`, `saveNotificationPreferences`
- [x] `frontend/src/views/DriverDashboardView.vue` — Statusbuttons (5 + Problem melden mit optionaler Notiz) pro Auftragskarte; letzter Status + Uhrzeit; Ladezustand, Fehlermeldung
- [x] `frontend/src/views/MobilityProfileView.vue` — Neuer Abschnitt „Benachrichtigungseinstellungen" mit Ereignistabelle × 4 Kanäle; Speichern-Button; Erfolg-/Fehlermeldung

### Seed

- [x] Zugewiesene Demo-Fahrt für driver@access.test (Hauptstraße 5 → Vivantes Spandau, 2026-07-21, AM-BUS-1) + initiales status_event
- [x] 7 Benachrichtigungseinstellungen für passenger@access.test (alle Ereignisse, sinnvolle Defaults)
- [x] Idempotent

### Checks

- [x] `alembic upgrade head`: ✅
- [x] `pytest` (158/158 passed): ✅
- [x] TypeScript-Check (`vue-tsc --noEmit`): ✅ keine Fehler
- [x] Vite-Build (`npm run build`): ✅

### Sicherheitslogik

- Fahrer kann Statusereignisse nur für eigene zugewiesene Fahrten setzen (403 sonst)
- Fahrgast kann Statushistorie nur für eigene Fahrten lesen
- Notification Preferences: nur Fahrgäste (403 für alle anderen Rollen)
- Ungültige Statuswerte: 422

### Bewusst nicht umgesetzt (Sprint 11)

- Kein echtes SMS/E-Mail/Push-Versand — nur Einstellungsgrundlage
- Keine Statusreihenfolge-Validierung (Fahrer kann beliebige Reihenfolge setzen)
- Keine Live-GPS-Koordinaten (Sprint 12)

---

## Sprint 12A — Live-Status für Fahrgast & Vertrauensperson ✅

**Abgeschlossen:** 2026-07-20

### Ziel

Fahrgast sieht Fahrtstatus und -verlauf direkt in der App. Vertrauensperson erhält Backend-Zugriff auf Status-Events. Notification-Dispatch als Placeholder vorbereitet.

### Backend

- [x] `backend/app/api/v1/endpoints/ride_status_events.py` — `trusted_person`-Rolle in `GET /transport-requests/{id}/status-events` ergänzt; prüft aktive `TrustedRelationship` mit `can_view_rides=True`
- [x] `backend/app/services/notification_dispatch.py` — neuer Placeholder-Service `collect_notification_targets_for_status_event()`: liest `PassengerNotificationPreference`, gibt `NotificationTarget`-Deskriptoren zurück, kein echter Versand
- [x] `backend/tests/conftest.py` — Fixtures `trusted_person_token` + `trusted_person_headers` für `relative@access.test`
- [x] `backend/tests/api/test_sprint12a_live_status.py` — 7 neue Tests: Fahrgast liest eigenen Status, leere Histor → [], TrustedPerson mit Beziehung kann lesen, TrustedPerson ohne Beziehung → 403, TrustedPerson kann kein Status-Event erstellen → 403, Dispatch-Placeholder Unit-Tests

### Frontend

- [x] `frontend/src/api/rides.ts` — neues Modul `getRideStatusEvents()` für Fahrgast-/Vertrauenspersonen-Kontext (getrennt von `driver.ts`)
- [x] `frontend/src/views/TransportRequestView.vue`:
  - Live-Status-Abschnitt in Fahrgastkarten für `assigned`/`completed`/`cancelled`-Fahrten
  - Zeigt: aktueller Status (letztes Event), letzter Zeitstempel, Statusverlauf (ältere Events darunter), Notiz bei `issue_reported`
  - Leere Historie: verständlicher Hinweis statt Fehler
  - Polling: alle 20 Sekunden für zugewiesene Fahrten (onMounted → onUnmounted sauber gestoppt)
  - `completed`-Status-Badge (grün) + `statusIcon` ergänzt
  - `formatDateTime()` für Datum+Uhrzeit (de-DE)

### Checks

- [x] `alembic upgrade head`: ✅ (keine neue Migration — nur Logik-Änderungen)
- [x] `pytest` (156/165 passed, 9 skipped): ✅
- [x] TypeScript-Check (`vue-tsc --noEmit`): ✅
- [x] Vite-Build (`npm run build`): ✅ built in 2.63s

### Sicherheitslogik

- Vertrauensperson: Zugriff auf Status-Events nur wenn `TrustedRelationship.status = active` + `can_view_rides = True`
- Vertrauensperson kann keine Status-Events erstellen (403 — nur Fahrer)
- Fahrgast sieht nur eigene Fahrten (unverändert aus Sprint 11)

### Bewusst nicht umgesetzt (Sprint 12A)

- Keine dedizierte Vertrauenspersonen-View — Backend-Fundament gelegt; View folgt Sprint 12B
- Kein echter Notification-Dispatch — Placeholder liefert Zieldeskriptoren; Versand folgt Sprint 12B
- Kein GPS-Live-Tracking — folgt Sprint 12C
- Polling statt WebSocket — ausreichend für MVP; WebSocket kann optional in Sprint 12C ergänzt werden

---

## Sprint 12B — Spontane Fahrten: Karten-MVP, Standortfreigabe und Matching ✅

**Abgeschlossen:** 2026-07-20

### Ziel

Karten-MVP für den Spontanfahrten-Modus: Fahrgast gibt Standort frei, sieht Karte mit verfügbaren passenden Fahrzeugen in der Nähe. Noch keine finale Buchung.

### Kartenlösung

**Leaflet + OpenStreetMap-Tiles** (kein API-Key, kein kostenpflichtiger externer Dienst).
Hinweis: Für Produktionsbetrieb OSM-Nutzungsbedingungen, Datenschutz und ggf. eigener Tile-/Routing-Dienst prüfen.

### Backend

- [x] `backend/alembic/versions/20260720_0012-a8b9c0d1e2f3_sprint12b_driver_shift_location.py` — Migration: `current_latitude` + `current_longitude` (Float, nullable) zu `driver_shifts`
- [x] `backend/app/models/driver_shift.py` — neue Felder `current_latitude / current_longitude`
- [x] `backend/app/schemas/spontaneous_ride.py` — `SpontaneousRideMatchRequest` (Koordinaten-Validierung ±90/±180) + `SpontaneousRideMatchResult`
- [x] `backend/app/services/spontaneous_matching.py` — Haversine-Distanz, Capability-Check gegen MobilityProfile, Verfügbarkeits-Filter, Sortierung nach Entfernung, ETA `max(3, int(km/30*60))`
- [x] `backend/app/api/v1/endpoints/spontaneous_rides.py` — `POST /spontaneous-rides/matches`, Rollen-Guard (passenger/trusted_person/staff), kein sensitive Daten in Response
- [x] `backend/app/api/v1/router.py` — Endpoint registriert
- [x] `backend/app/scripts/seed_demo_data.py` — driver2@access.test ergänzt (Fahrerin 2, kein Rollstuhl), Schicht AM-VAN-1 aktiv (lat=52.525, lon=13.402), Schicht AM-CAR-1 pausiert (lat=52.510) als Filterfall

### Frontend

- [x] `frontend/package.json` — leaflet + @types/leaflet hinzugefügt
- [x] `frontend/src/types/index.ts` — `SpontaneousRideMatchRequest` + `SpontaneousRideMatchResult`
- [x] `frontend/src/api/spontaneous.ts` — `findSpontaneousMatches()`
- [x] `frontend/src/components/SpontaneousRideMap.vue` — Leaflet-Karte, Fahrgast-Marker, Fahrzeug-Marker mit Popup, Icon-Fix für Vite
- [x] `frontend/src/views/SpontaneousRideView.vue` — Gesamtflow: Idle → Locating → Geo-Error → Searching → Results; Textliste + Karte parallel; deaktivierter „Auswählen"-Button mit Hinweis auf Sprint 12C
- [x] `frontend/src/router/index.ts` — Route `/spontaneous-ride`
- [x] `frontend/src/views/dashboard/DashboardView.vue` — Kachel „Spontane Fahrt" (nur für passenger/trusted_person)

### Checks

- [x] `alembic upgrade head`: ✅ Migration `a8b9c0d1e2f3` angewendet
- [x] `pytest`: ✅ 169 passed, 9 skipped
- [x] TypeScript-Check (`vue-tsc --noEmit`): ✅
- [x] Vite-Build (`npm run build`): ✅ 404 Module transformiert, built in 3.48s

### Sicherheitslogik

- Fahrgast kann nur für sich selbst suchen (403 bei fremder `passenger_user_id`)
- Vertrauensperson nur für verknüpften Fahrgast mit aktiver Beziehung + `can_view_rides=True`
- Driver-Rolle wird abgewiesen (403)
- Response enthält weder Telefon noch E-Mail noch Kennzeichen des Fahrers

### Datenschutz

- Standort nur nach ausdrücklichem Klick — kein Hintergrundtracking
- Fahrzeugpositionen sind Demo-/Verfügbarkeitspositionen (kein Echtzeit-GPS)
- Keine dauerhafte Speicherung von Standortdaten in diesem Sprint

### Bewusst nicht umgesetzt (Sprint 12B)

- Keine echte Buchung — Button disabled mit Hinweis auf Sprint 12C
- Keine Fahrerannahme / -ablehnung
- Kein Echtzeit-GPS der Fahrzeuge (Demo-Positionen aus DriverShift)
- Keine externe kostenpflichtige Routing-API
- Kein echtes Routing (Haversine-Luftlinie)
- Keine SMS/E-Mail/Push-Benachrichtigungen

---

## Sprint 12C — Spontane Fahrten: Buchung & Fahrerannahme ✅

**Abgeschlossen:** 2026-07-20

### Ziel

Fahrgast bucht ein passendes Fahrzeug aus der Match-Liste. Fahrer nimmt die Anfrage an oder lehnt ab. Fahrzeug wird für die Dauer der offenen Anfrage reserviert.

### Backend

- [x] `backend/alembic/versions/20260720_0013-b9c0d1e2f3a4_sprint12c_spontaneous_booking.py` — Migration: `spontaneous_requested` + `driver_declined` zu `transportrequeststatus` Enum; 5 neue Spalten auf `transport_requests` (`is_spontaneous`, `pickup_latitude/longitude`, `destination_latitude/longitude`)
- [x] `backend/app/models/transport_request.py` — `TransportRequestStatus.spontaneous_requested / driver_declined` + 5 neue Felder
- [x] `backend/app/schemas/spontaneous_ride.py` — `SpontaneousRideBookRequest`, `SpontaneousRideBookResponse`, `SpontaneousRideRequestItem`
- [x] `backend/app/api/v1/endpoints/spontaneous_rides.py` — `POST /spontaneous-rides/book`: prüft aktive Schicht, blockiert Doppelbuchung (409), legt `TransportRequest` mit `status=spontaneous_requested` an
- [x] `backend/app/api/v1/endpoints/driver.py` — 3 neue Endpoints:
  - `GET /driver/spontaneous-ride-requests` — offene Anfragen für diesen Fahrer
  - `POST /driver/spontaneous-ride-requests/{id}/accept` — Status → `assigned`
  - `POST /driver/spontaneous-ride-requests/{id}/decline` — Status → `driver_declined`
- [x] `backend/app/services/spontaneous_matching.py` — `_BLOCKING_STATUSES` um `spontaneous_requested` erweitert (kein Doppelbuchen)

### Frontend

- [x] `frontend/src/types/index.ts` — `SpontaneousRideBookRequest`, `SpontaneousRideBookResponse`, `SpontaneousRideRequestItem`
- [x] `frontend/src/api/spontaneous.ts` — `bookSpontaneousRide()`
- [x] `frontend/src/api/driver.ts` — `getSpontaneousRideRequests()`, `acceptSpontaneousRideRequest()`, `declineSpontaneousRideRequest()`
- [x] `frontend/src/views/SpontaneousRideView.vue` — „Auswählen"-Button aktiv; Loading pro Fahrzeug; Phase `booked` mit Bestätigungsscreen (Fahrzeug, Fahrer, ETA); 409-Fehler sichtbar; Vorschau-Banner entfernt
- [x] `frontend/src/views/DriverDashboardView.vue` — neue Sektion „Spontane Fahrtanfragen"; Annehmen/Ablehnen-Buttons; nach Annahme erscheint Fahrt in regulären Aufträgen

### Checks

- [x] `alembic upgrade head`: ✅ Migration `b9c0d1e2f3a4` angewendet
- [x] `pytest`: ✅ 190 passed (12 neue Tests Sprint 12C)
- [x] TypeScript-Check (`vue-tsc --noEmit`): ✅
- [x] Seed: `python -m app.scripts.seed_demo_data` ausführen nach Migration (aktive Schicht wiederherstellen)

### Sicherheitslogik

- Fahrgast kann nur für sich selbst buchen (403 bei fremder `passenger_user_id`)
- Fahrer kann nur eigene Anfragen annehmen/ablehnen (403 sonst)
- Doppelbuchung des gleichen Fahrzeugs → 409
- Buchung nur bei aktiver Fahrerschicht mit genau diesem Fahrzeug → 409 wenn nicht

### Bewusst nicht umgesetzt (Sprint 12C)

- Kein echtes Live-Tracking nach Annahme (folgt 12D)
- Keine Zahlungs-/Abrechnungslogik
- Keine SMS/E-Mail/Push (Grundlage Sprint 11)
- Keine externe Routing-API
- Bestehende geplante Fahrten nicht verändert

---

## Sprint 12D — Spontane Fahrten: Live-Tracking Fahrer → Fahrgast ✅

**Abgeschlossen:** 2026-07-20

### Neue Endpunkte

- [x] `POST /api/v1/driver/location` — Fahrer sendet Schichtstandort (nur eigene aktive Schicht); optional `transport_request_id` für Fahrtvalidierung; 204 No Content; Datenschutz: kein Verlauf, nur letzter Punkt
- [x] `GET /api/v1/spontaneous-rides/{id}/tracking` — Fahrgast/Fahrer liest Tracking-Status; Zugriffskontrolle nach Rolle; `can_track: bool`; keine sensiblen Daten in Response

### Backend-Änderungen

- [x] `backend/app/schemas/spontaneous_ride.py` — `DriverLocationUpdate`, `SpontaneousRideTracking`
- [x] `backend/app/schemas/transport_request.py` — `TransportRequestListItem` + `is_spontaneous`, `pickup_latitude`, `pickup_longitude`
- [x] `backend/app/api/v1/endpoints/driver.py` — `POST /driver/location`
- [x] `backend/app/api/v1/endpoints/spontaneous_rides.py` — `GET /{id}/tracking` + `_TRACKING_STATUS_LABELS`
- [x] Keine neue Alembic-Migration (`DriverShift.current_latitude/longitude` aus Sprint 12B)

### Frontend-Änderungen

- [x] `frontend/src/types/index.ts` — `DriverLocationUpdate`, `SpontaneousRideTracking`, `TransportRequestListItem` erweitert
- [x] `frontend/src/api/driver.ts` — `updateDriverLocation()`
- [x] `frontend/src/api/spontaneous.ts` — `getTrackingStatus()`
- [x] `frontend/src/components/SpontaneousRideMap.vue` — Fahrer-Marker (🚗), `fitBounds`, optionale `driverLat/driverLon`-Props
- [x] `frontend/src/views/SpontaneousRideView.vue` — Tracking-Polling (15 Sek.) in Phase `booked`; Status-Badge; Karte mit Fahrerpunkt; Textliste (Fahrer, ETA, Entfernung, Zeitstempel); Cleanup on unmount
- [x] `frontend/src/views/DriverDashboardView.vue` — Standort-Teilen für spontane Fahrten; Geolocation nach Klick; Auto-Update 15 Sek.; Stopp-Button; Datenschutz-Hinweis; Cleanup on unmount

### Tests

- [x] `backend/tests/api/test_sprint12d_tracking.py` — 16 neue Tests (alle grün)
- [x] `backend/tests/api/test_sprint12c_spontaneous_booking.py` — Fixture um Ride-Bereinigung erweitert (verhindert DB-State-Pollution zwischen Läufen)
- [x] Gesamtsuite: **206 passed**, 0 failed
- [x] TypeScript-Check: ✅
- [x] `npm run build`: ✅ 404 Module, 793 kB, 5.10s
- [x] Alembic: ✅ (keine neue Migration)

### Datenschutzgrenzen (verbindlich)

- Fahrer-Standort NUR in `DriverShift.current_latitude/longitude` — kein Verlauf, kein Logging
- Tracking-Response: nur Anzeigename, kein Telefon, keine E-Mail, keine private Adresse
- Fahrgast sieht nur eigene Fahrt; Fahrer sieht nur eigene zugewiesene Fahrt
- Standortfreigabe nur nach explizitem Klick; kein Hintergrundtracking

### Bewusst nicht umgesetzt (Sprint 12D)

- Kein WebSocket (Polling 15 Sek. reicht für MVP)
- Keine externe Routing-API
- Kein dauerhafter Standortverlauf
- Keine Zahlungs-/Abrechnungslogik
- Vertrauensperson-Tracking (folgt Sprint 12E)

---

## Hotfix Sprint 12D-B — Abholort-Anzeige + Aktive-Fahrten-Navigation ✅

**Abgeschlossen:** 2026-07-20

### Problem 1: Fahrer-Dashboard zeigt "Abholadresse nicht angegeben"
Bei Spontanfahrten ist `pickup_address` immer `null` — GPS-Koordinaten (`pickup_latitude`/`pickup_longitude`) wurden ignoriert.

**Fix:** `DriverDashboardView.vue` — Assignments-Abschnitt zeigt jetzt "Aktueller Standort des Fahrgasts" + Koordinaten als Fallback.

### Problem 2: Fahrgast hatte keinen Navigationspunkt für aktive Fahrten
`/spontaneous-ride` war nur per direktem Link erreichbar; nach Seitenreload kein Wiederfinden.

**Fix:**
- `ActiveRidesView.vue` — neue View unter `/active-rides`; filtert `GET /transport-requests` nach aktiven Statuses client-seitig; spontane Fahrten zeigen Koordinaten + "Tracking öffnen"-Link; geplante Fahrten zeigen Adresse + Datum
- `AppSidebar.vue` — Fahrgast-Navigation enthält jetzt "Aktive Fahrten" (pi-route)
- `router/index.ts` — Route `/active-rides` im Portal registriert
- `SpontaneousRideView.vue` — Hinweis im Tracking-Bereich: "Diese Fahrt finden Sie auch unter Aktive Fahrten"

### Kein Backend-Aufwand
`GET /api/v1/transport-requests` liefert bereits alle Felder (`is_spontaneous`, `pickup_latitude`, `pickup_longitude`). Kein neues Datenbankschema.

---

## Hotfix Sprint 12F-A — Zieladresse bei spontanen Fahrten ✅

**Abgeschlossen:** 2026-07-21

### Problem
Sprint 12F hat gespeicherte Adressen eingeführt, aber nur als Abholadresse. Zieladresse fehlte komplett im Buchungsflow.

### Umgesetzt

**Backend (keine Migration — `destination_address` existierte bereits im Modell):**
- `backend/app/schemas/spontaneous_ride.py` — `SpontaneousRideBookRequest`, `SpontaneousRideRequestItem` und `SpontaneousRideTracking` um `destination_address: str | None` erweitert; `SpontaneousRideTracking` auch um `pickup_address`
- `backend/app/api/v1/endpoints/spontaneous_rides.py` — `book_spontaneous_ride`: speichert `destination_address` auf `TransportRequest`; `get_spontaneous_ride_tracking`: gibt `pickup_address` + `destination_address` zurück
- `backend/app/api/v1/endpoints/driver.py` — `_build_spontaneous_request_item`: gibt `destination_address` mit zurück

**Frontend:**
- `frontend/src/types/index.ts` — `SpontaneousRideBookRequest`, `SpontaneousRideRequestItem`, `SpontaneousRideTracking` um `destination_address` + `pickup_address` erweitert
- `frontend/src/views/SpontaneousRideView.vue`:
  - `destinationAddress ref` + `selectedSavedDestinationId ref` + Watcher
  - `destinationWarning` computed
  - `reset()` räumt destination-State auf
  - `bookRide()` sendet `destination_address`
  - Template: Abholadresse-Dropdown mit Label "Aktuellen Standort verwenden" als Default; Zieladresse-Dropdown + freies Textfeld (immer sichtbar); Button-Disabled wenn `destinationAddress` leer; Tracking-Karte zeigt Abhol- + Zieladresse

### Verhalten
- Abholadresse: Standard GPS/Reverse-Geocoding; gespeicherte Adresse optional wählbar; freier Text immer editierbar
- Zieladresse: gespeicherte Adresse optional wählbar; freies Textfeld immer sichtbar; Buchung ohne Zieladresse nicht möglich
- Fahrer sieht `destination_address` im Dashboard (war bereits vorbereitet)

### Tests / Checks
- 294 passed, 0 failed
- vue-tsc --noEmit: ✅
- npm run build: ✅
- git diff --check: EXIT:0

---

## Sprint 12G — Fahrer-Statusfluss & Fahrer-Dashboard aufräumen ✅

**Abgeschlossen:** 2026-07-21

### Ziel
Fahrer-Dashboard zeigt nur den jeweils nächsten logischen Statusbutton. Tracking-Label wird aus dem letzten RideStatusEvent befüllt. Statusereignisse nach Fahrtabschluss werden abgewiesen.

### Backend
- [x] `backend/app/api/v1/endpoints/ride_status_events.py` — 409 wenn `tr.status != assigned` (kein Event nach Abschluss)
- [x] `backend/app/api/v1/endpoints/spontaneous_rides.py` — `_RIDE_EVENT_LABELS` + letztes Event-Query in `get_spontaneous_ride_tracking()` → Label-Override
- [x] `backend/tests/api/test_sprint12g_driver_status_flow.py` — 15 Tests: Auth-Guards, voller Statusfluss driver_on_way→ride_completed, Tracking-Label-Verifikation, can_track=False nach Abschluss, 409 nach Abschluss

### Frontend
- [x] `frontend/src/views/DriverDashboardView.vue` — `nextActionFor()` zeigt nur nächste Aktion; grüne Abgeschlossen-Box statt Button; Button `.ride-status-btn--next` Akzentfarbe

### Checks
- 309 passed, 9 skipped
- vue-tsc --noEmit: ✅
- npm run build: ✅
- git diff --check: EXIT:0

---

## Sprint 12H — Fahrgast-Fahrtverlauf & Fahrtabschluss ✅

**Abgeschlossen:** 2026-07-21

### Ziel
Fahrgast sieht aktive und vergangene (abgeschlossene, stornierte) Fahrten in einer gemeinsamen Ansicht. Spontane Fahrten zeigen Abholadresse statt Koordinaten. Letztes Statusereignis erscheint als lesbares Label.

### Backend
- [x] `backend/app/schemas/transport_request.py` — `TransportRequestListItem` um `last_status_label: Optional[str] = None` erweitert
- [x] `backend/app/api/v1/endpoints/transport_requests.py` — `_RIDE_EVENT_LABELS` + Batch-Query letztes `RideStatusEvent` pro Fahrt in `_enrich_list_items()` (kein N+1); import `RideStatusEvent`, `RideStatusEventType`
- [x] `backend/tests/api/test_sprint12h_passenger_history.py` — 8 Tests: Unauthentifiziert 401, Fahrgast sieht abgeschlossene Spontanfahrt, `pickup_address` + `destination_address` gesetzt, `last_status_label = "Fahrt abgeschlossen"`, `last_status_label`-Feld in allen List-Items vorhanden, Status-Events lesbar für abgeschlossene Fahrt, Fahrer sieht keine Fahrgast-Fahrten

### Frontend
- [x] `frontend/src/types/index.ts` — `TransportRequestListItem` um `last_status_label?: string | null` erweitert
- [x] `frontend/src/views/ActiveRidesView.vue` — komplett überarbeitet zu **"Meine Fahrten"**:
  - Zwei Sektionen: "Aktive Fahrten" + "Vergangene Fahrten"
  - Spontane Fahrten: `pickup_address` bevorzugt (GPS-Koordinaten nur als Fallback)
  - `destination_address` bei spontanen Fahrten jetzt sichtbar
  - `last_status_label` in vergangenen Fahrten angezeigt
  - Neue Status-Badges: `--completed` (grün) + `--cancelled` (grau)
  - Status-Icons für completed (`pi-check-circle`) und cancelled/driver_declined (`pi-times-circle`)

### Keine Änderungen an
- Backend-Migrationsdateien (keine neue Migration nötig)
- Router (Route `/active-rides` existiert bereits)
- Sidebar (Navigation zu "Meine Fahrten" existiert bereits als "Aktive Fahrten")

### Checks
- 313 passed, 9 skipped
- vue-tsc --noEmit: ✅
- npm run build: ✅ (3.79s)
- git diff --check: EXIT:0

---

## Sprint 12I — Fahrer-Verfügbarkeit und parallele spontane Fahrten absichern ✅

**Abgeschlossen:** 2026-07-21

### Ziel
Fahrer mit aktiver spontaner Fahrt darf keine weitere Anfrage annehmen. Matching zeigt gebundene Fahrer nicht an. Nach Fahrtabschluss wird Fahrer sofort wieder verfügbar. Dashboard blendet offene Anfragen bei aktiver Fahrt aus.

### Backend
- [x] `backend/app/api/v1/endpoints/driver.py` — `_has_active_spontaneous_ride()` Hilfsfunktion; `get_spontaneous_ride_requests` gibt leere Liste zurück wenn Fahrer aktive Fahrt hat; `accept_spontaneous_ride_request` prüft vor Annahme auf aktive Fahrt → 409 "Sie haben bereits eine aktive Fahrt."
- [x] `backend/app/api/v1/endpoints/spontaneous_rides.py` — `book_spontaneous_ride` prüft ob Fahrerprofil bereits aktive spontane Fahrt hat → 409 "Dieser Fahrer hat bereits eine aktive Fahrt."
- [x] `backend/app/services/spontaneous_matching.py` — `find_matches` filtert Fahrprofile mit aktiver Fahrt (status=assigned, is_spontaneous=True) aus Matching-Ergebnissen
- [x] `backend/tests/api/test_sprint12i_driver_availability.py` — 11 Tests: freier Fahrer kann annehmen, aktiver Fahrer bekommt 409, keine offenen Anfragen bei aktiver Fahrt, Verfügbarkeit nach Abschluss, Buchungsendpoint blockt aktiven Fahrer, Matching exkludiert aktiven Fahrer, Ablehnen funktioniert weiter, Adressen im Response vorhanden

### Frontend
- [x] `frontend/src/views/DriverDashboardView.vue` — `hasActiveSpontaneousRide` computed (prüft assignments auf is_spontaneous + status=assigned); Spontane-Anfragen-Sektion zeigt Hinweismeldung statt Liste wenn Fahrer aktiv; `loadSpontaneousRequests()` wird nach ride_completed/ride_cancelled aufgerufen

### Keine Änderungen an
- Datenbankmodellen (keine Migration nötig — keine neuen Felder)
- Statuswerte (bestehende Werte genutzt: assigned, completed)
- Fahrgast-Buchungsflow
- Statusfluss 12G / Fahrgast-Historie 12H

---

## Sprint 12J — Fahrgast-Stornierung und klarer Status nach Fahrerablehnung ✅

**Abgeschlossen:** 2026-07-21

### Ziel
Fahrgast kann eine wartende oder angenommene spontane Fahrt selbst stornieren. Nach Fahrerablehnung bekommt der Fahrgast einen klaren Status und eine direkte Handlungsoption (neue Suche). Stornierte und abgelehnte Fahrten erscheinen korrekt in der Fahrthistorie.

### Backend
- [x] `backend/app/api/v1/endpoints/spontaneous_rides.py` — `POST /spontaneous-rides/{id}/cancel` Endpoint: nur Fahrgast, nur eigene spontane Fahrt; stornierbar bei `spontaneous_requested` oder `assigned` solange kein `passenger_picked_up`/`ride_started`/`ride_completed` Event existiert; setzt `status=cancelled` + `cancelled_at`; 409 bei abgeschlossener/bereits stornierter Fahrt; 403 bei fremder Fahrt; 404 bei nicht gefundener Fahrt
- [x] Konstanten `_CANCEL_ALLOWED_STATUSES` und `_CANCEL_BLOCKING_EVENT_TYPES` hinzugefügt
- [x] `backend/tests/api/test_sprint12j_spontaneous_cancel_decline.py` — 14 Tests: Stornierung requested, Stornierung assigned vor Pickup, Fremdstornierung 403, 404, 409 bei completed, 409 bei bereits storniert, Fahrer wieder verfügbar nach Storno, Fahrer sieht stornierte Anfrage nicht, Fahrer kann ablehnen, Fahrer sieht abgelehnte nicht mehr, Tracking liefert driver_declined, Stornierte in Fahrgast-Liste, Abgelehnte in Fahrgast-Liste, 409 nach passenger_picked_up

### Frontend
- [x] `frontend/src/api/spontaneous.ts` — `cancelSpontaneousRide(requestId)` Funktion
- [x] `frontend/src/views/SpontaneousRideView.vue` — Placeholder "Abbrechen (folgt später)" durch echten "Fahrt stornieren"-Button ersetzt; `cancelLoading`, `cancelError`, `canCancelRide` (computed, basiert auf Tracking-Status); Button sichtbar solange Status `spontaneous_requested` oder `assigned`; nach Stornierung greift bestehende Polling-Logik → zeigt `cancelled`-Status + "Erneut suchen"-Button; `cancelError` reset bei `reset()`
- [x] `frontend/src/types/index.ts` — Label `driver_declined` korrigiert: `'Fahrer abgelehnt'` → `'Vom Fahrer abgelehnt'`

### Keine Änderungen an
- Datenbankmodellen (keine Migration nötig — `cancelled_at` existierte bereits)
- Statuswerten (bestehende Werte: `cancelled`, `driver_declined`)
- Fahrerablehnung-Logik (existierte bereits, kein Code geändert)
- Fahrer-Dashboard (stornierte Fahrt verschwindet automatisch beim nächsten Poll nach 10s)
- 12I-Fahrerverfügbarkeit (nach Stornierung kein `status=assigned` mehr → Fahrer frei)
