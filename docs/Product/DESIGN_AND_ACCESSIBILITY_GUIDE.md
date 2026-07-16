# Design & Accessibility — Konsolidierte Regeln

Übergeordnete Quelle: `docs/SOURCE_OF_TRUTH.md`
CSS-Tokens und Farbwerte: `docs/Design/DESIGN_GUIDE.md`
Matching-Anforderungen: `docs/Product/ACCESSIBILITY_AND_MATCHING_REQUIREMENTS.md`
Letzte Aktualisierung: 2026-07-16

---

## Plattform-Architektur: Drei Oberflächen-Welten

Access Mobility ist eine Plattform mit drei klar getrennten Nutzungswelten.
Jede Welt hat eigene Design-Prioritäten — alle teilen dieselbe Designsprache
(dunkel, Gelb-Akzent, klar, barrierefrei).

| Welt | Design-Priorität | Kompromisse |
|---|---|---|
| **Fahrgast-App** | Einfachheit, Barrierefreiheit, Sprachassistenz | Informationsdichte bewusst reduziert |
| **Fahrer-App** | Mobile Robustheit, große Buttons, Ablenkungsarmut | Keine komplexen Tabellen oder Filter |
| **Dispo-/Admin-Web** | Funktionsreichtum, Effizienz, Informationsdichte | Komplexität ist hier akzeptiert |

**Gemeinsame Designbasis für alle drei Welten:**
- Farbpalette: Schwarz/Anthrazit + Gelb (`#FFD600`)
- Typografie: Inter → Segoe UI → sans-serif
- Barrierefreiheit: WCAG AA minimum für alle, AAA für Fahrgast-Kernbereiche
- Fokus-Style: gelber Outline-Ring überall

**Trennlinie:** Dieselbe Designsprache — aber unterschiedliche Komplexitätsstufen.
Ein Disponent darf eine komplexe Tabellenansicht bekommen.
Ein Fahrgast oder Fahrer nie.

---

## Verbindlicher Grundsatz

**Access Mobility wird accessibility-first entwickelt.**

Barrierefreiheit ist kein nachträgliches Feature und kein optionales Goodie.
Sie ist die Grundlage jeder Designentscheidung — von der Datenbankstruktur bis zur Oberfläche.

Das Zielbild: Eine Person, die blind ist, einen Rollstuhl nutzt oder motorisch eingeschränkt ist,
kann eine Fahrt vollständig selbstständig buchen — oder eine Vertrauensperson tut es für sie.

---

## 1. Design-Grundprinzipien

### Look & Feel

| Aspekt | Vorgabe |
|---|---|
| Grundfarbe | Schwarz / dunkles Anthrazit (`#111111`) |
| Akzentfarbe | Gelb (`#FFD600`) — Buttons, aktive Navigation, CTAs, Hervorhebungen |
| Stil | Modern, premium, klar, vertrauenswürdig — kein bunter Consumer-Look |
| Qualitätsniveau | SaaS / Mobilitätsplattform, professionell, nicht verspielt |
| Karten | Groß, klar strukturiert, keine überladenen Informationsdichten |
| Texte | Einfache Sprache, kurze Sätze, kein Verwaltungsjargon |

### Was vermieden wird

- Überladene Admin-Oberflächen für Fahrgäste
- Icon-only-Bedienung (jedes Icon braucht einen sichtbaren Textlabel)
- Rein farbbasierte Statusinformation (Status immer mit Icon oder Text kombinieren)
- Zeitgesteuerte Interaktionen ohne Verlängerungsoption
- Kleine Klickflächen unter 44 × 44 px
- Fachjargon in der Fahrgastoberfläche

---

## 2. Farbpalette (verbindlich)

Vollständige CSS-Tokens: `docs/Design/DESIGN_GUIDE.md`

| Farbe | Wert | Verwendung |
|---|---|---|
| Hintergrund | `#111111` | Seitenhintergrund Portal |
| Surface | `#1a1a1a` | Cards, Kacheln, Tabellen |
| Sidebar | `#0d0d0d` | Linke Navigation |
| Akzent | `#FFD600` | Buttons, aktive Nav, CTAs, Icons |
| Akzent-Hover | `#B89E00` | Hover auf Akzent-Elementen |
| Text primär | `#F0F0F0` | Überschriften, Zahlenwerte |
| Text sekundär | `#9A9A9A` | Beschreibungen, Metainfos |
| Text auf Akzent | `#111111` | Text auf gelbem Hintergrund |
| Border | `#2a2a2a` | Trennlinien, Card-Rahmen |
| Erfolg | `#22C55E` | Status „Bestätigt" |
| Gefahr | `#EF4444` | Fehler, Stornierung |

**Kontrastverhältnisse:**
- Gelb (`#FFD600`) auf Schwarz (`#111111`): ~9,5:1 → WCAG AAA ✓
- Hellgrau (`#F0F0F0`) auf `#1a1a1a`: ~14:1 → WCAG AAA ✓

