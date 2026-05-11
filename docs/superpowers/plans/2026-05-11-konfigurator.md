# Widget-Konfigurator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Baue einen lokalen HTML-Konfigurator (`tools/konfigurator.html`) mit Live-Vorschau und Embed-Code-Generator, der `window.FFS_WIDGET_CONFIG` im Widget aktiviert.

**Architecture:** `widget.js` und `widget.css` werden um Config-Support (CSS Custom Properties + JS Config Object) erweitert. Der Konfigurator ist eine einzelne statische HTML-Datei ohne Server — er setzt `reviewsUrl` intern auf GitHub Pages, damit die Live-Vorschau trotz `file://`-Aufruf funktioniert.

**Tech Stack:** Vanilla JS, CSS Custom Properties, HTML `<input type="color">` / `<input type="range">` / `<details>`, IntersectionObserver (Lazy Load), Clipboard API.

---

### Task 0: widget.css auf CSS Custom Properties umstellen

**Goal:** Alle Hard-Coded Farbwerte und konfigurierbaren Größen in `widget.css` durch CSS Custom Properties ersetzen, die via `style`-Attribut auf `.ffs-gr-widget` überschreibbar sind.

**Files:**
- Modify: `docs/widget.css`

**Acceptance Criteria:**
- [ ] CSS-Variablen `--ffs-accent`, `--ffs-star`, `--ffs-card-bg`, `--ffs-radius` sind auf `.ffs-gr-widget` definiert
- [ ] CTA-Button nutzt `var(--ffs-accent)` statt Hard-Coded `#ddb357`
- [ ] Sterne nutzen `var(--ffs-star)` statt Hard-Coded `#FBBC04`
- [ ] Karten nutzen `var(--ffs-card-bg)` und `var(--ffs-radius)`
- [ ] Bestehendes Widget ohne Config-Objekt sieht identisch aus (Defaults unverändert)

**Verify:** `docs/widget.css` öffnen → kein Hard-Coded `#ddb357` oder `#FBBC04` außerhalb der Variable-Deklaration

**Steps:**

- [ ] **Step 1: CSS-Variablen in `.ffs-gr-widget` ergänzen**

In `docs/widget.css` die bestehende `.ffs-gr-widget`-Regel anpassen. Aktuell sind `--ffs-gold` und `--ffs-star` schon vorhanden — umbenennen auf kanonische Namen und fehlende ergänzen:

```css
.ffs-gr-widget {
  --ffs-accent: #ddb357;        /* war: --ffs-gold */
  --ffs-star: #FBBC04;
  --ffs-card-bg: #ffffff;
  --ffs-radius: 10px;
  --ffs-card-width: 300px;      /* NEU: Kartenbreite */
  --ffs-card-gap: 16px;         /* NEU: Abstand */
  --ffs-max-lines: 8;           /* NEU: Zeilen vor Weiterlesen */
  --ffs-text: #1f1f1f;
  --ffs-muted: #5f6368;
  --ffs-header-color: #f1f3f4;
  --ffs-header-muted: #b8bcc2;
  --ffs-border: #e8eaed;
  --ffs-shadow: 0 1px 3px rgba(0,0,0,.08);
  --ffs-shadow-hover: 0 4px 12px rgba(0,0,0,.12);
  /* ... rest unverändert ... */
}
```

- [ ] **Step 2: `--ffs-gold` → `--ffs-accent` ersetzen**

Alle Stellen in `widget.css` die `var(--ffs-gold)` nutzen auf `var(--ffs-accent)` umbenennen:
- `.ffs-gr-header .cta-button { background: var(--ffs-accent); }`
- `.ffs-gr-modal .box .owner-reply { border-left: 3px solid var(--ffs-accent); }`

- [ ] **Step 3: Hard-Coded Werte durch Variablen ersetzen**

```css
/* border-radius überall ersetzen */
border-radius: var(--ffs-radius);
/* Betrifft: .ffs-gr-header, .review-card, .ffs-gr-modal .box, .ffs-gr-modal .box .owner-reply */

/* Kartenbreite */
.review-card {
  flex: 0 0 var(--ffs-card-width);
  /* min-width bleibt 240px als Fallback */
}

/* Track-Gap */
.ffs-gr-track {
  gap: var(--ffs-card-gap);
}

/* Max-Zeilen */
.review-card .text {
  -webkit-line-clamp: var(--ffs-max-lines);
}
```

