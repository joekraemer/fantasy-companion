import os
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from functools import lru_cache

# Load environment variables at module import
load_dotenv()

@dataclass(frozen=True)
class Settings:
    LEAGUE_ID: int
    SWID: str
    ESPN_S2: str
    TEAM_NAME: str
    SEASON_YEAR: int

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Factory to retrieve typed settings from environment variables.
    Cached via lru_cache to ensure singleton-like behavior.
    """
    # Required variables
    required_vars = ["LEAGUE_ID", "SWID", "ESPN_S2"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please check your .env file."
        )

    try:
        league_id = int(os.environ["LEAGUE_ID"])
    except ValueError:
        raise EnvironmentError("LEAGUE_ID must be an integer.")

    swid = os.environ["SWID"]
    espn_s2 = os.environ["ESPN_S2"]

    # Optional variables with defaults
    team_name = os.environ.get("TEAM_NAME", "Turn Your Head and Goff")
    
    season_year_str = os.environ.get("SEASON_YEAR")
    if season_year_str:
        try:
            season_year = int(season_year_str)
        except ValueError:
            raise EnvironmentError("SEASON_YEAR must be an integer.")
    else:
        season_year = datetime.now().year

    return Settings(
        LEAGUE_ID=league_id,
        SWID=swid,
        ESPN_S2=espn_s2,
        TEAM_NAME=team_name,
        SEASON_YEAR=season_year
    )
