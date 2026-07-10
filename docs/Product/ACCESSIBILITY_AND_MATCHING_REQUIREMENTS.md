# Accessibility & Matching — Anforderungen

Freigegeben: 2026-07-10  
Status: **Dokumentiert — noch keine technische Umsetzung in diesem Schritt.**  
Vollständige Architekturentscheidung: `docs/DECISIONS.md` → Abschnitt „Accessibility-first"

---

## Zielbild

Access Mobility wird **accessibility-first** entwickelt. Die Plattform richtet sich
an Menschen, die auf barrierefreie Mobilität angewiesen sind. Barrierefreiheit ist
deshalb kein optionales Feature, sondern Grundlage jeder Entwicklungs- und
Designentscheidung — von der Datenbankstruktur bis zur Bedienoberfläche.

Das Zielbild: Eine Person, die blind ist, einen Rollstuhl nutzt oder motorisch
eingeschränkt ist, kann eine Fahrt vollständig selbstständig buchen — oder eine
Vertrauensperson kann es stellvertretend für sie tun.

---

## Fahrgast-Bedienprinzipien

Die Buchungsoberfläche für Fahrgäste folgt diesen unveränderlichen Prinzipien:

1. **Wizard-Prinzip:** Eine Entscheidung pro Schritt. Kein Schritt überlastet den Nutzer
   mit mehreren gleichzeitigen Wahlmöglichkeiten.

2. **Große Bedienelemente:** Alle interaktiven Elemente haben mindestens 44 × 44 px
   Klickfläche (WCAG 2.5.5 Target Size).

3. **Icon + Text immer gemeinsam:** Kein Icon ohne sichtbaren Textlabel.
   Kein Text-only-Element, wenn ein Icon die Verständlichkeit verbessert.

4. **Einfache Sprache:** Klare, kurze Sätze. Keine Fachbegriffe ohne Erklärung.
   Kein Verwaltungsjargon in der Fahrgastoberfläche.

5. **Keine überladenen Ansichten:** Fahrgäste sehen nur das, was für ihre Buchung
   relevant ist. Verwaltungsfunktionen (Disposition, Abrechnung, Org-Management)
   sind ausschließlich im Portal für Fahrdienste und Organisationen sichtbar.

6. **Rückgängig & Korrektur:** Fahrgäste können jeden Buchungsschritt zurückgehen
   und korrigieren, bevor sie bestätigen.

---

## Anforderungen für blinde und sehbehinderte Menschen

- Alle UI-Elemente haben aussagekräftige `aria-label`- oder `aria-labelledby`-Attribute
- Bilder und Icons haben `alt`-Text oder `aria-hidden="true"` (wenn dekorativ)
- Statusänderungen werden über `aria-live`-Regionen angekündigt
  (z. B. „Fahrt bestätigt", „Fehler beim Speichern")
- Formulare: Jedes Feld hat ein programmatisch verknüpftes `<label>`
- Fehlermeldungen: mit `aria-describedby` an das betroffene Feld gebunden,
  vorlesbar durch Screenreader
- Fokusreihenfolge: logisch, der visuellen Lesereihenfolge folgend
- Modale Dialoge: Fokus wird beim Öffnen hineinversetzt, beim Schließen zurückgegeben
- Farbe ist nie das einzige Unterscheidungsmerkmal (Status immer zusätzlich mit Icon/Text)
- Kontrastverhältnis: mindestens WCAG AA (4.5:1 für Text, 3:1 für UI-Elemente)
  — Ziel WCAG AAA (7:1) für Kernbereiche der Fahrgastoberfläche

---

## Anforderungen für Sprachführung / Sprachmenü

> **Nicht im MVP — späteres Kernfeature.**

Langfristig sollen Fahrgäste Fahrten per Spracheingabe buchen können:

- Sprachgesteuerte Navigation durch den Buchungs-Wizard
- Sprachausgabe (Text-to-Speech) für alle Schritte und Bestätigungen
- Vereinfachter Dialogflow: Abfahrtsort → Zielort → Datum & Uhrzeit → Bestätigung
- Unterstützung für Plattform-Sprachassistenten (Browser-native SpeechRecognition API)
- Fallback auf manuelle Eingabe jederzeit möglich

Technische Voraussetzungen (spätere Sprints):
- Web Speech API (Speech Recognition + Speech Synthesis) oder externer TTS-Dienst
- Sprachdialog-Zustandsmaschine
- Barrierefreie Aktivierungsmöglichkeit (Button mit `aria-label="Sprachbuchung starten"`)

---

## Anforderungen für Angehörigen- / Remote-Buchung

