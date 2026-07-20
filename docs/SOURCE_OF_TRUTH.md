# SOURCE OF TRUTH — access-mobility

**Dieses Dokument ist die verbindliche Quelle für alle Sprint-Entscheidungen, Designvorgaben,
Architekturgrundsätze und Claude-Arbeitsregeln.**

Bei Widersprüchen zwischen diesem Dokument und anderen Docs gilt dieses Dokument.
Letzte Aktualisierung: 2026-07-20 · Sprint FAHRANDO-GATE-PROTECTS-LOGIN-DIRECTLINK-1 abgeschlossen · Sprint 11 geplant

---

## 1. Projektziel

Access Mobility ist eine **Plattform für barrierefreie Mobilität**.

Sie verbindet Fahrgäste mit besonderem Mobilitätsbedarf, spezialisierte Fahrdienste,
Disponenten, Fahrer und Organisationen in einem gemeinsamen digitalen System.

Langfristiges Ziel: eine Uber-ähnliche Buchungserfahrung für Menschen mit Behinderung oder
Mobilitätseinschränkung — mit passenden Fahrzeugen, geschultem Personal, automatischem
Matching, Sprachassistenz und vollständiger Abrechnung.

**Das ist kein Rettungsdienst-System. Es ist kein Notfallmedizin-Portal.**
Access Mobility deckt qualifizierten Krankentransport (KTP) und barrierefreie Alltagsmobilität ab.

---

## 2. Zielgruppen

| Zielgruppe | Beschreibung | Phase |
|---|---|---|
| **Fahrgäste** | Menschen mit Rollstuhl, Sehbehinderung, eingeschränkter Mobilität | MVP |
| **Blinde / sehbehinderte Nutzer** | Benötigen Sprachassistenz als gleichwertige Bedienalternative | MVP → Sprint 8 |
| **Angehörige / Vertrauenspersonen** | Buchen für andere Fahrgäste stellvertretend | MVP-Datenmodell / UI später |
| **Organisationen / Einrichtungen** | Buchen für Mitglieder/Klient:innen (Heime, Werkstätten) | MVP |
| **Fahrdienste (Provider)** | Verwalten Flotte, Fahrer, Qualifikationen | MVP |
| **Disponenten** | Ordnen Anfragen zu Fahrzeugen und Fahrern zu | MVP |
| **Fahrer** | Sehen und quittieren Aufträge, führen Fahrt durch | Sprint 8 |
| **Kostenträger / Praxen / Kliniken** | Buchen für Patienten, Abrechnungsworkflow | Phase 3 |

---

## 3. Rollen (aktuelle MVP-Rollen)

| Rolle | Bezeichnung | Rechte (Kurzform) |
|---|---|---|
| `passenger` | Fahrgast | Eigene Anfragen, Mobilitätsprofil |
| `trusted_person` | Vertrauensperson | Bucht für Fahrgäste (Datenmodell vorhanden, UI später) |
| `organization_admin` | Organisations-Admin | Verwaltet Org, Mitglieder |
| `organization_coordinator` | Org-Koordinator | Bucht für Org-Mitglieder |
| `provider_admin` | Fahrdienst-Admin | Verwaltet Flotte, Fahrer |
| `dispatcher` | Disponent | Disposition, Matching, Zuweisung |
| `driver` | Fahrer | Tagesaufträge, Statuswechsel (ab Sprint 8) |
| `platform_admin` | Plattform-Admin | Vollzugriff |

---

## 4. Technischer Stack (verbindlich)

| Komponente | Technologie | Port |
|---|---|---|
| Frontend | Vue 3 + TypeScript + Vite + PrimeVue 4 + Pinia | 5180 |
| Backend | FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2 | 8010 |
| Datenbank | PostgreSQL (Docker) | 5440 |
| API-Pfad | `/api/v1/` | — |

**Wichtig:** `frontend/.env.local` überschreibt `frontend/.env`. Bei Port-Fehlern zuerst dort prüfen.
Korrekter Wert lokal: `VITE_API_BASE_URL=http://localhost:8010/api/v1`

