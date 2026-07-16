# Architekturentscheidungen

**Verbindliche Grundsätze und Sprint-Regeln:** `docs/SOURCE_OF_TRUTH.md`
Dieses Dokument enthält die technischen Begründungen für getroffene Entscheidungen.
Bei inhaltlichen Widersprüchen gilt SOURCE_OF_TRUTH.md.

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

## Dual-UI-Modus: Fahrgast vs. Disposition (Sprint 7)

`/transport-requests` rendert zwei verschiedene Ansichten abhängig von der Nutzerrolle:

- **Fahrgast-Modus** (`passenger`, `trusted_person`, alle anderen): Seitentitel „Meine Fahrten", „Neue Anfrage"-Button, Booking-Wizard (Abschnitte 1–4), Speichern/Absenden-Leiste
- **Dispo-Modus** (`provider_admin`, `dispatcher`, `platform_admin`): Seitentitel „Disposition", kein „Neue Anfrage"-Button, kein Wizard; stattdessen Fahrgastdaten-Infobox + schreibgeschützte Anfragedetails + Disposition-Abschnitt (Matching, Zuweisung)

Die Rollenprüfung erfolgt im Frontend via `authStore.role` (computed `isDispositionUser`). Die API filtert die Liste bereits serverseitig: Dispo-Rollen erhalten alle `requested`/`assigned`-Anfragen, Fahrgäste nur ihre eigenen.

**Fahrgast-Kontaktfelder** (`passenger_display_name`, `passenger_email`, `passenger_phone`, `passenger_emergency_contact_name`, `passenger_emergency_contact_phone`) werden serverseitig per Batch-Query (List) bzw. Einzelabfrage (Detail) aus `users`- und `mobility_profiles`-Tabellen befüllt und nur bei Bedarf gerendert. `User.phone` ist nullable — das Frontend zeigt „nicht hinterlegt" wenn kein Wert vorhanden.

**Sidebar:** Das Nav-Label „Fahrten anfragen" / „Disposition" wird ebenfalls rollenbasiert berechnet (computed `navItems`).

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

## Fahrzeuge und Fahrerprofile (Sprint 5)

### Soft-Delete vs. endgültiges Löschen

`DELETE /vehicles/{id}` und `DELETE /drivers/{id}` setzen `is_active=False` (Soft-Delete).
`DELETE /vehicles/{id}/permanent` und `DELETE /drivers/{id}/permanent` löschen den Datensatz endgültig.

**Soft-Delete (Standard):** Fahrzeuge und Fahrer sind historisch relevante Entitäten. Wenn eine Fahrt bereits einem Fahrzeug zugewiesen war, darf das Fahrzeug nicht verschwinden. Soft-Delete erhält die Referenzintegrität für künftige Fahrtenhistorie.

**Permanentes Löschen (Ausnahme):** Nur für Datensätze ohne Fahrtenreferenz sinnvoll. Sobald `Ride`-Modell (Sprint 6) existiert, muss vor hartem Löschen geprüft werden, ob noch Fahrten auf das Fahrzeug/Fahrerprofil verweisen. Bis Sprint 6: kein automatischer Block — der Dispatcher ist verantwortlich.

**Reaktivierung:** `PUT /vehicles/{id}` mit `{ is_active: true }` reaktiviert ein deaktiviertes Fahrzeug. Ebenso für Fahrer. Im UI per "Wieder aktivieren"-Button.

### Fahrzeugausstattung als Matching-Grundlage

25 boolesche Ausstattungsmerkmale (8 allgemein + 11 medizinisch) spiegeln Mobilitätsbedarfe aus Sprint 4 und 5 wider.

**Allgemein:** Rampe, Lift, Rollstuhl-Sicherung, E-Rollstuhl, Liegendtransport-Basis, Kindersitz, Niedriger Einstieg, Breite Tür.

**Medizinisch (Sprint 5):** Transportliege, Liegenaufnahme, med. Stauraum, Sauerstoffhalterung, Erste-Hilfe-Ausstattung, Hygienebedarf, qualifizierter Krankentransport (KTP), Tragestuhl, Infusionshalterung, Zweimann-Besatzung.

**Maße, Gewicht & Zufahrt (Sprint 5):** Länge/Breite/Höhe (cm), Breite mit Spiegeln, Radstand, Wendekreis (m), Leergewicht, zul. Gesamtgewicht, Nutzlast (kg) — alle nullable. Außerdem 4 boolesche Zufahrtsmerkmale: großer Stellplatz nötig, enge Straßen geeignet, Tiefgarage geeignet, Einparkhilfe. Diese Werte fließen als Zukunftsoptimierung in Routenplanung und Dispositionshilfen ein.

