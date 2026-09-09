import pytest
from unittest.mock import patch, MagicMock
from src.engines.espn_client import ESPNClient

@pytest.fixture
def mock_league():
    with patch('src.engines.espn_client.League') as MockLeague:
        # Create a mock league instance
        mock_instance = MockLeague.return_value
        
        # Mock Team
        mock_team = MagicMock()
        mock_team.team_name = "Turn Your Head and Goff"
        
        # Mock Player on Roster
        mock_player_1 = MagicMock()
        mock_player_1.name = "Jared Goff"
        mock_player_1.position = "QB"
        mock_player_1.injuryStatus = "ACTIVE"
        mock_player_1.proTeam = "DET"
        mock_player_1.eligibleSlots = ["QB", "OP", "BE"]
        
        mock_team.roster = [mock_player_1]
        
        # Set up teams
        mock_instance.teams = [mock_team]
        
        # Mock Free Agents
        mock_fa = MagicMock()
        mock_fa.name = "Amon-Ra St. Brown"
        mock_fa.position = "WR"
        mock_fa.injuryStatus = "QUESTIONABLE"
        mock_fa.proTeam = "DET"
        mock_fa.projected_points = 15.2
        
        mock_instance.free_agents.return_value = [mock_fa]
        
        # Mock Settings
        mock_instance.settings = MagicMock()
        mock_instance.settings.scoring_format = {"pass_yds": 0.04, "pass_td": 4}
        
        yield mock_instance

def test_espn_client_init(mock_league):
    client = ESPNClient(league_id=123, year=2024, swid="{XYZ}", espn_s2="ABC")
    assert client.league_id == 123
    assert client.year == 2024
    assert client.swid == "{XYZ}"
    assert client.espn_s2 == "ABC"

def test_get_team_by_name(mock_league):
    client = ESPNClient(league_id=123, year=2024)
    team = client.get_team_by_name("Turn Your Head and Goff")
    assert team is not None
    assert team.team_name == "Turn Your Head and Goff"
    
    # Test case insensitive
    team = client.get_team_by_name("turn your head and goff")
    assert team is not None

    # Test not found
    assert client.get_team_by_name("Nonexistent Team") is None

def test_get_team_roster(mock_league):
    client = ESPNClient(league_id=123, year=2024)
    roster = client.get_team_roster("Turn Your Head and Goff")
    
    assert len(roster) == 1
    assert roster[0]["name"] == "Jared Goff"
    assert roster[0]["position"] == "QB"
    assert roster[0]["proTeam"] == "DET"

    with pytest.raises(ValueError):
        client.get_team_roster("Nonexistent Team")

def test_get_free_agents(mock_league):
    client = ESPNClient(league_id=123, year=2024)
    fa_pool = client.get_free_agents(size=1)
    
    assert len(fa_pool) == 1
    assert fa_pool[0]["name"] == "Amon-Ra St. Brown"
    assert fa_pool[0]["position"] == "WR"
    assert fa_pool[0]["injuryStatus"] == "QUESTIONABLE"
    assert fa_pool[0]["projectedPoints"] == 15.2

def test_get_scoring_rules(mock_league):
    client = ESPNClient(league_id=123, year=2024)
    rules = client.get_scoring_rules()
    
    assert rules["pass_yds"] == 0.04
    assert rules["pass_td"] == 4

def test_get_scoring_rules_missing(mock_league):
    client = ESPNClient(league_id=123, year=2024)
    # Simulate missing settings
    delattr(client.league, 'settings')
    rules = client.get_scoring_rules()
    assert rules == {}
