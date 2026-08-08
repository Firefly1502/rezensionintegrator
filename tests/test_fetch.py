import json
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from fetcher import fetch as fetch_module


@patch("fetcher.fetch.fetch_place")
@patch("fetcher.fetch.cache_avatar")
def test_run_writes_valid_reviews_json(mock_cache, mock_fetch, tmp_path, monkeypatch):
    sample = json.loads(
        (Path(__file__).parent / "fixtures" / "places_response_sample.json").read_text("utf-8")
    )
    mock_fetch.return_value = sample
    mock_cache.return_value = "avatars/fake.jpg"

    docs_dir = tmp_path / "docs"
    monkeypatch.setenv("PLACE_ID", "ChIJZybyS393vUcRmrlk8nxVyuE")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "FAKE")
    monkeypatch.setenv("REVIEWS_SOURCE", "places")

    fetch_module.run(docs_dir=docs_dir)

    out = docs_dir / "reviews.json"
    assert out.exists()
    data = json.loads(out.read_text("utf-8"))
    assert data["version"] == 1
    assert data["source"] == "places_api"
    assert len(data["reviews"]) == 2
    assert data["reviews"][0]["author"]["avatar_url"] == "avatars/fake.jpg"


def test_run_missing_env_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("PLACE_ID", raising=False)
    with pytest.raises(SystemExit):
        fetch_module.run(docs_dir=tmp_path / "docs")


@patch("fetcher.fetch.fetch_business")
@patch("fetcher.fetch.cache_avatar")
def test_run_business_source_writes_json(mock_cache, mock_fetch, tmp_path, monkeypatch):
    sample = json.loads(
        (Path(__file__).parent / "fixtures" / "business_response_sample.json").read_text("utf-8")
    )
    biz_info = {
        "place_id": "ChIJZybyS393vUcRmrlk8nxVyuE",
        "name": "Full Flight Sim",
        "google_url": "https://maps.google.com/?cid=123",
    }
    mock_fetch.return_value = (sample, biz_info)
    mock_cache.return_value = "avatars/fake.jpg"

    docs_dir = tmp_path / "docs"
    monkeypatch.setenv("PLACE_ID", "ChIJZybyS393vUcRmrlk8nxVyuE")
    monkeypatch.setenv("GOOGLE_TOKEN_JSON", '{"token": "fake", "refresh_token": "r"}')
    monkeypatch.setenv("REVIEWS_SOURCE", "business")

    fetch_module.run(docs_dir=docs_dir)

    out = docs_dir / "reviews.json"
    assert out.exists()
    data = json.loads(out.read_text("utf-8"))
    assert data["version"] == 1
    assert data["source"] == "business_api"
    assert len(data["reviews"]) == 2


def test_run_business_missing_token_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("PLACE_ID", "X")
    monkeypatch.delenv("GOOGLE_TOKEN_JSON", raising=False)
    monkeypatch.setenv("REVIEWS_SOURCE", "business")
    with pytest.raises(SystemExit):
        fetch_module.run(docs_dir=tmp_path / "docs")


@patch("fetcher.fetch.fetch_business")
def test_run_business_graceful_exit_on_http_error(mock_fetch, tmp_path, monkeypatch):
    mock_fetch.side_effect = requests.HTTPError("503 Server Error")
    docs_dir = tmp_path / "docs"
    monkeypatch.setenv("PLACE_ID", "X")
    monkeypatch.setenv("GOOGLE_TOKEN_JSON", '{"token": "fake"}')
    monkeypatch.setenv("REVIEWS_SOURCE", "business")

    # Kein SystemExit, keine Exception — reviews.json bleibt einfach ungeschrieben.
    fetch_module.run(docs_dir=docs_dir)

    assert not (docs_dir / "reviews.json").exists()
