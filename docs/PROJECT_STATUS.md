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

## Aktueller Sprint: Sprint 2 — Designbasis, Landingpage & Portal-Layout ✅

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
- [x] „Anmelden / Registrieren" führt zu `/dashboard` (kein echter Login)

**Backend**
- [x] Unverändert — Health-Endpoint bleibt, keine neuen Modelle

### Noch nicht umgesetzt (bewusst)

- Authentifizierung / JWT / Login
- Rollenmodell / RBAC
- Echte Daten: Benutzer, Organisationen, Fahrzeuge, Fahrer
- Fahrtenbuchung (Wizard)
- Serienfahrten
- Zahlungsintegration, Krankenkassenabrechnung
- Externe APIs / Live-GPS / Kartenintegration
- Native Mobile App

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

## Nächster Sprint: Sprint 3 — Auth, User & Stammdaten
