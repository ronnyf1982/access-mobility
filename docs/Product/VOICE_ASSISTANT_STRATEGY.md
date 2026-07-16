# Sprachassistenten-Strategie — access-mobility

Übergeordnete Quelle: `docs/SOURCE_OF_TRUTH.md`
Modul-Anforderungen: `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`
Letzte Aktualisierung: 2026-07-16

---

## Grundprinzip

**Der Sprachassistent ist kein späteres Add-on.**

Er ist von Anfang an als **Kernarchitektur** berücksichtigt.
Jedes neue Modul wird von Beginn an auf Sprachassistenz-Tauglichkeit geprüft.

Zielgruppe des Assistenten: **insbesondere blinde und sehbehinderte Nutzer** —
aber auch alle anderen Fahrgäste, die Sprache als Eingabe bevorzugen.

---

## 1. Zielgruppe

| Nutzergruppe | Bedarf | Priorität |
|---|---|---|
| Blinde Nutzer | Vollständige Bedienalternative zur visuellen UI | Hoch |
| Sehbehinderte Nutzer | Unterstützung bei kleinen Elementen, Vergrößerung, Vorlesen | Hoch |
| Nutzer mit motorischen Einschränkungen | Sprachsteuerung als Alternative zur Tastatur | Mittel |
| Ältere Nutzer | Vereinfachte Interaktion, klare Führung | Mittel |
| Alle Fahrgäste | Optionale Komfortfunktion | Normal |

**Disponenten und Fahrer** haben Sekundärzugang zum Assistenten — ihre Oberflächen sind
primär visuell optimiert.

---

## 2. Erstkontakt / Onboarding

Beim ersten Start (nach Login oder nach Registrierung) wird gefragt:

> „Möchten Sie die sprachgeführte Bedienung aktivieren?"

**Gestaltungsgrundsätze:**
- Die Frage ist nicht stigmatisierend — keine Formulierung wie „Sind Sie behindert?"
- Beide Optionen sind gleichwertig dargestellt.
- Die Einstellung kann jederzeit in den Einstellungen geändert werden.
- Screenreader-Nutzer erhalten die Frage automatisch vorgelesen.

| Antwort | Konsequenz |
|---|---|
| Ja | Sprachgeführter Fragenkatalog für Onboarding und Profil-Einrichtung |
| Nein | Normale visuelle Einrichtung |
| Später | Normaler Start, Einstellung in Account-Einstellungen verfügbar |

---

## 3. Offline-Modus

**Was offline funktioniert:**

- Feste Dialogsequenzen (vorprogrammierte Fragen und Antwortoptionen)
- Lokale Regelauswertung (welche Antwort zu welchem Feld gehört)
- Strukturierte Felder setzen (Checkboxen, Auswahlfelder)
- Entwürfe lokal speichern
- Vorlesen von UI-Inhalten (TTS aus Browser-API oder betriebssystem-nativ)

**Offline-Dialogaufbau:**

Fester Fragenkatalog — jede Frage führt zu genau einem strukturierten Datenwert:

```
Frage: "Nutzen Sie einen Rollstuhl?"
→ Ja / Nein → uses_wheelchair = true / false

Frage: "Welche Art von Rollstuhl?"
→ Manuell / Elektrisch / Unbekannt → wheelchair_type = manual / electric / unknown

Frage: "Benötigen Sie eine Rampe oder Hebebühne?"
→ Rampe / Hebebühne / Beides / Nein → needs_ramp / needs_lift

[...]
```

**Keine Cloud erforderlich** — der Offline-Assistent funktioniert ohne Internet.

---

## 4. Online-Modus

**Zusätzliche Fähigkeiten mit Online-Verbindung:**

- Natürliche Sprache verstehen (nicht nur feste Antworten)
- Rückfragen bei Unklarheiten stellen
- Strukturierte Felder aus natürlichem Satz extrahieren
- Kontext über mehrere Schritte hinweg halten
- Vorschläge auf Basis des gesamten Profils machen

**Beispiel Online-Interaktion:**

```
Nutzer: "Ich brauche eine Fahrt mit meinem Elektrorollstuhl, der ziemlich groß ist,
         und meine Begleiterin kommt mit."

Assistent: "Ich habe das verstanden. Ich würde folgende Felder setzen:
            - Elektrorollstuhl: Ja
            - Rollstuhlplatz erforderlich: Ja
            - Begleitperson: Ja
            Ist das korrekt?"

Nutzer: "Ja"

Assistent: "Möchten Sie noch etwas hinzufügen, zum Beispiel Rampe oder Hebebühne?"
```

**Technische Umsetzung:**
- KI-Verarbeitung ausschließlich über Backend (`/api/v1/assistant/...`)
- Kein direkter KI-Aufruf aus dem Frontend
- API-Key niemals im Frontend, nur in Backend-Umgebungsvariablen
- Nutzerzustimmung vor Verarbeitung sensibler Daten

---

## 5. Datenschutz