- [ ] **Step 4: Commit**

```bash
git add docs/widget.css
git commit -m "refactor(widget): CSS custom properties für konfigurierbare Werte"
```

---

### Task 1: widget.js um Config-Support erweitern

**Goal:** `widget.js` liest `window.FFS_WIDGET_CONFIG`, merged es mit Defaults, setzt CSS-Variablen auf dem Mount-Element und respektiert alle Verhaltens-Config-Keys (maxReviews, minRating, lazyLoad, reviewsUrl, arrows, autoRotate, showDate, showAvatar, showHeader, showCtaButton, ctaButtonText).

**Files:**
- Modify: `docs/widget.js`

**Acceptance Criteria:**
- [ ] `window.FFS_WIDGET_CONFIG` wird mit DEFAULTS gemergt
- [ ] CSS-Variablen (`--ffs-accent`, `--ffs-star`, `--ffs-card-bg`, `--ffs-radius`) werden auf `mount.style` gesetzt
- [ ] `maxReviews` begrenzt die Anzahl der gerenderten Karten
- [ ] `minRating` filtert Reviews unterhalb der Mindestbewertung
- [ ] `lazyLoad: true` → Widget bootet erst wenn Mount-Element im Viewport sichtbar ist (IntersectionObserver)
- [ ] `lazyLoad: false` → Widget bootet sofort (bisheriges Verhalten)
- [ ] `reviewsUrl` überschreibt den Fetch-URL wenn gesetzt
- [ ] `arrows: 'always'` → Pfeile immer sichtbar; `'never'` → Pfeile ausgeblendet; `'desktop'` → nur bei Hover (bisheriges Verhalten)
- [ ] `autoRotate > 0` → Widget scrollt automatisch alle N Sekunden eine Karte weiter
- [ ] `showHeader: false` → Header-Element wird nicht gerendert
- [ ] `showCtaButton: false` → CTA-Button wird nicht gerendert
- [ ] `ctaButtonText` ersetzt den Button-Text
- [ ] `showDate: false` → Datum in Karten ausgeblendet
- [ ] `showAvatar: false` → Avatar in Karten ausgeblendet
- [ ] Widget ohne `window.FFS_WIDGET_CONFIG` verhält sich identisch wie zuvor

**Verify:** `docs/widget.js` in Browser öffnen via GitHub Pages → Widget rendert mit Defaults korrekt

**Steps:**

- [ ] **Step 1: DEFAULTS-Objekt und CFG-Merge am Anfang der IIFE einfügen**

In `docs/widget.js`, direkt nach `'use strict';`:

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
  lazyLoad: true,
  reviewsUrl: null
};
const CFG = Object.assign({}, DEFAULTS, window.FFS_WIDGET_CONFIG || {});
```

- [ ] **Step 2: CSS-Variablen auf Mount-Element setzen**

`renderWidget`-Funktion: direkt nach `mount.classList.add('ffs-gr-widget')`:

```js
mount.style.setProperty('--ffs-accent', CFG.accentColor);
mount.style.setProperty('--ffs-star', CFG.starColor);
mount.style.setProperty('--ffs-card-bg', CFG.cardBackground);
mount.style.setProperty('--ffs-radius', CFG.cardBorderRadius + 'px');
mount.style.setProperty('--ffs-card-width', CFG.cardWidth + 'px');
mount.style.setProperty('--ffs-card-gap', CFG.cardGap + 'px');
mount.style.setProperty('--ffs-max-lines', String(CFG.maxLines));
```

- [ ] **Step 3: `reviewsUrl`-Override im fetch**

`boot`-Funktion — `JSON_URL` ersetzen durch:

```js
const fetchUrl = CFG.reviewsUrl || JSON_URL;
const resp = await fetch(fetchUrl, { cache: 'no-cache' });
```

- [ ] **Step 4: `maxReviews` + `minRating` filtern**

In `renderWidget`, vor `data.reviews.map(renderCard)`:

```js
let reviews = data.reviews;
if (CFG.minRating > 1) reviews = reviews.filter(r => r.rating >= CFG.minRating);
if (CFG.maxReviews > 0) reviews = reviews.slice(0, CFG.maxReviews);
```

- [ ] **Step 5: `showDate` + `showAvatar` in `renderCard` respektieren**

In `renderCard`:

```js
// Avatar
${CFG.showAvatar ? renderAvatar(review.author) : ''}

