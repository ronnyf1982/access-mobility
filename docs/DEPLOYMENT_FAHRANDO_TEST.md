# Deployment-Anleitung — Fahrando Testzugang

> Diese Anleitung beschreibt den Aufbau und die Inbetriebnahme der Fahrando-Testumgebung.
> Zielgruppe: technisch verantwortliche Person (Ronny Forschner).

---

## 1. Voraussetzungen

| Anforderung | Version / Hinweis |
|---|---|
| Python | 3.13+ |
| Node.js | 20+ |
| Docker Desktop | Läuft, Compose-Plugin vorhanden |
| PostgreSQL | Wird via Docker bereitgestellt — keine lokale Installation nötig |
| Git | `git pull --ff-only` ausführen vor Deployment |

---

## 2. Repository klonen / aktualisieren

```powershell
git clone <repo-url> C:\access-mobility
cd C:\access-mobility
git pull --ff-only
```

---

## 3. Umgebungsvariablen Backend

Datei `backend/.env` (nie in Git — nur lokal):

```env
DATABASE_URL=postgresql://am_user:am_password@localhost:5440/access_mobility
SECRET_KEY=<sicherer-zufallswert>
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:5180
```

Für Produktion `ALLOWED_ORIGINS` auf die tatsächliche Domain setzen.
Aktuell produktiv in Railway: `ALLOWED_ORIGINS=https://fahrando.com,https://www.fahrando.com`

---

## 4. Umgebungsvariablen Frontend

Datei `frontend/.env.local` (nie in Git — nur lokal):

```env
VITE_API_BASE_URL=http://localhost:8010/api/v1
```

Für Produktion: Datei `frontend/.env.production` anlegen (nicht committen, ist in `.gitignore`):

```env
VITE_API_BASE_URL=https://fahrando-api-production.up.railway.app/api/v1
```

---

## 5. Datenbank starten

```powershell
docker compose -f docker-compose.dev.yml up -d
```

Prüfen:

```powershell
docker compose -f docker-compose.dev.yml ps
```

`access_mobility_db` muss `running` zeigen.

---

## 6. Python-Venv einrichten (Backend)

```powershell
cd C:\access-mobility\backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

---

## 7. Datenbankmigrationen ausführen

```powershell
cd C:\access-mobility\backend
.venv\Scripts\python.exe -m alembic upgrade head
```

Erwartete Ausgabe: alle Migrationen bis `(head)` erfolgreich.

---

## 8. Demo-Daten laden (Seed)

```powershell
cd C:\access-mobility\backend
.venv\Scripts\python.exe -m app.scripts.seed_demo_data
```

Das Script ist idempotent — mehrfaches Ausführen ist sicher.

---

## 9. Platform-Admin anlegen (Bootstrap)

**Sicherheitsregel:** Das Passwort darf niemals in Dateien, Logs, Tests oder Dokumentation erscheinen.
Den Befehl lokal im Terminal ausführen. Die Env-Var danach sofort löschen.

```powershell
$env:FAHRANDO_BOOTSTRAP_ADMIN_EMAIL="platform-admin@fahrando.test"
$env:FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME="<Vorname>"
$env:FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME="<Nachname>"
$env:FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD="<SICHERES_PASSWORT_HIER_EINGEBEN>"
cd C:\access-mobility\backend
.venv\Scripts\python.exe -m app.scripts.ensure_platform_admin
Remove-Item Env:\FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD
```

Das Script ist idempotent. Wird der Nutzer erneut gestartet, bleibt das bestehende Passwort unverändert.

---

## 10. Backend starten

```powershell
cd C:\access-mobility\backend
.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8010 --reload
```

Prüfen:

```powershell
Invoke-WebRequest http://localhost:8010/api/v1/health | Select-Object -ExpandProperty Content
```

Erwartete Antwort: `{"status":"ok"}`

---

## 11. Frontend-Abhängigkeiten installieren

```powershell
cd C:\access-mobility\frontend
npm install
```

---

## 12. Frontend im Entwicklungsmodus starten

```powershell
cd C:\access-mobility\frontend
npm run dev
```

Aufruf: `http://localhost:5180`

---

## 13. Frontend für Produktion bauen

Voraussetzung: `frontend/.env.production` muss vorhanden sein (siehe Abschnitt 4).

```powershell
cd C:\access-mobility\frontend
npm run build
```

Build-Artefakte liegen in `frontend/dist/`. Für den Webspace-Upload den Staging-Ordner verwenden (Abschnitt 22).

