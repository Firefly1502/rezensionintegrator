import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fetcher.places_api import fetch_place

FIXTURES = Path(__file__).parent / "fixtures"


def _mock_response(status=200, payload=None):
    m = MagicMock()
    m.status_code = status
    m.ok = 200 <= status < 300
    m.json.return_value = payload or {}
    m.text = json.dumps(payload or {})
    return m


@patch("fetcher.places_api.requests.get")
def test_fetch_place_success(mock_get):
    sample = json.loads((FIXTURES / "places_response_sample.json").read_text("utf-8"))
    mock_get.return_value = _mock_response(200, sample)

    result = fetch_place("ChIJtest", "FAKE_KEY")

    assert result["displayName"]["text"] == "Full Flight Sim"
    assert len(result["reviews"]) == 2

    args, kwargs = mock_get.call_args
    assert "places/ChIJtest" in args[0]
    headers = kwargs["headers"]
    assert headers["X-Goog-Api-Key"] == "FAKE_KEY"
    assert "reviews" in headers["X-Goog-FieldMask"]


@patch("fetcher.places_api.requests.get")
def test_fetch_place_http_error(mock_get):
    mock_get.return_value = _mock_response(403, {"error": {"message": "denied"}})
    with pytest.raises(RuntimeError, match="403"):
        fetch_place("ChIJtest", "FAKE_KEY")
