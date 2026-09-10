from src.core.name_matcher import normalize_name, match_names

def test_normalize_name_punctuation():
    assert normalize_name("D.K. Metcalf") == "d.k. metcalf"
    assert normalize_name("A.J. Brown") == "aj brown"
    assert normalize_name("Patrick Mahomes II") == "patrick mahomes"

def test_normalize_name_suffixes():
    assert normalize_name("Odell Beckham Jr.") == "odell beckham"
    assert normalize_name("Marvin Harrison Jr.") == "marvin harrison"
    assert normalize_name("Mark Ingram II") == "mark ingram"
    assert normalize_name("Will Fuller V") == "will fuller"

def test_edge_cases():
    assert normalize_name("DK Metcalf") == "d.k. metcalf"
    assert normalize_name("Gabriel Davis") == "gabe davis"

def test_match_names():
    assert match_names("D.K. Metcalf", "DK Metcalf") == True
    assert match_names("Patrick Mahomes", "Patrick Mahomes II") == True
    assert match_names("Odell Beckham Jr.", "Odell Beckham") == True
    assert match_names("Gabriel Davis", "Gabe Davis") == True
    assert match_names("Josh Allen", "Josh Allen") == True
    assert match_names("Josh Allen", "Tom Brady") == False
