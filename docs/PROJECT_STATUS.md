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

## Nächster Sprint: Sprint 4 — Stammdaten

- Modelle: `MobilityProfile`, `Vehicle`, `Driver`, `Qualification`
- CRUD-Endpoints für Stammdaten
- Pinia Stores + List-/Detail-Views
- Mobilitätsprofil: GET/PUT für eigenes Nutzerprofil
