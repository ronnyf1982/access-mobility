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

## Nächster Sprint: Sprint 11 — Fahrtstatus & Fahrer-App

- Backend: `RideStatusEvent`-Protokoll (driver_on_way / arrived_pickup / passenger_picked_up / arrived_destination / completed / delayed)
- Frontend: Statuswechsel-Buttons in Fahrer-App
- Benachrichtigungseinstellungen im Fahrgastprofil (Vertrauenspersonen, Kanäle, Ereignisse)
