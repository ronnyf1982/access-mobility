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

## Nächster Sprint: Sprint 6 — Fahrtenbuchung

- Modell: `Ride` mit Statusmaschine (`pending → confirmed → in_progress → completed → cancelled`)
- Buchungs-Wizard für Fahrgäste
- Disponenten-Zuteilung (Fahrzeug + Fahrer)
- Fahrtenliste (reale Daten statt Dummy)
- Fahrer-View: zugewiesene Aufträge + Statuswechsel