// Datum
${CFG.showDate ? `<div class="date">${escapeHtml(review.date_display)}</div>` : ''}
```

- [ ] **Step 6: `showHeader`, `showCtaButton`, `ctaButtonText` in `renderHeader`**

```js
function renderHeader(business) {
  if (!CFG.showHeader) return '';
  const ctaHtml = CFG.showCtaButton
    ? `<a class="cta-button" href="${escapeHtml(business.write_review_url)}" target="_blank" rel="noopener nofollow">${escapeHtml(CFG.ctaButtonText)}</a>`
    : '';
  return `
    <header class="ffs-gr-header">
      ${GOOGLE_WORDMARK_HTML}
      <span class="label">${escapeHtml(ratingLabel(business.rating_avg))}</span>
      <span class="stars" aria-label="${escapeHtml(String(business.rating_avg))} von 5 Sternen">${starsFilled(business.rating_avg)}</span>
      <span class="score">${Number(business.rating_avg).toFixed(1).replace('.', ',')}</span>
      <span class="separator">│</span>
      <span class="count">${escapeHtml(String(business.rating_count))} Bewertungen</span>
      ${ctaHtml}
    </header>`;
}
```

- [ ] **Step 7: `arrows`-Config in CSS-Klasse übersetzen**

Nach `renderWidget` in `bindSlider`, Pfeile ein/ausblenden:

```js
if (CFG.arrows === 'always') {
  prev.style.opacity = '1';
  next.style.opacity = '1';
  prev.style.transition = 'none';
  next.style.transition = 'none';
} else if (CFG.arrows === 'never') {
  prev.style.display = 'none';
  next.style.display = 'none';
}
// 'desktop' = Standard CSS (opacity bei hover) — kein JS nötig
```

- [ ] **Step 8: `autoRotate` — automatisches Weiterscollen**

In `bindSlider`, nach den Event-Listenern:

```js
if (CFG.autoRotate > 0) {
  setInterval(() => scrollBy(1), CFG.autoRotate * 1000);
}
```

- [ ] **Step 9: `lazyLoad` — IntersectionObserver**

`boot`-Funktion ersetzen:

```js
async function boot() {
  const mount = document.getElementById(MOUNT_ID);
  if (!mount) return;

  if (!CFG.lazyLoad) {
    await loadAndRender(mount);
    return;
  }

  // Lazy: erst laden wenn sichtbar
  renderSkeletonState(mount);
  const observer = new IntersectionObserver(async (entries, obs) => {
    if (!entries[0].isIntersecting) return;
    obs.disconnect();
    await loadAndRender(mount);
  }, { rootMargin: '200px' });
  observer.observe(mount);
}