---

## 3. Fahrgastoberfläche — Besondere Regeln

Die Fahrgastoberfläche ist bewusst reduziert und einfach gehalten.

### Wizard-Prinzip

- **Eine Entscheidung pro Schritt** — kein Schritt überlastet den Nutzer.
- Zurück-Funktion jederzeit möglich.
- Klarer Fortschrittsindikator.
- Bestätigung vor dem Absenden.

### Bedienelemente

- Alle interaktiven Elemente: **mind. 44 × 44 px** Klickfläche (WCAG 2.5.5).
- Buttons immer mit Text + optionalem Icon (niemals Icon allein).
- Primäre Aktion klar hervorgehoben (gelber Button).

### Sprache

- Einfache, klare Sätze.
- Keine Abkürzungen ohne Erklärung.
- Keine medizinischen Fachbegriffe ohne Kontext.
- Fehlermeldungen: verständlich formuliert, nicht technisch.

### Rollenbasierte Ansichten

- Fahrgäste sehen **nur** Buchungsfunktionen.
- Verwaltung, Disposition, Abrechnung: ausschließlich für Provider/Dispo/Admin.
- Route `/transport-requests` rendert je nach Rolle zwei völlig unterschiedliche Ansichten.

---

## 4. Technische Barrierefreiheit

### ARIA

- Alle UI-Elemente haben `aria-label` oder `aria-labelledby` wo kein sichtbarer Text ausreicht.
- Bilder: `alt`-Text oder `aria-hidden="true"` wenn dekorativ.
- Statusänderungen: `aria-live`-Regionen (z. B. „Fahrt bestätigt", „Fehler beim Speichern").
- Toggle-Cards: `role="checkbox"` + `aria-checked`.
- Modale Dialoge: Fokus beim Öffnen hineinschieben, beim Schließen zurückgeben.

### Formulare

- Jedes Feld hat ein programmatisch verknüpftes `<label>`.
- Fehlermeldungen: mit `aria-describedby` an das betroffene Feld gebunden.
- Pflichtfelder: `aria-required="true"` + sichtbarer Indikator.

### Tastatur

- Vollständige Tastatur-Navigation (kein Element nur per Maus erreichbar).
- Fokusreihenfolge: logisch, der visuellen Lesereihenfolge folgend.
- Fokus-Style: gelber Outline-Ring (`outline: 2px solid #FFD600`), immer sichtbar.

### Kontrast

- Minimum: WCAG AA (4,5:1 Text, 3:1 UI-Elemente).
- Ziel: WCAG AAA (7:1) für Kernbereiche der Fahrgastoberfläche.

---

## 5. Anforderungen für blinde und sehbehinderte Nutzer

Diese Anforderungen haben Priorität — blinde Nutzer sind eine Kernzielgruppe.

- Alle Zustände und Statusänderungen sind per Screenreader hörbar.
- Keine rein visuellen Informationen (z. B. Farbe = Status).
- Fokusreihenfolge: entspricht dem logischen Ablauf der Seite.
- Sprachassistenz (ab Sprint 8): vollständige Bedienalternative zur visuellen UI.

Spezifische Anforderungen:
- Fahrer holt blinde Fahrgäste an der Tür ab (Profilfeld: `is_blind_or_visually_impaired`)
- Fahrer hat Qualifikation `can_assist_blind_passengers`
- Disponent sieht Hinweis in Fahrgastdaten-Infobox

---

## 6. Disponentenoberfläche — Besondere Regeln

Disponenten brauchen keine vereinfachte, sondern eine **effiziente, übersichtliche** Oberfläche.

- Kompaktere Darstellung als Fahrgastoberfläche.
- Fahrgastdaten (Kontakt, Notfallkontakt) immer sichtbar in Detailansicht.
- Matching-Bewertung (suitable / warning / unsuitable) klar gekennzeichnet.
- Direkte Telefon-Shortcut-Links (`tel:`) für schnellen Kontakt.
- Keine medizinischen Diagnosen in der Dispo-Ansicht — nur transportrelevante Bedarfsfelder.

---

## 7. Komponentenregeln

### Buttons

| Variante | Hintergrund | Text | Rahmen |
|---|---|---|---|
| Primary | `#FFD600` | `#111111` | — |
| Secondary | transparent | `#FFD600` | `#FFD600` |
| Ghost | transparent | `#F0F0F0` | `#2a2a2a` |
| Danger | `#EF4444` | `#FFFFFF` | — |

- `border-radius: 6px`, `padding: 0.5rem 1.25rem`, `font-weight: 600`

### Status-Badges

- Bestätigt / Suitable: grün (`#22C55E`-Töne)
- In Bearbeitung / Warning: gedimmtes Gelb, `#FFD600` Text
- Storniert / Unsuitable: rot (`#EF4444`-Töne)
- **Immer** zusätzlich mit Icon oder Text — nie nur Farbe.

