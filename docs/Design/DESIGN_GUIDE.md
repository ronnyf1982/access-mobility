# Design Guide — access-mobility

Verbindliche Designbeschreibung auf Basis der Referenzbilder in `docs/Design/`.
Die Referenzbilder sind keine 1:1-Vorlage — sie definieren Richtung, Qualitätsniveau und Farbgebung.
UI wird ausschließlich mit Vue-Komponenten und CSS umgesetzt.
**Barrierefreiheit (WCAG AA) und Lesbarkeit haben Vorrang vor exakter Optik.**

---

## Farbpalette

| Token              | Wert        | Verwendung                                             |
|--------------------|-------------|--------------------------------------------------------|
| `color-bg-base`    | `#111111`   | Seitenhintergrund (Dashboard, Portal)                  |
| `color-bg-surface` | `#1a1a1a`   | Cards, Kacheln, Tabellen                               |
| `color-bg-raised`  | `#222222`   | Hover-Zustände, aktive Zeilen                          |
| `color-bg-sidebar` | `#0d0d0d`   | Linke Sidebar (minimal dunkler als Base)               |
| `color-accent`     | `#FFD600`   | Primärer Akzent: Buttons, aktive Nav, Icons, CTAs      |
| `color-accent-dim` | `#B89E00`   | Hover auf Akzent-Elementen                             |
| `color-text-primary`   | `#F0F0F0` | Überschriften, Zahlenwerte, Labels                   |
| `color-text-secondary` | `#9A9A9A` | Beschreibungen, Metainfos, Placeholder               |
| `color-text-on-accent` | `#111111` | Text auf gelbem Hintergrund (Buttons, Badges)        |
| `color-border`     | `#2a2a2a`   | Subtile Trennlinien, Card-Rahmen                       |
| `color-success`    | `#22C55E`   | Status "Bestätigt", positive Rückmeldungen             |
| `color-warning`    | `#FFD600`   | Status "In Bearbeitung" (= Akzentfarbe)                |
| `color-danger`     | `#EF4444`   | Fehler, Stornierung, kritische Zustände                |

---

## Typografie

- **Schriftart:** System-Schrift-Stack — Inter → Segoe UI → sans-serif
- **Hierarchie:**
  - H1 (Hero-Headline): 2.5–3.5rem, bold, Akzentfarbe für Schlüsselwort
  - H2 (Sektionsüberschriften): 1.75rem, semibold, `color-text-primary`
  - H3 (Card-Titel, Widget-Titel): 1rem–1.1rem, semibold
  - Body: 0.875rem–1rem, regular, `color-text-secondary`
  - Label / Meta: 0.75rem, `color-text-secondary`
  - KPI-Zahl: 1.75–2rem, bold, `color-text-primary`

---

## Bereich 1 — Landingpage (öffentlich)

### Struktur

```
Topnav  →  Logo | Nav-Links | CTA-Button
Hero    →  Headline + Subline + Buttons | Fahrzeugbild
Icons   →  3 Feature-Punkte (Icon + Text)
Zielgruppen  →  3 Kacheln nebeneinander
Vorteile     →  Feature-Cards auf dunklem Hintergrund
Footer  →  Logo + mehrspaltiges Link-Grid
```

### Topnav
- Hintergrund: transparent (über Hero) → `color-bg-base` beim Scrollen
- Links: `color-text-secondary`, Hover `color-text-primary`
- CTA-Button rechts: gelber Hintergrund, schwarzer Text, `border-radius: 6px`

### Hero
- Vollbreite, dunkler Hintergrund
- Headline: `color-text-primary`, Schlüsselwort in `color-accent`
- Primär-CTA: `color-accent` Hintergrund, `color-text-on-accent` Text
- Sekundär-CTA: transparenter Hintergrund, `color-accent` Rahmen + Text

### Feature-Kacheln / Zielgruppen-Cards
- Hintergrund: `color-bg-surface`
- Rahmen: `color-border`
- Icon-Hintergrund: `color-accent` (kleines quadratisches Feld, ~36px)
- Hover: leicht aufgehellt (`color-bg-raised`)

