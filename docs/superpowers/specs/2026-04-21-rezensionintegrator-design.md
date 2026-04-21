# Rezensionintegrator – Design-Dokument

**Datum:** 2026-04-21
**Autor:** Michael (MSL12) + Claude
**Status:** Design (zur Review)

---

## 1. Ziel & Motivation

Ein selbstgebautes Widget zur Anzeige von Google-Rezensionen auf der IONOS/Duda-Website von Full Flight Sim (Griesheim bei Darmstadt) – als Ersatz für das aktuell eingesetzte Trustindex-Widget, um monatliche Kosten zu sparen und volle Gestaltungs-/Funktionshoheit zu gewinnen.

**Optisches Vorbild:** Das bestehende Trustindex-Widget (horizontale Karten-Leiste mit Google-Logo, Ausgezeichnet-Label, 5,0★, 217 Bewertungen, CTA-Button "Eine Bewertung schreiben" und 4–5 sichtbaren Review-Karten).

---

## 2. Rahmenbedingungen

| Aspekt | Beschränkung |
|---|---|
| **Hosting Website** | IONOS Website Builder (Duda-basiert) – kein eigenes Backend möglich (kein PHP/Node) |
| **Einbettung** | Über Dudas "HTML"-/"Embed Code"-Baustein |
| **Google Business Profile API** | OAuth-Zugang vorhanden, aber **Quota-Freigabe ausstehend** (Antrag 2026-04-17, 1–6 Wochen Prüfzeit) |
| **Google Places API (New)** | Verfügbar, 5 Reviews/Abruf, großzügiges Gratiskontingent ($200/Monat) |
| **Ionos-Hosting** | Keine serverseitige Logik auf der Duda-Seite ausführbar |
| **Programmier­kenntnisse Nutzer** | Python stark, TypeScript neu, GitHub-Grundlagen vorhanden aber nicht routiniert |
| **Bestehende Code-Assets** | `RENZENSIONBEANTWORTER` (Flask-App + `reviews_fetcher.py`) mit funktionierendem OAuth-Flow zur Business Profile API |

---

## 3. Architektur-Überblick

```
┌────────────────────────┐                        ┌──────────────────┐
│  Google (Datenquelle)  │                        │  IONOS / Duda    │
│                        │                        │  (Website)       │
│  • Places API (Phase1) │                        │                  │
│  • Business API (Ph.2) │                        │  <HTML Widget>   │
└──────────┬─────────────┘                        │   <div id=…>     │
           │                                      │   <link css>     │
           │ (fetch via Python)                   │   <script js>    │
           ▼                                      │                  │
┌────────────────────────┐                        └──────────┬───────┘
│  GitHub Repo           │                                   │
│  rezensionintegrator   │                                   │ fetch()
│                        │                                   │
│  ├── fetcher/*.py      │  ─── cron täglich ───┐            │
│  ├── widget/*.js/.css  │                      │            │
│  └── docs/reviews.json │ ◄────── schreibt ────┘            │
│                        │                                   │
│  + GitHub Actions      │                                   │
│  + GitHub Pages        │ ─── serviert via CDN ────────────►│
└────────────────────────┘        (widget + JSON)
```

**Kernidee: Entkopplung über stabiles JSON-Schema.** Widget und Datenquelle kennen nur die `reviews.json` als Schnittstelle. Dadurch kann der Fetcher (Phase 1 → Phase 2) getauscht werden, ohne das Widget anzufassen.

---

## 4. Datenmodell (JSON-Schema v1)

Die zentrale Schnittstelle. Wird unter `docs/reviews.json` abgelegt und via GitHub Pages statisch ausgeliefert.

```json
{
  "version": 1,
  "updated_at": "2026-04-21T03:00:00Z",
  "source": "places_api",
  "business": {
    "place_id": "ChIJZybyS393vUcRmrlk8nxVyuE",
    "name": "Full Flight Sim",
    "rating_avg": 5.0,
    "rating_count": 217,
    "google_url": "https://maps.google.com/?cid=…",
    "write_review_url": "https://search.google.com/local/writereview?placeid=ChIJZybyS393vUcRmrlk8nxVyuE"
  },
  "reviews": [
    {
      "id": "…",
      "author": {
        "name": "Juville Beats ™",
        "initial": "J",
        "avatar_url": "https://lh3.googleusercontent.com/…",
        "profile_url": "https://www.google.com/maps/contrib/…"
      },
      "rating": 5,
      "date_iso": "2026-04-16",
      "date_display": "16 April 2026",
      "text": "Absolut geiles Erlebnis! …",
      "language": "de",
      "verified": true,
      "photos": [
        { "url": "…", "thumbnail_url": "…" }
      ],
      "owner_reply": null,
      "source_url": "https://maps.google.com/?cid=…"
    }
  ]
}
```

