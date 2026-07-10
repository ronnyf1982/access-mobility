# Architekturentscheidungen

## Stack

**Frontend:** Vue 3 + TypeScript + Vite + PrimeVue 4 + Pinia + Vue Router + Axios

Bewusst gewählt statt Next.js/React, weil dieser Stack dem bestehenden Arbeitsmodus entspricht.
PrimeVue bietet barrierefreie, fertige Komponenten (passend zum Projektthema).

**Backend:** FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2 + PostgreSQL

FastAPI liefert automatische OpenAPI-Dokumentation (Swagger UI), Typvalidierung via Pydantic
und ist produktionsreif bei minimalem Boilerplate.

**Datenbank:** PostgreSQL

Relationale Integrität ist für Organisations-Hierarchien, Fahrtbuchungen und Rollenzuweisungen
zwingend. PostgreSQL ist produktionserprobt und wird lokal via Docker betrieben.

---

## Ports

| Dienst       | Port   | Begründung                                      |
|--------------|--------|-------------------------------------------------|
| FastAPI       | 8010   | Ports 8000 + 8001 durch anderes lokales Projekt belegt |
| Vue/Vite      | 5180   | Port 5173 durch anderes lokales Projekt belegt  |
| PostgreSQL    | 5440   | Standard 5432 vermieden, um Konflikte zu vermeiden |

---

## CORS

Nur `http://localhost:5180` ist als erlaubter Origin konfiguriert — auch im Dev kein Wildcard `*`.
Verhindert versehentliche Cross-Origin-Zugriffe aus anderen laufenden Projekten.

---

## Alembic-Strategie

- Modelle werden in `app/db/base.py` importiert, damit `target_metadata` alle Tabellen kennt.
- Migrationen werden immer committet (kein `.gitignore` auf `alembic/versions/`).
- Dateiname enthält Timestamp: leichter zu lesen als reine Hex-Revision-IDs.

---

## Design & Plattformstrategie

**Plattformtyp:** Responsive Webplattform — keine native App (bewusste MVP-Entscheidung).

Zwei Bereiche:
- **Öffentlicher Bereich:** Landingpage / Marketing (informiert über die Plattform)
- **Geschützter Bereich:** Web-App / Portal (Buchungen, Verwaltung, Dashboard)

**Designrichtung:**
- Grundfarbe: Schwarz / dunkles Anthrazit
- Akzentfarbe: Gelb — eingesetzt für Buttons, aktive Navigation, Icons, Status-Hervorhebungen und primäre Call-to-Actions
- Stil: modern, premium, hochwertig, klar, vertrauenswürdig, barrieregerecht, nicht überladen
- Orientierung: SaaS- / Mobilitätsplattform mit professioneller Landingpage und funktionalem Dashboard

**Begründung:** Anthrazit/Schwarz mit gelbem Akzent erzeugt visuelle Hierarchie und hohen Kontrast — unterstützt Barrierefreiheit (WCAG) und passt zur Zielgruppe (Fahrdienste, Organisationen, institutionelle Auftraggeber).

---

## Designreferenzen

Die visuellen Leitbilder liegen unter `docs/Design/` und wurden am 2026-07-05 freigegeben.
Sie sind keine 1:1-Pflichtvorlage, sondern definieren Farbgebung, Struktur und Qualitätsniveau.
UI wird ausschließlich mit Vue-Komponenten und CSS umgesetzt — keine Bilddateien als UI-Elemente.
Barrierefreiheit und Lesbarkeit haben Vorrang vor exakter Reproduktion der Referenz.

### `docs/Design/Landingpage.png` — Öffentlicher Bereich

**Aufbau:**
- Topnav: Logo links, Navigationslinks (Für Fahrgäste, Für Fahrdienste, Organisationen, Kontakt), CTA-Button rechts
- Hero: großer Headlineblock links, Fahrzeugbild rechts, gelber Subheadline-Akzent
- Feature-Iconleiste unterhalb Hero (3 Punkte: Zuverlässigkeit, Bedarfsanpassung, Flexibilität)
- Zielgruppen-Sektion: drei Kacheln nebeneinander (Fahrgäste / Fahrdienste / Organisationen)
- Vorteile-Sektion: Feature-Cards auf dunklem Hintergrund
- Footer: mehrspaltiges Link-Grid mit Logo

**Farben & Stil:**
- Hintergrund: nahezu schwarz (`#0d0d0d` / sehr dunkles Anthrazit)
- Headline-Akzent: leuchtendes Gelb (`~#F5C400` / `#FFD600`)
- Fließtext: helles Grau auf dunklem Grund
- Buttons primär: gelber Hintergrund, schwarzer Text
- Buttons sekundär: transparenter Hintergrund, gelber Rahmen/Text
- Karten/Sektionen: leicht aufgehelltes Dunkelgrau als Trennebene

### `docs/Design/dashboard.png` — Portal / geschützter Bereich

**Layout:**
- Linke Sidebar (fixiert): Logo oben, Navigationsitems mit Icon + Label, aktiver Eintrag gelb hinterlegt, Support-Block unten
- Topbar: globale Suche, Benachrichtigungs-Glocke, User-Avatar + Name rechts
- Hauptbereich: KPI-Kachelreihe oben, darunter Datentabelle (Anstehende Fahrten), rechts schmale Sidebar (Buchungsübersicht, Karte, Schnellaktionen)

**KPI-Kacheln (Beispiele aus Referenz):**
- Fahrten heute, Ausstehende Buchungen, Erfolgsquote, Plankapazität
- Kacheln: dunkle Card, gelbes Icon-Hintergrundfeld, weißer Zahlenwert, graues Label

**Datentabelle Anstehende Fahrten:**
- Spalten: Datum, Uhrzeit, Fahrgast, Strecke (Von → Nach), Fahrzeug, Fahrer, Status, Aktionen
- Status-Badges: Grün für "Bestätigt", Gelb für "In Bearbeitung"
- Zeilendesign: dunkler Hintergrund, dezente Trennlinien, kein starkes Grid

**Rechte Sidebar:**
- Buchungsübersicht (Donut-Chart-Bereich)
- Einsatzübersicht (Karten-/Kartenblock, dunkles Tile-Design)
- Schnellaktionen (gelbe Icon-Buttons)

**Sidebar-Navigation (Referenz):**
- Dashboard, Fahrten, Buchen, Fahrgäste, Fahrer, Fahrzeuge, Abrechnung, Einstellungen
- Aktiver Eintrag: gelb hinterlegt, schwarzer Text/Icon

**Farben & Stil (Dashboard):**
- Hintergrund gesamt: `~#111111` bis `#1a1a1a`
- Sidebar: `~#0f0f0f`, leicht dunkler als Hauptbereich
- Cards/Kacheln: `~#1e1e1e` mit subtiler Border
- Akzent aktiv/primär: Gelb (`~#FFD600`)
- Text primär: Weiß / helles Grau
- Text sekundär: mittleres Grau
- Erfolg/Grün: für positive Status-Badges
- Warnung/Gelb: für "In Bearbeitung"-Status

---

## Bewusst nicht umgesetzt (MVP-Scope)

- Auth/JWT: Sprint 2
- Rollenmodell: Sprint 2
- Echte Fachmodule: ab Sprint 2
- Serienfahrten (RRULE): Sprint 5
- Zahlungen, Abrechnung, externe APIs: außerhalb MVP
