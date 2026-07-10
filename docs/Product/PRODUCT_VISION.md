# Produktvision — access-mobility

Grundlage: `MobilityCare_Berlin_Konzept_final.pdf` (abgelegt in `docs/Product/`).
Das PDF ist Referenz und Vision — keine Bauanweisung für den MVP.

---

## 1. Langfristige Vision

access-mobility (konzeptuell: MobilityCare Berlin) ist ein **geschlossenes digitales Ökosystem**
für barrierefreien Transport. Es verbindet Fahrgäste, spezialisierte Fahrdienste sowie
Arztpraxen und Krankenkassen in einer gemeinsamen Plattform.

Langfristiges Ziel: Eine Uber-ähnliche Buchungserfahrung für Menschen mit Behinderung oder
besonderem Mobilitätsbedarf — mit passenden Fahrzeugen, geschultem Personal, automatischem
Matching, Live-Tracking und vollständiger Krankenkassenabrechnung.

Das Ökosystem soll rechtssicher, DSGVO-konform, inklusiv und skalierbar sein.

---

## 2. Zielgruppen

| Zielgruppe | Rolle | Kanal (langfristig) |
|---|---|---|
| **Fahrgäste** | Buchen Fahrten, verwalten Profil & Notfallkontakt | Native App (Phase 2) + Web |
| **Fahrer:innen** | Nehmen Aufträge an, führen Status, quittieren Zahlung | Native App (Phase 1) + Web |
| **Fahrdienst-Betreiber** | Verwalten Flotte, Fahrer, Qualifikationen, Abrechnung | Web-Portal |
| **Arztpraxen** | Buchen Fahrten für Patienten, laden Verordnungen hoch | Web-Portal (Phase 3) |
| **Krankenkassen** | Prüfen, genehmigen, rechnen ab | Web-Portal (Phase 3) |
| **Organisationen** | Buchen für Mitarbeiter:innen / Klient:innen | Web-Portal |

---

## 3. Langfristige Module (aus Konzept-PDF)

### Phase 1 — Fahrer- & Unternehmens-App
- Fahrzeugverwaltung: Typ, Größe, Ausstattung (Rampe, Hebebühne, Rollstuhlplatz)
- Schichtverwaltung: Online/Offline-Status
- Auftragsmatching nach Fahrzeugausstattung und Bedarfsprofil des Fahrgastes
- Aufträge annehmen / ablehnen
- Statusführung: `Unterwegs → Ankunft → Fahrgast an Bord → Abgeliefert`
- Navigation & ETA-Anzeige
- Abrechnung: SoftPOS (Kartenzahlung am Handy via Stripe), Barzahlung, Verordnungen scannen
- Notfallzugriff: Kontaktperson des Fahrgastes einsehbar

### Phase 2 — Fahrgast-App
- Profil: Behinderung, Erkrankungen (freiwillig), Notfallkontakt, Fahrzeugpräferenzen
- Buchung: Sofort oder Termin, automatisches Fahrzeug-Matching
- Zahlungsarten: Stripe (Karte, Apple Pay, Google Pay, SEPA, Klarna, Giropay), Barzahlung, Verordnung
- Live-Tracking: Fahrerstandort und ETA in Echtzeit
- Fahrzeuge in der Nähe (auch ohne Buchung sichtbar)
- Fahrt teilen mit Angehörigen (Link per SMS / WhatsApp / E-Mail)
- Notfallbutton: informiert Fahrer & aktiviert hinterlegte Kontaktperson
- Fahrtende: Tracking stoppt automatisch

### Phase 3 — Portal für Krankenkassen & Praxen
- Fahrt für Patient:innen buchen, Verordnungen hochladen
- Prüf- und Freigabe-Workflows (Kasse genehmigt oder retourniert)
- Sammelabrechnungen, Export (CSV, xRechnung, ZUGFeRD)
- Revisionssichere Speicherung, DSGVO-konform
- Desktop-optimierte Oberfläche

