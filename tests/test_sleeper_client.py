import pytest
import requests
import requests_mock
from src.engines.sleeper_client import SleeperClient

def test_get_trending_adds():
    client = SleeperClient()
    
    with requests_mock.Mocker() as m:
        m.get(f"{client.BASE_URL}/players/nfl/trending/add?lookback_hours=24&limit=25", 
              json=[{"player_id": "123", "count": 500}])
              
        data = client.get_trending_adds()
        assert len(data) == 1
        assert data[0]["player_id"] == "123"
        assert data[0]["count"] == 500

def test_get_trending_drops():
    client = SleeperClient()
    
    with requests_mock.Mocker() as m:
        m.get(f"{client.BASE_URL}/players/nfl/trending/drop?lookback_hours=24&limit=25", 
              json=[{"player_id": "456", "count": 300}])
              
        data = client.get_trending_drops()
        assert len(data) == 1
        assert data[0]["player_id"] == "456"
        assert data[0]["count"] == 300

def test_get_trending_adds_error():
    client = SleeperClient()
    
    with requests_mock.Mocker() as m:
        m.get(f"{client.BASE_URL}/players/nfl/trending/add?lookback_hours=24&limit=25", status_code=500)
              
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_trending_adds()
