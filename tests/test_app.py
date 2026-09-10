import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
import pandas as pd

@pytest.fixture
def mock_app_dependencies():
    with patch("src.core.config.get_settings") as mock_settings, \
         patch("src.core.data_manager.ESPNClient") as mock_espn, \
         patch("src.core.data_manager.SleeperClient") as mock_sleeper, \
         patch("src.core.data_manager.get_player_stats") as mock_stats, \
         patch("src.core.data_manager.get_schedule") as mock_schedule, \
         patch("src.core.data_manager.load_schedule_metadata") as mock_metadata:
        
        mock_settings_obj = MagicMock()
        mock_settings_obj.LEAGUE_ID = 123
        mock_settings_obj.SEASON_YEAR = 2024
        mock_settings_obj.TEAM_NAME = "Team Test"
        mock_settings_obj.SWID = "TEST_SWID"
        mock_settings_obj.ESPN_S2 = "TEST_S2"
        mock_settings.return_value = mock_settings_obj
        
        # Setup ESPN
        espn_instance = mock_espn.return_value
        espn_instance.get_team_roster.return_value = [{"name": "Test Player", "proTeam": "TEST", "position": "QB"}]
        espn_instance.get_free_agents.return_value = [{"name": "FA Player", "proTeam": "TEST", "position": "RB"}]
        espn_instance.league.settings.name = "Test League"
        
        # Setup Sleeper
        sleeper_instance = mock_sleeper.return_value
        sleeper_instance.get_trending_adds.return_value = [{"player_id": "1", "count": 100}]
        
        # Setup NFLverse
        mock_stats.return_value = pd.DataFrame([{"player_name": "Test Player", "fantasy_points": 20.0}])
        mock_schedule.return_value = pd.DataFrame([{"week": 1, "home_team": "TEST", "away_team": "OPP"}])
        mock_metadata.return_value = pd.DataFrame([{"week": 1, "home_team": "TEST", "away_team": "OPP", "spread_line": -3.0, "total_line": 45.0, "roof": "dome", "temp": 70, "wind": 0}])
        
        yield mock_settings

def test_app_successful_boot(mock_app_dependencies):
    at = AppTest.from_file("../app.py", default_timeout=10)
    at.run()
    
    assert not at.exception, f"App crashed with exception: {at.exception}"
    
    # Check if expected UI elements rendered
    assert at.title[0].value == "🏈 Fantasy Companion"
    assert "All data sources loaded successfully." in at.markdown[0].value
    
    # We expect DataFrames to render for Roster, Free Agents, and Schedule
    assert len(at.dataframe) >= 3

def test_app_boot_public_league_only(mock_app_dependencies):
    mock_settings = mock_app_dependencies
    
    # Configure settings for a public league (no SWID or ESPN_S2)
    mock_settings_obj = MagicMock()
    mock_settings_obj.LEAGUE_ID = 456
    mock_settings_obj.SEASON_YEAR = 2024
    mock_settings_obj.TEAM_NAME = "Public Team"
    mock_settings_obj.SWID = None
    mock_settings_obj.ESPN_S2 = None
    mock_settings.return_value = mock_settings_obj
    
    at = AppTest.from_file("../app.py", default_timeout=10)
    at.run()
    
    assert not at.exception, f"App crashed with public league settings: {at.exception}"
    assert at.title[0].value == "🏈 Fantasy Companion"
