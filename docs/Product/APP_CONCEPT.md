# App-Konzept — access-mobility

Übergeordnete Quelle: `docs/SOURCE_OF_TRUTH.md`
Langfristige Vision: `docs/Product/PRODUCT_VISION.md`
Letzte Aktualisierung: 2026-07-22

---

## Was ist access-mobility?

Access Mobility ist eine **digitale Plattform für barrierefreie Mobilität**.

Sie ermöglicht Menschen mit besonderem Mobilitätsbedarf, spezialisierte Fahrdienste zu
buchen — per Webportal, später per Sprachassistent und nativer App.

Die Plattform verbindet:
- Fahrgäste und ihre Vertrauenspersonen
- Fahrdienste mit geeigneten Fahrzeugen und qualifizierten Fahrern
- Disponenten, die Anfragen und Ressourcen koordinieren
- Organisationen, die für ihre Mitglieder buchen

Langfristig: Krankenkassen, Praxen und Kliniken als weitere Beteiligte.

---

## Für wen ist die App?

### Fahrgäste

Menschen, die auf barrierefreie Mobilität angewiesen sind:
- Rollstuhlnutzer (manuell oder elektrisch)
- Menschen mit Rollator oder Gehhilfen
- Blinde und sehbehinderte Personen
- Gehörlose Personen
- Menschen mit Liegendtransportbedarf
- Menschen, die qualifizierten Krankentransport (KTP) benötigen
- Menschen mit medizinischen Geräten (Sauerstoff, Infusion)

Fahrgäste bedienen eine bewusst **einfach gehaltene Oberfläche**:
Wizard-Prinzip, große Elemente, Icon + Text, einfache Sprache.
Blinde Nutzer erhalten einen vollwertigen Sprachassistenz-Modus.

### Angehörige / Vertrauenspersonen

Können für Fahrgäste buchen (stellvertretend).
Im MVP: Datenmodell vorhanden (`TrustedRelationship`), UI-Ausbau folgt.
Ziel: Person A darf für Person B buchen — mit expliziter Freigabe durch B.

### Organisationen / Einrichtungen

Sozialeinrichtungen, Heime, Werkstätten, Schulen buchen für ihre Mitglieder oder Klienten.
Koordinatoren buchen im Namen der Einrichtungs-Mitglieder.
Org-Admins verwalten Mitgliederlisten, Kontingente, Abrechnungsübersichten.

### Fahrdienste (Provider)

Fahrdienst-Betreiber verwalten ihre Ressourcen:
- Fahrzeugflotte (Typ, Ausstattung, Maße, Sonderausstattung)
- Fahrerprofil mit Qualifikationen (Grundqualifikationen, medizinische Zusätze, Technikschulungen)
- Zugehörige Organisation mit Kontaktdaten und Einsatzgebiet

### Disponenten

Koordinieren den operativen Betrieb:
- Eingehende Transportanfragen prüfen
- Matching-Bewertung (suitable / warning / unsuitable) lesen
- Manuell Fahrzeug und Fahrer zuweisen
- Anfragen unassignen oder stornieren
- Direkte Kontaktdaten der Fahrgäste einsehen

### Fahrer

Erhalten ihre Tagesaufträge digital:
- **Schichtstart & Fahrzeugwahl (Sprint 10):** Schicht beginnen mit Standardfahrzeug oder Kennzeichen-Suche; Pause / Schicht beenden; Zeitstempel werden automatisch gesetzt
- **Zwei Auftragsarten:** Linienfahrten (vorgeplant, optimiert — ab Sprint 15) und Spontane Fahrten (einzelne zugewiesene TransportRequests)
- **Statuswechsel (Sprint 11):** unterwegs → angekommen → Fahrgast an Bord → abgeschlossen
- Kein Verwaltungsbereich, keine Tabellen — nur große klare Arbeitsbuttons

### Spätere Zielgruppen (Phase 3)