**Kein Rettungsdienst / Notfallmedizin:** Access Mobility ist kein Rettungsdienstportal. Alle medizinischen Felder beziehen sich auf qualifizierten Krankentransport (KTP) ohne Notfallindikation. Kein Notruf, keine Patientenüberwachung, keine Abrechnung mit Kostenträgern.

**Begründung:** Späteres Matching vergleicht `MobilityProfile`-Felder gegen `Vehicle`-Felder. Das Datenmodell ist so gebaut, dass Matching ohne Umstrukturierung möglich ist (vgl. `ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md`).

### Fahrerqualifikationen als Pflichtprüfung bei Zuweisung

23 Qualifikationsflags in 3 Kategorien:
- **Grundqualifikationen (9):** Rollstuhl begleiten/sichern, Lift bedienen, blinde/gehörlose Fahrgäste unterstützen, Liegendtransport, Erste Hilfe, P-Schein, med. Krankentransport (KTP).
- **Medizinische Qualifikationen (7, Sprint 5):** Sanitätshelfer, Rettungshelfer, Rettungssanitäter, Rettungsassistent, Notfallsanitäter, Pflegefachkraft, Med. Fachangestellte/r.
- **Technische Zusatzausbildungen (7, Sprint 5):** Hygiene, Infektionsschutz (IfSG), Rollstuhlsicherung (zertifiziert), Liftsystem, Liegendtransport (Trage), Tragestuhl, Sauerstoffgeräte.

`can_support_medical_transport` kennzeichnet Fahrer, die für qualifizierten Krankentransport (KTP) ausgebildet sind — kein Rettungssanitäter, kein Notfalleinsatz.

**Begründung:** Eine Fahrt darf nur einem Fahrer zugewiesen werden, der alle für den Fahrgastbedarf notwendigen Qualifikationen hat. Dispatcher kann im Sprint 6 manuell prüfen — automatische Validierung folgt.

### Transporttypen-Endpunkt (Sprint 5 / Sprint 5B)

`GET /api/v1/transport-options` (ohne Auth) liefert 5 vordefinierte Transportprofile.

**Zentrale Konfiguration:** Alle Preset-Definitionen liegen in `backend/app/core/transport_presets.py` — ein einziger Import in `transport_options.py`. Späterer Ausbau (admin-konfigurierbar, DB-basiert) ist damit isoliert möglich.

Felder je Transporttyp:
- `id`, `label`, `description`, `warning` (optional), `icon_key`
- `suggested_profile_fields`: welche `MobilityProfile`-Felder für diesen Typ typischerweise gesetzt werden (alle boolean)
- `suggested_field_values`: nicht-boolesche Feld-Überschreibungen, z. B. `attendant_type_required: "unknown"` für KTP
- `suggested_vehicle_requirements`: passende `Vehicle`-Ausstattungsmerkmale (Orientierung)
- `suggested_driver_requirements`: erwartete Fahrerqualifikationen (Orientierung)
- `preset_controlled_profile_fields`: alle Felder, die beim Wechsel der Schnellauswahl zurückgesetzt werden (12 boolesche Felder — Frontend-Reset-Grundlage)

**Fachliche Preset-Grenzen (Sprint 5B):**
- `accessible_ride` / `patient_ride_no_medical_care` / `recurring_school_work_facility_route`: Null medizinische Detailfelder — Liegendtransport, Sauerstoff, Begleitung werden nicht vorausgewählt
- `patient_ride_no_medical_care`: enthält ausdrücklich **nicht** `needs_stretcher_transport`
- `stretcher_ride`: nur `needs_stretcher_transport` + `requires_special_positioning`
- `qualified_medical_transport` (KTP): nur `requires_medical_transport` + `requires_medical_attendant`; `attendant_type_required` wird auf `"unknown"` gesetzt (via `suggested_field_values`). Sauerstoff, Geräte, Hygiene, Zweimann — hängen vom konkreten Fahrgast ab und werden **nicht** auto-gesetzt.

**Frontend-Reset-Mechanismus (Sprint 5B):**
`applyTransportType` in `MobilityProfileView.vue` baut den Reset-Patch dynamisch aus `tt.preset_controlled_profile_fields` auf (anstatt einer lokal hart kodierten Feldliste). `attendant_type_required` wird immer auf `"none"` zurückgesetzt, bevor `suggested_field_values` angewendet werden. Fallback auf lokales `PRESET_RESET`, falls `preset_controlled_profile_fields` leer.

