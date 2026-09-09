import pandas as pd

GAMES_URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"

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
    
    # Clean up empty values in weather for dome games
    if 'temp' in df.columns:
        df['temp'] = df['temp'].fillna('N/A')
    if 'wind' in df.columns:
        df['wind'] = df['wind'].fillna('N/A')
        
    return df
