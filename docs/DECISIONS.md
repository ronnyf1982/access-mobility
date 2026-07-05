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

## Bewusst nicht umgesetzt (MVP-Scope)

- Auth/JWT: Sprint 2
- Rollenmodell: Sprint 2
- Echte Fachmodule: ab Sprint 2
- Serienfahrten (RRULE): Sprint 5
- Zahlungen, Abrechnung, externe APIs: außerhalb MVP
