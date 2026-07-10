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

## Accessibility-first — Produktgrundsatz (freigegeben 2026-07-10)

Access Mobility wird **accessibility-first** entwickelt. Barrierefreiheit ist kein
nachträgliches Feature, sondern Grundlage jeder Designentscheidung.

### Fahrgast-Oberfläche

Die Buchungsoberfläche für Fahrgäste folgt streng dem Prinzip: **weniger ist mehr**.

- Große, eindeutig beschriftete Buttons (min. 44×44 px Klickfläche)
- Jedes Icon hat einen sichtbaren Textlabel — keine Nur-Icon-Bedienung
- Maximal eine Entscheidung pro Schritt (Wizard-Prinzip)
- Klare, einfache Sprache — keine Fachjargon-Oberflächen
- Keine überladenen Verwaltungsansichten für Fahrgäste (Verwaltung liegt beim Portal)

### Barrierefreiheit (technisch)

- Screenreader-taugliche UI: ARIA-Labels, Rollen, Live-Regions für Statusänderungen
- Vollständige Tastaturbedienung (kein Element nur per Maus erreichbar)
- Sichtbare Fokuszustände auf allen interaktiven Elementen (bereits in Sprint 2 umgesetzt)
- Kontrastverhältnisse ≥ WCAG AA — Ziel WCAG AAA für kritische Bereiche
- Fehlermeldungen: verständlich formuliert, programmatisch mit Feldern verknüpft (`aria-describedby`), vorlesbar
- Keine zeitgesteuerten Interaktionen ohne Verlängerungsoption

### Sprachführung / Sprachmenü

- Wird als **späteres Kernfeature** vorgesehen (nicht im MVP)
- Fahrgäste sollen Fahrten per Spracheingabe buchen können
- Erfordert separat: Speech-to-Text-Integration, Sprachausgabe (TTS), vereinfachter Dialogflow

### Remote-Buchung

Angehörige, Betreuer:innen und Organisationen müssen Fahrten **für andere Personen aus der Ferne** buchen können.
- Im MVP: Organisations-Koordinator kann Fahrt für Org-Mitglied buchen
- Später: erweitertes Vertrauenspersonen-Modell (Person A darf für Person B buchen, mit expliziter Freigabe)
- Erfordert separates Berechtigungsmodell (außerhalb MVP)

### Mobilitätsbedarf (Datenmodell-Grundsatz)

Jeder Fahrgast hat ein **Mobilitätsprofil**. Die Auswahl des Bedarfs erfolgt über
eindeutige Icons mit Textlabel — niemals nur über Text-Dropdowns.

Definierte Mobilitätsbedarfe (vollständige Liste in `docs/Product/ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md`):
Rollstuhl · Elektrorollstuhl · Rollator · Krücken · blind/sehbehindert · gehörlos ·
Begleitperson · Einstiegshilfe · Rampe · Lift · Liegendtransport

### Fahrzeugausstattung (Datenmodell-Grundsatz)

Fahrdienste erfassen ihre Fahrzeuge mit **exakter Ausstattung** — Grundlage für das spätere Matching.

Definierte Ausstattungsmerkmale (vollständige Liste in `docs/Product/ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md`):
Rollstuhlplätze · Sitzplätze · Rampe · Lift · Fixiersystem · E-Rollstuhl geeignet ·
Begleitplatz · Tragestuhl · Liegendfahrt · Fahrerqualifikation

### Matching-Grundsatz

Das System darf nur Fahrten an Fahrzeuge und Fahrdienste vermitteln, die zum
Mobilitätsbedarf des Fahrgastes **vollständig passen**.

Geprüft werden müssen:
1. Fahrgastbedarf (Mobilitätsprofil)
2. Fahrzeugausstattung
3. Fahrerqualifikation

Automatisches Matching ist außerhalb des MVP — das Datenmodell wird jedoch so aufgebaut,
dass Matching später ohne Umstrukturierung implementiert werden kann.

---

## Auth & JWT (Sprint 3)