- Arztpraxen: buchen Fahrten für Patienten, laden Verordnungen hoch
- Krankenkassen: prüfen, genehmigen, rechnen ab
- Kliniken: Patientenlogistik

---

## Kernmodule (aktueller Stand)

| Modul | Beschreibung | Status |
|---|---|---|
| **Auth / Login** | JWT-Login, 8 Rollen, Demo-User, Route-Guard | ✅ Sprint 3 |
| **Mobilitätsprofil** | 22 Bedarfsfelder + 14 med. Detailfelder, Notfallkontakt | ✅ Sprint 4+5 |
| **Fahrzeugverwaltung** | 7 Fahrzeugtypen, 25 Ausstattungsmerkmale, Maße, Soft-Delete | ✅ Sprint 5 |
| **Fahrerverwaltung** | 23 Qualifikationsflags (3 Kategorien), Soft-Delete | ✅ Sprint 5 |
| **Transport-Presets** | 5 vordefinierte Profile, zentrales Backend-Config | ✅ Sprint 5B |
| **Transportanfragen** | Draft → Requested → Assigned / Cancelled, Snapshot-Strategie | ✅ Sprint 6+7 |
| **Matching / Disposition** | Snapshot-basiertes Matching, 3 Levels, manuelle Zuweisung | ✅ Sprint 7 |
| **Dashboard** | KPI-Kacheln, Fahrtliste, rollenbasierte Ansichten | ✅ Sprint 2+7 |
| **Assistant Core** | Sprachassistenz-Fundament, barrierefreies Onboarding | ✅ Sprint 8 |
| **Geführter Mobilitätscheck** | Offline-fähiger sprachgeführter Profil-Assistent | ✅ Sprint 9 |
| **Verbesserter Sprachassistent** | TTS-Flow, STT-Bestätigung, Tastaturkürzel | ✅ Sprint 9B |
| **Fahrer-Schichtstart & Fahrzeugwahl** | Schicht beginnen/pausieren/beenden, Standard- + Kennzeichen-Fahrzeugwahl, Auftragsstruktur | ✅ Sprint 10 |
| **Fahrtstatus / Fahrer-App** | Statusereignisse, RideStatusEvent-Protokoll | ✅ Sprint 11 |
| **Live-Status für Fahrgast** | Status + Verlauf für angefragte/geplante Fahrten, Polling | ✅ Sprint 12A |
| **Spontane Fahrten: Matching, Buchung, Live-Tracking** | Verfügbarkeitsprüfung, Buchung, Fahrerannahme, GPS-Tracking | ✅ Sprint 12B–12D |
| **Notfallkontakte & Notfallmodus** | Notfallkontakt-CRUD, Fahrer-Notfallmodus | ✅ Sprint 12E |
| **Gespeicherte Adressen & Geburtsdatum** | PassengerSavedAddress CRUD, date_of_birth | ✅ Sprint 12F |
| **Fahrer-Statusfluss & Fahrgast-Fahrtverlauf** | Nur nächster Button, Statushistorie, vergangene Fahrten | ✅ Sprint 12G+12H |
| **Fahrer-Verfügbarkeit & Stornierung** | Kein Parallel-Accept, Fahrgast-Storno, Rematch | ✅ Sprint 12I–12J |
| **Auto-Rematch & vereinfachte Buchung** | Automatische Weiterleitung, 1-Button-Buchung | ✅ Sprint 12K–12K-C |
| **Fahrer-Flow nach Rematch** | Fahrer-Storno, Fahrgast-Storno-Erkennung; Statusbuttons ⚠️ offen | ⚠️ Sprint 12K-D |
| **Mandantenfähiges Rollen- und Berechtigungsmodell** | Organizations, Rollen, Permissions, Mandantentrennung | Sprint 13 |
| **Vertrauenspersonen-View & Benachrichtigungen** | Dedizierte View, echter Notification-Dispatch | Sprint 14 |
| **Stammtouren & Linienverkehr** | Regelmäßige Fahrten, feste Fahrer-Fahrgast-Zuordnung | Sprint 15 |
| **Abwesenheits- und Ausfallmanagement** | Abmeldung, Ersatzfahrer, Zeitänderungen | Sprint 16 |
| **Stabilitätsorientierte Tourenoptimierung** | Minimale Neuplanung bei Änderungen | Sprint 17 |
| **Live-Toursteuerung** | Verkehr, ETA, Kapazitäten je Abschnitt, Navigation | Sprint 18 |