**Designentscheidungen:**
- `version` erlaubt zukünftige Breaking Changes ohne Widget-Bruch
- `source` signalisiert dem Widget, ob alle oder nur 5 Reviews vorhanden sind
- `date_display` wird **im Fetcher** vorformatiert → Widget bleibt locale-unabhängig
- `author.initial` + `avatar_url` → Fallback-Mechanismus (farbiger Buchstabenkreis)
- `photos` und `owner_reply` optional – Schema zukunftsbereit, auch wenn Places API diese nicht liefert
- Max. Größe bei 217 Reviews: ~150–200 KB JSON – unkritisch, Browser-Cache greift

**Bewusst ausgelassen (YAGNI):** `sentiment`, `tags`, `helpful_count`, `detailed_ratings`.

---

## 5. Widget-Design

### 5.1 Struktur (HTML-Skelett)

```
<section class="ffs-gr-widget">
  <header class="ffs-gr-header">
    <img src="google-logo.svg">
    <span class="label">Ausgezeichnet</span>
    <span class="stars">★★★★★</span>
    <span class="score">5.0</span>
    <span class="separator">│</span>
    <span class="count">217 Bewertungen</span>
    <a class="cta-button" href="[write_review_url]">Eine Bewertung schreiben</a>
  </header>

  <div class="ffs-gr-slider">
    <button class="nav-prev" aria-label="Vorherige">‹</button>
    <div class="ffs-gr-track">
      <article class="review-card">…</article>
      <article class="review-card">…</article>
      …
    </div>
    <button class="nav-next" aria-label="Nächste">›</button>
  </div>
</section>
```

### 5.2 Verhaltens-Entscheidungen