### Infrastruktur (langfristig)
- Cloud (GCP oder AWS) mit Kubernetes / Docker
- PostgreSQL, Redis (Cache), Pub/Sub (Messaging)
- Auth: Keycloak oder Auth0
- CI/CD (GitHub Actions), Infrastruktur als Code (Terraform)
- Monitoring, Logging, DSGVO-Sicherheitsmaßnahmen

---

## 4. MVP-Abgrenzung

Der aktuelle MVP (access-mobility, lokale Entwicklung) deckt das Web-Portal ab —
**ohne** native Apps, externe Zahlungen, Echtzeitdienste oder Krankenkassen-Anbindung.

| Thema | MVP (jetzt) | Langfristig (später) |
|---|---|---|
| Plattform | Responsive Web-App | Native iOS/Android-Apps (Phase 1 & 2) |
| Auth | JWT, einfaches Login | Keycloak / Auth0, SSO |
| Fahrgastprofil | Mobilitätsprofil (Rollstuhl, Rampe, Escort) | Erkrankungen, Fahrzeugpräferenzen, Notfallkontakt (App) |
| Buchung | Transportanfrage erfassen (Sprint 6 ✅) + Matching & Disposition (Sprint 7 ✅) | Sofortbuchung mit Live-Matching, Fahrzeuge in der Nähe |
| Disposition | Manuelles Snapshot-Matching + Zuweisung (Sprint 7 ✅) | Automatische Optimierung, KI-gestützte Vorschläge |
| Fahrtstatus | Manuell im Portal (Dispatcher) | App-geführt durch Fahrer, Live-Updates |
| Fahrzeug-Matching | Snapshot-basiertes Regelwerk (Sprint 7 ✅) | Automatisches Echtzeit-Matching nach Ausstattung & Bedarf |
| Verordnungen | Notiz-Feld, keine echte Prüfung | Scan/Upload, Markierung als KK-abrechenbar |
| Zahlung | Keine | Stripe (Karte, Apple/Google Pay, SEPA, Klarna, Giropay), Barzahlung, Verordnung |
| Abrechnung | Keine | Sammelabrechnung, xRechnung, ZUGFeRD |
| Krankenkassen | Nicht vorhanden | Eigenes Portal mit Prüf-/Freigabe-Workflow |
| Live-Tracking | Nicht vorhanden | GPS, ETA, Fahrt teilen mit Angehörigen |
| Notfall | Nicht vorhanden | Notfallbutton (App), Kontaktperson hinterlegen |
| Infrastruktur | Lokal (Docker Compose) | Cloud, Kubernetes, Redis, Pub/Sub |

---

## 5. Themen, die bewusst später kommen

Die folgenden Punkte sind im Konzept-PDF beschrieben, aber **außerhalb des aktuellen MVP**:

- **Zahlung & SoftPOS:** Stripe-Integration, Apple/Google Pay, SEPA, Klarna, Giropay, Barzahlungsquittung
- **Krankenkassenabrechnung:** Sammelabrechnung, xRechnung, ZUGFeRD, revisionssichere Speicherung
- **Verordnungs-Workflow:** Scan/Upload von Verordnungen, KK-Markierung, Praxis-Portal
- **Live-GPS & Tracking:** Fahrerstandort in Echtzeit, ETA, Fahrt-Teilen-Funktion
- **Notfallfunktion:** Notfallbutton, automatische Aktivierung der Kontaktperson
- **Native Apps:** Fahrgast-App und Fahrer-App (iOS / Android)
- **Automatisches Matching:** Fahrzeug-Ausstattungs-Matching nach Bedarfsprofil
- **Schichtverwaltung:** Online/Offline-Status für Fahrer
- **Cloud-Infrastruktur:** GCP/AWS, Kubernetes, Terraform, Redis, Pub/Sub
- **Auth-Provider:** Keycloak / Auth0

