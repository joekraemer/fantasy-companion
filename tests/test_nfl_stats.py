import pandas as pd
from unittest.mock import patch
from src.engines.nfl_stats import load_schedule_metadata

def test_load_schedule_metadata():
    # Mock data to simulate the games.csv file
    mock_data = pd.DataFrame({
        'season': [2024, 2024, 2023],
        'week': [1, 1, 17],
        'away_team': ['DET', 'BAL', 'KC'],
        'home_team': ['KC', 'KC', 'BAL'],
        'spread_line': [4.5, 3.0, -1.0],
        'total_line': [54.0, 47.5, 45.0],
        'roof': ['outdoors', 'dome', 'outdoors'],
        'temp': [80.0, None, 45.0],
        'wind': [5.0, None, 15.0],
        'extra_col': ['ignore', 'ignore', 'ignore']
    })

    with patch('src.engines.nfl_stats.pd.read_csv') as mock_read_csv:
        mock_read_csv.return_value = mock_data
        
        df = load_schedule_metadata(2024)
        
        # Should only have 2024 data (2 rows)
        assert len(df) == 2
        
        # Check columns (extra_col should be filtered out, season shouldn't be strictly kept unless explicitly asked, but our logic didn't ask for it)
        assert 'extra_col' not in df.columns
        assert 'week' in df.columns
        assert 'spread_line' in df.columns
        
        # Check NaN preservation for temp and wind
        # The second game (BAL @ KC in dome) has None for temp/wind
        dome_game = df[df['away_team'] == 'BAL'].iloc[0]
        assert pd.isna(dome_game['temp'])
        assert pd.isna(dome_game['wind'])
        
        # The first game (DET @ KC) has numeric temp/wind
        outdoor_game = df[df['away_team'] == 'DET'].iloc[0]
        assert outdoor_game['temp'] == 80.0
        assert outdoor_game['wind'] == 5.0