| Aspekt | Regel |
|---|---|
| API-Key | Nur im Backend — niemals im Frontend oder in versioniertem Code |
| Sensible Daten | Nicht unnötig an KI senden — nur relevante Felder für die aktuelle Anfrage |
| Zustimmung | Explizite Nutzer-Zustimmung vor jeder KI-Verarbeitung von Gesundheitsdaten |
| Logging | KI-Anfragen dürfen keine personenbezogenen Daten unverschlüsselt loggen |
| Offline-Fallback | Assistent muss ohne KI grundlegend funktionieren |
| Datenlokalisierung | KI-API-Anbieter gemäß DSGVO auswählen (EU-Rechenzentrumsoption prüfen) |

---

## 6. Bestätigungspflicht — unverhandelbar

**Der Assistent darf:**
- Erklären und informieren
- Vorschläge machen
- Felder vorbefüllen (als Vorschlag, nicht als Fakt)
- Zusammenfassen, was er machen würde

**Der Assistent darf NICHT ohne explizite Nutzerbestätigung:**
- Ein Profil speichern
- Eine Fahrtanfrage absenden
- Ein Fahrzeug oder Fahrer zuweisen
- Medizinische Einschätzungen als Tatsache darstellen
- Rechtliche oder administrative Entscheidungen treffen

**Bestätigungs-UX:**
- Immer klare Zusammenfassung vor Aktion: „Ich werde jetzt folgendes speichern: ..."
- Bestätigung explizit: „Ja, speichern" / „Nein, ändern"
- Abbrechen jederzeit möglich

---

## 7. Assistent-Architektur (technisch)

### Phasen

**Phase 1 — Assistant Core (Sprint 8) ✅:**
- Onboarding-Dialog: Sprachführungs-Wahl beim ersten Login
- `voice_mode_enabled` auf User-Modell
- `/assistant/capabilities` Endpunkt (rollenbasiert)
- Kein STT in diesem Sprint

**Phase 2 — Offline-Mobilitätscheck (Sprint 9) ✅:**
- Route `/mobility-profile/assistant` — geführter Fragenflow
- 10 Fragen, zentraler Fragenkatalog (`mobilityAssistantQuestions.ts`)
- Button-Antworten: Ja / Nein / Weiß ich nicht / Überspringen
- TTS: Browser Web Speech API (optional, Fallback visuell), kein STT
- Speicherung erst nach Bestätigung der Zusammenfassung
- Fehlende Felder dokumentiert, keine unautorisierten Migrationen