### Toggle-Cards (für Bedarfsauswahl)

- Große, klickbare Cards (Rollstuhl, Rampe, Blind, ...)
- Aktiver Zustand: gelber Hintergrund, schwarzer Text
- Icon + Textlabel immer beide sichtbar
- ARIA: `role="checkbox"`, `aria-checked`

---

## 7a. Live-Standortteilung — UI-Grundsätze

### Fahrgast-Ansicht

- **Prominenter Button** „Fahrt teilen" — sichtbar während aktiver Fahrt, groß, gelber Primär-Button.
- **Klarer Hinweis**, mit wem aktuell geteilt wird (Name der Empfänger sichtbar).
- **Button „Teilen beenden"** immer sichtbar wenn aktive Freigabe besteht — Widerruf mit einem Tap.
- **Keine versteckten Freigaben:** Aktive Freigaben sind immer explizit in der Oberfläche sichtbar.
- **Bestätigungsdialog** vor jeder Freigabe: Empfänger + Art + Dauer vor Aktivierung anzeigen.

### Vertrauenspersonen-Ansicht (Empfänger)

- **Einfache, reduzierte Ansicht:** Kein volles Portal — nur für diese Fahrt relevante Daten.
- **Fahrtstatus** (z. B. „Fahrzeug unterwegs", „Fahrgast abgeholt", „Angekommen").
- **Geschätzte Ankunftszeit (ETA)** sofern verfügbar.
- **Karte** als späteres Feature mit ungefährem Fahrzeugstandort.
- **Kein Zugriff auf medizinische Details** des Fahrgastes.
- **Kein Zugriff auf andere Fahrten** oder andere Fahrgäste.
- **Ablauf-Hinweis:** „Dieser Link ist bis Fahrtende gültig."

### Barrierefreiheit / Screenreader

- Button „Fahrt teilen": `aria-label="Fahrtstatus mit Vertrauensperson teilen"`
- Aktiver Freigabestatus: `aria-live`-Region — automatische Ansage wenn Freigabe aktiv/beendet.
- Alle Bestätigungsdialoge vollständig per Tastatur und Screenreader bedienbar.
- Sprachbefehl-Freigabe per Assistent: vollständiger Bestätigungsdialog vorlesbar.

---

## 8. Zugänglichkeit als Qualitätskriterium

Vor jedem Sprint mit UI-Änderungen prüfen:

- [ ] Sind alle neuen Elemente per Tastatur erreichbar?
- [ ] Haben alle Buttons, Icons und Felder korrekte ARIA-Attribute?
- [ ] Sind Statusänderungen in `aria-live`-Regionen angekündigt?
- [ ] Ist der Kontrast ≥ WCAG AA?
- [ ] Gibt es keine rein farbbasierte Information?
- [ ] Ist die Fokusreihenfolge logisch?
- [ ] Sind alle Klickflächen ≥ 44 × 44 px?
- [ ] Ist die Sprache einfach und klar (Fahrgastbereich)?
- [ ] Wurde der Sprachassistenz-Modus für neue Fahrgast-Felder berücksichtigt?

---

## 9. Sprachassistenz (Referenz)

Vollständiges Konzept: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`
Modul-Anforderungen: `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

**Kurzfassung:**
- Jeder Fahrgast-nahe Bereich muss sprachassistenz-tauglich sein.
- Strukturierte Felder (Checkboxen, Auswahl) müssen per Sprache setzbar sein.
- Der Assistent schlägt vor — der Nutzer bestätigt.
- Offline-Grundfunktion ohne Cloud: feste Fragen, lokale Regeln.
- Online-Erweiterung: natürliche Sprache über Backend-KI.

**TTS-Designregeln (Sprint 9B):**
- Fragen vorlesen: ja, automatisch wenn `voice_mode_enabled`.
- Antwortoptionen vorlesen: **nur auf explizite Nachfrage** — nie automatisch ungefragt.
- Nach dem Vorlesen einer Frage: aktiv fragen „Soll ich die Antwortmöglichkeiten vorlesen?".
- STT: nur aktiv wenn Nutzer Button „Antwort sprechen" drückt — kein dauerhaftes Mithören.
- Gesprochene Antworten: immer mit Bestätigungsdialog vor Übernahme.
- TTS-Utility: `frontend/src/utils/speech.ts` (Browser-only, kein Cloud-API).

**Tastaturkürzel-Designregeln (Sprint 9B):**
- Tastaturkürzel-Leiste ist immer sichtbar (nicht nur on hover).
- Shortcuts nur aktiv wenn kein Formularfeld fokussiert ist.
- Escape schließt aktive Zustände der Reihe nach: STT-Hören → Bestätigungsdialog → Abbrechen.
- Shortcuts mit sichtbaren `<kbd>`-Elementen kennzeichnen (nicht nur `aria-label`).
