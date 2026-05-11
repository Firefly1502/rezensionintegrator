# Widget-Konfigurator – Design-Dokument

**Datum:** 2026-05-11
**Autor:** Michael (MSL12) + Claude
**Status:** Approved

---

## 1. Ziel & Motivation

Ein lokaler Konfigurator, mit dem Stil, Farben und Layout des Google-Reviews-Widgets ohne Claude-Session angepasst werden können. Genutzt selten (bei Website-Designänderungen), nur von Michael.

Ersetzt das Herantasten über Code-Sessions für visuelle Änderungen.

---

## 2. Rahmenbedingungen

| Aspekt | Entscheidung |
|---|---|
| **Nutzer** | Nur Michael, selten |
| **Deployment** | Statische HTML-Datei, kein Server |
| **Config-Übertragung** | Embed-Code-Generator (JS Config Object) |
| **Live-Vorschau** | Ja — echte `reviews.json` von GitHub Pages |
| **Master Dashboard** | Bleibt getrennt vom Beantworter |
| **Datei-Ablage** | `tools/konfigurator.html` im REZENSIONINTEGRATOR-Repo |

---

## 3. Architektur

```
tools/konfigurator.html
│
├── Lädt widget.css + widget.js aus docs/ (relative Pfade)
├── Rendert Live-Vorschau direkt auf der Seite
├── Liest reviews.json von GitHub Pages für echte Daten
└── Erzeugt Embed-Code mit window.FFS_WIDGET_CONFIG

docs/widget.js (Erweiterung)
└── Liest window.FFS_WIDGET_CONFIG beim Boot, merged mit Defaults
```

**Kein Server nötig.** `konfigurator.html` per Doppelklick im Browser öffnen.

**Hinweis CORS:** Chrome blockiert `fetch()` von `file://`-Seiten auf lokale Pfade. Der Konfigurator umgeht das, indem er `reviewsUrl` im Config-Objekt auf die GitHub-Pages-URL setzt — das Widget lädt dann direkt von dort. Internetzugang beim Öffnen des Konfigurators nötig (aber das ist bei einem Tool das ein Live-Widget vorschaut ohnehin sinnvoll).

### Config-Flow

```
Michael öffnet konfigurator.html
  → ändert Einstellung (Farbe, Zahl, Toggle)
  → Vorschau aktualisiert sich sofort (CSS-Vars + Widget-Re-Render)
  → Embed-Code am Boden wird live aktualisiert
  → Michael kopiert Embed-Code
  → Fügt ihn in Duda ein (ersetzt vorherigen)
```

---

## 4. Erzeugter Embed-Code

```html
<!-- Full Flight Sim Google Reviews Widget -->
<div id="ffs-google-reviews"></div>
<link rel="stylesheet" href="https://firefly1502.github.io/rezensionintegrator/widget.css">
<script>window.FFS_WIDGET_CONFIG = {
  accentColor: '#ddb357',
  starColor: '#FBBC04',
  cardBackground: '#ffffff',
  cardBorderRadius: 12,
  cardWidth: 300,
  cardGap: 16,
  maxLines: 8,
  showDate: true,
  showAvatar: true,
  showHeader: true,
  showCtaButton: true,
  ctaButtonText: 'Eine Bewertung schreiben',
  arrows: 'desktop',
  autoRotate: 0,
  maxReviews: 50,
  minRating: 1
  /* reviewsUrl wird vom Konfigurator intern gesetzt, nicht in Duda-Embed-Code */
};</script>
<script src="https://firefly1502.github.io/rezensionintegrator/widget.js" defer></script>
```

---

## 5. Konfigurierbare Einstellungen

### 5.1 Farben & Style

| Einstellung | Typ | Default |
|---|---|---|
| Akzentfarbe (CTA-Button, Highlight) | Color Picker | `#ddb357` |
| Sternfarbe | Color Picker | `#FBBC04` |
| Karten-Hintergrundfarbe | Color Picker | `#ffffff` |
| Eckenradius Karten (px) | Zahl | `12` |

### 5.2 Karte

| Einstellung | Typ | Default |
|---|---|---|
| Kartenbreite (px) | Zahl | `300` |
| Abstand zwischen Karten (px) | Zahl | `16` |
| Max. Zeilen vor "Weiterlesen" | Zahl | `8` |
| Datum anzeigen | Toggle | `an` |
| Avatar anzeigen | Toggle | `an` |

### 5.3 Header

| Einstellung | Typ | Default |
|---|---|---|
| Header anzeigen | Toggle | `an` |
| CTA-Button anzeigen | Toggle | `an` |
| CTA-Button Text | Text | `Eine Bewertung schreiben` |

### 5.4 Navigation