**Kein direktes Matching:** Die `suggested_*`-Listen dienen als Orientierung für den Fahrgast, nicht als Matching-Regel. Die Matching-Logik wird separat im Backend implementiert.

### Mobilitätsprofil — medizinische Detailfelder (Sprint 5)

14 neue Felder auf `MobilityProfile` für qualifizierten Krankentransport:
- 11 boolesche Flags (z. B. `requires_medical_transport`, `brings_oxygen`, `requires_infusion_mount`)
- Neues Enum `AttendantType` mit 6 Werten (`none`, `escort_person`, `second_assistant`, `paramedic`, `medical_professional`, `unknown`)
- 2 Freitextfelder: `medical_device_notes`, `medical_transport_notes`

Alle Felder sind freiwillig. `attendant_type_required` erscheint in der UI nur, wenn `requires_medical_attendant = true`.

**Abgrenzung:** Diese Felder beschreiben den Transportbedarf des Fahrgastes, nicht eine medizinische Diagnose. Sie enthalten keine Gesundheitsdaten i. S. d. Art. 9 DSGVO — der Fahrgast gibt nur an, was für die Fahrt relevant ist (z. B. ob eine Halterung für sein Sauerstoffgerät gebraucht wird).

### Fahrzeug Maße, Gewicht & Zufahrt — spätere Verwendung

Die Dimensionsfelder sind jetzt erfassbar, werden aber noch nicht für Matching oder Routenoptimierung genutzt. Geplante Verwendung in späteren Sprints:
- Prüfung Tiefgarageneinfahrt bei Zieladresse
- Anzeige passender Stellplätze in der Disposition
- Optimierung Wendekreis bei engen Zuwegungen (KTP zu Wohngebäuden)

### Keine separate Provider-Tabelle

`Organization` mit `type=transport_provider` wird als Fahrdienst verwendet.  
**Begründung:** Eine eigene `Provider`-Tabelle wäre strukturelle Redundanz. Die optionalen Felder `dispatch_phone`, `dispatch_email`, `operating_area_notes` decken Fahrdienst-spezifische Daten ab.

### Vereinfachte Mandantentrennung in Sprint 5

Alle Fahrzeuge / Fahrer sind für jeden eingeloggten Nutzer einsehbar und bearbeitbar.  
**Begründung:** Vollständiges RBAC und Mandantentrennung (nur eigene Orgs sehen) folgen Sprint 7. Im MVP-Scope mit einem Testfahrdienst ist das unkritisch.

---

## Mobilitätsprofil (Sprint 4)

### Auto-Create bei GET

`GET /mobility-profile/me` erzeugt automatisch ein leeres Profil, falls noch keins existiert.  
**Begründung:** Das Frontend ist einfacher, wenn es nach dem ersten Login immer ein Profil-Objekt erhält — kein Sonderfall „404 → neues Formular vs. 200 → bestehende Daten".  
Das leere Profil ist vollständig gültig; alle Felder haben sinnvolle Defaults (`False`, `null`).

### Partial-Update via `exclude_unset=True`

`PUT /mobility-profile/me` schreibt nur die im JSON tatsächlich gesendeten Felder.  
**Begründung:** Der Client muss nicht das gesamte Profil zurücksenden. Nicht gesendete Felder werden nicht auf `null` zurückgesetzt. Implementiert über Pydantic v2 `model_dump(exclude_unset=True)`.

### Medizinische Angaben sind freiwillig

`medical_notes` hat keinen `nullable=False`-Constraint; in der UI kein `required`.  
**Begründung:** Medizinische Daten unterliegen erhöhten Datenschutzanforderungen. Fahrgäste entscheiden selbst, ob sie diese angeben. Das System darf sie nicht als Pflichtfeld voraussetzen.

### Rollstuhl-Typ nur bei aktivem Rollstuhl sichtbar

Die Rollstuhltyp-Auswahl (`wheelchair_type`) erscheint in der UI nur, wenn `uses_wheelchair = true`.  
Wird der Rollstuhl deaktiviert, wird `wheelchair_type` automatisch auf `null` zurückgesetzt.  
**Begründung:** Relevante Felder kontextsensitiv einblenden — reduziert kognitive Last für Fahrgäste.

---

## TransportRequest als Domänenobjekt (Sprint 6)

### Transportanfrage ≠ Fahrt

`TransportRequest` und `Ride` sind bewusst getrennte Modelle.

