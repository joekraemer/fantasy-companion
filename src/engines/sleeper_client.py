import requests
from typing import List, Dict, Any

class SleeperClient:
    """
    Sleeper API client for retrieving trending data.
    """
    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self):
        pass

    def get_trending_adds(self, lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Retrieves trending player additions from the Sleeper API.
        """
        url = f"{self.BASE_URL}/players/nfl/trending/add"
        params = {
            "lookback_hours": lookback_hours,
            "limit": limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_trending_drops(self, lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Retrieves trending player drops from the Sleeper API.
        """
        url = f"{self.BASE_URL}/players/nfl/trending/drop"
        params = {
            "lookback_hours": lookback_hours,
            "limit": limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