Dritte Personen müssen Fahrten **für Fahrgäste stellvertretend buchen** können.

### Im MVP (bereits umsetzbar)

- Organisations-Koordinator kann Fahrt für Org-Mitglied buchen
- Fahrt trägt Fahrgast als Passagier, Koordinator als Buchender

### Später — Vertrauenspersonen-Modell

- Fahrgast kann bestimmten Personen (Angehörige, Betreuer:innen) explizit erlauben,
  Fahrten für ihn/sie zu buchen
- Einladung per E-Mail oder Link
- Vertrauensperson sieht nur Fahrten des/der Fahrgastes — keine anderen Daten
- Fahrgast kann Berechtigungen jederzeit entziehen
- Protokollierung: wer hat wann eine Fahrt für wen gebucht

Erfordert separates Datenmodell: `TrustedPerson`-Relation zwischen zwei `User`-Einträgen
mit explizitem Genehmigungsstatus.

---

## Mobilitätsbedarfe — vollständige Liste

Fahrgäste wählen ihren Bedarf über **eindeutige Icons mit Textlabel** aus.
Mehrfachauswahl ist möglich (z. B. Rollstuhl + Begleitperson).

| ID | Bezeichnung | Beschreibung |
|---|---|---|
| `wheelchair` | Rollstuhl | Manueller Rollstuhl, Transport im Fahrzeug |
| `wheelchair_electric` | Elektrorollstuhl | Elektrischer Rollstuhl (höheres Gewicht, mehr Platz) |
| `rollator` | Rollator | Gehhilfe, wird ggf. im Fahrzeug verstaut |
| `crutches` | Krücken / Gehstützen | Einstiegshilfe empfohlen |
| `blind` | Blind / sehbehindert | Fahrer:in holt Fahrgast an der Tür ab, verbale Führung |
| `deaf` | Gehörlos / hörbehindert | Schriftliche Kommunikation, kein Signalhorn |
| `escort` | Begleitperson | Eine Begleitperson fährt mit (Begleitplatz erforderlich) |
| `boarding_aid` | Einstiegshilfe | Fahrer:in unterstützt beim Ein-/Aussteigen |
| `ramp` | Rampe erforderlich | Fahrzeug muss über Auffahrrampe verfügen |
| `lift` | Lift / Hebebühne | Fahrzeug muss über Hebebühne verfügen |
| `stretcher` | Liegendtransport | Fahrgast kann nicht sitzen, Transportliege erforderlich |

---

## Fahrzeugausstattungen — vollständige Liste

Fahrdienste hinterlegen die Ausstattung pro Fahrzeug.
Die Ausstattung ist die **Grundlage für das Matching** mit dem Mobilitätsbedarf des Fahrgastes.

### Allgemeine Ausstattung

| Feld (`Vehicle`) | Bezeichnung | Beschreibung |
|---|---|---|
| `seat_count` | Sitzplätze | Anzahl regulärer Sitzplätze (inkl. Beifahrer) |
| `wheelchair_space_count` | Rollstuhlplätze | Anzahl der gesicherten Rollstuhlstellplätze |
| `escort_seat_count` | Begleitplätze | Sitzplätze für Begleitpersonen |
| `has_ramp` | Rampe | Auffahrrampe vorhanden (manuell oder elektrisch) |
| `has_lift` | Hebebühne / Lift | Elektrische Hebebühne für Rollstühle |
| `has_wheelchair_restraint` | Rollstuhl-Sicherung | Gurtsystem zur Sicherung von Rollstühlen |
| `supports_electric_wheelchair` | E-Rollstuhl geeignet | Hebebühne + Fixierung für Elektrorollstühle ausgelegt |
| `supports_stretcher_transport` | Liegendtransport | Fahrzeug unterstützt Liegendtransport (Grundausstattung) |
| `has_child_seat` | Kindersitz | Kindersitz vorhanden oder nachrüstbar |
| `has_low_entry` | Niedriger Einstieg | Kneeling-Funktion oder abgesenkter Einstieg |
| `has_extra_wide_door` | Breite Tür | Seitentür für große Rollstühle geeignet |

### Medizinische Ausstattung / Qualifizierter Krankentransport (KTP)

> Kein Rettungsdienst, keine Notfallmedizin. Nur qualifizierter Krankentransport ohne Notfallindikation.
> Kein Notruf, keine Patientenüberwachung, keine Abrechnung mit Kostenträgern im MVP.

