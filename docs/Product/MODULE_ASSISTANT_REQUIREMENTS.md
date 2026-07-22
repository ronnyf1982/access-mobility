# Modul-Assistent-Anforderungen — access-mobility

Übergeordnete Quelle: `docs/SOURCE_OF_TRUTH.md`
Vollständiges Konzept: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`
Letzte Aktualisierung: 2026-07-16

---

## Plattform-Zuordnung der Module

Module gehören zu einer der drei Nutzungswelten (Details: `docs/Product/APP_CONCEPT.md`):

| Modul | Welt | Sprachassistenz-Priorität |
|---|---|---|
| Auth / Login | Alle | Niedrig |
| Onboarding | Fahrgast | **Hoch** |
| Mobilitätsprofil | Fahrgast | **Hoch** |
| Transporttypen / Presets | Fahrgast | **Hoch** |
| Transportanfragen | Fahrgast | **Hoch** |
| Benachrichtigungseinstellungen | Fahrgast | **Hoch** |
| Live-Standort & Statusfreigabe | Fahrgast | **Hoch** |
| Fahrzeugprofile | Dispo/Admin | Niedrig |
| Fahrerprofile | Dispo/Admin | Niedrig |
| Matching / Disposition | Dispo/Admin | Niedrig |
| Dashboard | Alle (rollenabhängig) | Niedrig |
| Schichtstart & Fahrzeugwahl | Fahrer | Mittel |
| Fahrtstatus / Statuswechsel | Fahrer | **Hoch** |
| Tourenliste | Fahrer | Mittel |

---

## Zweck dieses Dokuments

Für jedes Modul wird hier festgehalten:
- Welche strukturierten Felder es hat
- Wie die visuelle Bedienung funktioniert
- Was der Sprachassistent können muss
- Was offline möglich ist
- Wo eine explizite Bestätigung erforderlich ist
- Welche Datenschutzaspekte zu beachten sind

**Pflicht:** Bei jedem neuen Modul muss ein Eintrag hier ergänzt werden.

---

## Legende für Tabellen

- **Strukturierte Felder:** Checkboxen, Enums, Zahlen, Datum/Zeit — keine Freitext-only-Felder
- **Sprach-/Assistenzmodus:** Was der Assistent können muss (Fragen, Vorbefüllen, Bestätigen)
- **Offline möglich?** ✅ = vollständig offline, ⚠️ = eingeschränkt, ❌ = nur online
- **Online-KI sinnvoll?** ✅ = ja, ⚠️ = begrenzt, ❌ = nicht nötig
- **Bestätigung erforderlich?** ✅ = immer vor Aktion, — = nur Lesen

---

## Aktuelle Module (Sprint 10-Stand)

### Auth / Login

| Aspekt | Details |
|---|---|
| **Zweck** | Nutzer authentifizieren, Rolle bestimmen, Session aufbauen |
| **Strukturierte Felder** | E-Mail (Text, validiert), Passwort (verdeckt), Rolle (aus JWT) |
| **Visuelle Bedienung** | Login-Formular, Demo-User-Auswahl, Passwort anzeigen/verbergen |
| **Sprach-/Assistenzmodus** | E-Mail diktieren, Passwort per Tastatur eingeben (Sicherheit), Rolle vorlesen |
| **Offline möglich?** | ❌ (Authentifizierung erfordert Backend) |
| **Online-KI sinnvoll?** | ❌ (kein KI-Bedarf bei Login) |
| **Bestätigung erforderlich?** | — (Login ist bewusste Aktion) |
| **Datenschutz** | Passwort niemals loggen, Token in localStorage (MVP-akzeptiert) |

---

### Onboarding (ab Sprint 8)

| Aspekt | Details |
|---|---|
| **Zweck** | Neuen Nutzer einrichten: Profil-Grunddaten, Sprachassistenz-Wahl, erste Bedarfserfassung |
| **Strukturierte Felder** | Vorname, Nachname, Telefon, Sprachassistenz-Aktivierung (Boolean), Erstbedarf |
| **Visuelle Bedienung** | Schritt-für-Schritt-Wizard, 3–5 Schritte, große Elemente |
| **Sprach-/Assistenzmodus** | Frage: „Möchten Sie Sprachführung aktivieren?" → Ja/Nein → Vollständige Sprachführung durch alle Onboarding-Schritte |
| **Offline möglich?** | ⚠️ (Stammdaten offline erfassbar, Speichern erfordert Backend) |
| **Online-KI sinnvoll?** | ⚠️ (KI kann Bedarfserkennung verbessern, aber nicht nötig im Basis-Onboarding) |
| **Bestätigung erforderlich?** | ✅ vor Profil-Speichern |
| **Datenschutz** | Keine sensiblen Gesundheitsdaten im Onboarding-Schritt — erst im Mobilitätsprofil |

**Assistenten-Dialogschritte:**
1. „Wie heißen Sie?" → first_name, last_name
2. „Unter welcher Telefonnummer sind Sie erreichbar?" → phone
3. „Möchten Sie die Sprachführung für alle Formulare aktivieren?" → voice_mode_enabled
4. „Haben Sie einen besonderen Mobilitätsbedarf, den wir von Anfang an berücksichtigen sollen?" → Überleitung zu Mobilitätsprofil

---

### Mobilitätsprofil

| Aspekt | Details |
|---|---|
| **Zweck** | Dauerhaften Mobilitätsbedarf des Fahrgastes erfassen — Grundlage für Matching |
| **Strukturierte Felder** | 11 Bedarfs-Flags (Bool), 14 med. Detailfelder (Bool + Enum), Notfallkontakt (Text) |
| **Visuelle Bedienung** | 5 Abschnitte, Toggle-Karten mit Icon + Text, kontextsensitive Zusatzfelder |
| **Sprach-/Assistenzmodus** | Für jeden der 11 Basisbedarfe eine Ja/Nein-Frage; med. Felder nur bei positivem Trigger |
| **Offline möglich?** | ⚠️ (Felder offline erfassbar, Speichern erfordert Backend) |
| **Online-KI sinnvoll?** | ✅ (Nutzer kann Bedarf freitextlich beschreiben → KI befüllt Felder vor) |
| **Bestätigung erforderlich?** | ✅ vor Speichern des Profils |
| **Datenschutz** | Medizinische Felder sind freiwillig (nie Pflichtfeld); Art. 9 DSGVO beachten bei KI-Weitergabe |

**Assistenten-Dialogschritte — implementierter Offline-Katalog (Sprint 9):**
Fragenkatalog: `frontend/src/data/mobilityAssistantQuestions.ts`

| # | Frage (Kurzform) | Felder bei Ja |
|---|---|---|
| 1 | Sprachführung aktivieren? | `voice_mode_enabled` (User) |
| 2 | Blind oder sehbehindert? | `is_blind_or_visually_impaired` |
| 3 | Einstiegshilfe benötigt? | `needs_entry_assistance` |
| 4 | Tür-zu-Tür-Begleitung? | `needs_door_to_door_assistance` |
| 5 | Darf nicht allein warten? | *(Feld fehlt: `may_not_wait_alone` — Roadmap Sprint 10)* |
| 6 | Rollstuhlnutzer? | `uses_wheelchair` + `requires_wheelchair_space` |
| 7 | Rollator? | `uses_rollator` |
| 8 | Liegendtransport? | `needs_stretcher_transport` |
| 9 | Sauerstoff / med. Gerät? | `brings_oxygen` + `brings_medical_device` |
| 10 | Begleitperson? | `needs_escort` |

**Sprint 9B — Spracheingabe im geführten Check:**
- TTS-Flow: Frage vorlesen → fragen ob Optionen vorgelesen werden sollen → nur auf Anfrage vorlesen
- STT: Nur auf expliziten Nutzerwunsch (Button); kein dauerhaftes Mithören
- Bestätigungs-Dialog vor Übernahme jeder gesprochenen Antwort
- Tastaturkürzel: J / N / W / S / H / R / ← / Esc
- Utility: `frontend/src/utils/speech.ts`

---

### Transporttypen / Schnellauswahl-Presets

| Aspekt | Details |
|---|---|
| **Zweck** | Vorauswahl eines Transportprofils, das passende Felder im Mobilitätsprofil vorbefüllt |
| **Strukturierte Felder** | 5 Preset-IDs (Enum), preset_controlled_profile_fields (Array), suggested_field_values (Dict) |
| **Visuelle Bedienung** | 5 Kacheln mit Icon, Titel, Beschreibung, optional Warnhinweis |
| **Sprach-/Assistenzmodus** | „Welche Art von Transport benötigen Sie?" → Liste vorlesen → Auswahl per Sprache |
| **Offline möglich?** | ✅ (Preset-Liste statisch konfiguriert, kein API-Aufruf nötig) |
| **Online-KI sinnvoll?** | ✅ (Nutzer beschreibt Situation → KI wählt passendes Preset) |
| **Bestätigung erforderlich?** | ✅ vor Übernehmen der vorbefüllten Felder ins Profil |
| **Datenschutz** | Keine sensiblen Daten in Preset-Auswahl |

---

### Fahrzeugprofile

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrzeugflotte des Fahrdiensts erfassen — Grundlage für Matching |
| **Strukturierte Felder** | VehicleType (Enum, 7 Werte), 25 Bool-Ausstattungsfelder, Maße/Gewicht (Integer/Float) |
| **Visuelle Bedienung** | Liste + Inline-Formular, Toggle-Karten, Soft-Delete, Reaktivierung |
| **Sprach-/Assistenzmodus** | Für Provider-Admins nachrangig — keine Sprachassistenz-Priorität in Sprint 8 |
| **Offline möglich?** | ❌ (Fahrzeugdaten müssen persistent gespeichert werden) |
| **Online-KI sinnvoll?** | ⚠️ (KI könnte Fahrzeugdaten aus Kennzeichen/Typschein vorausfüllen — spätere Phase) |
| **Bestätigung erforderlich?** | ✅ vor Speichern, vor Löschen/Deaktivieren |
| **Datenschutz** | Keine personenbezogenen Daten in Fahrzeugprofilen |

---

### Fahrerprofile

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrerqualifikationen erfassen — Grundlage für Matching |
| **Strukturierte Felder** | 23 Qualifikations-Flags (Bool, 3 Kategorien), Verknüpfung mit User |
| **Visuelle Bedienung** | Liste + Inline-Formular, Qualifikations-Badges, Avatar-Initialen, Soft-Delete |
| **Sprach-/Assistenzmodus** | Für Provider-Admins nachrangig — Fahrerpflege primär visuell |
| **Offline möglich?** | ❌ |
| **Online-KI sinnvoll?** | ❌ (Qualifikationen sind binär — kein KI-Interpretationsbedarf) |
| **Bestätigung erforderlich?** | ✅ vor Speichern, vor Deaktivieren |
| **Datenschutz** | Qualifikationsdaten sind arbeitsbezogen, nicht als med. Daten einzustufen |

---

### Transportanfragen

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrgast erstellt Transportanfrage, sendet sie ab |
| **Strukturierte Felder** | passenger_user_id, transport_type_id, pickup/destination_address, pickup_date/time, selected_profile_fields (Array) |
| **Visuelle Bedienung** | Wizard-Light (4 Schritte), Adressfelder, Datum/Zeit-Picker, Anforderungsübersicht |
| **Sprach-/Assistenzmodus** | Vollständige Sprachführung durch alle 4 Schritte (Sprint 12-Ziel); Sprint 8: Grundvorbereitung |
| **Offline möglich?** | ⚠️ (Draft lokal speicherbar, Absenden erfordert Backend) |
| **Online-KI sinnvoll?** | ✅ (Adresseingabe vereinfachen, Datum aus Kontext erkennen, Anforderungen aus Beschreibung extrahieren) |
| **Bestätigung erforderlich?** | ✅ explizit vor Absenden (draft → requested) |
| **Datenschutz** | Snapshot eingefroren beim Absenden — danach unveränderlich |

**Assistenten-Dialogschritte (Zielzustand Sprint 12):**
1. „Welche Art von Transport benötigen Sie?" → transport_type_id
2. „Von welcher Adresse werden Sie abgeholt?" → pickup_address
3. „Wohin möchten Sie?" → destination_address
4. „Wann soll die Fahrt stattfinden?" → pickup_date + pickup_time
5. „Ich habe Ihre Anforderungen aus Ihrem Profil übernommen: ... Stimmt das so?" → Bestätigung
6. „Soll ich die Anfrage jetzt absenden?" → Absenden-Bestätigung

---

### Matching / Disposition

| Aspekt | Details |
|---|---|
| **Zweck** | Disponent weist Transportanfragen Fahrzeugen und Fahrern zu |
| **Strukturierte Felder** | assigned_vehicle_id, assigned_driver_id, match_level (suitable/warning/unsuitable) |
| **Visuelle Bedienung** | Matching-Karten mit Ampel-Bewertung, Zuweisungsformular, Unassign-Funktion |
| **Sprach-/Assistenzmodus** | Für Disponenten: nachrangig; Matching-Ergebnisse vorlesbar |
| **Offline möglich?** | ❌ (Matching erfordert Datenbank-Abfrage) |
| **Online-KI sinnvoll?** | ✅ (KI kann Matching-Vorschlag begründen, Ausnahmen erklären — Sprint 11) |
| **Bestätigung erforderlich?** | ✅ vor Zuweisung, vor Unassign |
| **Datenschutz** | Disponenten sehen nur Kontaktdaten + Bedarfsfelder, keine medizinischen Diagnosen |

---

### Dashboard

| Aspekt | Details |
|---|---|
| **Zweck** | Überblick über KPIs, Schnellzugriff auf wichtigste Funktionen |
| **Strukturierte Felder** | Zählwerte (Integer), rollenbasierte Ansicht |
| **Visuelle Bedienung** | KPI-Kacheln, Fahrtenliste, Profilstatus-Karte, Links |
| **Sprach-/Assistenzmodus** | KPIs vorlesbar; „Wie viele Anfragen habe ich heute?" → Antwort vorlesen |
| **Offline möglich?** | ❌ (Live-Daten aus Backend) |
| **Online-KI sinnvoll?** | ⚠️ (KI-basierte Tagesübersicht für Disponenten — späte Phase) |
| **Bestätigung erforderlich?** | — (nur Lesen) |
| **Datenschutz** | Rollenfilterung: Fahrgäste sehen nur eigene Daten |

---

### Fahrer-Schichtstart & Fahrzeugwahl (Sprint 10)

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrer meldet sich für Schicht an, wählt Fahrzeug per Kennzeichen, kann Schicht pausieren/beenden |
| **Strukturierte Felder** | `vehicle_id` (UUID oder Kennzeichen), `ShiftStatus` (active/paused/ended), `started_at`, `ended_at`, `break_started_at`, `notes` |
| **Visuelle Bedienung** | `DriverDashboardView`: Schichtstatus-Karte, Kennzeichen-Suchfeld, Fahrzeugtreffer-Liste, Pause/Beenden-Buttons mit Bestätigungsdialog, Tagesauftragsliste (read-only) |
| **Sprach-/Assistenzmodus** | `voice_mode: "voice_later"` — Spracheingabe geplant für späteren Sprint; vorerst nur visuell |
| **Offline möglich?** | ❌ (Datenbank-Lookup für Kennzeichen-Suche und Schichtstatus) |
| **Online-KI sinnvoll?** | ❌ (Schichtdaten sind strukturiert — kein KI-Bedarf) |
| **Bestätigung erforderlich?** | ✅ vor Schichtstart, Pause, Beenden |
| **Datenschutz** | Keine sensiblen Personendaten — nur Fahrzeug-ID und Zeitstempel |

**Implementierter Stand (Sprint 10 / Sprint 10B):**
- Backend: `DriverShift`-Modell, Migration `driver_shifts`, CRUD + 7 Endpoints unter `/driver/...` inkl. `GET /driver/me`
- `DriverProfile.default_vehicle_id` (nullable FK vehicles) + Migration, Seed-Daten: driver@access.test → AM-BUS-1
- Frontend: `DriverDashboardView` (mobile-first, große Buttons), Route `/driver`, Sidebar „Meine Schicht"
- Zwei Szenarien: Standardfahrzeug direkt anzeigen / Kennzeichen-Suche falls kein Standardfahrzeug
- Auftragsstruktur: „Linienfahrten" (Platzhalter) + „Spontane Fahrten" (aus assignments)
- Noch keine STT-Spracheingabe — voice_mode: "voice_later" (Sprint 11+)
- Sicherheitsnotizen: keine Statusänderung ohne Bestätigung, Schicht beenden nur nach Dialog

---

### Spontane Fahrt — Buchung, Tracking & Auto-Rematch (Sprint 12B–12K)

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrgast bucht sofort ein verfügbares, passendes Fahrzeug in der Nähe ohne Vorlaufzeit |
| **Strukturierte Felder** | `pickup_latitude/longitude`, `pickup_address`, `destination_address`, `rematch_group_id` (UUID), `rematch_attempt` (INT 0–3) |
| **Visuelle Bedienung** | `SpontaneousRideView`: Phasen Idle → Locating → Results → Booked; Karte + Textliste; Tracking-Statusbanner; Rematch-Infobanner; "Fahrt stornieren"-Button |
| **Sprach-/Assistenzmodus** | Hoch priorisiert für spätere Sprints: GPS-Standort diktieren, Zieladresse per Sprache, Fahrzeug vorlesen, Storno per Sprache |
| **Offline möglich?** | ❌ (GPS-Abfrage, Matching und Buchung erfordern Backend) |
| **Online-KI sinnvoll?** | ⚠️ (Zieladress-Interpretation per KI sinnvoll, Matching-Logik ist regelbasiert) |
| **Bestätigung erforderlich?** | ✅ vor Buchung; Stornierung immer explizit |
| **Datenschutz** | Standort nur nach ausdrücklichem Klick; kein Hintergrundtracking; kein Standortverlauf; Fahrer-GPS nur in `DriverShift.current_latitude/longitude` |

**Implementierter Stand (Sprint 12K-Stand):**
- Matching: Haversine-Luftlinie, ETA `max(3, int(km/30*60))`, Capability-Check, Verfügbarkeitscheck
- Buchung: `POST /spontaneous-rides/book` setzt `rematch_group_id=uuid4()` + `rematch_attempt=0`
- Tracking: `GET /{id}/tracking` liefert `can_track`, `next_request_id`, `request_expires_at`
- Timeout-Endpoint: `POST /{id}/timeout` (Frontend-getriggert nach `created_at + 120s`)
- Auto-Rematch: `do_rematch()` in `spontaneous_matching.py`; max. 3 Versuche; schließt alle Fahrer der Gruppe aus
- Stornierung: `POST /{id}/cancel` — manuelle Stornierung löst keinen Rematch aus
- Frontend: Rematch-Banner; Polling folgt `next_request_id`-Kette; endgültige Ablehnung zeigt Fehler + "Erneut suchen"
- Fahrer: Verfügbarkeit (12I) + Ablehnung (12J/12K: ruft `do_rematch()` auf) + Statusfluss (11/12G)

---

## Geplante Module (zukünftige Sprints)

### Fahrt per Sprache anfragen (Sprint 14)

| Aspekt | Details |
|---|---|
| **Zweck** | Vollständige Fahrtbuchung über Sprachführung |
| **Strukturierte Felder** | Alle Felder der Transportanfrage |
| **Sprach-/Assistenzmodus** | Vollständiger Buchungsdialog per Sprache (Online-KI + Offline-Fallback) |
| **Offline möglich?** | ⚠️ (Offline-Fragenkatalog als Fallback) |
| **Online-KI sinnvoll?** | ✅ (Kern-Feature dieses Sprints) |
| **Bestätigung erforderlich?** | ✅ explizit vor Absenden |

---

### KI-Berater (Sprint 11)

| Aspekt | Details |
|---|---|
| **Zweck** | KI hilft Fahrgästen, den richtigen Transporttyp und die richtigen Anforderungen zu wählen |
| **Strukturierte Felder** | Alle Mobilitätsprofil- und Anforderungsfelder (als Zielwerte) |
| **Sprach-/Assistenzmodus** | Natürlichsprachiger Dialog → strukturierte Felder → Bestätigung |
| **Offline möglich?** | ❌ (KI-Verarbeitung online) |
| **Online-KI sinnvoll?** | ✅ (Kern-Feature dieses Sprints) |
| **Bestätigung erforderlich?** | ✅ immer vor Profil- oder Anfrage-Übernahme |
| **Datenschutz** | Keine unnötige Weitergabe med. Details; Zustimmung erforderlich |

---

### Benachrichtigungseinstellungen (Sprint 11)

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrgast konfiguriert, wer bei welchen Fahrt-Ereignissen wie benachrichtigt wird |
| **Strukturierte Felder** | recipient_name, phone, email, is_app_user, can_see_live_location, can_receive_status_updates, notify_channels (Array), events (Array) |
| **Visuelle Bedienung** | Liste der Vertrauenspersonen + Toggles für Kanäle und Ereignisse |
| **Sprach-/Assistenzmodus** | „Meine Tochter soll benachrichtigt werden, wenn ich zugestiegen bin." → Konfiguration vorschlagen + bestätigen |
| **Offline möglich?** | ⚠️ (Einstellungen lokal änderbar, Sync erfordert Backend) |
| **Online-KI sinnvoll?** | ⚠️ (KI kann Empfänger aus Kontext erkennen) |
| **Bestätigung erforderlich?** | ✅ vor Speichern der Benachrichtigungseinstellungen |
| **Datenschutz** | Keine med. Details in Nachrichten; Standortdaten nur wenn explizit erlaubt |

---

### Fahrtstatus / Fahrer-App-Grundlage (Sprint 11)

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrtstatus-Ereignisse erfassen — Grundlage für Live-Tracking und Benachrichtigungen |
| **Strukturierte Felder** | RideStatusEvent: ride_id, status (Enum), timestamp, location (nullable), source |
| **Visuelle Bedienung** | Statuswechsel-Buttons in Fahrer-App (unterwegs / angekommen / an Bord / abgeliefert) |
| **Sprach-/Assistenzmodus** | „Fahrgast ist zugestiegen" → Bestätigung → Status setzen |
| **Offline möglich?** | ⚠️ (lokal queuen, bei Online-Gang senden) |
| **Online-KI sinnvoll?** | ❌ |
| **Bestätigung erforderlich?** | ✅ bei sicherheitskritischen Statuswechseln |
| **Datenschutz** | Standort bei Statuswechsel nur speichern wenn erlaubt |

---

### Live-Standort & Statusfreigabe (Sprint 12)

| Aspekt | Details |
|---|---|
| **Zweck** | Fahrgast teilt Fahrtstatus und optional Standort mit berechtigten Personen |
| **Strukturierte Felder** | LiveLocationShare: share_token, expires_at, revoked_at, share_channel (Enum), recipient_user_id / _name / _phone / _email |
| **Visuelle Bedienung** | Button „Fahrt teilen" (Fahrgast), Empfänger-Anzeige, Button „Teilen beenden", Vertrauenspersonen-Ansicht (Status + ETA) |
| **Sprach-/Assistenzmodus** | „Teile meine Fahrt mit meiner Tochter." → Bestätigungsdialog (Empfänger + Art + Dauer) → erst dann teilen |
| **Offline möglich?** | ❌ (Freigabe erfordert Backend) |
| **Online-KI sinnvoll?** | ⚠️ (KI kann Empfänger aus Kontext erkennen: „meine Tochter" → Anna Müller aus TrustedRelationship) |
| **Bestätigung erforderlich?** | ✅ immer — vor Aktivierung UND vor Widerruf |
| **Datenschutz** | Standortdaten sensibel; zeitliche Begrenzung; Widerruf; Protokollierung (wer/wann/mit wem/bis wann); keine medizinischen Details an Empfänger |

**Assistenten-Sprachbefehle:**

| Befehl | Aktion |
|---|---|
| „Teile meine Fahrt mit meiner Vertrauensperson." | Freigabe-Dialog starten |
| „Schick meiner Tochter meinen Standort." | Empfänger identifizieren + Dialog |
| „Sag meiner Einrichtung, wann ich ankomme." | Statusmeldung-Freigabe starten |
| „Beende die Standortfreigabe." | Widerruf mit Bestätigung |
| „Wer kann meinen Standort sehen?" | Aktive Freigaben vorlesen |

**Pflichtinhalt des Bestätigungsdialogs:**
1. Empfänger nennen
2. Art der Freigabe (Status / Standort)
3. Gültigkeitsdauer nennen
4. Explizites Ja abwarten

---

### Tourenplanung (Sprint 17)

| Aspekt | Details |
|---|---|
| **Zweck** | Optimierte Tourenplanung für mehrere Anfragen an einem Tag |
| **Strukturierte Felder** | Reihenfolge (Integer), tour_id, vehicle_id, driver_id, time_slots |
| **Sprach-/Assistenzmodus** | Tourplan vorlesen; Änderungen per Sprache — nachrangig |
| **Offline möglich?** | ❌ |
| **Online-KI sinnvoll?** | ✅ (KI-Optimierung ist Kern-Feature) |
| **Bestätigung erforderlich?** | ✅ vor Tourenveröffentlichung |
