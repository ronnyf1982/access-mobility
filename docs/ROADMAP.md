# Roadmap — access-mobility MVP

## Sprint 1 — Grundgerüst ✅
Lauffähiges Fullstack-Grundgerüst: FastAPI + Vue 3 + PostgreSQL via Docker.
Health-Endpoint, Axios-Client, PrimeVue, Pinia, Vue Router.

## Sprint 2 — Designbasis, Landingpage & Portal-Layout ✅
Globale CSS-Designbasis, Layouts (PublicLayout / PortalLayout), Komponenten (Sidebar, Topbar, Header, Footer),
LandingView, DashboardView (Dummy-Daten).

## Sprint 3 — Auth, Rollen & Benutzerstammdaten ✅
JWT-Authentifizierung (bcrypt + PyJWT), 8 Benutzerrollen, Login-View, Route-Guard,
Auth-Pinia-Store, 8 Demo-Nutzer + 2 Demo-Orgs.

## Sprint 4 — Fahrgastprofil & Mobilitätsbedarf ✅
MobilityProfile-Modell (22 Felder, 11 Bedarfstypen), GET/PUT-Endpunkte (Auto-Create, Partial-Update),
MobilityProfileView (Accessibility-first, 5 Sektionen), Pinia Store, Sidebar-Eintrag, Dashboard-Profilkarte.

## Sprint 5 — Fahrdienst, Fahrzeuge und Fahrerprofile ✅
Vehicle-Modell (7 Typen, 8 Ausstattungsmerkmale), DriverProfile-Modell (8 Qualifikationsflags),
CRUD-Endpoints, Fahrzeug- und Fahrerverwaltung im Portal, Dashboard-Flottenkachel.

## Sprint 5B — Konfigurierbare Schnellauswahl-Vorlagen ✅
Zentrale Preset-Konfiguration (`backend/app/core/transport_presets.py`), fachlich konservative
Presets (kein Auto-Setzen med. Felder außer was eindeutig zutrifft), Backend liefert
`preset_controlled_profile_fields` + `suggested_field_values`, Frontend-Reset dynamisch
aus Backend-Daten statt lokal hart kodiert.

## Sprint 6 — Fahrt-/Transportanfrage Grundlage ✅
`TransportRequest`-Domänenobjekt als Kern des Buchungsprozesses.

- Backend: `TransportRequest`-Modell (status: draft/requested/cancelled), Alembic-Migration, JSONB-Snapshots
- 6 REST-Endpunkte: list, create, get, update, submit (draft→requested), cancel
- Snapshots: `requirement_snapshot` + `mobility_profile_snapshot` frieren Anforderungen zum Anfragezeit­punkt ein
- Frontend: `TransportRequestView` (Liste + Wizard-light), Pinia Store, API-Modul, Route `/transport-requests`
- Sidebar-Eintrag „Fahrten anfragen", Dashboard-KPI-Kachel mit Count und Direktlink
- Seed-Daten: 1 draft + 1 requested für passenger@access.test (idempotent)
- Kein Matching, keine Disposition, keine Fahrerzuweisung in diesem Sprint

## Sprint 7 — Manuelles Matching & Disposition ✅
Anfrage-Snapshot → Matching-Bewertung → manuelle Zuweisung durch Disponenten.