---

## 6. Empfohlene Sprintfolge ab Sprint 3

### Sprint 3 — Auth & Benutzermodell
- JWT-Login im Backend (FastAPI, `/auth/login`, `/auth/me`)
- Passwort-Hashing (bcrypt)
- Benutzermodell + Alembic-Migration
- Login-View im Frontend, Pinia Auth-Store
- Route Guard (unauthentifiziert → `/login`)
- Rollenvorbereitung (Enum im User-Modell, noch kein vollständiges RBAC)

### Sprint 4 — Stammdaten: Organisationen, Fahrzeuge, Fahrer
- SQLAlchemy-Modelle + Migrationen: `Organization`, `Vehicle`, `Driver`, `Qualification`, `MobilityProfile`
- CRUD-Endpoints für alle Stammdaten
- Pinia Stores + List-/Detail-Views im Frontend
- Mobilitätsprofil: GET + PUT für eigenes Nutzerprofil
- Grundlage für das spätere Matching (Ausstattungsmerkmale bereits modelliert)

### Sprint 5 — Fahrtenbuchung (Einzelfahrt)
- `Ride`-Modell + Alembic-Migration
- Statusmaschine: `pending → confirmed → in_progress → completed → cancelled`
- Buchungs-Wizard (Stepper): Fahrgast → Adresse → Zeit & Anforderungen → Bestätigung
- Dispatcher-View: Fahrer + Fahrzeug einer Fahrt zuordnen
- Fahrer-View: eigene Aufträge, Statuswechsel
- Buchung für andere Person (Org-Koordinator-Flow)

### Sprint 6 — Fahrt-/Transportanfrage Grundlage ✅ (abgeschlossen)
- `TransportRequest`-Modell (status: draft/requested/cancelled)
- Alembic-Migration, JSONB-Snapshots (requirement + mobility profile)
- 6 REST-Endpunkte: list, create, get, update, submit, cancel
- TransportRequestView (Liste + Formular-Wizard), Pinia Store, Route `/transport-requests`
- Sidebar, Dashboard-KPI-Kachel, Seed-Daten

### Sprint 7 — Manuelles Matching & Disposition ✅ (abgeschlossen)
- `assigned`-Status + 5 Zuweisungsfelder direkt auf `TransportRequest` (kein separates `Ride`-Modell)
- Snapshot-basiertes Matching: 8 Fahrzeugregeln + 6 Fahrerregeln, 3 Match-Level (suitable/warning/unsuitable)
- 3 neue Endpoints: GET `matching-options`, POST `assign`, POST `unassign`
- Disposition als Entscheidungshilfe — kein automatischer Block durch Matching
- Frontend: Disposition-Abschnitt in `TransportRequestView`, Matching-Karten, Zuweisungsformular, Unassign
- Dashboard: `assignedCount` in KPI-Kachel
- 14 Pytest-Tests (alle grün), TypeScript ✅, Build ✅

### Sprint 8 — Fahrtstart & Fahrerverwaltung
- Fahrer-Dashboard, Tagesaufträge, Statuswechsel (unterwegs → abgeschlossen)
- Schichtverwaltung (Online/Offline-Status)

### Sprint 8+ — Erweiterungen (Reihenfolge nach Priorität)
- Verordnungs-Upload (Datei-Anhang an Fahrt, noch ohne KK-Prüfung)
- Notfallkontakt im Fahrgastprofil (Datenfeld, kein automatisierter Auslöser)
- Exportfunktion (Fahrtenliste als CSV)
- Vorbereitung Zahlungsintegration (Stripe, wenn freigegeben)
- Vorbereitung Kassen-/Praxis-Portal (eigener Bereich im Portal)
- Vorbereitung Live-Tracking (Datenmodell, ohne echtes GPS)
- Native App (wenn Web-Portal stabil und vollständig)