Prüfen, dass keine lokale URL im Build enthalten ist:

```powershell
Select-String -Path .\dist\assets\*.js -Pattern "localhost","8010","fahrando-api-production"
```

Erwartung: `localhost:8010` → nicht gefunden · `fahrando-api-production` → gefunden.

---

## 14. Schnellstart-Script (Windows)

Alle Schritte in einem:

```powershell
C:\access-mobility\scripts\windows\Start-AccessMobility-Dev.ps1
```

Das Script startet: Docker-DB, Alembic, Seed, uvicorn (neues Fenster), gibt Hinweis für Frontend.

---

## 15. Umgebungsprüfung vor Nutzung

| # | Prüfung | Befehl |
|---|---|---|
| 1 | PostgreSQL läuft (Port 5440) | `docker compose -f docker-compose.dev.yml ps` |
| 2 | Alembic auf Stand `(head)` | `cd backend && .venv\Scripts\python.exe -m alembic current` |
| 3 | Seed aktuell | `cd backend && .venv\Scripts\python.exe -m app.scripts.seed_demo_data` |
| 4 | Backend antwortet (Port 8010) | `GET /api/v1/health → {"status":"ok"}` |
| 5 | Frontend erreichbar (Port 5180) | `http://localhost:5180 → Fahrando Coming-Soon-Seite` |

---

## 16. Verfügbare Testzugänge (Demo-Nutzer)

Alle mit Passwort `Access123!`:

| E-Mail | Rolle |
|---|---|
| `passenger@access.test` | Fahrgast |
| `dispatcher@access.test` | Disponent |
| `provider@access.test` | Fahrdienst-Admin |
| `driver@access.test` | Fahrer |
| `admin@access.test` | Organisations-Admin |

Platform-Admin-Zugänge werden über das Bootstrap-Script angelegt (Abschnitt 9).

---

## 17. Website-Testzugang anlegen (Gate-Schutzseite)

Die Schutzseite `/gate` nutzt ein eigenes Benutzersystem (`preview_access_users`-Tabelle), vollständig getrennt vom App-Login.

**Option A — Über die Admin-UI (empfohlen):**
1. Als Platform-Admin einloggen (`/login`)
2. Sidebar → „Website-Testzugänge"
3. „Neuen Zugang anlegen" → E-Mail/Benutzernamen + Passwort (min. 10 Zeichen) eingeben

**Option B — Direkteintrag per Python (Ersteinrichtung):**

```powershell
$env:_GP = "<PASSWORT_HIER>"; cd C:\access-mobility\backend
.\.venv\Scripts\python.exe -c "
import os, bcrypt, psycopg2
h = bcrypt.hashpw(os.environ['_GP'].encode(), bcrypt.gensalt(12)).decode()
conn = psycopg2.connect('postgresql://access_user:access_pass@localhost:5440/access_mobility')
cur = conn.cursor()
cur.execute('''
  INSERT INTO preview_access_users (email, password_hash, is_active, created_at, updated_at)
  VALUES (%s, %s, TRUE, NOW(), NOW())
  ON CONFLICT (email) DO UPDATE SET password_hash=EXCLUDED.password_hash, is_active=TRUE, updated_at=NOW()
''', ('<BENUTZERNAME_HIER>', h))
conn.commit(); conn.close(); print('OK')
"
$env:_GP = ""
```

Das Passwort wird nur im Arbeitsspeicher verarbeitet — nie in Dateien gespeichert.

**Sicherheitsregeln:**
- `password_hash` nie in API-Responses
- Gleiche 401-Antwort für alle Fehler (kein Enumeration-Angriff)
- Unlock per `sessionStorage.fahrando_preview_unlocked = '1'` — kein Token, kein Cookie

---

## 17a. Vite Dev-Server Proxy

Der Vite Dev-Server leitet alle `/api`-Requests an das Backend (Port 8010) weiter.
Konfiguriert in `frontend/vite.config.ts`:

```ts
proxy: {
  '/api': {
    target: 'http://localhost:8010',
    changeOrigin: true,
  },
},
```

Für Produktivbetrieb: nginx/Caddy übernimmt das Forwarding — kein Proxy im Build nötig.

---

## 18. Login-Flow

1. `http://localhost:5180` öffnen → Fahrando Coming-Soon-Seite
2. E-Mail und Passwort eingeben → „Einloggen"
3. Weiterleitung:
   - Erster Login → `/onboarding`
   - Folgelogins → `/dashboard`
   - Platform-Admin → `/platform-admin/users` (über Sidebar)
