import pandas as pd
import pytest
from src.engines.streaming import StreamingEngine

@pytest.fixture
def sample_schedule():
    return pd.DataFrame({
        'week': [1, 1, 2, 2],
        'away_team': ['DET', 'BAL', 'DET', 'KC'],
        'home_team': ['KC', 'PIT', 'CHI', 'BAL'],
        'spread_line': [-4.5, 3.0, 1.0, -2.0],  # From home team perspective
        'total_line': [54.0, 42.0, 45.0, 48.0],
        'roof': ['outdoors', 'dome', 'outdoors', 'outdoors'],
        'temp': [80.0, 70.0, 60.0, 55.0],
        'wind': [5.0, 0.0, 16.0, 10.0]
    })
    
# Week 1 KC vs DET (KC home, DET away, spread -4.5 meaning KC favored by 4.5, total 54.0)
# KC implied: (54/2) - (-4.5/2) = 27 + 2.25 = 29.25
# DET implied: (54/2) + (-4.5/2) = 27 - 2.25 = 24.75
# KC is favored by 4.5. 

def test_streaming_engine_dst_score(sample_schedule):
    engine = StreamingEngine(sample_schedule)
    
    # KC Week 1: Home favored by 4.5. Opponent (DET) implied 24.75. Roof outdoors.
    # Score: spread is -4.5 (<= -3: +1). Opp implied is 24.75 (not <= 20). Roof not dome.
    # Total: 1.0
    assert engine.score_dst('KC', 1) == 1.0
    
    # DET Week 1: Away underdog by 4.5 (so their spread is +4.5). Opp implied 29.25. Roof outdoors.
    # Score: 0.0
    assert engine.score_dst('DET', 1) == 0.0
    
    # BAL Week 1: Away. Opponent (PIT). Home spread 3.0 (PIT underdog by 3).
    # Total 42. BAL implied: (42/2) + (3/2) = 22.5. PIT implied: 21 - 1.5 = 19.5
    # BAL opponent (PIT) implied is 19.5. This is <= 20, so +3.
    # BAL is not home, so spread doesn't give them a boost even though they are favored.
    # Roof is dome, so +1.
    # Total: 3 + 1 = 4.0
    assert engine.score_dst('BAL', 1) == 4.0

def test_streaming_engine_kicker_score(sample_schedule):
    engine = StreamingEngine(sample_schedule)
    
    # KC Week 1: Implied 29.25. (>= 27: +5.0). Roof outdoors. Wind 5.0.
    # Total: 5.0
    assert engine.score_kicker('KC', 1) == 5.0
    
    # DET Week 2 (vs CHI): Home is CHI (spread 1.0, so DET favored by 1).
    # DET implied (away): (45/2) + (1.0/2) = 22.5 + 0.5 = 23.0
    # Not >= 24. Wind is 16.0 (>= 15: -2.0).
    # Total: -2.0
    assert engine.score_kicker('DET', 2) == -2.0
    
    # PIT Week 1: Implied 19.5. Dome (+1.5). Wind 0.
    # Total: 1.5
    assert engine.score_kicker('PIT', 1) == 1.5

def test_corridor_score(sample_schedule):
    engine = StreamingEngine(sample_schedule)
    
    # KC DST Week 1 score = 1.0
    # KC DST Week 2 score (Away vs BAL. BAL home spread -2.0 -> KC spread +2.0. Opp implied BAL = 24+1=25. Roof outdoors).
    # KC week 2 score = 0.0
    # Corridor (wk 1..2) = 1.0 + (0.85 * 0.0) = 1.0
    assert engine.corridor_score('KC', 1, weeks_ahead=2, position='DST') == 1.0

def test_get_streaming_matrix(sample_schedule):
    engine = StreamingEngine(sample_schedule)
    matrix = engine.get_streaming_matrix('DST', 1, weeks_ahead=2)
    
    assert not matrix.empty
    assert 'Team' in matrix.columns
    assert 'Wk 1' in matrix.columns
    assert 'Wk 2' in matrix.columns
    assert 'Corridor' in matrix.columns
    
    # Ensure it's sorted by Corridor descending
    corridors = matrix['Corridor'].tolist()
    assert corridors == sorted(corridors, reverse=True)