**Bibliotheken:** `bcrypt==4.2.1` + `PyJWT==2.9.0`

- `passlib` nicht verwendet — Abhängigkeit von `crypt`-Modul, das in Python 3.13 entfernt wurde.
- `bcrypt` direkt verwendet (kein Zwischenschicht-Wrapper).
- `PyJWT` statt `python-jose`: aktiver gepflegt, Python 3.13 kompatibel.

**Token-Ablauf:** 60 Minuten (konfigurierbar via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`).

**Kein Refresh-Token:** Im MVP nur ein kurzlebiger Access-Token. Abgelaufene Tokens → erneuter Login.  
Begründung: Refresh-Tokens erfordern serverseitigen Widerruf-Mechanismus (Datenbankeintrag oder Redis),
was den MVP-Scope deutlich erweitert. Ein 60-Minuten-Token ist für interne Nutzer (Dispatcher, Admins)
ausreichend. Im Produktivbetrieb (Phase 2): Keycloak/Auth0 mit Refresh-Tokens.

---

## Token-Speicherung im Frontend (MVP/Dev-only)

**Entscheidung:** JWT wird in `localStorage` gespeichert (Key: `am_token`).

**Risiko:** `localStorage` ist anfällig für XSS-Angriffe — im Gegensatz zu `httpOnly`-Cookies,
die für JavaScript unzugänglich sind.

**Begründung für MVP:**
- Kein SSR, kein Cookie-basiertes Auth-Backend — ein `httpOnly`-Cookie würde einen separaten
  Cookie-Endpoint und CSRF-Schutz erfordern.
- Interne Plattform: keine öffentlich zugänglichen Seiten im Portal-Bereich.
- Vite-Dev-Server: kein HTTPS, daher Secure-Cookies ohnehin nicht möglich.

**Vorgesehene Ablösung:** In der Produktivversion (Phase 2) wird Auth über Keycloak/Auth0 mit
`httpOnly`-Cookies oder Auth-Code-Flow mit PKCE ersetzt. Bis dahin gilt:
- Kein `eval()`, kein dynamisches Script-Loading
- Strikte Content-Security-Policy vorbereiten (Sprint 7+)

---

## Rollenmodell (Sprint 3)

8 Rollen als Python `str`-Enum — werden im JWT-Payload als `role`-Claim mitgeführt:

| Rolle                    | Beschreibung |
|--------------------------|--------------|
| `passenger`              | Fahrgast — bucht eigene Fahrten |
| `trusted_person`         | Angehöriger/Betreuer — kann für Fahrgäste buchen (Berechtigungsmodell: TrustedRelationship) |
| `organization_admin`     | Verwaltet Organisation, Mitglieder, Kontingente |
| `organization_coordinator` | Bucht Fahrten für Org-Mitglieder |
| `provider_admin`         | Verwaltet Fahrdienst, Fahrzeuge, Fahrer |
| `dispatcher`             | Disponiert Fahrten, weist Fahrzeuge/Fahrer zu |
| `driver`                 | Sieht und quittiert zugewiesene Aufträge |
| `platform_admin`         | Vollzugriff auf alle Plattformfunktionen |

Vollständiges RBAC (rollenbasierte UI-Einschränkungen) folgt in Sprint 6.
Im MVP: Rolle wird im Dashboard angezeigt — Zugriffsbeschränkungen kommen schrittweise.

---

## Bewusst nicht umgesetzt (MVP-Scope)

- Auth/JWT: Sprint 3
- Rollenmodell: Sprint 3
- Stammdaten (Org, Fahrzeug, Fahrer): Sprint 4
- Fahrtenbuchung: Sprint 5
- Serienfahrten (RRULE): Sprint 7
- Automatisches Matching: nach MVP
- Sprachführung / Sprachmenü: nach MVP
- Vertrauenspersonen-Modell (Remote-Buchung): nach MVP
- Zahlungen, Abrechnung, externe APIs: außerhalb MVP