| Feld (`Vehicle`) | Bezeichnung | Beschreibung |
|---|---|---|
| `has_stretcher` | Transportliege | Fest eingebaute oder mitgeführte Transportliege (Gurney/Bahre) |
| `has_stretcher_mount` | Liegenaufnahme | Befestigungssystem für Krankentragen und Tragestühle |
| `has_medical_equipment_storage` | Med. Stauraum | Abgetrennter Stauraum für medizinisches Equipment (Trolley, Taschen) |
| `has_oxygen_mount` | Sauerstoffhalterung | Halterung und Sicherung für mobile Sauerstoffgeräte |
| `has_first_aid_kit` | Erste-Hilfe-Ausstattung | Erste-Hilfe-Koffer nach DIN 13157 oder höher |
| `has_hygiene_equipment` | Hygienebedarf | Schutzausrüstung, Desinfektionsmittel, Einwegmaterial |
| `supports_non_emergency_medical_transport` | Qual. Krankentransport (KTP) | Gesamtausstattung für qualifizierten Krankentransport erfüllt |
| `has_transport_chair` | Tragestuhl | Tragestuhl (Transportrollstuhl) für enge Zugänge vorhanden |
| `has_infusion_mount` | Infusionshalterung | Halterung für Infusionsständer im Patientenraum |
| `supports_two_person_crew` | Zweimann-Besatzung | Fahrzeug für 2-Personen-Besatzung ausgelegt (z. B. schwere Patienten) |
| `patient_compartment_notes` | Patientenraum-Hinweise | Freitext: z. B. Klimatisierung, Trennwand, Ladegerät |

### Maße, Gewicht & Zufahrt

> Diese Angaben dienen der späteren Routenoptimierung und Dispositionsplanung. Kein Matching-Kriterium im MVP.

| Feld (`Vehicle`) | Typ | Beschreibung |
|---|---|---|
| `vehicle_length_cm` | Integer, nullable | Fahrzeuglänge in cm |
| `vehicle_width_cm` | Integer, nullable | Fahrzeugbreite ohne Spiegel in cm |
| `vehicle_width_with_mirrors_cm` | Integer, nullable | Fahrzeugbreite mit ausgeklappten Spiegeln in cm |
| `vehicle_height_cm` | Integer, nullable | Fahrzeughöhe in cm |
| `wheelbase_cm` | Integer, nullable | Radstand in cm |
| `turning_circle_m` | Float, nullable | Wendekreis in Metern |
| `empty_weight_kg` | Integer, nullable | Leergewicht in kg |
| `gross_vehicle_weight_kg` | Integer, nullable | Zulässiges Gesamtgewicht (zGG) in kg |
| `payload_capacity_kg` | Integer, nullable | Nutzlast in kg |
| `requires_large_parking_space` | Boolean | Fahrzeug benötigt überbreiten/überlangen Stellplatz |
| `suitable_for_narrow_streets` | Boolean | Geeignet für einspurige Zuwegungen |
| `suitable_for_underground_parking` | Boolean | Tiefgaragengeeignet (Standardhöhe ≤ 2,0 m) |
| `has_parking_assist` | Boolean | Parksensor oder Kamerasystem vorhanden |
| `access_restriction_notes` | Text, nullable | Freitext: z. B. Zufahrtsbeschränkungen, geeignete Stellplätze |

---

## Erster Matching-Grundsatz

> **Das System darf eine Fahrt nur an ein Fahrzeug / einen Fahrdienst vermitteln,
> wenn Fahrgastbedarf, Fahrzeugausstattung und Fahrerqualifikation gemeinsam erfüllt sind.**

Konkret:

- `wheelchair` im Profil → Fahrzeug braucht `wheelchair_spaces ≥ 1` + `ramp` oder `lift`
- `wheelchair_electric` → zusätzlich `electric_wheelchair_suitable` + `securement`
- `escort` → `escort_seat ≥ 1`
- `stretcher` → Fahrzeug braucht `supports_stretcher_transport` = true; für KTP zusätzlich `has_stretcher` + `has_stretcher_mount`; Fahrer braucht `can_handle_stretcher`
- `blind` → Fahrer:in braucht Qualifikation `wheelchair_assistance` oder `escort`
- Kombination mehrerer Bedarfe → alle müssen gleichzeitig erfüllt sein

Das Matching-Modell wird im Backend als **Prüffunktion** implementiert, die für jede
Fahrt-Fahrzeug-Kombination einen `boolean`-Wert zurückgibt.

Automatisches Matching (Fahrt → passendes Fahrzeug ohne manuelle Zuteilung) ist
**außerhalb des MVP**. Im MVP weist der Dispatcher manuell zu — das System
prüft dabei, ob die Kombination valide ist (Validierung, kein Auto-Assign).

---

## Mobilitätsprofil — Medizinische Detailangaben (Sprint 5)