- Backend: `assigned`-Status + 5 Zuweisungsfelder auf `TransportRequest`, Alembic-Migration
- `manual_matching.py`: Snapshot-basiertes Matching (8 Fahrzeug- + 6 Fahrerregeln), 3 Status: `suitable` / `warning` / `unsuitable`
- 3 neue Endpoints: `GET matching-options`, `POST assign`, `POST unassign`
- Matching ist Entscheidungshilfe — kein Block, Disponent kann immer überschreiben
- **Dual-UI-Modus:** Fahrgast-Ansicht (Wizard, „Meine Fahrten") vs. Dispo-Ansicht (Fahrgastdaten, Matching, kein Wizard)
- Sidebar-Label rollenbasiert: „Fahrten anfragen" (Fahrgäste) / „Disposition" (Provider/Disponent)
- Fahrgast-Kontaktdaten (`passenger_display_name`, email, phone, emergency_contact_*) in API-Responses für Dispo-Rollen
- Frontend: Fahrgastdaten-Infobox + schreibgeschützte Anfragedetails in Dispo-Detailansicht
- Dashboard: `assignedCount` in KPI-Kachel
- Seed: 2 neue Demo-Anfragen (gute Übereinstimmung + Warnungsfall), Fahrer-Qualifikation aktualisiert
- Tests: 26 Pytest-Tests (alle bestanden), TypeScript-Check ✅, Build ✅

## Sprint 8 — Assistant Core & barrierefreies Onboarding-Fundament

Sprachassistenz-Fundament aufbauen und barrierefreies Erst-Onboarding implementieren.

- Assistant-Core-Komponente (`VoiceAssistantPanel`): Aktivierungsbutton, TTS (Text-to-Speech), STT (Speech-to-Text), Dialogprotokoll
- Frage beim ersten Start: „Möchten Sie die sprachgeführte Bedienung aktivieren?" (nicht stigmatisierend)
- Offline-Fragenkatalog für Mobilitätsprofil (alle 11 Basisbedarfe per Sprache setzbar)
- Fallback: strukturierte Buttons wenn kein Mikrofon verfügbar
- ARIA-Verbesserungen: aria-live für Assistenten-Status, vollständige Screenreader-Tauglichkeit
- Kontaktdaten-Verbesserung: Telefon, Abholkontakt, Notfallkontakt sichtbarer

Referenz: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`, `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

## Sprint 9 — Sprachgeführter Mobilitätscheck (offline-fähig)

Vollständiger sprachgeführter Durchlauf durch alle Mobilitätsprofil-Felder ohne Cloud-Abhängigkeit.

- Alle 11 Basisbedarfe + 14 med. Detailfelder per Sprache setzbar
- Lokale Regelauswertung: kontextsensitive Folgefragen (z. B. Rollstuhltyp nur wenn Rollstuhl = Ja)
- Draft lokal speicherbar, Sync beim nächsten Online-Gang
- Zusammenfassung vorlesen lassen vor Speichern

## Sprint 10 — Fahrer-Schichtstart & Fahrzeugwahl

Fahrer sieht Tagesaufträge, startet Schicht, wählt Fahrzeug.

- Backend: Schichtstart-/Abschluss-Endpoints, Fahrzeugwahl per Kennzeichen, Statuswechsel
- Frontend: Fahrer-Dashboard, Auftragsliste, Statuswechsel (unterwegs → angekommen → an Bord → abgeschlossen)
- Sprachassistenz: „Ich starte meine Schicht, Kennzeichen M-AM-1234" → Fahrzeug suchen + bestätigen

## Sprint 11 — Fahrtstatus & Benachrichtigungseinstellungen

Fahrtstatus-Grundlage und Benachrichtigungseinstellungen — Voraussetzung für Live-Tracking.

**Fahrtstatus / Fahrer-App:**
- Backend: `RideStatusEvent`-Protokoll mit Statuswechseln + Zeitstempel + optionalem Standort
- Statuswerte: `driver_on_way` / `arrived_pickup` / `passenger_picked_up` / `arrived_destination` / `completed` / `delayed`
- Frontend: Fahrer-App-Ansicht mit Statuswechsel-Buttons (7 Aktionen)
- Schichtverwaltung: Schicht beginnen / Pause / Schicht beenden (Zeitprotokoll als spätere Arbeitszeitgrundlage)
- Sprachassistenz: „Fahrgast ist zugestiegen" → Bestätigung → Status setzen
- Linienverkehr-Ansicht: optimierte Fahrgastliste (Adresse, geplante Zeit, Mobilitätsbedarf, Hinweise)

**Benachrichtigungseinstellungen (Fahrgastprofil):**
- Vertrauenspersonen mit Kontaktdaten + Berechtigungen (Standort ja/nein, Status ja/nein)
- Kanäle: In-App, SMS, E-Mail, System-Teilen
- Ereignisse konfigurierbar: Fahrzeug unterwegs, Fahrgast zugestiegen, angekommen, Verspätung, Stornierung

**Begründung:** Live-Tracking (Sprint 12) benötigt Statusereignisse und Berechtigungsstruktur.
Beides muss vor Live-Sharing vorhanden sein.

## Sprint 12 — Live-Status & Standortfreigabe

Fahrtstatus und optionaler Live-Standort mit berechtigten Personen teilen.

- Backend: `LiveLocationShare`-Modell (share_token, expires_at, revoked_at, share_channel, recipient_*)
- Datenschutz: Zustimmung, zeitliche Begrenzung auf Fahrtende, Widerruf jederzeit, Protokollierung
- In-App-Freigabe: Vertrauenspersonen sehen Fahrtstatus + ETA in der App
- Link-Freigabe: zeitlich begrenzter Token-Link (kein Account erforderlich)
- System-Teilen: native Browser-Share-API (WhatsApp, SMS, E-Mail)
- Statusnachrichten: „Fahrt gestartet", „Fahrzeug unterwegs", „Fahrgast abgeholt", „Angekommen", „Verspätung"
- Sprachassistent: Freigabe nur nach ausdrücklicher Bestätigung
- Frontend (Fahrgast): Button „Fahrt teilen", Button „Teilen beenden", Anzeige aktiver Freigaben
- Frontend (Vertrauensperson): Fahrtstatus-Ansicht, ETA, keine med. Details

Referenz: `docs/SOURCE_OF_TRUTH.md` (Abschnitt 7.9), `docs/DECISIONS.md`

## Sprint 13 — Online-KI-Berater / ChatGPT-Anbindung

Assistierter Anfrageprozess: KI schlägt Transporttyp und Anforderungen vor.

- Backend-Endpoint `/api/v1/assistant/interpret` (API-Key nur im Backend)
- Integration Claude API (claude-sonnet-4-6 oder höher) oder ChatGPT
- Kontext: Mobilitätsprofil + Fahrtdaten → Vorschlag-Text + strukturierte Feldvorschläge
- Fahrgast kann Vorschlag übernehmen oder manuell anpassen
- Datenschutz: Zustimmung erforderlich, keine unnötige Weitergabe med. Daten

## Sprint 14 — Fahrt per Sprache anfragen

Vollständige Fahrtbuchung per Sprachführung.

- Sprachgeführter Buchungs-Wizard: Abholort → Ziel → Datum/Zeit → Anforderungen → Bestätigung
- Adresseingabe per Sprache (Online-KI-Interpretation)
- Datum/Zeit-Erkennung aus natürlicher Sprache
- Bestätigungs-Dialog vor Absenden (kein automatisches Absenden)

## Sprint 15 — Regelmäßige Touren / Linienverkehr

Fahrgäste können regelmäßige Fahrten (täglich, wöchentlich) als Serienfahrten anlegen.
Disponenten können Touren mit festen Reihenfolgen und Zeitplänen konfigurieren (Linienverkehr).

## Sprint 16 — Ausfallmanagement

Ersatzfahrzeug, Fahrerausfall, Stornierung mit Neuzuweisung.

## Sprint 17 — Tourenoptimierung

KI-gestützte Routenoptimierung für Disponenten.

---

## Bewusst außerhalb des MVP

- Echte Krankenkassenabrechnung
- Zahlungsintegration
- Externe APIs (GTFS, Maps)
- Echtzeit-GPS-Tracking (Live-Positionsdaten vom Fahrzeug) — geplant Sprint 12+
- Native Mobile App
- Push-Notifications