async function loadAndRender(mount) {
  renderSkeletonState(mount);
  try {
    const fetchUrl = CFG.reviewsUrl || JSON_URL;
    const resp = await fetch(fetchUrl, { cache: 'no-cache' });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (!data || !Array.isArray(data.reviews) || !data.business) {
      throw new Error('invalid schema');
    }
    let reviews = data.reviews;
    if (CFG.minRating > 1) reviews = reviews.filter(r => r.rating >= CFG.minRating);
    if (CFG.maxReviews > 0) reviews = reviews.slice(0, CFG.maxReviews);
    renderWidget(mount, { ...data, reviews });
  } catch (err) {
    console.warn('[ffs-gr-widget] failed to load:', err);
    mount.style.display = 'none';
  }
}
```

- [ ] **Step 10: `ffsWidgetBoot` nach außen freigeben**

Damit der Konfigurator das Widget nach einer Config-Änderung neu starten kann, am Ende der IIFE, **nach** dem `if (document.readyState === 'loading') { ... } else { boot(); }` Block:

```js
// Export für Konfigurator — ermöglicht Re-Boot nach Config-Änderung
window.ffsWidgetBoot = boot;
```

- [ ] **Step 11: Commit**

```bash
git add docs/widget.js
git commit -m "feat(widget): config-system mit DEFAULTS + window.FFS_WIDGET_CONFIG"
```

---

### Task 2: `tools/konfigurator.html` bauen

**Goal:** Statische HTML-Datei mit zweigeteiltem Layout (Einstellungen links, Live-Vorschau rechts, Embed-Code unten), die das Widget direkt auf der Seite rendert und bei jeder Einstellungsänderung sofort aktualisiert.

**Files:**
- Create: `tools/konfigurator.html`

**Acceptance Criteria:**
- [ ] Datei öffnet sich per Doppelklick im Browser ohne Server
- [ ] Alle 16 Einstellungen (inkl. lazyLoad) sind als Formular-Controls vorhanden
- [ ] Vorschau zeigt echtes Widget mit aktuellen Einstellungen (lädt reviews.json von GitHub Pages)
- [ ] Jede Einstellungsänderung aktualisiert die Vorschau sofort (ohne Reload)
- [ ] Embed-Code am Boden aktualisiert sich live
- [ ] "Kopieren"-Button schreibt Embed-Code in Zwischenablage
- [ ] `lazyLoad` ist für die Konfigurator-Vorschau intern auf `false` gesetzt (Vorschau soll sofort laden)
- [ ] `reviewsUrl` zeigt intern auf `https://firefly1502.github.io/rezensionintegrator/reviews.json`

**Verify:** Datei im Browser öffnen → Akzentfarbe ändern → Widget-Vorschau ändert Farbe sofort → Embed-Code zeigt neuen Farbwert

**Steps:**

- [ ] **Step 1: HTML-Grundstruktur anlegen**

`tools/konfigurator.html` anlegen:

```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FFS Widget-Konfigurator</title>
  <link rel="stylesheet" href="../docs/widget.css">
  <style>
    /* Konfigurator-eigenes CSS — nicht im Widget-Scope */
    *, *::before, *::after { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
      font-size: 14px;
      background: #f8f9fa;
      color: #1f1f1f;
    }
    h1 {
      margin: 0;
      padding: 1rem 1.5rem;
      background: #1f1f1f;
      color: #fff;
      font-size: 1.1rem;
      font-weight: 600;
    }
    .layout {
      display: grid;
      grid-template-columns: 320px 1fr;
      height: calc(100vh - 48px);
    }

    /* Linke Seite: Einstellungen */
    .settings {
      overflow-y: auto;
      border-right: 1px solid #e0e0e0;
      background: #fff;
    }
    details {
      border-bottom: 1px solid #e8eaed;
    }
    summary {
      padding: .7rem 1rem;
      font-weight: 600;
      font-size: .8rem;
      text-transform: uppercase;
      letter-spacing: .05em;
      color: #1a73e8;
      cursor: pointer;
      user-select: none;
      list-style: none;
    }
    summary::before {
      content: '▼ ';
      font-size: .6rem;
    }
    details:not([open]) summary::before { content: '▶ '; }
    .settings-body {
      padding: .5rem 1rem 1rem;
    }
    .field {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: .4rem 0;
      gap: .5rem;
    }
    .field label {
      font-size: .85rem;
      color: #3c4043;
      flex: 1;
    }
    .field input[type="color"] {
      width: 40px;
      height: 28px;
      border: 1px solid #dadce0;
      border-radius: 4px;
      padding: 1px;
      cursor: pointer;
    }
    .field input[type="number"] {
      width: 70px;
      padding: .3rem .5rem;
      border: 1px solid #dadce0;
      border-radius: 4px;
      font-size: .85rem;
    }
    .field input[type="text"] {
      width: 160px;
      padding: .3rem .5rem;
      border: 1px solid #dadce0;
      border-radius: 4px;
      font-size: .85rem;
    }
    .field select {
      padding: .3rem .5rem;
      border: 1px solid #dadce0;
      border-radius: 4px;
      font-size: .85rem;
    }
    /* Toggle-Switch */
    .toggle { position: relative; display: inline-block; width: 36px; height: 20px; }
    .toggle input { opacity: 0; width: 0; height: 0; }
    .toggle .slider {
      position: absolute; inset: 0;
      background: #ccc; border-radius: 20px;
      transition: .2s;
      cursor: pointer;
    }
    .toggle .slider::before {
      content: '';
      position: absolute;
      height: 14px; width: 14px;
      left: 3px; bottom: 3px;
      background: #fff;
      border-radius: 50%;
      transition: .2s;
    }
    .toggle input:checked + .slider { background: #1a73e8; }
    .toggle input:checked + .slider::before { transform: translateX(16px); }

    /* Rechte Seite: Vorschau */
    .preview-pane {
      overflow-y: auto;
      padding: 1.5rem;
      background: #f8f9fa;
    }
    .preview-label {
      font-size: .75rem;
      text-transform: uppercase;
      letter-spacing: .05em;
      color: #80868b;
      margin-bottom: .75rem;
    }

    /* Embed-Code-Leiste unten */
    .embed-bar {
      position: fixed;
      bottom: 0; left: 320px; right: 0;
      background: #fff;
      border-top: 1px solid #e0e0e0;
      padding: .6rem 1rem;
      display: flex;
      align-items: center;
      gap: .75rem;
      z-index: 100;
    }
    .embed-bar label {
      font-weight: 600;
      font-size: .8rem;
      white-space: nowrap;
    }
    .embed-bar textarea {
      flex: 1;
      height: 52px;
      resize: none;
      font-family: 'Courier New', monospace;
      font-size: .75rem;
      border: 1px solid #dadce0;
      border-radius: 4px;
      padding: .4rem .6rem;
      background: #f8f9fa;
    }
    .embed-bar button {
      padding: .5rem 1rem;
      background: #1a73e8;
      color: #fff;
      border: 0;
      border-radius: 6px;
      font-size: .85rem;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
    }
    .embed-bar button:hover { background: #1557b0; }
    .preview-pane { padding-bottom: 80px; }
  </style>
</head>
<body>

<h1>FFS Widget-Konfigurator</h1>

<div class="layout">
  <!-- EINSTELLUNGEN -->
  <div class="settings">

    <details open>
      <summary>Farben &amp; Style</summary>
      <div class="settings-body">
        <div class="field">
          <label>Akzentfarbe (Button)</label>
          <input type="color" id="cfg-accentColor" value="#ddb357">
        </div>
        <div class="field">
          <label>Sternfarbe</label>
          <input type="color" id="cfg-starColor" value="#FBBC04">
        </div>
        <div class="field">
          <label>Karten-Hintergrund</label>
          <input type="color" id="cfg-cardBackground" value="#ffffff">
        </div>
        <div class="field">
          <label>Eckenradius (px)</label>
          <input type="number" id="cfg-cardBorderRadius" value="12" min="0" max="32">
        </div>
      </div>
    </details>

    <details open>
      <summary>Karte</summary>
      <div class="settings-body">
        <div class="field">
          <label>Kartenbreite (px)</label>
          <input type="number" id="cfg-cardWidth" value="300" min="200" max="600">
        </div>
        <div class="field">
          <label>Abstand (px)</label>
          <input type="number" id="cfg-cardGap" value="16" min="0" max="48">
        </div>
        <div class="field">
          <label>Max. Zeilen</label>
          <input type="number" id="cfg-maxLines" value="8" min="2" max="30">
        </div>
        <div class="field">
          <label>Datum anzeigen</label>
          <label class="toggle"><input type="checkbox" id="cfg-showDate" checked><span class="slider"></span></label>
        </div>
        <div class="field">
          <label>Avatar anzeigen</label>
          <label class="toggle"><input type="checkbox" id="cfg-showAvatar" checked><span class="slider"></span></label>
        </div>
      </div>
    </details>

    <details open>
      <summary>Header</summary>
      <div class="settings-body">
        <div class="field">
          <label>Header anzeigen</label>
          <label class="toggle"><input type="checkbox" id="cfg-showHeader" checked><span class="slider"></span></label>
        </div>
        <div class="field">
          <label>CTA-Button anzeigen</label>
          <label class="toggle"><input type="checkbox" id="cfg-showCtaButton" checked><span class="slider"></span></label>
        </div>
        <div class="field">
          <label>Button-Text</label>
          <input type="text" id="cfg-ctaButtonText" value="Eine Bewertung schreiben">
        </div>
      </div>
    </details>

    <details open>
      <summary>Navigation</summary>
      <div class="settings-body">
        <div class="field">
          <label>Pfeile</label>
          <select id="cfg-arrows">
            <option value="desktop">Nur Desktop</option>
            <option value="always">Immer</option>
            <option value="never">Nie</option>
          </select>
        </div>
        <div class="field">
          <label>Auto-Rotate (Sek, 0=aus)</label>
          <input type="number" id="cfg-autoRotate" value="0" min="0" max="60">
        </div>
      </div>
    </details>

    <details open>
      <summary>Filter</summary>
      <div class="settings-body">
        <div class="field">
          <label>Max. Reviews</label>
          <input type="number" id="cfg-maxReviews" value="50" min="1" max="300">
        </div>
        <div class="field">
          <label>Mindest-Sterne</label>
          <select id="cfg-minRating">
            <option value="1">Alle</option>
            <option value="3">3★ und mehr</option>
            <option value="4">4★ und mehr</option>
            <option value="5">Nur 5★</option>
          </select>
        </div>
      </div>
    </details>

    <details open>
      <summary>Performance</summary>
      <div class="settings-body">
        <div class="field">
          <label>Lazy Load</label>
          <label class="toggle"><input type="checkbox" id="cfg-lazyLoad" checked><span class="slider"></span></label>
        </div>
      </div>
    </details>

  </div>

  <!-- VORSCHAU -->
  <div class="preview-pane">
    <div class="preview-label">Live-Vorschau (echte Reviews von GitHub Pages)</div>
    <div id="ffs-google-reviews"></div>
  </div>
</div>

<!-- EMBED-CODE -->
<div class="embed-bar">
  <label>Embed-Code:</label>
  <textarea id="embed-code" readonly></textarea>
  <button id="copy-btn">Kopieren</button>
</div>

<script src="../docs/widget.js"></script>
<script>
(function () {
  const GITHUB_REVIEWS_URL = 'https://firefly1502.github.io/rezensionintegrator/reviews.json';

  function readConfig() {
    return {
      accentColor:      document.getElementById('cfg-accentColor').value,
      starColor:        document.getElementById('cfg-starColor').value,
      cardBackground:   document.getElementById('cfg-cardBackground').value,
      cardBorderRadius: Number(document.getElementById('cfg-cardBorderRadius').value),
      cardWidth:        Number(document.getElementById('cfg-cardWidth').value),
      cardGap:          Number(document.getElementById('cfg-cardGap').value),
      maxLines:         Number(document.getElementById('cfg-maxLines').value),
      showDate:         document.getElementById('cfg-showDate').checked,
      showAvatar:       document.getElementById('cfg-showAvatar').checked,
      showHeader:       document.getElementById('cfg-showHeader').checked,
      showCtaButton:    document.getElementById('cfg-showCtaButton').checked,
      ctaButtonText:    document.getElementById('cfg-ctaButtonText').value,
      arrows:           document.getElementById('cfg-arrows').value,
      autoRotate:       Number(document.getElementById('cfg-autoRotate').value),
      maxReviews:       Number(document.getElementById('cfg-maxReviews').value),
      minRating:        Number(document.getElementById('cfg-minRating').value),
      lazyLoad:         document.getElementById('cfg-lazyLoad').checked,
      reviewsUrl:       GITHUB_REVIEWS_URL  // intern immer GitHub Pages
    };
  }

  function buildEmbedCode(cfg) {
    // reviewsUrl + lazyLoad werden NICHT in den Duda-Embed-Code aufgenommen
    const embedCfg = Object.assign({}, cfg);
    delete embedCfg.reviewsUrl;
    const entries = Object.entries(embedCfg)
      .map(([k, v]) => `  ${k}: ${JSON.stringify(v)}`)
      .join(',\n');
    return `<div id="ffs-google-reviews"></div>\n` +
      `<link rel="stylesheet" href="https://firefly1502.github.io/rezensionintegrator/widget.css">\n` +
      `<script>window.FFS_WIDGET_CONFIG = {\n${entries}\n};<\/script>\n` +
      `<script src="https://firefly1502.github.io/rezensionintegrator/widget.js" defer><\/script>`;
  }

  function reloadPreview(cfg) {
    // Widget-Config global setzen, dann neu mounten
    window.FFS_WIDGET_CONFIG = cfg;
    const mount = document.getElementById('ffs-google-reviews');
    mount.innerHTML = '';
    mount.removeAttribute('style');
    mount.className = '';
    // Widget neu booten (IIFE neu aufrufen geht nicht — stattdessen
    // window.ffsWidgetBoot als Export aus widget.js nutzen)
    if (typeof window.ffsWidgetBoot === 'function') {
      window.ffsWidgetBoot();
    }
  }

  function update() {
    const cfg = readConfig();
    reloadPreview(cfg);
    document.getElementById('embed-code').value = buildEmbedCode(cfg);
  }

  // Event-Listener auf alle Inputs
  document.querySelectorAll('[id^="cfg-"]').forEach(el => {
    el.addEventListener('input', update);
    el.addEventListener('change', update);
  });

  // Kopieren-Button
  document.getElementById('copy-btn').addEventListener('click', () => {
    const ta = document.getElementById('embed-code');
    navigator.clipboard.writeText(ta.value).then(() => {
      const btn = document.getElementById('copy-btn');
      btn.textContent = 'Kopiert!';
      setTimeout(() => { btn.textContent = 'Kopieren'; }, 2000);
    });
  });

  // Initial laden
  update();
})();
</script>

</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add tools/konfigurator.html docs/widget.js
git commit -m "feat: widget-konfigurator mit live-vorschau und embed-code-generator"
```

