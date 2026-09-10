import pytest
from unittest.mock import patch, Mock
from src.engines.sleeper_client import SleeperClient

@patch("src.engines.sleeper_client.requests.get")
def test_get_trending_adds(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"player_id": "9482", "count": 1337688}]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = SleeperClient()
    result = client.get_trending_adds(lookback_hours=24, limit=1)

    assert len(result) == 1
    assert result[0]["player_id"] == "9482"
    mock_get.assert_called_once_with(
        "https://api.sleeper.app/v1/players/nfl/trending/add",
        params={"lookback_hours": 24, "limit": 1}
    )

@patch("src.engines.sleeper_client.requests.get")
def test_get_trending_drops(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"player_id": "10235", "count": 253064}]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = SleeperClient()
    result = client.get_trending_drops(lookback_hours=24, limit=1)

    assert len(result) == 1
    assert result[0]["player_id"] == "10235"
    mock_get.assert_called_once_with(
        "https://api.sleeper.app/v1/players/nfl/trending/drop",
        params={"lookback_hours": 24, "limit": 1}
    )