**Produktionsbetrieb (fahrando.com):**
- Backend läuft auf Railway, nicht auf dem Webspace
- Webspace enthält nur den statischen Frontend-Build (`index.html`, `assets/`, `.htaccess`, `Logo1.png`)
- `frontend/.env.production` (nicht committed): `VITE_API_BASE_URL=https://fahrando-api-production.up.railway.app/api/v1`
- Upload-Staging lokal: `deploy/fahrando-webspace-upload/` (nicht committed)

---

## 4a. Plattform-Architektur-Grundsatz (verbindlich)

Access Mobility ist **eine Plattform** — kein Verbund aus drei getrennten Systemen.

**Ein gemeinsames Backend · Eine API · Eine Datenbank · Ein Rollen-/Rechtesystem**

Fachlich gibt es jedoch drei klar getrennte Nutzungswelten mit unterschiedlichen
Oberflächen-Anforderungen:

| Welt | Zielgruppe | Oberfläche | Priorität |
|---|---|---|---|
| **Fahrgast-/Vertrauenspersonen-App** | Fahrgäste, Angehörige, Betreuer, Org-Koordinatoren | Extrem einfach, barrierefrei, Sprachassistenz, mobile-first | Hoch |
| **Fahrer-App** | Fahrer | Mobile, robust, große Buttons, wenig Ablenkung, offline-fähig | Mittel |
| **Dispositions-/Admin-Webapp** | Disponenten, Provider-Admins, Platform-Admins | Desktop-orientiert, tabellarisch, filterbar, funktionsreich | Mittel |

**Technische Strategie:**
- **MVP:** Eine Web-App mit rollenabhängigen Bereichen (aktuelle Umsetzung).
- **Später:** Fahrgast-App und Fahrer-App als eigene mobile / PWA / native Hüllen.
- **Langfristig:** Disposition bleibt primär Desktop-Webanwendung.
- Alle Welten teilen Backend, API, Auth und Datenmodell.
- Rollen bestimmen Navigation, Oberfläche und Berechtigungen vollständig.

Details: `docs/DECISIONS.md` (Abschnitt Plattform-Architektur)
Oberflächen-Grundsätze: `docs/Product/DESIGN_AND_ACCESSIBILITY_GUIDE.md`

---

## 5. Aktueller Sprintstand (Juli 2026)

| Sprint | Inhalt | Status |
|---|---|---|
| Sprint 1 | Grundgerüst (FastAPI + Vue 3 + PostgreSQL) | ✅ abgeschlossen |
| Sprint 2 | Designbasis, Landingpage, Portal-Layout | ✅ abgeschlossen |
| Sprint 3 | Auth, JWT, 8 Rollen, Demo-User | ✅ abgeschlossen |
| Sprint 4 | Mobilitätsprofil (22 Felder, 11 Bedarfstypen) | ✅ abgeschlossen |
| Sprint 5 | Fahrzeuge, Fahrerprofile, med. Ausstattung | ✅ abgeschlossen |
| Sprint 5B | Zentrale Transport-Presets (backend/app/core/transport_presets.py) | ✅ abgeschlossen |
| Sprint 6 | Transportanfragen (TransportRequest, Snapshots) | ✅ abgeschlossen |
| Sprint 7 | Manuelles Matching & Disposition | ✅ abgeschlossen |
| **Sprint 8** | **Assistant Core & barrierefreies Onboarding-Fundament** | ✅ abgeschlossen |
| **Sprint 9** | **Sprachgeführter Mobilitätscheck (offline-fähig)** | ✅ abgeschlossen |
| **Sprint 9B** | **Verbesserter Sprachassistent: TTS-Flow, STT, Tastaturkürzel** | ✅ abgeschlossen |
| **Sprint 10** | **Fahrer-Schichtstart & Fahrzeugwahl (mobile-first, Standardfahrzeug, Auftragsstruktur)** | ✅ abgeschlossen |
| **Sprint FAHRANDO-1** | **Fahrando Coming-Soon + Testzugang + Platform-Admin-Benutzerverwaltung** | ✅ abgeschlossen |
| **Sprint FAHRANDO-2** | **Gate-Schutzseite mit DB-basierten Testzugängen & Website-Testzugänge-Modul** | ✅ abgeschlossen |
| **Sprint FAHRANDO-PREVIEW-GATE-DIREKTLINK-SCHUTZ-1** | **Direktlink-Schutz für öffentliche Website-Routen** | ✅ abgeschlossen |
| **Sprint FAHRANDO-DEPLOYMENT-1** | **Railway-Deployment, CORS, API-Base-Fix, Production-Build für fahrando.com** | ✅ abgeschlossen |
| **Sprint FAHRANDO-GATE-PROTECTS-LOGIN-DIRECTLINK-1** | **Variante B: Gate schützt /login und alle App-Routen** | ✅ abgeschlossen |
| **Sprint 11** | **Fahrt-Statusereignisse, Fahrer-Statuswechsel, Benachrichtigungseinstellungen** | ✅ abgeschlossen |