| Einstellung | Typ | Default |
|---|---|---|
| Pfeile anzeigen | Dropdown | `Desktop only` |
| Auto-Rotate Intervall (Sek, 0=aus) | Zahl | `0` |

### 5.5 Filter

| Einstellung | Typ | Default |
|---|---|---|
| Anzahl Reviews (max.) | Zahl | `50` |
| Mindest-Sternzahl | Dropdown (alle / 3★ / 4★ / 5★) | `alle` |

---

## 6. UI-Layout

```
┌─────────────────────────────────────────────────────────────┐
│  FFS Widget-Konfigurator                                    │
├──────────────────────┬──────────────────────────────────────┤
│  EINSTELLUNGEN       │  VORSCHAU                           │
│  (links, scrollbar)  │  (rechts, sticky)                   │
│                      │                                      │
│  ▼ Farben & Style    │  ┌──────────────────────────────┐   │
│    Akzentfarbe  [■]  │  │ Google Ausgezeichnet ★★★★★   │   │
│    Sternfarbe   [■]  │  │ 5,0 │ 219 Bewertungen  [CTA] │   │
│    Card-BG      [■]  │  ├──────────────────────────────┤   │
│    Eckenradius  [12] │  │ [Karte][Karte][Karte][Karte]>│   │
│                      │  └──────────────────────────────┘   │
│  ▼ Karte             │                                      │
│    Breite       [300]│  (echte reviews.json von GitHub)     │
│    Abstand      [16] │                                      │
│    Max-Zeilen   [8]  │                                      │
│    Datum        [✓]  │                                      │
│    Avatar       [✓]  │                                      │
│                      │                                      │
│  ▼ Header            │                                      │
│  ▼ Navigation        │                                      │
│  ▼ Filter            │                                      │
├──────────────────────┴──────────────────────────────────────┤
│  EMBED-CODE                                    [Kopieren]   │
│  <div id="ffs-google-reviews"></div>...                     │
└─────────────────────────────────────────────────────────────┘
```

**UX-Details:**
- Sektionen aufklappbar (Standard: alle offen)
- Embed-Code aktualisiert sich live mit jeder Änderung
- "Kopieren"-Button schreibt Embed-Code in die Zwischenablage
- Farben via nativer `<input type="color">`
- Kein "Speichern"-Button nötig — alles ist im Embed-Code

---

## 7. widget.js Erweiterung

`widget.js` liest beim Boot `window.FFS_WIDGET_CONFIG` und merged es mit den Defaults:

```js
const DEFAULTS = {
  accentColor: '#ddb357',
  starColor: '#FBBC04',
  cardBackground: '#ffffff',
  cardBorderRadius: 12,
  cardWidth: 300,
  cardGap: 16,
  maxLines: 8,
  showDate: true,
  showAvatar: true,
  showHeader: true,
  showCtaButton: true,
  ctaButtonText: 'Eine Bewertung schreiben',
  arrows: 'desktop',
  autoRotate: 0,
  maxReviews: 50,
  minRating: 1,
  reviewsUrl: null   // null = relativer Pfad (Produktion), URL-String = Override (Konfigurator)
};

const CFG = Object.assign({}, DEFAULTS, window.FFS_WIDGET_CONFIG || {});
```

CSS-Werte werden als CSS-Variablen auf das Mount-Element gesetzt (`style="--ffs-accent: …"`). Verhaltenswerte (maxReviews, minRating, etc.) steuern die Render-Logik direkt.

**Wichtig:** Bestehendes Widget ohne Config-Objekt bleibt 100 % kompatibel — alle Defaults entsprechen dem aktuellen Hard-Coded-Stand.

---

## 8. Dateien

| Datei | Änderung |
|---|---|
| `tools/konfigurator.html` | NEU — Konfigurator |
| `docs/widget.js` | Erweiterung: Config-Merge + CSS-Vars |
| `docs/widget.css` | Erweiterung: CSS Custom Properties statt Hard-Coded-Werte |

---

## 9. Nicht im Scope (YAGNI)

- Rich Snippets / Schema.org
- WebP Sprite / Lazy-Load-Optionen
- Trustindex-Verifizierungs-Badge
- Mehrsprachigkeit / Auto-Translate
- Dark Mode
- Muster/Pattern für Card-Background
- Pro-Karte-Konfiguration
- Export als separate config.json

---

## 10. Nächste Schritte

1. Spec reviewen (Michael)
2. Implementierungsplan erstellen (writing-plans skill)
3. `widget.js` um Config-Support erweitern
4. `widget.css` auf CSS Custom Properties umstellen
5. `tools/konfigurator.html` bauen
6. Testen: Konfigurator öffnen, Embed-Code in Duda einfügen
