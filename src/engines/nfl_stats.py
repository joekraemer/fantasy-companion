import pandas as pd
from typing import Optional

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
    url = "https://github.com/nflverse/nfldata/raw/master/data/games.csv"
    df = pd.read_csv(url)
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