---

## 6. Geplante Sprints (Roadmap-Richtung)

| Sprint | Schwerpunkt |
|---|---|
| Sprint 8 | Assistant Core: Sprachassistenz-Fundament, barrierefreies Erst-Onboarding |
| Sprint 9 | Sprachgeführter Mobilitätscheck (offline-fähig) |
| Sprint 10 | Fahrer-Schichtstart & Fahrzeugwahl |
| Sprint 11 | Fahrtstatus, Fahrer-App, Benachrichtigungseinstellungen |
| Sprint 12A | Live-Status für Fahrgast & Vertrauensperson (Polling, kein GPS) |
| Sprint 12B | Vertrauenspersonen-View, Notification-Dispatch (geplant) |
| Sprint 12C | Live-Status & Standortfreigabe, GPS (geplant) |
| Sprint 13 | Online-KI-Berater / ChatGPT-Anbindung (Backend-only) |
| Sprint 14 | Fahrt per Sprache anfragen |
| Sprint 15 | Regelmäßige Touren / Serienfahrten |
| Sprint 16 | Ausfallmanagement |
| Sprint 17 | Tourenoptimierung |

---

## 7. Verbindliche Grundentscheidungen

### 7.1 Strukturierte Daten vor Freitext

Alles, was Matching beeinflusst, muss strukturiert erfasst werden:
- Checkbox / Boolean
- Auswahlfeld / Enum
- Zahl / Integer
- Datum / Zeit
- Eindeutiger Bezeichner

Freitext (`notes`, `medical_transport_notes` etc.) ist **nur ergänzend** zulässig.
Freitext darf **niemals** als alleinige Matching-Grundlage dienen.

### 7.2 Sprachassistent als Kernarchitektur

Der Sprachassistent ist kein späteres Add-on.
Er wird **von Anfang an** als Kernbestandteil der Architektur berücksichtigt.

**Bei jedem neuen Modul gilt:**
- Wie bedient ein blinder Nutzer dieses Modul?
- Welche Fragen stellt der Assistent?
- Welche strukturierten Felder werden gesetzt?
- Was funktioniert offline?
- Was kann online mit KI verbessert werden?
- Wo braucht es Bestätigung?

Details: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`
Modul-Anforderungen: `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

### 7.3 Offline-/Online-Hybrid

**Offline:** feste Dialoge, lokale Regeln, strukturierte Felder, Entwürfe speichern.
**Online:** KI/ChatGPT über Backend (nie direkt aus Frontend), natürliche Sprache,
Rückfragen, Vorschläge. API-Key niemals im Frontend.

### 7.4 Keine automatische Entscheidung ohne Bestätigung

Der Assistent **darf:**
- erklären
- vorschlagen
- Felder vorbefüllen
- zusammenfassen

Der Assistent **darf nicht** ohne explizite Bestätigung:
- Profil speichern
- Fahrt absenden
- Fahrzeug / Fahrer zuweisen
- Medizinische oder rechtliche Entscheidungen treffen