---

## Kernabläufe

### 1. Registrierung / Onboarding

Aktuell: kein öffentlicher Registrierungsfluss.
Demo-User werden über Seed-Skript angelegt.

Geplant (Sprint 8):
- Barrierefreies Erst-Onboarding: Schritt für Schritt, sprachführbar
- Frage beim ersten Start: „Möchten Sie die sprachgeführte Bedienung aktivieren?"
- Ja → sprachgeführter Fragenkatalog
- Nein → normale Einrichtung

Später:
- Selbstregistrierung für Fahrgäste
- Org-Einladungs-Workflow
- Vertrauenspersonen-Einladung

### 2. Mobilitätsprofil erfassen

Fahrgäste hinterlegen einmalig ihren Mobilitätsbedarf:
- 11 Basisbedarfe (Rollstuhl, Rampe, Blind, Gehörlos, Escort, ...)
- 14 medizinische Detailfelder (KTP, Sauerstoff, Tragestuhl, ...)
- Notfallkontakt
- Fahrzeughinweise (Freitext, ergänzend)

Beim Absenden einer Anfrage: Profil wird als Snapshot eingefroren.

Sprachassistenz: Jedes Profilfeld muss per Sprachdialog erreichbar sein.

### 3. Transportanfrage erstellen

**Fahrgast-Wizard (Schritte):**
1. Transporttyp / Schnellauswahl (5 Presets)
2. Abholadresse + Zieladresse
3. Datum + Uhrzeit
4. Anforderungs-Bestätigung (Felder aus Profil + Anpassungen)
5. Absenden

Status: `draft` → nach Absenden `requested`.

Sprachassistenz: Schritte 1–4 müssen vollständig sprachgeführt buchbar sein.

### 4. Disposition / Matching

**Disponent-Ansicht:**
- Liste aller `requested`-Anfragen
- Fahrgastdaten-Infobox (Kontakt, Notfallkontakt)
- Anforderungsdetails aus Snapshot
- Matching-Optionen: Fahrzeuge und Fahrer mit Bewertung (suitable / warning / unsuitable)
- Manuelle Zuweisung: Fahrzeug + Fahrer auswählen, bestätigen
- Status wechselt zu `assigned`
- Unassign möglich (zurück zu `requested`)

Automatisches Matching: außerhalb MVP — geplant in Sprint 15.

### 5. Fahrer-Schichtstart & Fahrzeugwahl (Sprint 10)

- Fahrer meldet sich für Schicht an
- Wählt Fahrzeug per Kennzeichen oder aus Liste
- Sieht Tagesaufträge
- Führt Statuswechsel durch: unterwegs → angekommen → Fahrgast an Bord → abgeschlossen

### 6. Sprachassistent (Sprint 8–12)

