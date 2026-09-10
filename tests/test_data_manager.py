import pandas as pd
from unittest.mock import patch, MagicMock
from src.core.data_manager import DataManager

@patch('src.core.data_manager.ESPNClient')
@patch('src.core.data_manager.load_schedule_metadata')
def test_data_manager_get_merged_player_pool(mock_load_schedule, MockESPNClient):
    # Mock ESPN free agent pull
    mock_espn_instance = MockESPNClient.return_value
    mock_espn_instance.get_free_agents.return_value = [
        {"name": "Amon-Ra", "proTeam": "DET", "position": "WR", "projectedPoints": 15.0},
        {"name": "Patrick Mahomes", "proTeam": "KC", "position": "QB", "projectedPoints": 20.0},
        {"name": "Free Agent Guy", "proTeam": "FA", "position": "WR", "projectedPoints": 0.0}
    ]
    
    # Mock NFLverse schedule pull
    mock_schedule = pd.DataFrame({
        'week': [1],
        'away_team': ['DET'],
        'home_team': ['KC'],
        'spread_line': [4.5],
        'total_line': [54.0],
        'roof': ['outdoors'],
        'temp': [80.0],
        'wind': [5.0]
    })
    mock_load_schedule.return_value = mock_schedule
    
    # Initialize DataManager
    dm = DataManager(league_id=123, year=2024, swid="X", espn_s2="Y")
    
    # Avoid streamlit caching issues during testing by mocking the public loading methods directly
    with patch.object(dm, 'load_espn_context', return_value=mock_espn_instance), \
         patch.object(dm, 'load_game_environment', return_value=mock_schedule), \
         patch.object(dm, 'get_free_agent_pool', return_value=mock_espn_instance.get_free_agents()):
        
        merged_df = dm.get_merged_player_pool(week=1, size=3)
        
        # Verify basic merging
        assert len(merged_df) == 3
        assert 'opponent' in merged_df.columns
        assert 'total_line' in merged_df.columns
        
        # Check DET player (Away team)
        det_player = merged_df[merged_df['name'] == 'Amon-Ra'].iloc[0]
        assert det_player['opponent'] == 'KC'
        assert det_player['is_home'] == False
        assert det_player['total_line'] == 54.0
        
        # Check KC player (Home team)
        kc_player = merged_df[merged_df['name'] == 'Patrick Mahomes'].iloc[0]
        assert kc_player['opponent'] == 'DET'
        assert kc_player['is_home'] == True
        
        # Check FA player (No team)
        fa_player = merged_df[merged_df['name'] == 'Free Agent Guy'].iloc[0]
        # Opponent will be NaN for FA
        assert pd.isna(fa_player['opponent'])

def test_data_manager_empty_data():
    dm = DataManager(league_id=123, year=2024, swid="X", espn_s2="Y")
    
    # Test when FA pool is empty
    with patch.object(dm, 'get_free_agent_pool', return_value=[]), \
         patch.object(dm, 'load_game_environment', return_value=pd.DataFrame()):
        
        merged_df = dm.get_merged_player_pool(week=1)
        assert merged_df.empty

def test_data_manager_schedule_empty():
    dm = DataManager(league_id=123, year=2024, swid="X", espn_s2="Y")
    
    with patch.object(dm, 'get_free_agent_pool', return_value=[{"name": "Amon-Ra", "proTeam": "DET"}]), \
         patch.object(dm, 'load_game_environment', return_value=pd.DataFrame()):
        
        merged_df = dm.get_merged_player_pool(week=1)
        
        # Check that we still have 1 player
        assert len(merged_df) == 1
        
        # Check that schema was guaranteed
        assert 'opponent' in merged_df.columns
        assert 'total_line' in merged_df.columns
        
        # Values should be NA
        assert pd.isna(merged_df['opponent'].iloc[0])