### 7.5 Keine Notfallmedizin

Access Mobility ist:
- kein Rettungsdienst
- kein Notfallmedizin-Portal
- keine medizinische Diagnose-App
- keine Krankenkassenabrechnung (im MVP)

Die App erfasst **transportrelevante Bedarfe** (Liegendtransport, Sauerstoffmitnahme,
qualifizierte Begleitung etc.) — keine medizinischen Diagnosen.
Alle medizinischen Felder beschreiben den Transportbedarf, nicht den Gesundheitszustand.

### 7.6 Matching-Grundsatz

Das System vermittelt eine Fahrt nur dann, wenn alle drei Ebenen erfüllt sind:
1. Fahrgastbedarf (Mobilitätsprofil / Snapshot)
2. Fahrzeugausstattung
3. Fahrerqualifikation

Matching ist **Entscheidungshilfe**, kein automatischer Block.
Der Disponent kann immer überschreiben — fachliche Verantwortung liegt beim Menschen.

### 7.7 Snapshot-Strategie

`TransportRequest` friert Anforderungen beim Absenden ein (`requirement_snapshot`,
`mobility_profile_snapshot`). Matching und Dispatcher lesen immer den Snapshot,
nie das aktuelle Profil.

### 7.8 Soft-Delete für Fahrzeuge und Fahrer

`DELETE` setzt `is_active=False`. Permanentes Löschen nur über separaten Endpoint.
Fahrzeuge und Fahrer sind historisch relevante Entitäten.

### 7.9 Fahrer-App, Linienverkehr & Benachrichtigungen — Konzept (Sprint 10–12)

**Fahrer-App (Sprint 10 ✅ / Sprint 11 ✅):**
- Fahrer startet Schicht — wählt Fahrzeug primär über Kennzeichen.
- Fahrer kann Pause starten/beenden und Schicht beenden.
- Schicht- und Pausenzeiten werden als Ereignisse protokolliert — mögliche spätere Grundlage für Arbeitszeiterfassung. Keine Lohnabrechnung im MVP.
- Fahrer sieht **Tagesaufträge**: Einzelfahrten (spontan) und Tourenblöcke (Linienverkehr).
- Linienverkehr: optimierte Fahrgastliste mit Reihenfolge, Adresse, Einstiegszeit, Mobilitätsbedarf, Abholhinweisen. Reihenfolge ist vom Disponenten anpassbar.
- Spontanfahrten: Einzelne zugewiesene Fahrten außerhalb des Linienverkehrs.

**Statusereignisse (Sprint 11 ✅ implementiert):**
Modell `RideStatusEvent` — 7 Typen: `driver_on_way` · `driver_arrived` · `passenger_picked_up` · `ride_started` · `ride_completed` · `ride_cancelled` · `issue_reported`

API: `POST /driver/transport-requests/{id}/status-events` (nur Fahrer, nur zugewiesene Fahrten)
`GET /transport-requests/{id}/status-events` (Fahrer, Fahrgast, Vertrauensperson [aktive can_view_rides-Beziehung], Staff-Rollen)

`ride_completed` → setzt TransportRequest.status auf `completed`
`ride_cancelled` → setzt TransportRequest.status auf `cancelled`

**Benachrichtigungseinstellungen im Fahrgastprofil (Sprint 11 ✅ Grundlage):**
Modell `PassengerNotificationPreference` — pro Ereignistyp 4 Flags:
- `notify_trusted_persons`, `channel_in_app`, `channel_email`, `channel_sms`
- UI: Tabelle im Fahrgastprofil mit Checkboxen
- API: `GET/PUT /passenger/notification-preferences`
- **Kein Versand in Sprint 11** — nur Einstellungsgrundlage