| Aspekt | Entscheidung | Begründung |
|---|---|---|
| **Kartenanordnung** | Horizontaler Slider mit CSS Scroll-Snap | 1:1 wie Vorbild, keine JS-Carousel-Lib nötig |
| **Scroll-Pfeile** | Links/Rechts, erscheinen bei Hover/Fokus | Minimal invasiv |
| **Karten pro Ansicht** | Desktop 4, Tablet 2–3, Mobile 1 (Swipe) | Responsive via Media Queries |
| **"Weiterlesen"** | Modal-Overlay mit vollem Text + Fotos + ggf. Inhaber-Antwort | Bessere Lesbarkeit bei langen Texten |
| **Auto-Rotation** | Nein | Stört Leseverhalten, nicht im Vorbild |
| **Hover Karte** | 2px-Lift + verstärkter Shadow | Dezent, signalisiert Klickbarkeit |
| **CTA-Button** | Gold ~#D4A94C, öffnet Google-Review-Dialog in neuem Tab | Match Vorbild |
| **Sterne** | SVG in Google-Yellow (#FBBC04) | Pixel-scharf |
| **Google-Logo** | Offizielles mehrfarbiges "G" (SVG nach Brand Guidelines) | Rechtskonform |
| **Avatar** | `avatar_url` falls vorhanden, sonst Initial-Kreis, Farbe via Hash | Fallback wie Vorbild |
| **Verified-Badge** | Kleiner blauer Haken neben Sternreihe | Match Vorbild |
| **Schrift** | Vom Parent geerbt (keine Webfont-Ladelast) | Integriert sich in Duda-Design |
| **Review-Fotos** | Thumbnail in Karte, Klick → Modal | Match Vorbild |
| **"Ausgezeichnet"-Label** | Abgeleitet: 5.0=Ausgezeichnet, ≥4.7=Sehr gut, ≥4.0=Gut | Dezent, deutsch |
| **Loading-State** | Skeleton-Karten (grau pulsierend) | Keine Layout-Verschiebung |
| **Error-State** | Widget verstecken | Nie kaputte Seite für Besucher |

### 5.3 Responsive Breakpoints

- **Desktop (≥1024px):** 4 Karten sichtbar, Pfeile erscheinen bei Hover
- **Tablet (768–1023px):** 2–3 Karten sichtbar, Pfeile permanent sichtbar
- **Mobile (<768px):** 1 Karte sichtbar, native Touch-Swipe, Punkt-Navigation

### 5.4 Accessibility

- Tastatur-Navigation: `←`/`→` im fokussierten Slider
- `aria-label` auf Nav-Buttons und CTA
- `alt` auf Avataren und Fotos
- `prefers-reduced-motion` respektieren (keine Transitions)

### 5.5 Größen-Budget

- `widget.js` ≈ 8–10 KB minified (Vanilla JS, keine Framework-Lib)
- `widget.css` ≈ 4–6 KB minified
- Gesamt-Overhead auf Duda-Seite: **<20 KB** + ~150 KB `reviews.json` (Cache-freundlich)

---

## 6. Fetcher-Pipeline

### 6.1 Verzeichnisstruktur

```
rezensionintegrator/
├── .github/workflows/fetch.yml
├── fetcher/
│   ├── fetch.py              # Orchestrator (Env-Var-Switch)
│   ├── places_api.py         # Phase 1: Places API Client
│   ├── business_api.py       # Phase 2: Business Profile API Client
│   ├── normalize.py          # API-Response → Schema
│   └── requirements.txt
├── docs/                     # GitHub Pages Root = Widget-Verzeichnis
│   ├── reviews.json          # Auto-generiert von GitHub Action, täglich
│   ├── widget.js             # Widget-Code (direkt hier entwickelt)
│   ├── widget.css
│   └── avatars/              # Lokal gecachte Reviewer-Avatare
│       └── {hash}.jpg
└── README.md
```

Alle öffentlich ausgelieferten Dateien (`widget.js`, `widget.css`, `reviews.json`, `avatars/*.jpg`) liegen direkt in `docs/`. Kein Symlink, kein Copy-Schritt nötig – GitHub Pages serviert den Ordner 1:1.

**Avatar-Caching (DSGVO-Maßnahme):** Der Fetcher lädt beim Abruf jedes neue Reviewer-Profilbild von `lh3.googleusercontent.com` herunter und speichert es als `docs/avatars/{sha1_hash_der_url}.jpg`. Die `avatar_url` in der `reviews.json` verweist dann auf die lokale Kopie. Dadurch lädt der Besucher-Browser keine Bilder mehr direkt von Google-Servern – Google erhält keine Besucher-IP-Adressen über den Widget-Pfad. Bereits vorhandene Dateien werden übersprungen (Idempotenz).

### 6.2 Phase-1-Fetcher (Places API)

Nutzt Places API (New) Endpoint `places.googleapis.com/v1/places/{place_id}`. Liefert:
- Business-Metadaten (Name, Rating, Total Count, Google-URL)
- Bis zu 5 neueste Reviews mit Autor, Rating, Text, Datum, Foto-URL

Kosten: ~30 Requests/Monat × $0,017 = ~$0,50 – fällt ins $200-Free-Tier.

### 6.3 Phase-2-Fetcher (Business Profile API)

Aktivierung sobald Google-Quota freigegeben (ausstehend seit 2026-04-17). Nutzt 90 % des vorhandenen `RENZENSIONBEANTWORTER/reviews_fetcher.py` Codes. Anpassungen:
- Secrets (Client ID, Secret, Refresh Token) aus GitHub Secrets laden statt aus `credentials.json`
- Rückgabe durch `normalize.py` → gleiches Schema wie Phase 1
- Pagination vollständig (alle 217 Reviews in einem Durchlauf)

Dieser Fetcher liefert zusätzlich:
- `owner_reply` (Ihre Antworten als Inhaber)
- `photos` pro Review (von Reviewern hochgeladene Fotos)
- Stabile Review-IDs über die Zeit

### 6.4 Umschaltung Phase 1 → Phase 2

Ein Umgebungsvariablen-Switch in der GitHub Action:
```yaml
env:
  REVIEWS_SOURCE: places    # Phase 1
  # REVIEWS_SOURCE: business  # Phase 2 (nach Quota-Freigabe)
```
Nach Änderung dieser einen Zeile + einmaligem lokalen OAuth-Flow für den Refresh Token → alle 217 Reviews live.

### 6.5 GitHub Actions Workflow

- **Trigger:** Cron `0 3 * * *` (täglich 3 Uhr UTC / 5 Uhr DE) + manuelles Workflow-Dispatch
- **Runner:** `ubuntu-latest`, Python 3.11
- **Commit-Policy:** Nur committen, wenn sich `docs/reviews.json` geändert hat (kein Commit-Rauschen)
- **Fehler-Policy:** Fetch schlägt fehl → Workflow fehlt rot → keine neue JSON gepusht → Widget behält letzten guten Stand
- **Log:** Jeder Fetch-Run ist in der Action-History einsehbar

### 6.6 Secrets-Inventar

| Secret | Phase | Zweck |
|---|---|---|
| `GOOGLE_MAPS_API_KEY` | 1 | Places API Authentifizierung |
| `GOOGLE_OAUTH_CLIENT_ID` | 2 | OAuth-Client |
| `GOOGLE_OAUTH_CLIENT_SECRET` | 2 | OAuth-Client |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | 2 | Token für Access-Token-Refresh |

---

## 7. Deployment & Integration

### 7.1 GitHub-Repository

- **Name:** `rezensionintegrator`
- **Owner:** `Firefly1502`
- **Sichtbarkeit:** Public (nötig für kostenlose GitHub Pages)
- **Pages-Konfig:** Source = `main` branch, Folder = `/docs`
- **Pages-URL:** `https://firefly1502.github.io/rezensionintegrator/`

### 7.2 Duda-Einbettung

In der Duda-Editor-Seite einen "HTML"/"Embed Code"-Baustein an die gewünschte Stelle ziehen und folgenden Code einfügen:

```html
<div id="ffs-google-reviews"></div>
<link rel="stylesheet" href="https://firefly1502.github.io/rezensionintegrator/widget.css">
<script src="https://firefly1502.github.io/rezensionintegrator/widget.js" defer></script>
```

Drei Zeilen. Alle Widget-/Daten-Updates erfolgen automatisch im Hintergrund.

---

## 8. Phasierung

### V1 (Scope dieses Designs)

- Widget pixel-genau nach Trustindex-Vorbild
- Fetcher Phase 1 (Places API, 5 Reviews) aktiv
- Deployment auf GitHub Pages
- Einbettung auf Duda via HTML-Baustein
- **Build-only** – noch nicht auf Produktions-Domain ersetzt (Trustindex läuft parallel weiter)

### V1.1 (nach Quota-Freigabe)

- Fetcher Phase 2 (Business Profile API, alle 217 Reviews) aktivieren
- Owner-Reply und Photos in Review-Karten anzeigen
- Trustindex auf Website ablösen
- API-Key in Google Cloud rotieren

### V2 ("Review Console" – zukünftig)

Ein einheitliches HTML-basiertes Admin-Tool, das zwei Funktionen vereint:

1. **Widget-Konfigurator:** Anzahl der angezeigten Reviews, Filter (z.B. nur 5-Sterne), Farben, Layout-Varianten, ob Owner-Antworten mit angezeigt werden, etc. → schreibt eine `config.json` die das Widget liest
2. **Rezensions-Beantworter:** Migration von `RENZENSIONBEANTWORTER` Flask-App in das gemeinsame Admin-Tool – gleiche Datenbasis (`reviews.json`), gleiche OAuth-Credentials, gleiche KI-Antwort-Generierung

→ Das alte `RENZENSIONBEANTWORTER`-Projekt wird damit obsolet. Alles unter einem Dach.

### Nicht im Scope (YAGNI)

- Mehrere Google-Standorte
- Quellen-Mix (ProvenExpert, Trustpilot, …)
- Echtzeit-Updates (Live-Push)
- A/B-Testing des Widgets
- Sentiment-Analyse / automatische Tag-Generierung

---

## 9. Risiken & Offene Punkte

| Risiko | Mitigation |
|---|---|
| Google Business Profile API Quota wird abgelehnt | Phase 1 (Places API) läuft dauerhaft – Widget funktioniert, nur mit 5 Reviews |
| Google-API-Key leakt | Restriction auf Places API (New) → maximal $200-Gratiskontingent verbrauchbar; Rotation vor Go-Live |
| GitHub Pages Ausfall | Extrem selten; Widget versteckt sich bei 404 |
| Schema-Evolution | `version`-Feld + Widget liest defensiv (optional chains) |
| Datenschutz (DSGVO) | Reviewer-Avatare werden **lokal** in `docs/avatars/` gecacht – Besucher-IPs fließen nicht an Google. Datenschutzerklärung wird um zwei Abschnitte erweitert: (a) Google Business Profile als Datenquelle für Rezensionen, (b) GitHub Pages als Hosting für Widget-Assets. Texte liegen in `docs/datenschutz-text-entwuerfe.md`. |

---

## 10. Projektdaten (Appendix)

| | |
|---|---|
| **Place ID** | `ChIJZybyS393vUcRmrlk8nxVyuE` |
| **Business** | Full Flight Sim (Griesheim bei Darmstadt) |
| **Google Cloud Projekt** | `FFS-Rezensionbeantworter` |
| **GitHub Username** | `Firefly1502` |
| **Pages-URL** | `https://firefly1502.github.io/rezensionintegrator/` |
| **Refresh-Cadence** | Täglich 03:00 UTC |
| **Quota-Antrag Business Profile API** | 2026-04-17 eingereicht |

---

## 11. Nächste Schritte

1. Dieses Design-Dokument vom Nutzer reviewen lassen
2. Implementierungsplan (writing-plans skill) erstellen
3. Code schreiben (Fetcher, Widget)
4. GitHub-Repo gemeinsam einrichten (geführt)
5. Erste Iteration live schalten (Build-only, kein Ersatz Trustindex)
6. Auf Quota warten → Phase 2 aktivieren → Trustindex ablösen
