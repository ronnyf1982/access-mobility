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

| ID | Bezeichnung | Beschreibung |
|---|---|---|
| `wheelchair_spaces` | Rollstuhlplätze | Anzahl der gesicherten Rollstuhlstellplätze |
| `seats` | Sitzplätze | Anzahl regulärer Sitzplätze (inkl. Beifahrer) |
| `ramp` | Rampe | Auffahrrampe vorhanden (manuell oder elektrisch) |
| `lift` | Hebebühne / Lift | Elektrische Hebebühne für Rollstühle |
| `securement` | Fixiersystem | Gurtsystem zur Sicherung von Rollstühlen |
| `electric_wheelchair_suitable` | E-Rollstuhl geeignet | Hebebühne + Fixierung für Elektrorollstühle ausgelegt |
| `escort_seat` | Begleitplatz | Sitzplatz für Begleitperson neben Rollstuhlplatz |
| `carry_chair` | Tragestuhl | Für enge Treppenhäuser / nicht barrierefreie Zugänge |
| `stretcher` | Liegendtransport | Transportliege eingebaut oder montierbar |
| `driver_qualification` | Fahrerqualifikation | Verknüpfung mit Qualifikationen des/der Fahrer:in |

---

## Erster Matching-Grundsatz

> **Das System darf eine Fahrt nur an ein Fahrzeug / einen Fahrdienst vermitteln,
> wenn Fahrgastbedarf, Fahrzeugausstattung und Fahrerqualifikation gemeinsam erfüllt sind.**

Konkret:

- `wheelchair` im Profil → Fahrzeug braucht `wheelchair_spaces ≥ 1` + `ramp` oder `lift`
- `wheelchair_electric` → zusätzlich `electric_wheelchair_suitable` + `securement`
- `escort` → `escort_seat ≥ 1`
- `stretcher` → Fahrzeug braucht `stretcher`
- `blind` → Fahrer:in braucht Qualifikation `wheelchair_assistance` oder `escort`
- Kombination mehrerer Bedarfe → alle müssen gleichzeitig erfüllt sein

Das Matching-Modell wird im Backend als **Prüffunktion** implementiert, die für jede
Fahrt-Fahrzeug-Kombination einen `boolean`-Wert zurückgibt.

Automatisches Matching (Fahrt → passendes Fahrzeug ohne manuelle Zuteilung) ist
**außerhalb des MVP**. Im MVP weist der Dispatcher manuell zu — das System
prüft dabei, ob die Kombination valide ist (Validierung, kein Auto-Assign).

---

## Abgrenzung — noch keine technische Umsetzung in diesem Schritt

Dieses Dokument definiert **fachliche Anforderungen und Datenmodell-Grundsätze**.
Technisch umgesetzt wird in folgenden Sprints:

| Thema | Sprint |
|---|---|
| Mobilitätsprofil-Modell (`MobilityProfile`) | Sprint 4 |
| Fahrzeugausstattungs-Modell (`VehicleFeature`) | Sprint 4 |
| Fahrerqualifikations-Modell (`Qualification`) | Sprint 4 |
| Matching-Validierung (manuell, Dispatcher) | Sprint 5 |
| Mobilitätsprofil-UI (Icon-Auswahl) | Sprint 5 |
| Automatisches Matching | nach MVP |
| Vertrauenspersonen-Modell | nach MVP |
| Sprachführung / Sprachmenü | nach MVP |
