"""Google Business Profile API Client (Phase 2).

Wird aktiviert, sobald die Quota freigegeben ist (Antrag seit 2026-04-17).
Bis dahin NotImplementedError — der Orchestrator fällt dann mit einer
klaren Meldung aus. Der produktive Pfad läuft über places_api.py.

Plan für die Implementierung (später):
- Auf `RENZENSIONBEANTWORTER/reviews_fetcher.py` aufsetzen
  (funktionierender OAuth-Flow, paginierter Review-Abruf).
- Credentials aus GitHub Secrets laden statt aus `credentials.json`.
- Rückgabe in den Places-Response analogen Dict, damit `normalize.py`
  mit einer zweiten `normalize_business_response()`-Variante
  das gleiche Schema erzeugen kann.
"""

from __future__ import annotations


def fetch_all_reviews(*args, **kwargs):
    raise NotImplementedError(
        "Business Profile API fetcher ist noch nicht implementiert. "
        "Aktivierung geplant nach Google-Quota-Freigabe. "
        "Bis dahin bitte REVIEWS_SOURCE=places verwenden."
    )