Vollständiges Konzept: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`

- Sprint 8: Assistant Core — Fundament für Sprachführung
- Sprint 9: Sprachgeführter Mobilitätscheck offline
- Sprint 12: Vollständige Fahrtbuchung per Sprache

### 6a. Drei Fahrtarten

Access Mobility unterscheidet drei technisch verschiedene Fahrtarten:

#### Angefragte/geplante Fahrt ✅ implementiert (Sprint 6–12A)
Fahrgast oder Organisation stellt Anfrage mit Vorlaufzeit. Disponent weist Fahrzeug und Fahrer zu. Status `draft → requested → assigned → completed`. Fahrgast sieht Live-Status per Polling.

#### Linienfahrt (Sprint 15)
Wiederkehrende oder fest geplante Fahrten mit Fahrplan und Reihenfolge. Disponenten konfigurieren Touren. Optimierte Fahrgastliste für Fahrer.

#### Spontane Fahrt / Sofortfahrt (Sprint 12B–12D, Hotfix 12F-A, Sprint 12I, Sprint 12J, Sprint 12K)
Fahrgast bucht jetzt sofort. GPS-Standort als Abholort (Reverse-Geocoding). System zeigt passende freie Fahrzeuge in der Nähe. Fahrer nimmt an oder lehnt ab. Kein Disponent erforderlich.

**Adressauswahl (Sprint 12F + Hotfix 12F-A):**
- Abholadresse: Standard GPS/Reverse-Geocoding; gespeicherte Adresse optional wählbar; freies Textfeld immer editierbar
- Zieladresse: gespeicherte Adresse optional wählbar; freies Textfeld immer sichtbar; Buchung ohne Zieladresse nicht möglich
- Gespeicherte Adressen (Zuhause, Schule, Werkstatt, …) in Mobilitätsprofil pflegbar (CRUD)
- Fahrer sieht Abhol- und Zieladresse im Dashboard

**Matching-Pflichtkriterien für Spontanfahrten:**
- Mobilitätsprofil des Fahrgastes (Rollstuhl, Rampe, Lift, Einstiegshilfen, med. Bedarf)
- Fahrzeugtyp und -kapazität passend
- Fahrer hat aktive Schicht, ist nicht in Pause
- Fahrer und Fahrzeug sind keiner anderen aktiven Fahrt zugewiesen
- Fahrer hat keine bereits angenommene (assigned) spontane Fahrt — Sprint 12I
- Nächstes geeignetes freies Fahrzeug (Distanz/geschätzte Ankunftszeit)

**Fahrer-Verfügbarkeit (Sprint 12I):**
- Fahrer mit `assigned` spontaner Fahrt kann keine weitere Anfrage annehmen → 409 Conflict
- Buchungsendpoint prüft ebenfalls ob Fahrer bereits aktive Fahrt hat
- Matching exkludiert Fahrer mit aktiver Fahrt aus Ergebnisliste
- Nach `ride_completed` wird Fahrer sofort wieder als verfügbar betrachtet
- Dashboard zeigt Hinweismeldung statt offener Anfragen, solange Fahrer gebunden ist

**Fahrgast-Stornierung (Sprint 12J):**
- Fahrgast kann eigene spontane Fahrt stornieren solange kein Pickup-Event gesetzt wurde
- Stornierbar: Status `spontaneous_requested` oder `assigned` ohne `passenger_picked_up`/`ride_started` Event
- Nicht stornierbar: nach Fahrgastaufnahme, nach Fahrtstart, nach Fahrtabschluss, bereits stornierte Fahrt
- Frontend: "Fahrt stornieren"-Button in aktiver Tracking-Ansicht; nach Storno zeigt Polling `cancelled`-Status + "Erneut suchen"-Button
- Fahrer: stornierte Fahrt verschwindet beim nächsten Dashboard-Poll (10s); Fahrer wird sofort wieder verfügbar
- Nach Fahrerablehnung: klarer Status "Vom Fahrer abgelehnt" + "Erneut suchen"-Button

**Automatische Weiterleitung / Auto-Rematch (Sprint 12K):**
- Bei Fahrerablehnung sucht das System automatisch den nächsten verfügbaren Fahrer (max. 3 Versuche)
- Fahrgast sieht blaues Banner „Wir suchen ein anderes Fahrzeug …" statt Fehlermeldung
- Kein UI-Reset: Fahrgast bleibt in der Tracking-Ansicht während der Weitersuche
- Alle Versuche einer Rematch-Kette teilen dieselbe `rematch_group_id` — ausgeschlossene Fahrer werden nicht erneut angefragt
- Timeout-Erkennung: Tracking-Antwort enthält `request_expires_at` (2-Minuten-Grenze); Frontend ruft Timeout-Endpoint auf wenn Anfrage abgelaufen ist → Rematch wird ausgelöst
- Endgültige Ablehnung (kein weiterer Fahrer verfügbar): klarer Fehlertext + "Erneut suchen"-Button
- Manuelle Stornierung durch Fahrgast löst keinen Rematch aus

**GPS-Datenschutz (Spontanfahrten):**
- Standort nur mit ausdrücklicher Zustimmung
- Nur für die konkrete Sofortfahrt — kein Hintergrundtracking im MVP
- Vertrauenspersonen nur gemäß Benachrichtigungseinstellungen informiert

### 6b. Live-Status & Standortfreigabe (Sprint 12A–12D)

Sprint 12A: Fahrgast sieht Status und Verlauf für angefragte/geplante Fahrten per Polling.
Sprint 12C/12D: Spontanfahrten + GPS-Standort des Fahrzeugs. Freigabe an Vertrauenspersonen.

Während einer aktiven Fahrt kann der Fahrgast seinen Fahrtstatus und optional seinen Standort
mit berechtigten Personen teilen.

**Wer teilt:**
- Fahrgast selbst (per Button in der App)
- Sprachbefehl: „Teile meine Fahrt mit meiner Vertrauensperson."

**Mit wem:**
- Vertrauenspersonen / Angehörige (in-App oder per Link)
- Betreuer / Einrichtung
- Abhol- oder Zielkontakt

**Freigabewege:**
1. **In-App-Freigabe** — Empfänger sieht Fahrtstatus + ETA in der App
2. **Link-Freigabe** — zeitlich begrenzter Token-Link, ohne Account nutzbar
3. **System-Teilen** — native Browser-Share-API (WhatsApp, SMS, E-Mail)
4. **Statusnachrichten** — „Fahrt gestartet", „Fahrzeug unterwegs", „Fahrgast abgeholt", „Angekommen"

**Datenschutz-Grundregeln:**
- Teilen ist immer freiwillig, Zustimmung erforderlich.
- Freigabe ist zeitlich begrenzt (maximal bis Fahrtende).
- Freigabe ist jederzeit widerrufbar.
- Vertrauenspersonen sehen Fahrtstatus und ETA — keine medizinischen Details.
- Sprachassistent aktiviert Freigabe nur nach ausdrücklicher Bestätigung.

Vollständige Datenschutzregeln: `docs/SOURCE_OF_TRUTH.md` (Abschnitt 7.9)
Datenmodell-Konzept: `docs/DECISIONS.md`

### 7. Tourenplanung (Sprint 15–18)

- Sprint 15: Stammtouren — feste Fahrgast-Fahrer-Zuordnung, Tourenvorlagen für tägliche Planung
- Sprint 16: Abwesenheits- und Ausfallmanagement — Krankmeldungen, Ersatzfahrzeuge, Zeitänderungen
- Sprint 17: Stabilitätsorientierte Tourenoptimierung — minimale Neuplanung bei Änderungen; Tourenvorschläge brauchen Disponent-Bestätigung
- Sprint 18: Live-Toursteuerung — Verkehr, ETA-Updates, Kapazitätsverwaltung je Tourabschnitt, Navigation

---

## MVP-Abgrenzung (was bewusst nicht im MVP ist)

- Echte Krankenkassenabrechnung
- Zahlungsintegration (Stripe, SEPA)
- Externe APIs (GTFS, Live-Maps)
- Live-GPS / Fahrzeug-Tracking
- Native Mobile App
- Push-Notifications
- Automatisches Matching (ohne Disponent)
- Öffentliche Selbstregistrierung
- Verordnungs-Upload und KK-Prüfworkflow
- Schichtverwaltung für Fahrer

---

## Wichtigste Datenmodell-Beziehungen

```
User ──────────────────────── MobilityProfile (1:1, Auto-Create)
  │
  ├── TransportRequest ──── requirement_snapshot (JSONB)
  │         │               mobility_profile_snapshot (JSONB)
  │         │
  │         ├── assigned_vehicle_id → Vehicle
  │         └── assigned_driver_id  → DriverProfile
  │
  ├── OrganizationMembership → Organization
  └── TrustedRelationship → User (Vertrauensperson)

