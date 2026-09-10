import pandas as pd
from src.core.name_matcher import normalize_name, create_merge_key

def test_normalize_name():
    # Basic cases
    assert normalize_name("Patrick Mahomes") == "patrick mahomes"
    
    # Punctuation
    assert normalize_name("A.J. Brown") == "aj brown"
    assert normalize_name("D'Andre Swift") == "dandre swift"
    
    # Suffixes
    assert normalize_name("Odell Beckham Jr.") == "odell beckham"
    assert normalize_name("Melvin Gordon III") == "melvin gordon"
    assert normalize_name("Allen Robinson II") == "allen robinson"
    assert normalize_name("Irv Smith Jr") == "irv smith"
    
    # Edge cases
    assert normalize_name("DK Metcalf") == "dk metcalf" # Because EDGE_CASES handles it before punct stripping, wait, EDGE_CASES says "dk metcalf": "d.k. metcalf"
    assert normalize_name("Gabe Davis") == "gabriel davis"
    
    # Nulls / Invalid
    assert normalize_name(None) == ""
    assert normalize_name(123) == ""

def test_create_merge_key():
    df = pd.DataFrame({
        "name": ["A.J. Brown", "Patrick Mahomes II", "DK Metcalf"]
    })
    
    df = create_merge_key(df)
    
    assert "merge_name" in df.columns
    assert df["merge_name"].iloc[0] == "aj brown"
    assert df["merge_name"].iloc[1] == "patrick mahomes"
    assert df["merge_name"].iloc[2] == "dk metcalf"