4. Logout → Rückkehr zu `http://localhost:5180` (Startseite)

---

## 18. Gate-Login-Flow

**Variante B (aktiv seit Sprint FAHRANDO-GATE-PROTECTS-LOGIN-DIRECTLINK-1):**
Alle Routen außer `/gate`, `/impressum`, `/datenschutz` erfordern Gate-Unlock.

1. Beliebige Route direkt aufrufen (z. B. `/`, `/login`, `/platform-admin`) → automatische Weiterleitung zu `/gate?redirect=<Ziel>`
2. Website-Testzugang (E-Mail + Passwort) eingeben → „Einloggen"
3. Bei Erfolg: `sessionStorage.fahrando_preview_unlocked = '1'` gesetzt → Weiterleitung zur ursprünglich angefragten Route (Fallback: `/`)
4. Nach Gate-Unlock:
   - `/login` → normaler App-Login erscheint
   - `/platform-admin` → App-Auth-Guard greift → bei nicht App-eingeloggt → `/login`
   - `/` → Landingpage
5. `/impressum` und `/datenschutz` sind **ohne** Gate-Freigabe zugänglich (`gateExempt`)
6. App-Login ist vollständig getrennt vom Gate — kein App-JWT durch Gate

---

## 19. Platform-Admin-Zugang verifizieren

```powershell
# Login
$body = '{"email":"platform-admin@fahrando.test","password":"<PASSWORT>"}'
$r = Invoke-WebRequest -Uri "http://localhost:8010/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
$token = ($r.Content | ConvertFrom-Json).access_token

# Eigenes Profil prüfen
$headers = @{Authorization = "Bearer $token"}
Invoke-WebRequest -Uri "http://localhost:8010/api/v1/auth/me" -Headers $headers | Select-Object -ExpandProperty Content

# Nutzerliste abrufen
Invoke-WebRequest -Uri "http://localhost:8010/api/v1/platform-admin/users" -Headers $headers | Select-Object -ExpandProperty Content
```

---

## 20. Sicherheitsregeln (unverhandelbar)

- CORS: nur konfigurierte Origins in `ALLOWED_ORIGINS` — niemals `*`
- JWT: `SECRET_KEY` muss ein sicherer Zufallswert sein (mind. 32 Bytes, kryptografisch sicher)
- Platform-Admin-Passwort: nur per Env-Var, nie in Dateien, Logs, Tests, Seed oder Doku
- Passwort-Hashing: bcrypt via `passlib`/`bcrypt`-Direktaufruf (Python 3.13-kompatibel)
- Medizinische Felder: freiwillig, kein Pflichtfeld (Art. 9 DSGVO)
- API-Key (KI-Features): nur im Backend, nie im Frontend-Code oder Build-Output

---

## 22. Statisches Frontend — Webspace-Upload via FileZilla

### Voraussetzungen

- `frontend/.env.production` vorhanden mit Railway-URL (nicht committen)
- Frontend gebaut: `cd C:\access-mobility\frontend && npm run build`
- Upload-Staging-Ordner befüllt:
  ```powershell
  cd C:\access-mobility
  Remove-Item .\deploy\fahrando-webspace-upload\* -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item .\frontend\dist\* .\deploy\fahrando-webspace-upload\ -Recurse -Force
  ```
- **Upload-Quelle: `C:\access-mobility\deploy\fahrando-webspace-upload\`** (nicht `frontend/dist/` direkt)
- `.htaccess` muss im Upload-Ordner vorhanden sein (SPA-Fallback, Apache)
- Backend läuft auf Railway — kein Backend-Upload auf Webspace

### Inhalt von dist (wird hochgeladen)

| Datei/Ordner | Zweck |
|---|---|
| `index.html` | Einstiegspunkt der SPA |
| `assets/` | JS, CSS, Fonts, Icons |
| `Logo1.png` | Branding-Bild |
| `.htaccess` | SPA-Fallback für Apache (Direktlinks) |

### .htaccess (SPA-Fallback für Apache)

Liegt in `frontend/dist/.htaccess` — muss hochgeladen werden, damit Direktlinks wie `/login`, `/impressum`, `/datenschutz` nicht 404 geben.

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /

  RewriteRule ^index\.html$ - [L]

  RewriteCond %{REQUEST_FILENAME} -f [OR]
  RewriteCond %{REQUEST_FILENAME} -d
  RewriteRule ^ - [L]

  RewriteRule . /index.html [L]
</IfModule>
```

