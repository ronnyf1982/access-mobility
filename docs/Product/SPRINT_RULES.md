# Sprint-Regeln — access-mobility

Übergeordnete Quelle: `docs/SOURCE_OF_TRUTH.md`
Letzte Aktualisierung: 2026-07-16

---

## Verbindlichkeit

Diese Regeln gelten für jeden Sprint — unabhängig von der Größe der Aufgabe.
Sie sind nicht optional. Bei Widerspruch zu kurzfristigen Anforderungen gilt: Regeln haben Vorrang.

---

## Vor jedem Sprint

```
✅ git status prüfen (sauberes Working Directory sicherstellen)
✅ git pull --ff-only (aktuellen Stand vom Remote holen)
✅ docs/SOURCE_OF_TRUTH.md lesen
✅ docs/ROADMAP.md und docs/PROJECT_STATUS.md lesen
✅ Ziel des Sprints klar verstehen — keine ungefragten Erweiterungen
✅ Bei neuem Modul: docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md prüfen
```

---

## Während des Sprints

### Grundregeln

- **Kein Overengineering:** Nur umsetzen, was explizit gefordert ist.
- **Keine ungefragten Features:** Kein „Ich habe noch schnell X ergänzt".
- **Keine neuen Felder ohne Begründung:** Jedes neue Datenbankfeld braucht eine fachliche Rechtfertigung.
- **Keine Fremdänderungen:** Nur die Dateien ändern, die der Sprint erfordert.
- **Kein Commit ohne Freigabe.** Kein Push ohne Freigabe.

### Datenmodell

- **Strukturierte Felder vor Freitext:** Alles, was Matching beeinflusst, muss strukturiert sein.
- **Freitext nur ergänzend:** `notes`-Felder sind ergänzend, niemals alleinige Datenquelle.
- **Soft-Delete für historische Entitäten:** Fahrzeuge, Fahrer, Anfragen nicht hart löschen.
- **Snapshots für Matching:** Anforderungen beim Absenden einfrieren, nie live-Daten matchen.

### UI

- **Accessibility bei jeder Komponente prüfen** (siehe Checkliste am Ende).
- **Kein Icon ohne Textlabel.**
- **Keine rein farbbasierte Information** (Status immer mit Icon oder Text).
- **Mindestgröße 44 × 44 px** für alle interaktiven Elemente.
- **Fahrgastoberfläche: Wizard-Prinzip**, eine Entscheidung pro Schritt.
- **Einfache Sprache** in der Fahrgastoberfläche.

### Sprachassistent

- Bei **jedem neuen Fahrgast-nahen Modul** prüfen:
  - Ist das Modul per Tastatur vollständig bedienbar?
  - Haben alle Felder ARIA-Labels?
  - Welche Dialogschritte braucht der Sprachassistent?
  - Eintrag in `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md` aktualisieren.

### Sicherheit

- **Kein API-Key im Frontend.**
- **Keine sensiblen Daten im Klartext loggen.**
- **CORS-Origin nicht auf Wildcard `*` setzen.**
- **Medizinische Daten niemals als Pflichtfeld** (DSGVO, Art. 9).

---

## Nach dem Sprint

```
✅ pytest (alle Tests grün)
✅ npx vue-tsc --noEmit (TypeScript-Check: 0 Fehler)
✅ npm run build (Build erfolgreich)
✅ PFLICHT-Umgebungsprüfung (siehe Abschnitt unten) — vor Browser-Test!
✅ Browser-Test: Golden Path manuell durchklicken
✅ Browser-Test: Demo-Login alle betroffenen Rollen prüfen
✅ git status --short (Überblick über Änderungen)
✅ docs/PROJECT_STATUS.md aktualisieren
✅ docs/ROADMAP.md aktualisieren (Sprint als ✅ markieren)
✅ KEIN Commit ohne explizite Freigabe
✅ KEIN Push ohne explizite Freigabe
```

---

## PFLICHT: Umgebungsprüfung vor jedem Browser-Test

**Diese Prüfung ist nicht optional.** Kein Login-Test, kein Browser-Test, keine
API-Prüfung darf stattfinden, ohne dass alle fünf Punkte bestätigt sind.

```
✅ 1. Docker läuft — PostgreSQL erreichbar auf Port 5440
       docker compose -f docker-compose.dev.yml ps

✅ 2. Alembic auf aktuellem Stand (zeigt "(head)")
       cd backend && .venv\Scripts\python.exe -m alembic current

✅ 3. Seed-Daten vorhanden / aktuell
       cd backend && .venv\Scripts\python.exe -m app.scripts.seed_demo_data

✅ 4. Backend läuft und antwortet
       GET http://localhost:8010/api/v1/health → 200 OK

✅ 5. Frontend erreichbar
       http://localhost:5180 → HTTP 200
```