---

### Task 3: Smoke-Test & Feinschliff

**Goal:** Konfigurator im Browser testen, Edge Cases prüfen, sicherstellen dass das Produktiv-Widget auf GitHub Pages nach den widget.js-Änderungen identisch aussieht wie zuvor.

**Files:**
- Modify: `docs/widget.js` (falls Bugfixes nötig)
- Modify: `tools/konfigurator.html` (falls Bugfixes nötig)

**Acceptance Criteria:**
- [ ] `tools/konfigurator.html` öffnet sich per Doppelklick und zeigt Live-Vorschau (reviews von GitHub Pages geladen)
- [ ] Akzentfarbe ändern → CTA-Button + Owner-Reply-Border ändert Farbe sofort
- [ ] Sternfarbe ändern → Sterne in Vorschau ändern Farbe
- [ ] `maxReviews: 3` → nur 3 Karten sichtbar
- [ ] `minRating: 5` → nur 5-Sterne-Reviews
- [ ] `showHeader: false` → kein Header in Vorschau
- [ ] Embed-Code: `reviewsUrl` ist NICHT enthalten
- [ ] "Kopieren" kopiert Embed-Code in Clipboard
- [ ] Produktiv-Widget auf `https://firefly1502.github.io/rezensionintegrator/widget-test` sieht identisch aus wie vor diesem Plan (Backwards-Compat)

