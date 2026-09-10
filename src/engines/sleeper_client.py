import requests
from typing import List, Dict, Any

class SleeperClient:
    """
    Client for interacting with the public Sleeper API, specifically for 
    fetching player trending data.
    """
    BASE_URL = "https://api.sleeper.app/v1"

    def get_trending_adds(self, lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetches trending player additions from Sleeper.
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
        Fetches trending player drops from Sleeper.
        """
        url = f"{self.BASE_URL}/players/nfl/trending/drop"
        params = {
            "lookback_hours": lookback_hours,
            "limit": limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
