import re
import pandas as pd
from typing import Dict

EDGE_CASES: Dict[str, str] = {
    "dk metcalf": "d.k. metcalf",
    "gabe davis": "gabriel davis",
}

def normalize_name(name: str) -> str:
    """
    Normalizes a player's name by:
    - Converting to lowercase
    - Checking edge cases
    - Removing punctuation
    - Removing suffixes (Jr., Sr., II, III, IV, V)
    """
    if not isinstance(name, str):
        return ""
        
    # Convert to lowercase
    name = name.lower().strip()
    
    # Check manual edge cases first
    if name in EDGE_CASES:
        name = EDGE_CASES[name]
        
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    
    # Remove suffixes (jr, sr, ii, iii, iv, v)
    suffixes = r'\b(jr|sr|ii|iii|iv|v)\b'
    name = re.sub(suffixes, '', name)
    
    # Clean up excess whitespace
    name = ' '.join(name.split())
    
    return name

def create_merge_key(df: pd.DataFrame, name_column: str = "name", new_column: str = "merge_name") -> pd.DataFrame:
    """
    Helper to apply normalize_name to a pandas DataFrame column.
    Mutates the DataFrame in place and returns it.
    """
    if name_column in df.columns:
        df[new_column] = df[name_column].apply(normalize_name)
    return df