**Phase 2B — Sprachgeführte Antwortauswahl (Sprint 9B) ✅:**
- TTS-Flow: Frage vorlesen → dann aktiv fragen „Soll ich die Antwortmöglichkeiten vorlesen?"
- Antwortoptionen werden nur auf explizite Nachfrage vorgelesen (kein automatisches Vorlesen)
- Neue Buttons: „Antwortmöglichkeiten vorlesen", „Frage wiederholen"
- Optionaler STT: `window.SpeechRecognition` / `window.webkitSpeechRecognition`
  - Nur aktiv auf Nutzerwunsch (Button „Antwort sprechen") — kein dauerhaftes Mithören
  - Bestätigungs-Dialog vor Übernahme jeder gesprochenen Antwort
  - Sprachbefehle: Ja/Nein/Weiß ich nicht/Überspringen + Vorlesen/Wiederholen/Zurück/Abbrechen
  - Fallback-Meldung wenn Browser STT nicht unterstützt
- Tastaturkürzel: J / N / W / S / R / H / ArrowLeft / Escape
  - Hinweisleiste mit sichtbaren Kürzeln im UI
  - Kein Konflikt mit Formularelementen
- Speech-Hilfsfunktionen: `frontend/src/utils/speech.ts`
  - TTS: `isTTSSupported()`, `speak()`, `stopSpeaking()`
  - STT: `isSTTSupported()`, `startRecognition()`, `stopRecognition()`, `normalizeSpokenInput()`
- Kein Cloud-Speech — ausschließlich Browser-API

**Phase 3 — Online-KI (Sprint 11):**
- Backend-Endpoint `/api/v1/assistant/interpret`
- Natürlichsprachige Eingabe → strukturierte Felder
- Kontext-Management (Session-basiert)
- ChatGPT / Claude API (Backend-only)

**Phase 4 — Fahrtbuchung per Sprache (Sprint 12):**
- Vollständiger Buchungsprozess per Sprache
- Adresseingabe per Sprache
- Datum/Zeit-Erkennung
- Bestätigungs-Dialog

### Frontend-Komponente

```
<VoiceAssistantPanel>
  - Aktivierungsbutton (persistent, aria-label="Sprachassistent")
  - Gesprächsprotokoll (Scroll-Bereich)
  - Aktueller Assistent-Status (aria-live)
  - Mikrofon-Button (Start / Stopp)
  - Vorgeschlagene Antworten als Buttons (Fallback ohne Mikrofon)
  - Bestätigungs-Dialog
</VoiceAssistantPanel>
```

### Fallbacks

- Kein Mikrofon verfügbar → Texteingabe als Alternative
- Browser unterstützt keine Web Speech API → Strukturierte Buttons statt Sprache
- KI offline → Offline-Fragenkatalog als Fallback
- Spracherkennung nicht verstanden → Wiederholung + Alternative anbieten

---

## 8. Dialogdesign-Grundsätze

- Jede Frage hat eine klare, eindeutige Antwortmöglichkeit.
- Komplexe Themen werden in Teilfragen zerlegt (eine Entscheidung pro Frage).
- Der Assistent wiederholt zur Bestätigung, was er verstanden hat.
- Technische Bezeichnungen (Feldnamen) sind dem Nutzer niemals sichtbar.
- Sprache: einfach, freundlich, nicht bevormundend.
- Fehler: klar benennen, korrigierbar, nie kritisch formulieren.

---

## 8. Sprachassistenz Fahrer-App (Sprint 11)

Die Fahrer-App erhält ebenfalls Sprachunterstützung — insbesondere für Aktionen,
bei denen der Fahrer die Hände nicht frei hat.

**Mögliche Sprachbefehle:**

| Befehl | Aktion |
|---|---|
| „Schicht beginnen" | `shift_start` setzen |
| „Ich fahre Fahrzeug B-AM 1234" | Fahrzeug über Kennzeichen suchen + zuweisen |
| „Pause beginnen" | `break_start` setzen |
| „Pause beenden" | `break_end` setzen |
| „Fahrgast ist zugestiegen" | `passenger_picked_up` → Bestätigung → Status setzen |
| „Fahrgast ist ausgestiegen" | `arrived_destination` → Bestätigung → Status setzen |
| „Nächster Halt" | Nächste Adresse vorlesen |
| „Problem melden" | Problem-Dialog öffnen, Beschreibung diktieren |
| „Schicht beenden" | `shift_end` → Bestätigung |

**Sicherheitsregel:**
Alle statusrelevanten Aktionen (Fahrgast zugestiegen, ausgestiegen, Schicht beenden)
erfordern eine Bestätigung — auch wenn der Befehl klar war.

Beispiel:
> Fahrer: „Fahrgast ist zugestiegen."
> Assistent: „Soll ich Max Mustermann als zugestiegen markieren?"
> Fahrer: „Ja."

**Offline-Fähigkeit:**
Grundlegende Statusbefehle müssen ohne Internetverbindung lokal queuen können
und beim nächsten Online-Gang synchronisiert werden.

---

## 8a. Standortfreigabe per Sprache

Sobald Live-Standortteilung implementiert ist (Sprint 12), muss der Assistent folgende
Sprachbefehle unterstützen:

**Freigabe starten:**
- „Teile meine Fahrt mit meiner Vertrauensperson."
- „Schick meiner Tochter meinen Standort."
- „Sag meiner Einrichtung, wann ich ankomme."

**Freigabe beenden:**
- „Beende die Standortfreigabe."
- „Stoppe das Teilen."

**Status abfragen:**
- „Wer kann meinen Standort sehen?"
- „Ist mein Standort geteilt?"

**Pflichtanforderung Bestätigungsdialog:**

Der Assistent muss vor jeder Aktivierung einer Standortfreigabe immer alle vier Punkte
explizit nennen und bestätigen lassen:

1. **Empfänger:** Wer erhält die Freigabe?
2. **Art der Freigabe:** Fahrtstatus und/oder Standort?
3. **Dauer:** Nur für diese Fahrt / bis Fahrtende.
4. **Bestätigung:** Explicit Ja/Nein abwarten.

**Beispieldialog:**

> Nutzer: „Teile meine Fahrt mit meiner Tochter."
>
> Assistent: „Ich teile den Fahrtstatus und Standort für diese Fahrt mit Anna Müller.
> Der Link ist nur bis Fahrtende gültig. Soll ich das jetzt tun?"
>
> Nutzer: „Ja."
>
> Assistent: „Anna Müller wurde informiert. Sie kann jetzt Ihren Fahrtstatus sehen.
> Um die Freigabe zu beenden, sagen Sie: Standortfreigabe beenden."

**Wichtig:** Der Assistent darf ohne explizites „Ja" des Nutzers **niemals** eine
Standortfreigabe aktivieren. Das gilt auch, wenn der Nutzer seinen Wunsch sehr klar
formuliert hat.

---

## 9. Sprachassistent-Prüfung bei neuen Modulen

Bei jedem neuen Modul (Fahrgast-Bereich):

| Frage | Erwartet |
|---|---|
| Wie bedient ein blinder Nutzer dieses Modul? | Vollständige Keyboard + Screenreader-Tauglichkeit |
| Welche Fragen stellt der Assistent? | Liste der Dialogschritte je Modul |
| Welche strukturierten Felder werden gesetzt? | Feldnamen + erlaubte Werte |
| Was funktioniert offline? | Offline-Fragenkatalog |
| Was verbessert Online-KI? | Natürlichsprachige Interpretation |
| Wo braucht es Bestätigung? | Vor Speichern / Absenden / Zuweisen |

Ergebnis dokumentieren in: `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`
