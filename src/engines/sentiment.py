import streamlit as st
from typing import Dict, Any, List

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

@st.cache_data(ttl=900)
def load_trending_adds(limit: int = 500) -> List[Dict[str, Any]]:
    client = SleeperClient()
    return client.get_trending_adds(lookback_hours=24, limit=limit)

@st.cache_data(ttl=900)
def load_trending_drops(limit: int = 500) -> List[Dict[str, Any]]:
    client = SleeperClient()
    return client.get_trending_drops(lookback_hours=24, limit=limit)

class SentimentEngine:
    """
    Analytics engine to surface market sentiment based on Sleeper trending data.
    """
    def __init__(self, client: SleeperClient = None):
        self.client = client or SleeperClient()
        
        # Load trending data (cached to prevent API hammering)
        adds = load_trending_adds(limit=500)
        drops = load_trending_drops(limit=500)
        
        # O(1) lookup dictionaries
        self.adds_dict = {str(p.get('player_id')): p.get('count', 0) for p in adds if p.get('player_id')}
        self.drops_dict = {str(p.get('player_id')): p.get('count', 0) for p in drops if p.get('player_id')}
        
        # Load players mapping
        self.players = load_sleeper_players()
        self.name_to_ids = self._build_name_map()
        
    def _build_name_map(self) -> Dict[str, List[str]]:
        mapping = {}
        for pid, data in self.players.items():
            if not isinstance(data, dict):
                continue
            name = data.get('full_name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
            if name:
                norm = normalize_name(name)
                if norm not in mapping:
                    mapping[norm] = []
                mapping[norm].append(str(pid))
        return mapping

    def get_buzz_score(self, player_name: str) -> int:
        """
        Computes velocity = add_count - drop_count for a player.
        """
        norm_name = normalize_name(player_name)
        player_ids = self.name_to_ids.get(norm_name, [])
        
        if not player_ids:
            return 0
            
        add_count = sum(self.adds_dict.get(pid, 0) for pid in player_ids)
        drop_count = sum(self.drops_dict.get(pid, 0) for pid in player_ids)
                
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
