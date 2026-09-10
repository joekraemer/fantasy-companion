import streamlit as st
from typing import Dict, Any

from src.engines.sleeper_client import SleeperClient
from src.core.name_matcher import normalize_name
import requests

@st.cache_data(ttl=86400)
def load_sleeper_players() -> Dict[str, Any]:
    """
    Downloads the master player dictionary from Sleeper.
    Cached for 24 hours to avoid repeatedly downloading the 40MB payload.
    """
    response = requests.get("https://api.sleeper.app/v1/players/nfl")
    response.raise_for_status()
    return response.json()

class SentimentEngine:
    """
    Analytics engine to surface market sentiment based on Sleeper trending data.
    """
    def __init__(self, client: SleeperClient):
        self.client = client
        
        # Load trending data
        self.adds = self.client.get_trending_adds(lookback_hours=24, limit=500)
        self.drops = self.client.get_trending_drops(lookback_hours=24, limit=500)
        
        # Load players mapping
        self.players = load_sleeper_players()
        self.name_to_id = self._build_name_map()
        
    def _build_name_map(self) -> Dict[str, str]:
        mapping = {}
        for pid, data in self.players.items():
            if not isinstance(data, dict):
                continue
            name = data.get('full_name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
            if name:
                mapping[normalize_name(name)] = pid
        return mapping

    def get_buzz_score(self, player_name: str) -> int:
        """
        Computes velocity = add_count - drop_count for a player.
        """
        norm_name = normalize_name(player_name)
        player_id = self.name_to_id.get(norm_name)
        
        if not player_id:
            return 0
            
        add_count = 0
        drop_count = 0
        
        for p in self.adds:
            if str(p.get('player_id')) == str(player_id):
                add_count = p.get('count', 0)
                break
                
        for p in self.drops:
            if str(p.get('player_id')) == str(player_id):
                drop_count = p.get('count', 0)
                break
                
        velocity = add_count - drop_count
        return velocity

    def get_hype_meter(self, player_name: str) -> str:
        """
        Normalizes velocity into categorical labels.
        """
        velocity = self.get_buzz_score(player_name)
        
        if velocity >= 5000:
            return "🔥 Extreme Hype"
        elif velocity >= 1000:
            return "📈 Trending Up"
        elif velocity <= -5000:
            return "📉 Panic Drop"
        elif velocity <= -1000:
            return "🧊 Cooling Off"
        else:
            return "😐 Neutral"