**Verify:** GitHub Pages aufrufen nach Push → Widget-Test-Seite prüfen → kein visueller Unterschied zum Status vor diesem Plan

**Steps:**

- [ ] **Step 1: Konfigurator lokal öffnen und alle Controls durchklicken**

```
Doppelklick auf tools/konfigurator.html
```

Prüfen:
- Vorschau lädt (Reviews sichtbar)
- Farb-Picker ändern Widget-Farben in Echtzeit
- Zahlen-Inputs ändern Layout
- Toggles zeigen/verstecken Elemente
- Embed-Code-Textarea aktualisiert sich

- [ ] **Step 2: Embed-Code in leerem Browser-Tab testen**

Embed-Code aus dem Konfigurator kopieren, in eine leere HTML-Testseite einbauen:

```html
<!DOCTYPE html>
<html><body style="background:#222;padding:2rem;">
<!-- hier Embed-Code einfügen -->
</body></html>
```

Lokal als `test.html` speichern → Browser öffnen → Widget muss korrekt rendern.

- [ ] **Step 3: Backwards-Compat prüfen**

GitHub Pages Widget-Test-Seite aufrufen:
```
https://firefly1502.github.io/rezensionintegrator/widget-test
```
→ Widget ohne Config-Objekt muss identisch zu vorher aussehen.

- [ ] **Step 4: Finale Commits pushen**

```bash
git push origin claude/gallant-shtern-6feb70
```

Dann PR auf `main` erstellen.
