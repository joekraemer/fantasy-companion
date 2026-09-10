import pandas as pd
from typing import Optional

GAMES_URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"

def get_player_stats(year: int) -> pd.DataFrame:
    """
    Downloads and parses season-level player stats parquet file.
    """
    url = f"https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_{year}.parquet"
    df = pd.read_parquet(url)
    
    cols_to_keep = [
        "player_id", "player_name", "recent_team", "targets", "target_share", 
        "air_yards_share", "wopr", "receiving_epa", "rushing_epa", "headshot_url"
    ]
    # Filter only columns that exist to prevent errors if schema changes or some aren't present
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    return df[existing_cols]

def get_snap_counts(year: int) -> pd.DataFrame:
    """
    Downloads and parses season-level snap counts parquet file.
    """
    url = f"https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{year}.parquet"
    df = pd.read_parquet(url)
    
    cols_to_keep = ["player", "team", "offense_snaps", "offense_pct"]
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    return df[existing_cols]

def get_schedule(year: int) -> pd.DataFrame:
    """
    Downloads and parses the games.csv schedule and filters by year.
    """
    df = pd.read_csv(GAMES_URL)
    df = df[df['season'] == year].copy()
    
    cols_to_keep = ["game_id", "week", "home_team", "away_team", "spread_line", "total_line", "roof", "temp", "wind"]
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    return df[existing_cols]

def get_implied_team_totals(year: int, week: int) -> pd.DataFrame:
    """
    Derives implied totals from schedule for a specific year and week.
    Returns a dataframe with game_id, home_team, away_team, and implied totals.
    """
    df = get_schedule(year)
    if 'week' in df.columns:
        df = df[df['week'] == week].copy()
        
    if 'total_line' in df.columns and 'spread_line' in df.columns:
        df['home_implied_total'] = (df['total_line'] - df['spread_line']) / 2
        df['away_implied_total'] = (df['total_line'] + df['spread_line']) / 2
        
    return df

def load_schedule_metadata(year: int) -> pd.DataFrame:
    """
    Fetches the games schedule and Vegas odds from NFLverse.
    Filters for the requested season and returns a cleaned DataFrame.
    """
    df = pd.read_csv(GAMES_URL)
    
    # Filter by year
    if 'season' in df.columns:
        df = df[df['season'] == year]
    
    # Keep only relevant columns
    cols_to_keep = [
        'week', 'away_team', 'home_team', 
        'spread_line', 'total_line', 'roof', 'temp', 'wind'
    ]
    
    # Ensure columns exist before selecting
    existing_cols = [col for col in cols_to_keep if col in df.columns]
    df = df[existing_cols].copy()
    
    return df