**Sprint 12A — Live-Status für Fahrgast & Vertrauensperson (umgesetzt):**
- Fahrgast sieht Status und Verlauf direkt in der Fahrtenkarte (Polling 20 s, onUnmounted gestoppt)
- `trusted_person` kann Status-Events für verknüpfte Fahrten lesen (aktive TrustedRelationship + can_view_rides)
- Placeholder-Service `notification_dispatch.py` — liest Präferenzen, kein echter Versand
- `frontend/src/api/rides.ts` — separates API-Modul für Fahrgast-Kontext

**Sprint 12B — Vertrauenspersonen-View & echter Versand (geplant):**
- Dedizierte View für Vertrauenspersonen
- Echter Benachrichtigungs-Dispatch basierend auf `PassengerNotificationPreference`

**Sprint 12C — GPS-Live-Tracking (geplant):**
- Live-Standortfreigabe des Fahrers (GPS-Koordinaten)
- Kanäle: In-App, E-Mail (extern), SMS (extern)

Details: `docs/DECISIONS.md` (Abschnitt Fahrer-App & Benachrichtigungen)

### 7.10 Live-Standortteilung — Konzeptentscheidung (Sprint 12)

Live-Standortteilung ist als geplantes Feature (Sprint 12) vorgesehen.
**Noch nicht implementiert — nur konzeptionell festgeschrieben.**

Mögliche Empfänger einer Standortfreigabe:
- Vertrauenspersonen / Angehörige (in-App oder per Link)
- Betreuer / Einrichtungen
- Abhol- oder Zielkontakt

Freigabewege:
1. **In-App-Freigabe** — Empfänger nutzt ebenfalls die App
2. **Link-Freigabe** — zeitlich begrenzter Tracking-Link, auch ohne App nutzbar
3. **System-Teilen** — native Teilen-Funktion (WhatsApp, SMS, E-Mail)
4. **Statusnachrichten** — textuelle Fahrtmeldungen (gestartet / unterwegs / angekommen)

**Verbindliche Datenschutz-Grundregeln (vor Implementierung festgeschrieben):**
- Standortdaten sind sensible Daten — besonderer Schutzbedarf.
- Teilen ist immer freiwillig und erfordert explizite Zustimmung des Fahrgastes.
- Freigabe ist zeitlich begrenzt (maximal bis Fahrtende).
- Freigabe ist jederzeit widerrufbar.
- Tracking-Links sind nicht dauerhaft gültig — automatischer Ablauf bei Fahrtende.
- Keine öffentliche Auffindbarkeit des Tracking-Links.
- Keine Standortweitergabe außerhalb aktiver Fahrten oder ohne klare Berechtigung.
- Protokollierung: wer hat wann mit wem geteilt, wann beendet.
- **Sprachassistent darf Standortfreigabe nur nach ausdrücklicher Bestätigung aktivieren.**

Datenmodell-Konzept: `docs/DECISIONS.md` (Abschnitt Live-Standortteilung)
Sprachassistenz: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`
UI-Grundsätze: `docs/Product/DESIGN_AND_ACCESSIBILITY_GUIDE.md`

---

## 8. Design-Grundsätze (verbindlich)

Vollständige Design-Regeln: `docs/Design/DESIGN_GUIDE.md`
Konsolidierte Übersicht: `docs/Product/DESIGN_AND_ACCESSIBILITY_GUIDE.md`

| Aspekt | Vorgabe |
|---|---|
| Grundfarbe | Schwarz / dunkles Anthrazit (`#111111`) |
| Akzentfarbe | Gelb (`#FFD600`) — Buttons, aktive Navigation, CTAs |
| Stil | Modern, premium, klar, vertrauenswürdig |
| Karten | Große, klar strukturierte Cards |
| Texte | Einfache Sprache, kein Verwaltungsjargon |
| Bedienelemente | Min. 44×44 px, immer Icon + Text (kein Icon-only) |
| Fokus | Sichtbarer gelber Outline-Ring auf allen interaktiven Elementen |
| Screenreader | ARIA-Labels, aria-live, programmatische Feldverknüpfung |
| Kontrast | WCAG AA Minimum, AAA für Kernbereiche |
| Tastatur | Vollständige Tastatur-Navigation obligatorisch |

---

