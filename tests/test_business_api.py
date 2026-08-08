from unittest.mock import MagicMock, patch

import pytest
import requests

from fetcher import business_api


def _mock_response(status=200, payload=None):
    m = MagicMock(spec=requests.Response)
    m.status_code = status
    m.json.return_value = payload or {}
    if status >= 400:
        m.raise_for_status.side_effect = requests.HTTPError(f"{status} Error", response=m)
    else:
        m.raise_for_status.return_value = None
    return m


@patch("fetcher.business_api.time.sleep")
@patch("fetcher.business_api.requests.get")
def test_get_with_retry_succeeds_after_transient_503(mock_get, mock_sleep):
    mock_get.side_effect = [
        _mock_response(503),
        _mock_response(503),
        _mock_response(200, {"ok": True}),
    ]

    resp = business_api._get_with_retry("https://example/x", headers={})

    assert resp.status_code == 200
    assert mock_get.call_count == 3
    assert mock_sleep.call_args_list[0].args[0] == 2
    assert mock_sleep.call_args_list[1].args[0] == 4


@patch("fetcher.business_api.time.sleep")
@patch("fetcher.business_api.requests.get")
def test_get_with_retry_exhausted_raises(mock_get, mock_sleep):
    mock_get.side_effect = [_mock_response(503) for _ in range(4)]

    with pytest.raises(requests.HTTPError):
        business_api._get_with_retry("https://example/x", headers={})

    assert mock_get.call_count == 4  # 1 initial + 3 retries


@patch("fetcher.business_api.time.sleep")
@patch("fetcher.business_api.requests.get")
def test_get_with_retry_non_retryable_status_raises_immediately(mock_get, mock_sleep):
    mock_get.return_value = _mock_response(403)

    with pytest.raises(requests.HTTPError):
        business_api._get_with_retry("https://example/x", headers={})

    assert mock_get.call_count == 1
    mock_sleep.assert_not_called()