**Wenn eine Prüfung fehlschlägt:** Dienste starten, dann erneut prüfen.
Schnellstart: `scripts\windows\Start-AccessMobility-Dev.ps1`

**Was Claude tun muss:**
1. Alle fünf Ports / Dienste aktiv prüfen (kein Annahmen treffen)
2. Alle Ergebnisse explizit melden (Port 8010: ✅ / ❌)
3. Erst nach vollständiger Bestätigung: Browser-Test durchführen
4. Erst nach erfolgreichem Browser-Test: Sprint als "fertig" melden

---

## Bei jedem neuen Modul

Folgende Prüfungen sind **Pflicht** bevor ein neues Modul als fertig gilt:

| # | Frage | Konsequenz bei Ja |
|---|---|---|
| 1 | Fahrgäste nutzen dieses Modul? | Sprachassistenz prüfen, Wizard-Prinzip anwenden |
| 2 | Enthält das Modul Matching-relevante Daten? | Strukturierte Felder, kein Freitext-only |
| 3 | Modul hat neue UI-Komponenten? | Accessibility-Checkliste durchgehen |
| 4 | Modul verarbeitet sensible Daten? | Datenschutz + Bestätigungspflicht sicherstellen |
| 5 | Modul führt Aktionen durch (Speichern, Senden)? | Bestätigung vor Aktion einbauen |
| 6 | Modul ist ein neues Datenbankmodell? | Alembic-Migration + Seed-Daten ergänzen |
| 7 | Modul ist neu? | Eintrag in MODULE_ASSISTANT_REQUIREMENTS.md anlegen |

---

## Accessibility-Checkliste (UI-Komponenten)

```
[ ] Alle interaktiven Elemente per Tastatur erreichbar?
[ ] Alle Buttons/Icons haben aria-label oder sichtbaren Textlabel?
[ ] Statusänderungen in aria-live-Regionen?
[ ] Kontrast ≥ WCAG AA (4,5:1 Text, 3:1 UI)?
[ ] Keine rein farbbasierte Information?
[ ] Fokusreihenfolge logisch?
[ ] Alle Klickflächen ≥ 44 × 44 px?
[ ] Sprache einfach und klar (Fahrgastbereich)?
[ ] Fehlermeldungen programmatisch mit Feldern verknüpft (aria-describedby)?
[ ] Sprachassistenz-Modus für neue Fahrgastfelder berücksichtigt?
```

---

## Was Claude in keinem Sprint tun darf

- Features bauen, die nicht explizit angefordert wurden
- Commiten ohne Freigabe
- Pushen ohne Freigabe
- Migrationen erstellen ohne Notwendigkeit
- Bestehende Architekturentscheidungen ignorieren
- Freitext als Ersatz für strukturierte Felder verwenden
- Accessibility-Anforderungen als optional behandeln
- API-Keys ins Frontend schreiben
- Medizinische Felder als Pflichtfelder setzen
- Den Sprachassistenten als „kann man später machen" einordnen
- **Einen Browser-Test oder Login-Test durchführen oder behaupten, ohne vorher alle 5 Umgebungs-Checks bestätigt zu haben**
- **Einen Sprint als abgeschlossen melden, wenn die lokale Umgebung beim Browser-Test nicht vollständig lief**

---

## Git-Workflow

```bash
# Vor dem Sprint
git status
git pull --ff-only

# Während des Sprints
# (Änderungen nach Freigabe)
git add <spezifische Dateien>
git status  # nochmal prüfen

# Nach Freigabe durch User
git commit -m "..."
# Push nur nach expliziter Freigabe
git push
```

**Immer spezifische Dateien stagen**, nie `git add .` oder `git add -A` —
sonst besteht die Gefahr, `.env.local` oder andere lokale Dateien einzuchecken.

---

## Demo-Zugangsdaten (Referenz)

| E-Mail | Rolle | Passwort |
|---|---|---|
| passenger@access.test | Fahrgast | Access123! |
| provider@access.test | Fahrdienst-Admin | Access123! |
| dispatcher@access.test | Disponent | Access123! |
| admin@access.test | Plattform-Admin | Access123! |
| relative@access.test | Vertrauensperson | Access123! |
| orgadmin@access.test | Organisations-Admin | Access123! |
| coordinator@access.test | Koordinator:in | Access123! |
| driver@access.test | Fahrer:in | Access123! |

Seed-Befehl: `python -m app.scripts.seed_demo_data` (aus `backend/` mit aktiver venv)