## 9. Accessibility-Grundsätze (verbindlich)

Vollständige Regeln: `docs/Product/DESIGN_AND_ACCESSIBILITY_GUIDE.md`
Matching-Details: `docs/Product/ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md`

- **Accessibility-first**: Barrierefreiheit ist kein Feature, sondern Entwicklungsgrundlage.
- **Fahrgastoberfläche**: Wizard-Prinzip, eine Entscheidung pro Schritt, einfache Sprache.
- **Blinde Nutzer**: Vollständige Bedienung per Tastatur und Screenreader.
- **Sprachassistenz**: Als Kernbestandteil für jeden Fahrgast-nahen Bereich vorsehen.
- **Keine Icon-only-Bedienung**: Jedes Icon braucht einen sichtbaren Textlabel.
- **Farbe niemals das einzige Unterscheidungsmerkmal**: Status immer mit Icon/Text kombinieren.

---

## 10. Sicherheits- und Datenschutzregeln

- JWT wird im MVP in `localStorage` gespeichert (Schlüssel: `am_token`) — bekanntes Risiko, MVP-akzeptiert.
- Produktivbetrieb: Keycloak/Auth0 mit httpOnly-Cookies oder Auth-Code-Flow mit PKCE.
- CORS: Nur konfigurierte Origins in `ALLOWED_ORIGINS` — kein Wildcard `*`.
  - Lokal: `ALLOWED_ORIGINS=http://localhost:5180`
  - Produktion Railway: `ALLOWED_ORIGINS=https://fahrando.com,https://www.fahrando.com`
