/* Rezensionintegrator — Vanilla-JS Widget
 * Liest reviews.json (relativer Pfad), rendert Header + Slider + Modal.
 */
(function () {
  'use strict';

  const MOUNT_ID = 'ffs-google-reviews';
  const BASE_URL = new URL('./', document.currentScript.src).href;
  const JSON_URL = new URL('reviews.json', BASE_URL).href;

  function resolveUrl(u) {
    if (!u) return u;
    // Absolute URLs (http/https/data) bleiben unverändert
    if (/^(https?:|data:)/i.test(u)) return u;
    return new URL(u, BASE_URL).href;
  }

  function ratingLabel(avg) {
    if (avg >= 5.0) return 'Ausgezeichnet';
    if (avg >= 4.7) return 'Sehr gut';
    if (avg >= 4.0) return 'Gut';
    return 'Bewertet';
  }

  function starsFilled(rating) {
    const r = Math.round(rating);
    return '★'.repeat(r) + '☆'.repeat(5 - r);
  }

  // "G"-Logo (kreisrund, bunt) — für die obere rechte Ecke jeder Karte
  const GOOGLE_G_SVG = `
    <svg class="google-g" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
    </svg>`;

  // Google-Wordmark (bunt) — HTML/CSS-basiert, robust ohne Product-Sans.
  const GOOGLE_WORDMARK_HTML = `
    <span class="google-wordmark" aria-label="Google">
      <span style="color:#4285F4">G</span><span style="color:#EA4335">o</span><span style="color:#FBBC04">o</span><span style="color:#4285F4">g</span><span style="color:#34A853">l</span><span style="color:#EA4335">e</span>
    </span>`;

  const VERIFIED_SVG = `
    <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M12 2 3 6v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V6l-9-4zm-2 15-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
    </svg>`;

  function avatarColor(name) {
    // Simple hash → HSL
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return `hsl(${h}, 45%, 55%)`;
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function renderAvatar(author) {
    if (author.avatar_url) {
      return `<img class="avatar" src="${escapeHtml(resolveUrl(author.avatar_url))}" alt="${escapeHtml(author.name)}" loading="lazy">`;
    }
    const color = avatarColor(author.name || '?');
    return `<div class="avatar" style="background:${color}" aria-hidden="true">${escapeHtml(author.initial || '?')}</div>`;
  }

  function renderCard(review) {
    return `
      <article class="review-card" data-review-id="${escapeHtml(review.id)}" tabindex="0" role="button" aria-label="Rezension von ${escapeHtml(review.author.name)} lesen">
        ${GOOGLE_G_SVG}
        <div class="author-row">
          ${renderAvatar(review.author)}
          <div class="meta">
            <div class="name">${escapeHtml(review.author.name)}</div>
            <div class="date">${escapeHtml(review.date_display)}</div>
          </div>
        </div>
        <div class="rating-row">
          <span class="stars" aria-label="${escapeHtml(String(review.rating))} von 5 Sternen">${starsFilled(review.rating)}</span>
          ${review.verified ? `<span class="verified" title="Google-Nutzer">${VERIFIED_SVG}</span>` : ''}
        </div>
        <p class="text">${escapeHtml(review.text)}</p>
        <span class="read-more">Weiterlesen</span>
      </article>`;
  }

  function renderSkeleton() {
    let out = '';
    for (let i = 0; i < 4; i++) {
      out += `
        <article class="review-card skeleton" aria-hidden="true">
          <div class="author-row">
            <div class="avatar"></div>
            <div class="meta">
              <div class="sk-line"></div>
              <div class="sk-line short"></div>
            </div>
          </div>
          <div class="sk-line"></div>
          <div class="sk-line"></div>
          <div class="sk-line short"></div>
        </article>`;
    }
    return out;
  }

  function renderHeader(business) {
    return `
      <header class="ffs-gr-header">
        ${GOOGLE_WORDMARK_HTML}
        <span class="label">${escapeHtml(ratingLabel(business.rating_avg))}</span>
        <span class="stars" aria-label="${escapeHtml(String(business.rating_avg))} von 5 Sternen">${starsFilled(business.rating_avg)}</span>
        <span class="score">${Number(business.rating_avg).toFixed(1).replace('.', ',')}</span>
        <span class="separator">│</span>
        <span class="count">${escapeHtml(String(business.rating_count))} Bewertungen</span>
        <a class="cta-button" href="${escapeHtml(business.write_review_url)}" target="_blank" rel="noopener nofollow">Eine Bewertung schreiben</a>
      </header>`;
  }

  function renderModal(review) {
    const reply = review.owner_reply
      ? `<div class="owner-reply"><strong>Antwort des Inhabers (${escapeHtml(review.owner_reply.date_iso || '')}):</strong><br>${escapeHtml(review.owner_reply.text)}</div>`
      : '';
    return `
      <div class="ffs-gr-modal" open role="dialog" aria-modal="true" aria-label="Volle Rezension">
        <div class="box">
          <button class="close" aria-label="Schließen">×</button>
          <div class="author-row" style="margin-bottom:1rem;">
            ${renderAvatar(review.author)}
            <div class="meta">
              <div class="name">${escapeHtml(review.author.name)}</div>
              <div class="date">${escapeHtml(review.date_display)}</div>
            </div>
          </div>
          <div class="rating-row"><span class="stars">${starsFilled(review.rating)}</span></div>
          <p style="white-space:pre-wrap; line-height:1.55;">${escapeHtml(review.text)}</p>
          ${reply}
        </div>
      </div>`;
  }

  function mountModal(review) {
    const wrap = document.createElement('div');
    wrap.innerHTML = renderModal(review);
    const modal = wrap.firstElementChild;
    document.body.appendChild(modal);
    const close = () => modal.remove();
    modal.querySelector('.close').addEventListener('click', close);
    modal.addEventListener('click', e => { if (e.target === modal) close(); });
    document.addEventListener('keydown', function esc(e) {
      if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc); }
    });
  }

  function bindSlider(root, reviewsById) {
    const track = root.querySelector('.ffs-gr-track');
    const prev = root.querySelector('.nav-prev');
    const next = root.querySelector('.nav-next');
    const scrollBy = dir => {
      const card = track.querySelector('.review-card');
      if (!card) return;
      track.scrollBy({ left: (card.offsetWidth + 16) * dir, behavior: 'smooth' });
    };
    prev.addEventListener('click', () => scrollBy(-1));
    next.addEventListener('click', () => scrollBy(1));

    track.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft') { scrollBy(-1); e.preventDefault(); }
      if (e.key === 'ArrowRight') { scrollBy(1); e.preventDefault(); }
    });

    track.addEventListener('click', e => {
      const card = e.target.closest('.review-card');
      if (!card || card.classList.contains('skeleton')) return;
      const id = card.getAttribute('data-review-id');
      const r = reviewsById.get(id);
      if (r) mountModal(r);
    });
    track.addEventListener('keydown', e => {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      const card = e.target.closest('.review-card');
      if (!card || card.classList.contains('skeleton')) return;
      e.preventDefault();
      const id = card.getAttribute('data-review-id');
      const r = reviewsById.get(id);
      if (r) mountModal(r);
    });
  }

  function renderWidget(mount, data) {
    mount.classList.add('ffs-gr-widget');
    mount.innerHTML = `
      ${renderHeader(data.business)}
      <div class="ffs-gr-slider">
        <button class="nav-prev" aria-label="Vorherige Rezensionen" type="button">‹</button>
        <div class="ffs-gr-track" tabindex="0">
          ${data.reviews.map(renderCard).join('')}
        </div>
        <button class="nav-next" aria-label="Nächste Rezensionen" type="button">›</button>
      </div>`;
    const byId = new Map(data.reviews.map(r => [r.id, r]));
    bindSlider(mount, byId);
  }

  function renderSkeletonState(mount) {
    mount.classList.add('ffs-gr-widget');
    mount.innerHTML = `
      <header class="ffs-gr-header">
        <span class="label">Rezensionen werden geladen…</span>
      </header>
      <div class="ffs-gr-slider">
        <div class="ffs-gr-track">${renderSkeleton()}</div>
      </div>`;
  }

  async function boot() {
    const mount = document.getElementById(MOUNT_ID);
    if (!mount) return;
    renderSkeletonState(mount);

    try {
      const resp = await fetch(JSON_URL, { cache: 'no-cache' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      if (!data || !Array.isArray(data.reviews) || !data.business) {
        throw new Error('invalid schema');
      }
      renderWidget(mount, data);
    } catch (err) {
      console.warn('[ffs-gr-widget] failed to load:', err);
      mount.style.display = 'none';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