- **`TransportRequest`** = Wunsch eines Fahrgastes (wer, wann, wohin, welche Anforderungen)
- **`Ride`** (Sprint 7) = die tatsächlich disponierte und bestätigte Fahrt mit Fahrzeug + Fahrer

**Begründung:** Eine Anfrage kann abgelehnt, umgeplant oder nie bedient werden. Eine Fahrt existiert
erst, wenn ein Disponent sie aktiv erstellt. Beide Domänenobjekte nebeneinander ermöglichen
spätere KI-unterstützte Vorschlagsgenerierung, ohne das Datenmodell umstrukturieren zu müssen.

### Snapshot-Strategie: Anforderungen einfrieren

`requirement_snapshot` und `mobility_profile_snapshot` werden als JSONB beim Erstellen oder
Absenden der Anfrage befüllt und danach nicht mehr verändert.

**Begründung:** Ein Fahrgast kann sein Mobilitätsprofil nach dem Absenden einer Anfrage ändern.
Die Anforderungen, die der Fahrdienst zu bedienen hat, müssen den Stand zum Anfragezeit­punkt
festhalten — nicht den aktuellen Profilstand. Ohne Snapshot könnte ein Profil-Update bestehende
Anfragen lautlos inkonsistent machen.

Der Snapshot ist gleichzeitig die Matching-Grundlage für Sprint 7: Dispatcher und (später) die
Matching-Engine lesen den Snapshot, nicht das aktuelle Profil.

### Statusmodell

```
draft → requested → (aus dem Scope dieses Modells)
draft → cancelled
requested → cancelled
```

Nur `draft`-Anfragen können über `POST /submit` abgesendet werden.  
Pflichtfelder für Submit: `passenger_user_id`, `transport_type_id`, `pickup_address`,
`destination_address`, `pickup_date`, `pickup_time`.

Stornierung ist jederzeit möglich (draft oder requested). Stornierte Anfragen sind schreibgeschützt.

### Kein Matching, keine Disposition in Sprint 6

`TransportRequest` ist reine Daten-Erfassung. Keine automatische Fahrtplanung, kein Fahrer
wird informiert, kein Fahrzeug wird vorgeschlagen. Das Matching folgt in Sprint 7.

---

## Manuelles Matching (Sprint 7)

### Snapshot-basiertes Matching

Das Matching liest ausschließlich `requirement_snapshot` und `mobility_profile_snapshot` — nicht das aktuelle `MobilityProfile` des Fahrgastes. Begründung: Profil-Updates nach Anfragedatum dürfen das Matching bestehender Anfragen nicht beeinflussen. Der Snapshot ist die vertragliche Grundlage.

**`_extract_needs(request) → set[str]`:** Vereinigt beide Snapshot-Quellen. Die `selected_profile_fields` aus dem Anforderungs-Snapshot werden mit allen auf `True` gesetzten booleschen Feldern aus `mobility_profile_snapshot` gemergt. Das Ergebnis ist eine Menge von Anforderungsbezeichnern, die von Fahrzeug- und Fahrerregeln abgefragt werden.

### Drei Match-Level

- **`suitable`** — keine fehlenden Anforderungen
- **`warning`** — nur weiche Anforderungen fehlen (fachlich prüfbar, nicht strukturell ausschließend)
- **`unsuitable`** — mindestens eine harte Anforderung fehlt (strukturell nicht bedienbar ohne Anpassung)

**Harte Anforderungen (→ `unsuitable`):** Liegendtransport-Grundausstattung, Transportliege + -aufnahme, Tragestuhl, Sauerstoff-/Infusionshalterung, med. Stauraum, Rollstuhlplatz, Liegendtransport-Fahrerbefähigung.

**Weiche Anforderungen (→ `warning`):** KTP-Qualifikation, Rampe/Lift, Rollstuhlsicherung, KTP-Fahrerqualifikation, Trainings-Flags, Hygiene/Infektionsschutz.

### Matching als Entscheidungshilfe — kein Block

Der `POST /{id}/assign`-Endpoint prüft **nicht** das Matching-Ergebnis. Ein Disponent kann jede beliebige Kombination aus aktivem Fahrzeug + aktivem Fahrerprofil zuweisen, auch wenn das Matching `unsuitable` zurückgibt. Begründung: Das System hat keine Kenntnis von Sondersituationen, Zusatzvereinbarungen oder Notfallentscheidungen. Die fachliche Verantwortung liegt beim Menschen.

### Statusmodell Sprint 7

