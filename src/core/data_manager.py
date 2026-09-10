import os
import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from src.engines.espn_client import ESPNClient
from src.engines.nfl_stats import load_schedule_metadata

@st.cache_resource(ttl=900)
def _load_espn_client(league_id: int, year: int, swid: str, espn_s2: str) -> ESPNClient:
    return ESPNClient(
        league_id=league_id,
        year=year,
        swid=swid,
        espn_s2=espn_s2
    )

@st.cache_data(ttl=86400)
def _load_game_environment(year: int) -> pd.DataFrame:
    return load_schedule_metadata(year)

@st.cache_data(ttl=900)
def _get_team_roster(league_id: int, year: int, swid: str, espn_s2: str, team_name: str) -> List[Dict[str, Any]]:
    client = _load_espn_client(league_id, year, swid, espn_s2)
    return client.get_team_roster(team_name)

@st.cache_data(ttl=900)
def _get_free_agents(league_id: int, year: int, swid: str, espn_s2: str, size: int) -> List[Dict[str, Any]]:
    client = _load_espn_client(league_id, year, swid, espn_s2)
    return client.get_free_agents(size=size)

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

    def load_espn_context(self) -> ESPNClient:
        return _load_espn_client(self.league_id, self.year, self.swid, self.espn_s2)
        
    def load_game_environment(self) -> pd.DataFrame:
        return _load_game_environment(self.year)

    def get_merged_player_pool(self, week: int, size: int = 100) -> pd.DataFrame:
        """
        Fetches the free agent pool and merges it with the game environment (Vegas/Weather)
        for the given week.
        """
        schedule_df = self.load_game_environment()
        fa_list = self.get_free_agent_pool(size=size)
        fa_df = pd.DataFrame(fa_list)
        
        # Define required columns for the UI
        required_cols = ['opponent', 'spread_line', 'total_line', 'roof', 'temp', 'wind']
        
        if fa_df.empty or schedule_df.empty:
            if not fa_df.empty:
                for col in required_cols:
                    fa_df[col] = pd.NA
            else:
                fa_df = pd.DataFrame(columns=['name', 'position', 'proTeam'] + required_cols)
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

    def get_my_roster(self, team_name: str) -> List[Dict[str, Any]]:
        return _get_team_roster(self.league_id, self.year, self.swid, self.espn_s2, team_name)
        
    def get_free_agent_pool(self, size: int = 100) -> List[Dict[str, Any]]:
        return _get_free_agents(self.league_id, self.year, self.swid, self.espn_s2, size)
        
    def get_weekly_schedule(self, week: int) -> pd.DataFrame:
        schedule_df = self.load_game_environment()
        return schedule_df[schedule_df['week'] == week]
