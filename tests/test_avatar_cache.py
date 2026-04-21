from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fetcher.avatar_cache import cache_avatar, localize_avatars


def _mock_img_response(status=200, content=b"\xff\xd8\xff\xe0fakejpeg"):
    m = MagicMock()
    m.status_code = status
    m.ok = 200 <= status < 300
    m.content = content
    return m


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_downloads_and_returns_path(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response()
    url = "https://lh3.googleusercontent.com/a/test=s128"

    result = cache_avatar(url, tmp_path)

    assert result is not None
    assert result.startswith("avatars/")
    assert result.endswith(".jpg")
    assert (tmp_path / Path(result).name).exists()


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_idempotent(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response()
    url = "https://lh3.googleusercontent.com/a/test=s128"

    cache_avatar(url, tmp_path)
    cache_avatar(url, tmp_path)

    assert mock_get.call_count == 1  # zweites Mal kein neuer Fetch


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_none_url(mock_get, tmp_path):
    assert cache_avatar(None, tmp_path) is None
    mock_get.assert_not_called()


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_http_error_returns_none(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response(status=404)
    result = cache_avatar("https://example.invalid/x", tmp_path)
    assert result is None


@patch("fetcher.avatar_cache.requests.get")
def test_localize_avatars_rewrites_urls(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response()
    data = {
        "reviews": [
            {"author": {"avatar_url": "https://lh3.googleusercontent.com/a/1=s128"}},
            {"author": {"avatar_url": None}},
        ]
    }
    localize_avatars(data, tmp_path)
    assert data["reviews"][0]["author"]["avatar_url"].startswith("avatars/")
    assert data["reviews"][1]["author"]["avatar_url"] is None
