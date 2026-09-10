import os
import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from src.engines.espn_client import ESPNClient
from src.engines.nfl_stats import load_schedule_metadata

class DataManager:
    """
    Central orchestrator that manages ESPN league context and NFLverse data.
    Uses Streamlit caching to prevent hammering APIs.
    """
    def __init__(self, league_id: int, year: int, swid: str, espn_s2: str):
        self.league_id = league_id
        self.year = year
        self.swid = swid
        self.espn_s2 = espn_s2

    @st.cache_resource(ttl=900) # 15 minutes TTL for live league data
    def _get_espn_client(_self) -> ESPNClient:
        """
        Internal cached method to get the ESPNClient.
        """
        return ESPNClient(
            league_id=_self.league_id,
            year=_self.year,
            swid=_self.swid,
            espn_s2=_self.espn_s2
        )

    @st.cache_data(ttl=86400) # 24 hours TTL for static schedule/Vegas data
    def _get_game_environment(_self) -> pd.DataFrame:
        """
        Internal cached method to load the schedule, Vegas odds, and weather data.
        """
        return load_schedule_metadata(_self.year)

    def load_espn_context(self) -> ESPNClient:
        return self._get_espn_client()
        
    def load_game_environment(self) -> pd.DataFrame:
        return self._get_game_environment()

    def get_merged_player_pool(self, week: int, size: int = 100) -> pd.DataFrame:
        """
        Fetches the free agent pool and merges it with the game environment (Vegas/Weather)
        for the given week.
        """
        client = self.load_espn_context()
        schedule_df = self.load_game_environment()
        
        # Get free agents
        fa_list = client.get_free_agents(size=size)
        fa_df = pd.DataFrame(fa_list)
        
        # Define required columns for the UI
        required_cols = ['opponent', 'spread_line', 'total_line', 'roof', 'temp', 'wind']
        
        if fa_df.empty or schedule_df.empty:
            if not fa_df.empty:
                for col in required_cols:
                    fa_df[col] = pd.NA
            return fa_df

        # Filter schedule for the requested week
        week_schedule = schedule_df[schedule_df['week'] == week]

        # Melt schedule to get a mapping of Team -> Game Info
        home_teams = week_schedule.copy()
        if not home_teams.empty:
            home_teams['team'] = home_teams['home_team']
            home_teams['opponent'] = home_teams['away_team']
            home_teams['is_home'] = True
            
        away_teams = week_schedule.copy()
        if not away_teams.empty:
            away_teams['team'] = away_teams['away_team']
            away_teams['opponent'] = away_teams['home_team']
            away_teams['is_home'] = False
            
        team_games = pd.concat([home_teams, away_teams])
        
        if team_games.empty:
            for col in required_cols:
                fa_df[col] = pd.NA
            return fa_df

        # Merge free agents with their game info
        merged_df = fa_df.merge(
            team_games,
            left_on='proTeam',
            right_on='team',
            how='left'
        )
        
        return merged_df