### FileZilla — Schritt-für-Schritt

**A) Verbinden**

1. FileZilla öffnen → „Datei" → „Servermanager"
2. Zugangsdaten aus united-domains Kundencenter eintragen:
   - Host: aus Kundencenter (z. B. `ssh.hosting.example.com`)
   - Protokoll: **SFTP** bevorzugt, sonst FTP-TLS
   - Benutzer + Passwort: aus Kundencenter
   - Port: 22 (SFTP) oder 21 (FTP)
3. Verbinden

**B) Zielordner finden**

Typische Document-Root bei united-domains für `fahrando.com`:

- `/www/`
- `/htdocs/`
- `/html/`
- `/public_html/`
- `/fahrando.com/`

Im rechten FileZilla-Panel navigieren, bis `index.html` (falls schon vorhanden) sichtbar ist.

**C) Backup des bestehenden Webspace-Inhalts**

Vor dem Upload:
1. Im rechten Panel (Server) bestehenden Inhalt markieren
2. Lokal herunterladen in: `C:\access-mobility\backup-before-fahrando-upload\`
3. Erst danach hochladen

**D) Upload**

1. Im linken Panel (lokal) navigieren zu: `C:\access-mobility\deploy\fahrando-webspace-upload\`
2. Alle Dateien und Ordner **innerhalb** des Ordners markieren (nicht den Ordner selbst)
3. In die Document-Root des Servers ziehen / hochladen
4. Sicherstellen:
   - `index.html` liegt **direkt** in der Document-Root
   - `assets/` liegt **neben** `index.html`
   - `.htaccess` liegt **neben** `index.html`
   - `Logo1.png` liegt **neben** `index.html`
5. Upload abwarten — alle Dateien müssen übertragen sein

**E) Nicht hochladen**

- `src/`
- `node_modules/`
- `package.json` / `package-lock.json`
- `.env` / `.env.local`
- `.git/`
- `backend/`
- `docs/`
- Logdateien

### Wichtiger Hinweis: API / Gate-Login

> Das statische Frontend funktioniert vollständig für Optik, Routing und Direktlinks.
> Gate-Login und alle App-Funktionen laufen online gegen die Railway API (`https://fahrando-api-production.up.railway.app`).
> Voraussetzung: `frontend/.env.production` mit Railway-URL muss vor dem Build vorhanden sein.

---

## 23. Online-Test nach Webspace-Upload

Nach dem Upload auf fahrando.com folgende Tests ausführen (sessionStorage vor jedem Test leeren):

| # | Test | Erwartetes Ergebnis |
|---|---|---|
| 1 | `https://fahrando.com/` aufrufen | Gate erscheint (`/gate?redirect=/`) |
| 2 | Gate-Login (Website-Testzugang) | Weiterleitung zu `/`, Landingpage erscheint |
| 3 | sessionStorage löschen, `/login` aufrufen | Gate erscheint (`/gate?redirect=/login`) |
| 4 | Gate-Login | Weiterleitung zu `/login`, normaler App-Login erscheint |
| 5 | App-Login mit `admin@access.test` / `Access123!` | Weiterleitung zu `/dashboard` oder `/onboarding` |
| 6 | Platform-Admin → Website-Testzugänge | Liste lädt über Railway API |
| 7 | Platform-Admin → Benutzerverwaltung | Liste lädt über Railway API |
| 8 | sessionStorage löschen, `/platform-admin` aufrufen | Gate erscheint |
| 9 | `/impressum` aufrufen (ohne Gate-Unlock) | Direkt erreichbar, kein Gate |
| 10 | `/datenschutz` aufrufen (ohne Gate-Unlock) | Direkt erreichbar, kein Gate |
| 11 | Browser-DevTools → Network → Request an `/api/v1/...` | URL zeigt Railway (`fahrando-api-production.up.railway.app`) |

---

## 21. Bekannte Einschränkungen (Testumgebung)

- Kein E-Mail-Versand (kein SMTP konfiguriert)
- Kein SSL/TLS im Entwicklungsmodus (lokale Nutzung)
- JWT in `localStorage` — akzeptables Risiko für Testbetrieb, für Produktivbetrieb Keycloak/Auth0 mit httpOnly-Cookies vorgesehen
- Demo-Daten enthalten keine echten Personendaten
- Keine Zahlungsintegration
- Keine GPS-Daten / Live-Tracking (geplant Sprint 12)