```
draft → requested → assigned ← unassign
draft → cancelled
requested → cancelled
assigned → cancelled
```

`unassign` setzt `assigned` zurück auf `requested`. Alle 5 Zuweisungsfelder werden auf `NULL` zurückgesetzt.

PostgreSQL-Enum-Einschränkung: `ALTER TYPE ... ADD VALUE` kann in einer Transaktion ausgeführt werden (PostgreSQL 12+). Enum-Werte können **nicht** entfernt werden — die Alembic-Downgrade-Funktion lässt `assigned` bestehen und löscht nur die 5 Spalten.

---

## Fahrer-App, Linienverkehr & Benachrichtigungen — Konzept (Sprint 10–11, noch nicht implementiert)

### Fahrer-App

**Schichtverwaltung:**
- Fahrer startet Schicht (Zeitstempel) — wählt Fahrzeug primär über Kennzeichen.
- Fahrer kann Pause starten/beenden mit Zeitprotokoll.
- Fahrer beendet Schicht (Zeitstempel).
- Alle Schicht- und Pausenzeiten werden protokolliert — mögliche spätere Grundlage für Arbeitszeiterfassung. Keine Lohnabrechnung im MVP.

**Auftragstypen:**
1. **Linienverkehr** — optimierte Fahrgastliste für einen Tour-Block:
   - Nächster Fahrgast (Name, Adresse, geplante Einstiegszeit, geplante Ausstiegszeit)
   - Mobilitätsbedarf des Fahrgastes (aus Snapshot)
   - Hinweise zur Abholung
   - Reihenfolge vom Disponenten vorgeschlagen, manuell anpassbar
2. **Spontanfahrten** — einzelne zugewiesene Transporte außerhalb der Tour

**Statusbuttons (7 Aktionen):**

| Button | Aktion |
|---|---|
| Schicht beginnen | `shift_start` + Timestamp |
| Pause beginnen | `break_start` + Timestamp |
| Pause beenden | `break_end` + Timestamp |
| Fahrgast zugestiegen | `passenger_picked_up` + Timestamp + optionaler Standort |
| Fahrgast ausgestiegen | `arrived_destination` + Timestamp + optionaler Standort |
| Fahrt abgeschlossen | `completed` + Timestamp |
| Problem melden | `problem_reported` + Freitext + Timestamp |
| Schicht beenden | `shift_end` + Timestamp |

**Sprachassistenz Fahrer-App:**
Befehle: „Schicht beginnen" / „Ich fahre Fahrzeug B-AM 1234" / „Pause beginnen" / „Fahrgast ist zugestiegen" / „Fahrgast ist ausgestiegen" / „Nächster Halt" / „Problem melden" / „Schicht beenden"
Sicherheitskritische Aktionen erfordern Bestätigung: „Soll ich Max Mustermann als zugestiegen markieren?"

### Benachrichtigungseinstellungen

Konfigurierbar im Fahrgastprofil je Vertrauensperson:

| Feld | Typ | Beschreibung |
|---|---|---|
| `recipient_name` | Text | Name der Vertrauensperson |
| `recipient_phone` | Text | Telefonnummer |
| `recipient_email` | Text | E-Mail-Adresse |
| `is_app_user` | Bool | Nutzt ebenfalls die App |
| `can_see_live_location` | Bool | Darf Standort empfangen |
| `can_receive_status_updates` | Bool | Darf Statusmeldungen empfangen |
| `notify_channels` | Array[Enum] | app / sms / email / system_share |

**Konfigurierbare Ereignisse:**
- `shift_started` — Fahrer hat Schicht begonnen
- `driver_on_way` — Fahrzeug ist unterwegs
- `arriving_soon` — Fahrer ist bald da (ETA ≤ X Minuten)
- `passenger_picked_up` — Fahrgast zugestiegen
- `passenger_dropped_off` — Fahrgast ausgestiegen / angekommen
- `delayed` — Verspätung erkannt
- `trip_cancelled` — Fahrt storniert
- `problem_reported` — Problem gemeldet

**Datenschutz:**
- Benachrichtigungen nur wenn Fahrgast dies explizit konfiguriert hat.
- Medizinische Details werden niemals in Nachrichten übertragen.
- Vertrauenspersonen sehen nur ihren berechtigten Fahrgast — keine anderen Fahrgäste, keine Touren.
- Standortdaten in Nachrichten nur wenn `can_see_live_location = true`.

---

## Live-Standortteilung — Konzeptentscheidung (Sprint 12, noch nicht implementiert)

