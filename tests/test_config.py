import os
import pytest
from datetime import datetime
from unittest.mock import patch
from src.core.config import get_settings, Settings

@pytest.fixture(autouse=True)
def clear_lru_cache():
    # Clear the lru_cache of get_settings before each test
    get_settings.cache_clear()

def test_successful_load():
    mock_env = {
        "LEAGUE_ID": "12345",
        "SWID": "some_swid",
        "ESPN_S2": "some_cookie",
        "TEAM_NAME": "My Team",
        "SEASON_YEAR": "2025"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        settings = get_settings()
        assert settings.LEAGUE_ID == 12345
        assert settings.SWID == "some_swid"
        assert settings.ESPN_S2 == "some_cookie"
        assert settings.TEAM_NAME == "My Team"
        assert settings.SEASON_YEAR == 2025

def test_missing_league_id():
    mock_env = {
        "SWID": "some_swid",
        "ESPN_S2": "some_cookie"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        with pytest.raises(EnvironmentError, match="Missing required environment variables: LEAGUE_ID"):
            get_settings()

def test_default_season_year():
    mock_env = {
        "LEAGUE_ID": "12345",
        "SWID": "some_swid",
        "ESPN_S2": "some_cookie"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        settings = get_settings()
        assert settings.SEASON_YEAR == datetime.now().year
        assert settings.TEAM_NAME == "Turn Your Head and Goff"

def test_env_example_contains_all_keys():
    example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.example")
    
    with open(example_path, "r") as f:
        content = f.read()
        
    assert "LEAGUE_ID=" in content
    assert "SWID=" in content
    assert "ESPN_S2=" in content
    assert "TEAM_NAME=" in content
    assert "SEASON_YEAR=" in content

def test_invalid_league_id():
    mock_env = {
        "LEAGUE_ID": "abc",
        "SWID": "some_swid",
        "ESPN_S2": "some_cookie"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        with pytest.raises(EnvironmentError, match="LEAGUE_ID must be an integer."):
            get_settings()

def test_invalid_season_year():
    mock_env = {
        "LEAGUE_ID": "12345",
        "SWID": "some_swid",
        "ESPN_S2": "some_cookie",
        "SEASON_YEAR": "abc"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        with pytest.raises(EnvironmentError, match="SEASON_YEAR must be an integer."):
            get_settings()

def test_optional_swid_and_espn_s2():
    mock_env = {
        "LEAGUE_ID": "12345"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        settings = get_settings()
        assert settings.LEAGUE_ID == 12345
        assert settings.SWID is None
        assert settings.ESPN_S2 is None
