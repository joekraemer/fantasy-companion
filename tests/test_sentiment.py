import pytest
from unittest.mock import patch, MagicMock
from src.engines.sentiment import SentimentEngine
from src.engines.sleeper_client import SleeperClient

@pytest.fixture
def mock_sleeper_client():
    client = MagicMock(spec=SleeperClient)
    # Adds: Puka Nacua (+6000), Kyren Williams (+1500), Kadarius Toney (+10)
    client.get_trending_adds.return_value = [
        {"player_id": "9999", "count": 6000},
        {"player_id": "8888", "count": 1500},
        {"player_id": "7777", "count": 10},
    ]
    # Drops: Kadarius Toney (-6000), Cam Akers (-1500), Puka Nacua (-100)
    client.get_trending_drops.return_value = [
        {"player_id": "7777", "count": 6000},
        {"player_id": "6666", "count": 1500},
        {"player_id": "9999", "count": 100},
    ]
    return client

@pytest.fixture
def mock_players_dict():
    return {
        "9999": {"full_name": "Puka Nacua", "first_name": "Puka", "last_name": "Nacua"},
        "8888": {"full_name": "Kyren Williams", "first_name": "Kyren", "last_name": "Williams"},
        "7777": {"full_name": "Kadarius Toney", "first_name": "Kadarius", "last_name": "Toney"},
        "6666": {"full_name": "Cam Akers", "first_name": "Cam", "last_name": "Akers"},
        "5555": {"first_name": "NoFullName", "last_name": "Guy"}
    }

@patch('src.engines.sentiment.load_sleeper_players')
def test_sentiment_engine_buzz_score(mock_load, mock_sleeper_client, mock_players_dict):
    mock_load.return_value = mock_players_dict
    engine = SentimentEngine(mock_sleeper_client)
    
    # Puka: 6000 adds - 100 drops = 5900
    assert engine.get_buzz_score("Puka Nacua") == 5900
    
    # Toney: 10 adds - 6000 drops = -5990
    assert engine.get_buzz_score("Kadarius Toney") == -5990
    
    # Unknown player
    assert engine.get_buzz_score("John Doe") == 0

@patch('src.engines.sentiment.load_sleeper_players')
def test_sentiment_engine_hype_meter(mock_load, mock_sleeper_client, mock_players_dict):
    mock_load.return_value = mock_players_dict
    engine = SentimentEngine(mock_sleeper_client)
    
    assert engine.get_hype_meter("Puka Nacua") == "🔥 Extreme Hype" # 5900
    assert engine.get_hype_meter("Kyren Williams") == "📈 Trending Up" # 1500
    assert engine.get_hype_meter("Kadarius Toney") == "📉 Panic Drop" # -5990
    assert engine.get_hype_meter("Cam Akers") == "🧊 Cooling Off" # -1500
    assert engine.get_hype_meter("NoFullName Guy") == "😐 Neutral" # 0

@patch('src.engines.sentiment.load_sleeper_players')
def test_sentiment_engine_name_mapping_edge_cases(mock_load, mock_sleeper_client, mock_players_dict):
    mock_load.return_value = mock_players_dict
    engine = SentimentEngine(mock_sleeper_client)
    
    # Should work even without a full_name key if first and last name exist
    # 5555 has no adds or drops, so score should be 0, but it shouldn't crash
    assert engine.get_buzz_score("NoFullName Guy") == 0
    # Also normalizes punctuation
    assert engine.get_buzz_score("Puka Nacua, Jr.") == 5900
