import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.core.data_manager import DataManager

@patch("src.core.data_manager.get_espn_client")
@patch("src.core.data_manager.get_sleeper_client")
def test_data_manager_get_roster(mock_get_sleeper, mock_get_espn):
    # Setup mocks
    mock_espn = MagicMock()
    mock_get_espn.return_value = mock_espn
    mock_espn.get_team_roster.return_value = [{"name": "Josh Allen", "position": "QB"}]
    
    mock_sleeper = MagicMock()
    mock_get_sleeper.return_value = mock_sleeper
    
    dm = DataManager(league_id=123, year=2023, team_name="My Team")
    
    with patch.object(dm, '_fetch_nfl_stats', return_value=pd.DataFrame({"player_name": ["Josh Allen", "Stefon Diggs"], "targets": [0, 150]})):
        roster_df = dm.get_my_roster()
        
        assert len(roster_df) == 1
        assert "targets" in roster_df.columns
        assert roster_df.iloc[0]["targets"] == 0

@patch("src.core.data_manager.get_espn_client")
@patch("src.core.data_manager.get_sleeper_client")
def test_data_manager_get_free_agents(mock_get_sleeper, mock_get_espn):
    mock_espn = MagicMock()
    mock_get_espn.return_value = mock_espn
    mock_espn.get_free_agents.return_value = [{"name": "Gabe Davis", "position": "WR"}]
    
    mock_sleeper = MagicMock()
    mock_get_sleeper.return_value = mock_sleeper
    
    dm = DataManager(league_id=123, year=2023, team_name="My Team")
    
    with patch.object(dm, '_fetch_nfl_stats', return_value=pd.DataFrame({"player_name": ["Gabriel Davis"], "targets": [80]})):
        with patch.object(dm, '_fetch_sleeper_trending_raw', return_value=pd.DataFrame([{"name": "Gabe Davis", "count": 500}])):
            fa_df = dm.get_free_agent_pool()
            
            assert len(fa_df) == 1
            # Should have matched Gabriel Davis to Gabe Davis because of edge cases
            assert "targets" in fa_df.columns
            assert fa_df.iloc[0]["targets"] == 80
            assert "sleeper_adds" in fa_df.columns
            assert fa_df.iloc[0]["sleeper_adds"] == 500