Organization ─── Vehicle (Flotte)
              └── DriverProfile (Fahrer)
```

---

## Plattform-Architektur

Access Mobility ist **eine Plattform** — kein Verbund aus drei getrennten Systemen.

```
┌─────────────────────────────────────────────────────────┐
│              Gemeinsames Backend (FastAPI)               │
│         Gemeinsame API  ·  Gemeinsame Datenbank         │
│      Gemeinsames Auth  ·  Gemeinsames Datenmodell       │
└──────────────────────────┬──────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
   Fahrgast-App      Fahrer-App      Dispo-Webapp
  (barrierefrei,   (mobil, robust,  (Desktop, Tabellen,
   Sprache, MVP)    offline-fähig)   Matching, Admin)
```

**Rollen bestimmen Navigation, Oberfläche und Berechtigungen.**

Im MVP: Eine Web-App mit rollenabhängigen Bereichen.
Später: Fahrgast-App und Fahrer-App als eigene mobile / PWA / native Hüllen.

---

## Drei Nutzungswelten

### 1. Fahrgast-/Vertrauenspersonen-App

**Rollen:** `passenger`, `trusted_person`, `organization_coordinator`

Anforderungen an die Oberfläche:
- Extrem einfach, klar, überforderungsfrei
- Accessibility-first (Screenreader, Tastatur, Sprachassistenz)
- Mobile-first
- Wizard-Prinzip: eine Entscheidung pro Schritt
- Einfache Sprache, keine Fachbegriffe
- Große Bedienelemente (min. 44 × 44 px)
- Keine Verwaltungsfunktionen sichtbar

Kernfunktionen:
- Mobilitätsprofil pflegen
- Fahrt anfragen (Wizard)
- Fahrtstatus und Live-Standort einsehen
- Vertrauenspersonen und Benachrichtigungen konfigurieren
- Sprachassistenz für alle Kernfunktionen

### 2. Fahrer-App

**Rollen:** `driver`

Anforderungen an die Oberfläche:
- Mobile, robust, ablenkungsarm
- Wenige, große Buttons
- Keine Ablenkung durch Verwaltungsfunktionen
- Offline-fähige Kernfunktionen (Statuswechsel queuen)
- Sprachassistenz für häufige Aktionen (Sprint 11)

Kernfunktionen:
- Schicht beginnen / beenden
- Fahrzeug wählen (primär per Kennzeichen)
- Tourenliste / Tagesaufträge
- Fahrgast zugestiegen / ausgestiegen
- Pause starten / beenden
- Problem melden

### 3. Dispositions-/Admin-Webapp

**Rollen:** `provider_admin`, `dispatcher`, `platform_admin`, `organization_admin`

Anforderungen an die Oberfläche:
- Desktop-orientiert, informationsdicht
- Tabellarisch, filterbar, sortierbar
- Mehrere Aktionen gleichzeitig sichtbar
- Keine Vereinfachungs-Kompromisse zu Lasten der Funktionalität

Kernfunktionen:
- Eingehende Anfragen verwalten
- Matching und Disposition (Fahrzeug + Fahrer zuweisen)
- Tourenplanung und -optimierung (später)
- Live-Status der aktiven Fahrten überwachen
- Fahrzeuge, Fahrer, Organisationen verwalten
- Ausfallmanagement (später)

---

## Wichtigste Datenmodell-Beziehungen