Ergänzende Felder für qualifizierten Krankentransport auf `MobilityProfile`:

| Feld | Typ | Beschreibung |
|---|---|---|
| `requires_transport_chair` | bool | Tragestuhl für Zugänge ohne Aufzug benötigt |
| `requires_two_person_assistance` | bool | Transfer/Transport erfordert zwei Personen |
| `requires_medical_transport` | bool | Qualifizierter Krankentransport (KTP) erforderlich |
| `brings_oxygen` | bool | Eigenes mobiles Sauerstoffgerät vorhanden |
| `requires_oxygen_mount` | bool | Halterung für Sauerstoffgerät im Fahrzeug erforderlich |
| `brings_medical_device` | bool | Eigenes Medizingerät wird mitgebracht (Pumpe, Monitor etc.) |
| `requires_medical_equipment_storage` | bool | Med. Stauraum im Fahrzeug erforderlich |
| `requires_infusion_mount` | bool | Infusionshalterung während der Fahrt erforderlich |
| `requires_special_positioning` | bool | Besondere Lagerungsposition während der Fahrt |
| `infection_or_hygiene_note` | bool | Hygiene-/Infektionsschutzhinweis (z. B. Isolierpflicht) |
| `requires_medical_attendant` | bool | Medizinisch qualifizierte Begleitperson notwendig |
| `attendant_type_required` | Enum `AttendantType` | Art der Begleitperson (none / escort_person / second_assistant / paramedic / medical_professional / unknown) |
| `medical_device_notes` | Text, nullable | Hinweise zu mitgebrachten Medizingeräten |
| `medical_transport_notes` | Text, nullable | Sonstige medizinische Transporthinweise |

## Fahrerqualifikationen — Vollständige Liste (Sprint 5)

### Grundqualifikationen

| Feld | Beschreibung |
|---|---|
| `can_assist_wheelchair` | Rollstuhl-Begleitung |
| `can_secure_wheelchair` | Rollstuhl-Sicherung mit Gurtsystem |
| `can_operate_lift` | Hebebühnen-Bedienung |
| `can_assist_blind_passengers` | Begleitung blinder/sehbehinderter Fahrgäste |
| `can_assist_deaf_passengers` | Kommunikation mit gehörlosen/schwerhörigen Fahrgästen |
| `can_handle_stretcher` | Liegendtransport-Begleitung |
| `has_first_aid_training` | Erste-Hilfe-Ausbildung |
| `has_passenger_transport_license` | Personenbeförderungsschein (P-Schein) |
| `can_support_medical_transport` | Qualifizierter Krankentransport (KTP) |

### Medizinische Qualifikationen

| Feld | Beschreibung |
|---|---|
| `has_sanitaetshelfer_training` | Sanitätshelfer (SanH) |
| `has_rettungshelfer_qualification` | Rettungshelfer (RH) |
| `has_rettungssanitaeter_qualification` | Rettungssanitäter (RettSan / RS) |
| `has_rettungsassistent_qualification` | Rettungsassistent (RA, veraltet / Bestandsschutz) |
| `has_notfallsanitaeter_qualification` | Notfallsanitäter (NotSan) — höchste nichtärztliche Qualifikation |
| `has_nursing_qualification` | Examinierte Pflegefachkraft |
| `has_medical_assistant_qualification` | Medizinische Fachangestellte/r (MFA) |

### Technische Zusatzausbildungen

| Feld | Beschreibung |
|---|---|
| `has_hygiene_training` | Hygieneschulung |
| `has_infection_protection_training` | Infektionsschutz nach IfSG |
| `has_wheelchair_restraint_training` | Rollstuhlsicherung (zertifiziert) |
| `has_lift_operation_training` | Liftsystem-Bedienung |
| `has_stretcher_handling_training` | Liegendtransport / Krankentrage-Ergonomie |
| `has_transport_chair_training` | Tragestuhl-Einsatz in Treppenhäusern |
| `has_oxygen_equipment_training` | Mobiles Sauerstoffgerät |

## Transporttypen (Sprint 5 / Sprint 5B)

5 vordefinierte Transportprofile über `GET /api/v1/transport-options` (ohne Auth).
Zentrale Konfiguration: `backend/app/core/transport_presets.py`.