Verbindliche Grundentscheidung, die vor der Implementierung festgeschrieben wurde.

### Konzept

Während einer aktiven Fahrt kann der Fahrgast oder eine berechtigte Vertrauensperson
den Fahrtstatus und optional den Live-Standort mit ausgewählten Personen teilen.

### Freigabewege

| Weg | Beschreibung |
|---|---|
| In-App-Freigabe | Empfänger sieht Status + ETA in der App (erfordert Account) |
| Link-Freigabe | Zeitlich begrenzter Token-Link, ohne Account nutzbar |
| System-Teilen | Native Browser-Share-API (WhatsApp, SMS, E-Mail) |
| Statusnachrichten | Textuelle Ereignismeldungen je Fahrtstatusänderung |

### Datenmodell-Konzept (spätere Implementierung)

**`LiveLocationShare`** — eine Freigabe pro Fahrt und Empfänger:
- `id`, `transport_request_id` / `ride_id`, `passenger_user_id`, `shared_by_user_id`
- `recipient_user_id` (nullable — für App-Nutzer), `recipient_name`, `recipient_phone`, `recipient_email`
- `share_token` (eindeutiger Token für Link-Freigabe)
- `share_channel`: `app` / `sms` / `whatsapp` / `email` / `system_share`
- `status`: `active` / `expired` / `revoked`
- `expires_at` (spätestens bei Fahrtende), `revoked_at`, `created_at`

**`RideStatusEvent`** — Statusereignisse einer Fahrt:
- `id`, `ride_id`, `status`, `recorded_at`, `lat` (nullable), `lng` (nullable), `accuracy` (nullable)
- `source`: `driver_app` / `passenger_app` / `vehicle_device`

**Geplante Statuswerte:**
`requested` → `assigned` → `driver_on_way` → `arrived_pickup` → `passenger_picked_up` → `arrived_destination` → `completed`
Sonderstatus: `delayed`, `cancelled`

### Datenschutz-Grundregeln (verbindlich)

- Standortdaten sind sensible Daten — besonderer Schutzbedarf.
- Teilen ist immer freiwillig und erfordert explizite Zustimmung des Fahrgastes.
- Freigabe ist zeitlich begrenzt (automatischer Ablauf spätestens bei Fahrtende).
- Freigabe ist jederzeit widerrufbar (`revoked`-Status + `revoked_at`-Timestamp).
- Tracking-Links sind nicht dauerhaft gültig und nicht öffentlich auffindbar.
- Keine Standortweitergabe außerhalb aktiver Fahrten oder ohne klare Berechtigung.
- Vertrauenspersonen sehen Fahrtstatus und ETA — keine medizinischen Details.
- Protokollierung: `shared_by`, `recipient`, `created_at`, `expires_at`, `revoked_at`.
- Sprachassistent aktiviert Freigabe nur nach ausdrücklicher Bestätigung (Empfänger + Art + Dauer).

### Abhängigkeit

Live-Standortteilung (Sprint 12) setzt Sprint 11 (Fahrtstatus / Fahrer-App-Grundlage) voraus.
Ohne belastbare `RideStatusEvent`-Daten können Statusmeldungen nicht zuverlässig weitergegeben werden.

### Hinweis zur aktuellen Datenmodellstruktur

In Sprint 7 gibt es noch keine eigene `Ride`-Tabelle — `TransportRequest` trägt Zuweisungsfelder.
Für Live-Tracking wird in Sprint 11 entschieden, ob ein separates `Ride`-Modell eingeführt wird
oder ob `RideStatusEvent` direkt an `TransportRequest` hängt.

---

## Bewusst nicht umgesetzt (MVP-Scope)

- Auth/JWT: Sprint 3 ✅
- Rollenmodell: Sprint 3 ✅
- Stammdaten (Org, Fahrzeug, Fahrer): Sprint 4+5 ✅
- Fahrtenbuchung: Sprint 5 ✅
- Transportanfragen-Grundlage: Sprint 6 ✅
- Manuelles Matching & Disposition: Sprint 7 ✅
- Fahrerstatus / Fahrtstart: Sprint 8
- Automatisches Matching (KI): nach MVP
- Serienfahrten (RRULE): Sprint 8+
- Sprachführung / Sprachmenü: nach MVP
- Vertrauenspersonen-Modell (Remote-Buchung): nach MVP
- Zahlungen, Abrechnung, externe APIs: außerhalb MVP
- RBAC-Vollausbau (Mandantentrennung): nach Sprint 8
