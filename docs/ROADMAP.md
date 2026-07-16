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

## Sprint 8 — Assistant Core & barrierefreies Onboarding-Fundament ✅

Onboarding-Fundament und Sprachassistenz-Wahl nach erstem Login implementiert.

- **User-Modell erweitert:** `voice_mode_enabled`, `onboarding_completed_at`, `first_login_at`, `last_login_at` (Alembic-Migration `b3c4d5e6f7a8`)
- **Login-Verhalten:** `first_login_at` und `last_login_at` werden beim Login gesetzt
- **UserPublic-Schema:** `needs_onboarding` (computed: true wenn `onboarding_completed_at is None`), neue Felder in `/auth/login` + `/auth/me`
- **Neue Backend-Endpunkte:**
  - `GET /onboarding/status` — Onboarding-Status + Profil-Füllstand
  - `POST /onboarding/preferences` — Wahl speichern, `onboarding_completed_at` setzen
  - `GET /assistant/capabilities` — rollenbasierte Sprachassistenz-Fähigkeitenliste
- **OnboardingView** (`/onboarding`): Zwei große Kacheln „Ja, Sprachführung aktivieren" / „Nein, normale Einrichtung". ARIA, Tastatur, WCAG AA.
- **Router-Guard:** Automatische Weiterleitung nach `/onboarding` wenn `needs_onboarding === true`. Nach Abschluss: Fahrgäste → `/mobility-profile`, alle anderen → `/dashboard`.
- **Rollenbasierte Sidebar:** Fahrgäste sehen nur Dashboard/Fahrten/Mobilitätsprofil. Fahrer sehen Dashboard/Aufträge. Dispo/Provider/Admin sehen Disposition/Fahrzeuge/Fahrer/...
- **Frontend-API:** `api/onboarding.ts`, `api/assistant.ts` (Typen, API-Calls)
- Tests: 26 Pytest-Tests ✅, TypeScript-Check ✅, Vite-Build ✅

Referenz: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`, `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

## Sprint 9 — Sprachgeführter Mobilitätscheck (offline-fähig) ✅

Geführter Mobilitätscheck als offline-fähiges Dialogfundament implementiert.

- **Route:** `/mobility-profile/assistant` (unter PortalLayout, requiresAuth)
- **Fragenkatalog:** `frontend/src/data/mobilityAssistantQuestions.ts` — 10 Fragen, zentral konfiguriert
- **Feldmapping:** 10 vorhandene MobilityProfile-Felder + `voice_mode_enabled` (User) — nur tatsächlich vorhandene Felder
- **Keine Speicherung** bis zur expliziten Bestätigung — lokales Draft-Objekt
- **Zusammenfassung** zeigt alle Antworten mit gesetzten Feldern und ggf. fehlenden Feldhinweisen
- **Text-to-Speech (Browser Web Speech API):** optional, Fallback auf visuelle UI wenn nicht verfügbar. Auto-Vorlesen wenn `voice_mode_enabled = true`.
- **Onboarding-Verknüpfung:** Sprachführung Ja → Fahrgäste landen auf `/mobility-profile/assistant`
- **MobilityProfileView:** CTA-Karte „Geführten Check starten" sichtbar für alle Fahrgäste
- **Fehlende Felder (keine Migration):** `may_not_wait_alone`, `needs_screen_reader_optimized_ui`, `prefers_voice_guidance` → Roadmap Sprint 10+
- **Backend-Änderung:** `GET /assistant/capabilities` — `mobility_profile`-Capability um `guided_check: true`, `guided_check_route`, `offline_supported: true`, `online_ai_supported: false` erweitert
- Tests: 26 Pytest-Tests ✅, TypeScript-Check ✅, Vite-Build ✅

Referenz: `docs/Product/VOICE_ASSISTANT_STRATEGY.md`, `docs/Product/MODULE_ASSISTANT_REQUIREMENTS.md`

## Sprint 9B — Verbesserter Sprachassistent: TTS-Flow, STT-Bestätigung, Tastaturkürzel ✅

Erweiterte Sprachinteraktion für den geführten Mobilitätscheck.

- **TTS-Flow:** Frage vorlesen → nachfragen, ob Optionen vorgelesen werden sollen → nur auf Anfrage vorlesen
- **STT (optional):** Button-gesteuert, nie dauerhaft — `window.SpeechRecognition` / `webkitSpeechRecognition`
- **STT-Bestätigungsdialog:** Erkannte Antwort anzeigen + Bestätigung vor Übernahme
- **Tastaturkürzel:** J/N/W/S/R/H/ArrowLeft/Escape mit sichtbarer Hinweisleiste
- **Neues Utility:** `frontend/src/utils/speech.ts` (TTS + STT + `normalizeSpokenInput`)
- Browser-Test ✅, TypeScript-Check ✅, Vite-Build ✅

## Sprint 10 — Fahrer-Schichtstart & Fahrzeugwahl ✅

Fahrer startet Schicht, wählt Fahrzeug (Standardfahrzeug oder per Kennzeichen), pausiert/beendet Schicht, sieht Tagesaufträge.

- **Backend:** `DriverShift`-Modell mit `ShiftStatus` (active/paused/ended), Alembic-Migration `driver_shifts`-Tabelle
- **`DriverProfile.default_vehicle_id`:** Nullable FK, Seed setzt AM-BUS-1 für driver@access.test; neuer Endpoint `GET /driver/me` liefert Profil + Standardfahrzeug + aktive Schicht in einem Call
- **API-Endpoints:** `GET /driver/me`, `GET /driver/shift/current`, `POST /shift/start|end|pause|resume`, `GET /vehicles/search`, `GET /assignments`
- **Schicht starten:** vehicle_id > license_plate > default_vehicle_id des Profils (Fallback)
- **Fahrer-App (mobile-first):** Große Statuskarte oben, große Aktions-Buttons (56 px+), kein Verwaltungs-UI
  - Szenario A: Standardfahrzeug direkt sichtbar → ein Button „Schicht mit diesem Fahrzeug beginnen"
  - Szenario B: Kennzeichen-Suche → Fahrzeug wählen → „Schicht beginnen"
  - Schicht beenden: immer mit Bestätigungs-Modal (Bottom-Sheet)
- **Auftragsstruktur:** „Linienfahrten" (Platzhalter, Sprint 15) + „Spontane Fahrten" (TransportRequests)
- **Sidebar:** Fahrer-Nav mit „Meine Schicht" + „Meine Aufträge" → `/driver`
- **Tests:** 20/20 passed, TypeScript-Check ✅, Vite-Build ✅
- **Noch nicht:** STT/Spracheingabe, Live-GPS, Push-Notifications, Statusbuttons zugestiegen/ausgestiegen

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