---

## Bereich 2 — Portal / Dashboard (geschützt)

### Layout

```
┌─────────────┬───────────────────────────────┬──────────────┐
│   Sidebar   │         Hauptbereich           │ Rechte Panel │
│  (fixiert)  │  Topbar                        │              │
│             │  KPI-Kacheln                   │ Buchungs-    │
│  Logo       │  Datentabelle                  │ übersicht    │
│  Nav-Items  │  (Anstehende Fahrten)          │              │
│             │                                │ Karte        │
│  Support    │                                │ Schnell-     │
│             │                                │ aktionen     │
└─────────────┴───────────────────────────────┴──────────────┘
```

### Sidebar
- Breite: ~220px
- Hintergrund: `color-bg-sidebar`
- Nav-Item: Icon (24px) + Label, `color-text-secondary`
- Aktiver Nav-Item: `color-accent` Hintergrund, `color-text-on-accent` Text + Icon
- Hover: `color-bg-raised`
- Logo oben, Support-Block unten (abgesetzt)

### Topbar
- Hintergrund: `color-bg-base`, untere Border `color-border`
- Globale Suche: `color-bg-surface`, Placeholder in `color-text-secondary`
- Benachrichtigungs-Icon: `color-text-secondary`, Badge bei Aktivität in `color-accent`
- User-Bereich: Avatar + Name, `color-text-primary`

### KPI-Kacheln
- Hintergrund: `color-bg-surface`, Rahmen `color-border`
- Icon-Feld: `color-accent` Hintergrund, ~40×40px, `border-radius: 8px`
- Zahlenwert: 1.75rem, bold, `color-text-primary`
- Label: 0.75rem, `color-text-secondary`
- Trend/Sublabel: klein, `color-text-secondary`

### Datentabelle (Anstehende Fahrten)
- Hintergrund: `color-bg-surface`
- Header: `color-text-secondary`, 0.75rem, uppercase
- Zeilen: dezente untere Border `color-border`, Hover `color-bg-raised`
- Status-Badges:
  - Bestätigt: grüner Hintergrund (`#166534` / `color-success` gedimmt), grüner Text
  - In Bearbeitung: gedimmtes Gelb, `color-accent` Text
  - Storniert: roter Hintergrund, `color-danger` Text

### Rechte Panel
- Buchungsübersicht: Card mit Donut-Chart-Platzhalter, Legende
- Karte/Einsatzübersicht: dunkles Kartentile (in Sprint 1 Platzhalter)
- Schnellaktionen: Icon-Buttons mit `color-accent`-Hintergrund

---

## Buttons

| Variante   | Hintergrund     | Text/Icon           | Rahmen          |
|------------|-----------------|---------------------|-----------------|
| Primary    | `color-accent`  | `color-text-on-accent` | —            |
| Secondary  | transparent     | `color-accent`      | `color-accent`  |
| Ghost      | transparent     | `color-text-primary` | `color-border` |
| Danger     | `color-danger`  | `#FFFFFF`           | —               |

- `border-radius`: 6px
- Padding: 0.5rem 1.25rem
- Font-weight: 600

---

## Abstände & Radii

| Token           | Wert    |
|-----------------|---------|
| Radius klein    | 6px     |
| Radius mittel   | 10px    |
| Radius groß     | 16px    |
| Spacing XS      | 4px     |
| Spacing S       | 8px     |
| Spacing M       | 16px    |
| Spacing L       | 24px    |
| Spacing XL      | 40px    |

---

## Barrierefreiheit

- Kontrastverhältnis Gelb (`#FFD600`) auf Schwarz (`#111111`): ~9.5:1 — WCAG AAA ✓
- Kontrastverhältnis Hellgrau (`#F0F0F0`) auf `#1a1a1a`: ~14:1 — WCAG AAA ✓
- Fokus-Styles immer sichtbar (gelber Outline-Ring, `outline: 2px solid #FFD600`)
- Keine rein farbbasierten Status-Informationen — immer Icon oder Label zusätzlich
- Alle interaktiven Elemente mind. 44×44px Klickfläche