| ID | Bezeichnung | Auto-gesetzte Profilfelder | Nicht auto-gesetzt |
|---|---|---|---|
| `accessible_ride` | Barrierefreie Fahrt | Allgemeine Mobilitätsfelder | Alle med. Detailfelder |
| `patient_ride_no_medical_care` | Patientenfahrt ohne Betreuung | Rollstuhlplatz, Einstiegshilfe, Zusatzzeit | `needs_stretcher_transport`, alle med. Felder |
| `stretcher_ride` | Liegendtransport | `needs_stretcher_transport`, `requires_special_positioning` | Med. Begleitung, Sauerstoff, Geräte |
| `qualified_medical_transport` | Qualifizierter Krankentransport (KTP) | `requires_medical_transport`, `requires_medical_attendant` (Typ: "unknown") | Sauerstoff, Geräte, Hygiene, Zweimann-Begleitung |
| `recurring_school_work_facility_route` | Wiederkehrende Schul-/Arbeits-/Einrichtungsfahrt | Allgemeine Mobilitätsfelder | Alle med. Detailfelder |

**Fachliche Begründung für konservative Presets (Sprint 5B):**
- Presets sind Vorschläge für Laien — sie beantworten „Welche Art von Fahrt brauche ich?", nicht „Was genau brauche ich medizinisch?"
- Medizinische Detailfelder (Sauerstoff, Infusion, Hygiene, Zweimann-Besatzung) sind fahrgastspezifisch — kein Preset kann sie stellvertretend für alle Fahrgäste eines Typs setzen
- Der qualifizierte Krankentransport (KTP) setzt nur das Minimum: KTP-Bedarf + Begleitungsbedarf. Alle weiteren Details füllt der Fahrgast individuell aus

Zusätzliche Felder je Transporttyp (ab Sprint 5B):
- `preset_controlled_profile_fields`: die 12 booleschen Felder, die beim Wechsel der Schnellauswahl zurückgesetzt werden
- `suggested_field_values`: nicht-boolesche Feld-Überschreibungen (z. B. `attendant_type_required: "unknown"`)

Alle `suggested_*`-Listen sind Orientierungshilfen für den Fahrgast, keine bindenden Matching-Regeln.

## Transportanfragen-Snapshots als Matching-Grundlage (Sprint 6)

Ab Sprint 6 existiert `TransportRequest` mit zwei JSONB-Spalten:

### `requirement_snapshot`
Friert die Anforderungen zum Zeitpunkt der Anfrage ein:
- `transport_type_id`: gewählter Transporttyp
- `selected_profile_fields`: Bedarfsfelder, die für diese Fahrt gelten (aus Profil + Schnellauswahl)
- `selected_field_values`: nicht-boolesche Überschreibungen (z. B. `attendant_type_required`)
- `notes`: Freitext-Hinweis für den Fahrdienst

### `mobility_profile_snapshot`
Kopie der relevanten `MobilityProfile`-Felder zum Anfragezeit­punkt:
alle booleschen Bedarfsfelder + `wheelchair_type` + `attendant_type_required`

**Warum Snapshots?**
Ein Fahrgast kann sein Profil nach der Anfrage ändern. Dispatcher und Matching-Engine
lesen den eingefrorenen Snapshot — nie das aktuelle Profil. Dadurch bleibt eine
gespeicherte Anfrage konsistent, auch wenn sich das Profil ändert.

**Snapshot als Matching-Input (Sprint 7):**
Das Matching-Modul (Sprint 7) vergleicht `requirement_snapshot.selected_profile_fields`
gegen `Vehicle`-Ausstattungsmerkmale und `DriverProfile`-Qualifikationen.
Der Snapshot ersetzt dabei das direkte Profil-Lookup — schneller, konsistenter,
revisionsicher.

---

## Abgrenzung — Umsetzungsstand

Dieses Dokument definiert **fachliche Anforderungen und Datenmodell-Grundsätze**.
Technisch umgesetzt in folgenden Sprints:

| Thema | Sprint |
|---|---|
| Mobilitätsprofil-Modell (`MobilityProfile`) | Sprint 4 ✅ |
| Fahrzeugausstattungs-Modell | Sprint 5 ✅ |
| Fahrerqualifikations-Modell | Sprint 5 ✅ |
| Mobilitätsprofil-UI (Icon-Auswahl) | Sprint 5 ✅ |
| Medizinische Detailfelder (Profil, Fahrzeug, Fahrer) | Sprint 5 ✅ |
| Transporttypen-Schnellauswahl | Sprint 5B ✅ |
| `TransportRequest`-Modell + Snapshots | Sprint 6 ✅ |
| Matching-Validierung (manuell, Dispatcher) | Sprint 7 |
| KI-Transportberater (Advisor-Modul) | nach MVP |
| Routenoptimierung (Dimensionen, Wendekreis) | nach MVP |
| Automatisches Matching | nach MVP |
| Vertrauenspersonen-Modell | nach MVP |
| Sprachführung / Sprachmenü | nach MVP |
