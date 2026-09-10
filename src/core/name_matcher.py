import re

# Small static dictionary for edge cases
EDGE_CASES = {
    "dk metcalf": "d.k. metcalf",
    "gabriel davis": "gabe davis",
    "kenneth walker iii": "kenneth walker",
    "kenneth walker": "ken walker",
}

def normalize_name(name: str) -> str:
    """
    Normalizes a player's name for cross-platform joins (ESPN <-> NFLverse).
    Strips punctuation, suffixes (Jr., Sr., II, III, IV, V), and converts to lowercase.
    """
    if not name:
        return ""
    
    # Lowercase
    name = name.lower()
    
    # Strip punctuation (keep only alphanumeric and spaces)
    name = re.sub(r'[^\w\s]', '', name)
    
    # Suffixes to remove
    suffixes = [r'\bjr\b', r'\bsr\b', r'\bii\b', r'\biii\b', r'\biv\b', r'\bv\b']
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    # Apply edge cases if exists
    if name in EDGE_CASES:
        name = EDGE_CASES[name]
        
    return name

def match_names(name1: str, name2: str) -> bool:
    """
    Checks if two player names match after normalization.
    """
    return normalize_name(name1) == normalize_name(name2)
