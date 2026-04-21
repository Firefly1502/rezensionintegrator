import json
from pathlib import Path
from unittest.mock import patch

import pytest

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


def test_run_business_source_not_implemented(tmp_path, monkeypatch):
    monkeypatch.setenv("PLACE_ID", "X")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "Y")
    monkeypatch.setenv("REVIEWS_SOURCE", "business")
    with pytest.raises(NotImplementedError):
        fetch_module.run(docs_dir=tmp_path / "docs")
