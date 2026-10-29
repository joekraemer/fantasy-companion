import os
import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
import pandas as pd
import streamlit as st

@pytest.fixture(autouse=True)
def clear_cache():
    st.cache_resource.clear()
    st.cache_data.clear()

@pytest.fixture
def mock_dependencies():
    with patch('src.core.data_manager.DataManager._fetch_nfl_stats') as mock_stats, \
         patch('src.core.data_manager.DataManager._fetch_schedule') as mock_sched, \
         patch('src.core.data_manager.load_schedule_metadata') as mock_meta, \
         patch('src.core.data_manager.DataManager._fetch_my_roster_raw') as mock_roster, \
         patch('src.core.data_manager.DataManager._fetch_free_agents_raw') as mock_fa, \
         patch('src.core.data_manager.DataManager._fetch_sleeper_trending_raw') as mock_trending, \
         patch('src.core.data_manager.ESPNClient') as mock_espn_class, \
         patch('src.core.data_manager.SleeperClient') as mock_sleeper_class:
        
        mock_stats.return_value = pd.DataFrame()
        mock_sched.return_value = pd.DataFrame()
        mock_meta.return_value = pd.DataFrame()
        mock_roster.return_value = pd.DataFrame()
        mock_fa.return_value = pd.DataFrame()
        mock_trending.return_value = pd.DataFrame()
        
        mock_espn = MagicMock()
        mock_espn.get_team_roster.return_value = []
        mock_espn.get_free_agents.return_value = []
        mock_espn.league.settings.name = "Test League"
        mock_espn_class.return_value = mock_espn
        
        mock_sleeper = MagicMock()
        mock_sleeper.get_trending_adds.return_value = []
        mock_sleeper_class.return_value = mock_sleeper
        
        yield

def test_app_boot(mock_dependencies):
    """Simulates a successful app boot with all environment variables."""
    env_vars = {
        'LEAGUE_ID': '123456',
        'TEAM_NAME': 'My Team',
        'SEASON_YEAR': '2023',
        'SWID': '{some-swid}',
        'ESPN_S2': 'some_s2'
    }
    with patch.dict(os.environ, env_vars, clear=True):
        at = AppTest.from_file("../app.py", default_timeout=10)
        at.run()
        assert not at.exception, f"App raised exception: {at.exception[0]}"
        assert len(at.title) > 0, "No title found in the app"
        assert "Fantasy Companion" in at.title[0].value

def test_app_public_league(mock_dependencies):
    """Simulates running the app with only LEAGUE_ID (public league)."""
    env_vars = {
        'LEAGUE_ID': '123456'
    }
    with patch.dict(os.environ, env_vars, clear=True):
        at = AppTest.from_file("../app.py", default_timeout=10)
        at.run()
        assert not at.exception, f"App raised exception: {at.exception[0]}"
        assert len(at.title) > 0, "No title found in the app"
        assert "Fantasy Companion" in at.title[0].value

