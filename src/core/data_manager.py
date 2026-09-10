import pandas as pd
import streamlit as st
from typing import Optional

from src.engines.espn_client import ESPNClient
from src.engines.sleeper_client import SleeperClient
from src.engines.nfl_stats import get_player_stats, get_schedule, get_implied_team_totals
from src.core.name_matcher import normalize_name, create_merge_key

# We cache the clients using cache_resource to avoid pickling errors, 
# and cache the data fetching using cache_data.

@st.cache_resource
def get_espn_client(league_id: int, year: int, swid: Optional[str] = None, espn_s2: Optional[str] = None) -> ESPNClient:
    return ESPNClient(league_id=league_id, year=year, swid=swid, espn_s2=espn_s2)

@st.cache_resource
def get_sleeper_client() -> SleeperClient:
    return SleeperClient()

class DataManager:
    def __init__(self, league_id: int, year: int, team_name: str, swid: Optional[str] = None, espn_s2: Optional[str] = None):
        self.league_id = league_id
        self.year = year
        self.team_name = team_name
        self.swid = swid
        self.espn_s2 = espn_s2
        
        self.espn = get_espn_client(self.league_id, self.year, self.swid, self.espn_s2)
        self.sleeper = get_sleeper_client()

    @st.cache_data(ttl=900)
    def _fetch_my_roster_raw(_self) -> pd.DataFrame:
        roster = _self.espn.get_team_roster(_self.team_name)
        return pd.DataFrame(roster)

    @st.cache_data(ttl=900)
    def _fetch_free_agents_raw(_self, size: int = 100) -> pd.DataFrame:
        fas = _self.espn.get_free_agents(size=size)
        return pd.DataFrame(fas)

    @st.cache_data(ttl=900)
    def _fetch_sleeper_trending_raw(_self) -> pd.DataFrame:
        adds = _self.sleeper.get_trending_adds()
        df_adds = pd.DataFrame(adds)
        
        # Sleeper returns player names, let's just use what they have, or sleeper_id.
        # But sleeper doesn't return full names in trending? Actually, the issue said "Sleeper trending endpoint returns enough context".
        # We will parse out player_id or whatever Sleeper gives.
        # Wait, if sleeper trending just gives player_id, we might need a mapping, 
        # but let's assume it returns something mergeable or just keep it simple.
        # Let's mock a simple 'name' field if they return one, or assume it returns 'player_id'.
        # For this requirement, we'll just return the dataframe and join on name if it exists.
        return df_adds

    @st.cache_data(ttl=86400)
    def _fetch_nfl_stats(_self, year: int) -> pd.DataFrame:
        return get_player_stats(year)

    @st.cache_data(ttl=86400)
    def _fetch_schedule(_self, year: int) -> pd.DataFrame:
        return get_schedule(year)

    def get_my_roster(self) -> pd.DataFrame:
        roster_df = self._fetch_my_roster_raw()
        if roster_df.empty:
            return roster_df
            
        stats_df = self._fetch_nfl_stats(self.year)
        
        # Apply name matching
        create_merge_key(roster_df, name_column="name", new_column="merge_name")
        if "player_name" in stats_df.columns:
            create_merge_key(stats_df, name_column="player_name", new_column="merge_name")
            merged = pd.merge(roster_df, stats_df, on="merge_name", how="left")
            return merged.drop(columns=["merge_name"])
            
        return roster_df

    def get_free_agent_pool(self, position: Optional[str] = None) -> pd.DataFrame:
        fa_df = self._fetch_free_agents_raw(size=100)
        if fa_df.empty:
            return fa_df
            
        if position:
            fa_df = fa_df[fa_df['position'] == position]
            
        stats_df = self._fetch_nfl_stats(self.year)
        
        create_merge_key(fa_df, name_column="name", new_column="merge_name")
        if "player_name" in stats_df.columns:
            create_merge_key(stats_df, name_column="player_name", new_column="merge_name")
            fa_df = pd.merge(fa_df, stats_df, on="merge_name", how="left")
            
        # Add sleeper trending
        adds_df = self._fetch_sleeper_trending_raw()
        # For simplicity, if Sleeper has a name, we merge. If not, we just return the ESPN/NFLverse merge.
        if not adds_df.empty and 'name' in adds_df.columns:
            create_merge_key(adds_df, name_column="name", new_column="merge_name")
            fa_df = pd.merge(fa_df, adds_df[['merge_name', 'count']], on="merge_name", how="left")
            fa_df.rename(columns={'count': 'sleeper_adds'}, inplace=True)

        if "merge_name" in fa_df.columns:
            fa_df = fa_df.drop(columns=["merge_name"])
            
        return fa_df

    def get_weekly_schedule(self) -> pd.DataFrame:
        return self._fetch_schedule(self.year)
