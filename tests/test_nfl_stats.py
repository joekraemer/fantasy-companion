import pandas as pd
from unittest.mock import patch
from src.engines.nfl_stats import (
    get_player_stats,
    get_snap_counts,
    get_schedule,
    get_implied_team_totals,
    load_schedule_metadata
)

def test_get_player_stats():
    mock_df = pd.DataFrame({
        "player_id": ["1", "2"],
        "player_name": ["Player One", "Player Two"],
        "recent_team": ["Team A", "Team B"],
        "targets": [10, 5],
        "target_share": [0.3, 0.15],
        "air_yards_share": [0.4, 0.2],
        "wopr": [0.5, 0.25],
        "receiving_epa": [1.5, 0.5],
        "rushing_epa": [0.1, 0.0],
        "headshot_url": ["url1", "url2"],
        "extra_col": ["a", "b"]
    })
    
    with patch("pandas.read_parquet", return_value=mock_df) as mock_read:
        result = get_player_stats(2023)
        mock_read.assert_called_once_with("https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_2023.parquet")
        
        # Check if columns are filtered
        assert "extra_col" not in result.columns
        assert "player_name" in result.columns
        assert len(result.columns) == 10

def test_get_snap_counts():
    mock_df = pd.DataFrame({
        "player": ["Player One", "Player Two"],
        "team": ["Team A", "Team B"],
        "offense_snaps": [50, 60],
        "offense_pct": [0.8, 0.9],
        "extra_col": ["a", "b"]
    })
    
    with patch("pandas.read_parquet", return_value=mock_df) as mock_read:
        result = get_snap_counts(2023)
        mock_read.assert_called_once_with("https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2023.parquet")
        
        assert "extra_col" not in result.columns
        assert "team" in result.columns
        assert len(result.columns) == 4

def test_get_schedule():
    mock_df = pd.DataFrame({
        "game_id": ["game_1", "game_2", "game_3"],
        "season": [2022, 2023, 2023],
        "week": [1, 1, 2],
        "home_team": ["Team A", "Team B", "Team C"],
        "away_team": ["Team D", "Team E", "Team F"],
        "spread_line": [-3.0, 5.0, -7.0],
        "total_line": [50.0, 45.0, 52.0],
        "roof": ["dome", "outdoors", "dome"],
        "temp": [70, 65, 72],
        "wind": [0, 10, 0],
        "extra_col": ["x", "y", "z"]
    })
    
    with patch("pandas.read_csv", return_value=mock_df) as mock_read:
        result = get_schedule(2023)
        mock_read.assert_called_once_with("https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv")
        
        # Should filter by season == 2023
        assert len(result) == 2
        assert "game_1" not in result["game_id"].values
        assert "game_2" in result["game_id"].values
        
        assert "extra_col" not in result.columns
        assert "spread_line" in result.columns
        assert len(result.columns) == 9

def test_get_implied_team_totals():
    mock_df = pd.DataFrame({
        "game_id": ["game_1", "game_2"],
        "season": [2023, 2023],
        "week": [1, 2],
        "home_team": ["Team B", "Team C"],
        "away_team": ["Team E", "Team F"],
        "spread_line": [-5.0, 3.0], # game_1 home favored by 5, game_2 away favored by 3
        "total_line": [45.0, 50.0],
        "roof": ["outdoors", "dome"],
        "temp": [65, 72],
        "wind": [10, 0]
    })
    
    with patch("pandas.read_csv", return_value=mock_df):
        # We fetch week 1
        result = get_implied_team_totals(2023, 1)
        
        assert len(result) == 1
        row = result.iloc[0]
        assert row["game_id"] == "game_1"
        
        # total_line = 45, spread_line = -5
        # home_implied_total = (45 - (-5)) / 2 = 50 / 2 = 25
        # away_implied_total = (45 + (-5)) / 2 = 40 / 2 = 20
        assert row["home_implied_total"] == 25.0
        assert row["away_implied_total"] == 20.0
        
        # Fetch week 2
        result2 = get_implied_team_totals(2023, 2)
        row2 = result2.iloc[0]
        # total_line = 50, spread_line = 3
        # home = (50 - 3) / 2 = 23.5
        # away = (50 + 3) / 2 = 26.5
        assert row2["home_implied_total"] == 23.5
        assert row2["away_implied_total"] == 26.5

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
