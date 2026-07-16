# App-Konzept — access-mobility

Übergeordnete Quelle: `docs/SOURCE_OF_TRUTH.md`
Langfristige Vision: `docs/Product/PRODUCT_VISION.md`
Letzte Aktualisierung: 2026-07-16

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
- Auftragsliste mit Fahrgastdaten und Adresse
- Statuswechsel: unterwegs → angekommen → Fahrgast an Bord → abgeschlossen
- Schichtstart und Fahrzeugwahl (ab Sprint 10)

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
| **Assistant Core** | Sprachassistenz-Fundament, barrierefreies Onboarding | **Sprint 8** |
| **Fahrer-Schichtstart** | Tagesaufträge, Statuswechsel, Schichtverwaltung | Sprint 10 |
| **KI-Berater** | Online-ChatGPT-Integration (Backend-only) | Sprint 11 |
| **Fahrt per Sprache** | Vollständige Sprachführung durch Buchungsprozess | Sprint 12 |
| **Regelmäßige Touren** | Serienfahrten, RRULE | Sprint 13 |
| **Ausfallmanagement** | Ersatzfahrzeug, Fahrerausfall | Sprint 14 |
| **Tourenoptimierung** | KI-gestützte Routenoptimierung | Sprint 15 |

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

### 7. Tourenplanung (Sprint 13–15)

- Serienfahrten (RRULE)
- Ausfallmanagement
- KI-gestützte Routenoptimierung

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

## Zwei UI-Welten

Das Portal rendert unterschiedliche Ansichten je nach Rolle:

**Fahrgast-Welt** (`passenger`, `trusted_person`, `organization_coordinator`, ...):
- Vereinfachte Oberfläche
- Wizard-Prinzip
- Sprachassistenz-fähig
- Keine Dispo-Funktionen sichtbar

**Dispo-Welt** (`provider_admin`, `dispatcher`, `platform_admin`):
- Funktionale, übersichtliche Verwaltungsoberfläche
- Fahrgastdaten + Matching-Übersicht
- Zuweisungsfunktionen
- Kein Buchungs-Wizard