- **Fahrando-Marke:** Die `/`-Route zeigt die Fahrando-Coming-Soon-Seite. Das Login-Formular auf `/` nutzt **dasselbe** JWT/User-System wie das Portal — kein zweites Auth-System, keine zweite Datenbank.
- **Platform-Admin-Bootstrap-Passwort:** Nur über `backend/app/scripts/ensure_platform_admin.py` per Umgebungsvariablen. Das Passwort darf **niemals** in Dateien, Logs, Tests, Seed-Daten, Migrationen, Dokumentation oder API-Responses erscheinen. Nur der Hash wird in der DB gespeichert.
- `/login` leitet dauerhaft auf `/` um. Logout kehrt zu `/` zurück.
- Medizinische Daten sind freiwillig. Keine Pflichtfelder für Gesundheitsangaben.
- Medizinische Detailangaben (Art. 9 DSGVO): beschreiben Transportbedarf, nicht Gesundheitszustand.
- Disponenten sehen Kontaktdaten und Bedarfsfelder — keine medizinischen Diagnosen.
- KI/ChatGPT: API-Key nur im Backend. Kein direkter KI-Aufruf aus dem Frontend.
- Zustimmung vor jeder KI-Verarbeitung sensibler Daten erforderlich.
- Token-Ablauf: 60 Minuten (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Standortdaten** (Live-Tracking): sensible Daten, explizite Zustimmung erforderlich, zeitlich begrenzte Freigabe, jederzeit widerrufbar, Protokollierung (wer / wann / mit wem / bis wann).

---

## 11. Sprint-Regeln (Kurzfassung)

Vollständige Regeln: `docs/Product/SPRINT_RULES.md`

**Vor jedem Sprint:**
- `git status` und `git pull --ff-only`
- Bestehende Dokumentation lesen (insbesondere diese Datei)

**Während jedem Sprint:**
- Kein Overengineering, keine ungefragten Features
- Strukturierte Felder statt Freitext für Matching-relevante Daten
- Accessibility bei jeder UI-Komponente prüfen
- Sprachassistenz-Tauglichkeit bei jedem Fahrgast-nahen Modul prüfen

**Nach jedem Sprint:**
- Tests, TypeScript-Check, Browser-Test
- `docs/PROJECT_STATUS.md` + `docs/ROADMAP.md` aktualisieren
- `git status` — kein Commit, kein Push ohne Freigabe

**Pflicht-Umgebungsprüfung vor jedem Browser-Test (nicht optional):**

| # | Prüfung | Befehl |
|---|---|---|
| 1 | PostgreSQL läuft (Port 5440) | `docker compose -f docker-compose.dev.yml ps` |
| 2 | Alembic auf Stand `(head)` | `cd backend && .venv\Scripts\python.exe -m alembic current` |
| 3 | Seed-Daten aktuell | `cd backend && .venv\Scripts\python.exe -m app.scripts.seed_demo_data` |
| 4 | Backend antwortet (Port 8010) | `GET /api/v1/health → 200 OK` |
| 5 | Frontend erreichbar (Port 5180) | `http://localhost:5180 → 200` |

Alle fünf Punkte müssen ✅ sein, bevor ein Browser-Test beginnt.
Schnellstart: `scripts\windows\Start-AccessMobility-Dev.ps1`

---

## 12. Regel für künftige Claude-Sprints

Claude muss vor und während jedem Sprint folgende Prüfliste durchgehen:

| Nr. | Frage | Konsequenz |
|---|---|---|
| 1 | Betrifft der Sprint Fahrgäste? | Sprach-/Assistenzmodus für das Modul prüfen |
| 2 | Betrifft der Sprint strukturierte Anforderungen? | Keine Freitext-only-Lösung — strukturierte Felder vorschlagen |
| 3 | Betrifft der Sprint Matching? | Fahrzeuge, Fahrer, Qualifikationen, Snapshots berücksichtigen |
| 4 | Betrifft der Sprint die UI? | Accessibility, Screenreader, Tastatur, Fokus, einfache Sprache prüfen |
| 5 | Betrifft der Sprint sensible Daten? | Datenschutz, keine unnötige KI-Weitergabe, Bestätigungspflicht |
| 5a | Betrifft der Sprint Standortdaten? | Zustimmung, zeitliche Begrenzung, Widerruf, Protokollierung sicherstellen |
| 6 | Betrifft der Sprint Fahrt-Absenden, Zuweisung oder Standortfreigabe? | Assistent handelt erst nach expliziter Bestätigung |
| 7 | Wird ein neues Modul gebaut? | Eintrag in `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md` anlegen |
| 8 | Wird Code geändert? | TypeScript-Check + Browser-Test danach |
| 9 | Ist der Sprint fertig? | Git-Status prüfen — kein Commit ohne Freigabe |
| 10 | Wird ein Browser-Test durchgeführt? | **Pflicht-Umgebungsprüfung** (alle 5 Punkte ✅) vor dem Test — kein Browser-Test ohne laufende Umgebung |

---

## 13. Referenzen auf bestehende Dokumente

| Dokument | Inhalt |
|---|---|
| `docs/DECISIONS.md` | Alle Architekturentscheidungen mit Begründungen |
| `docs/ROADMAP.md` | Sprint-Planung (Vergangenheit + Zukunft) |
| `docs/PROJECT_STATUS.md` | Detaillierter Umsetzungsstand je Sprint |
| `docs/Product/PRODUCT_VISION.md` | Langfristige Vision, Phasen, MVP-Abgrenzung |
| `docs/Product/APP_CONCEPT.md` | Gesamtes App-Konzept verständlich beschrieben |
| `docs/Product/ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md` | Matching-Regeln, Mobilitätsbedarfe, Fahrzeugausstattung |
| `docs/Product/DESIGN_AND_ACCESSIBILITY_GUIDE.md` | Konsolidierte Design- und Accessibility-Regeln |
| `docs/Product/VOICE_ASSISTANT_STRATEGY.md` | Sprachassistenten-Gesamtkonzept |
| `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md` | Assistent-Anforderungen je Modul |
| `docs/Product/SPRINT_RULES.md` | Verbindliche Sprint-Regeln |
| `docs/Design/DESIGN_GUIDE.md` | CSS-Tokens, Farbpalette, Typografie, Layouts |
| `docs/DEPLOYMENT_FAHRANDO_TEST.md` | Deployment-Anleitung für Fahrando-Testzugang |
