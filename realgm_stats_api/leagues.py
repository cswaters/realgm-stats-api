import re
from typing import Dict, List, Tuple, Optional

# Basketball leagues dictionary with ID as key and name as value
BASKETBALL_LEAGUES = {
    47: "adidas Next Generation Tournament",
    117: "Adriatic Junior Liga ABA",
    18: "Adriatic League Liga ABA",
    58: "Argentinian Liga A",
    5: "Australian NBL",
    51: "Austrian A Bundesliga",
    138: "Basketball Africa League",
    139: "Basketball Africa League - Qualification",
    107: "Basketball Champions League - Qualification",
    137: "Basketball Champions League Americas",
    106: "Basketball Champions League Europe",
    154: "Basketball Super League",
    30: "Belarusian BPL",
    46: "Belgrade Tournament (ANGT)",
    145: "BNXT League",
    19: "Bosnian BiH Liga",
    59: "Brazilian NBB",
    26: "Bulgarian NBL",
    128: "Canadian Elite Basketball League",
    40: "Chinese CBA",
    14: "Croatian A-1 Liga",
    34: "Cypriot Division A",
    24: "Czech NBL",
    67: "Danish Basketligaen",
    123: "Estonian-Latvian Basketball League",
    2: "Eurocup",
    1: "Euroleague",
    102: "FIBA Europe Cup",
    108: "FIBA Europe Cup - Qualification",
    37: "Finnish Korisliiga",
    155: "French Basketball Cup",
    12: "French Jeep Elite",
    89: "French Leaders Cup LNB A",
    141: "French Leaders Cup LNB B",
    114: "French LNB Espoirs",
    50: "French LNB Pro B",
    96: "French NM1",
    33: "Georgian Super Liga",
    15: "German BBL",
    112: "German Cup",
    94: "German Pro A",
    101: "German Pro B",
    8: "Greek HEBA A1",
    113: "Greek HEBA A2",
    158: "Hungarian Cup",
    28: "Hungarian NBIA",
    97: "Intercontinental Cup",
    156: "Israel BSL Winner Cup",
    11: "Israeli BSL",
    143: "Istanbul Tournament (ANGT)",
    48: "Italian Cup",
    6: "Italian Lega Basket Serie A",
    54: "Italian Serie A2 Basket",
    105: "Japanese B.League",
    104: "Kosovo FBK",
    95: "Lebanese Division A",
    159: "Lithuanian Citadele KMT",
    10: "Lithuanian LKL",
    118: "Lithuanian NKL",
    92: "Luxembourg Total League",
    64: "Macedonian Superleague",
    77: "Mexican CIBACOPA",
    76: "Mexican LNBP",
    20: "Montenegrin Prva A Liga",
    115: "Munich Tournament (ANGT)",
    136: "NBL Blitz",
    75: "New Zealand NBL",
    68: "Norwegian BLNO",
    131: "PBA - Commissioners Cup",
    132: "PBA - Governors Cup",
    130: "PBA - Philippine Cup",
    157: "Polish Mens Cup",
    21: "Polish OBL",
    83: "Portuguese LPB",
    62: "Puerto Rican BSN",
    31: "Romanian Divizia A",
    13: "Serbian KLS",
    121: "Serbian RK Cup",
    29: "Slovakian Extraliga",
    17: "Slovenian SKL",
    160: "Slovenian Spar Cup",
    63: "South Korean KBL",
    4: "Spanish ACB",
    124: "Spanish ACB SuperCup",
    42: "Spanish Cup",
    55: "Spanish Primera FEB",
    78: "Spanish Segunda FEB",
    161: "Super League Basketball",
    32: "Swedish Basketligan",
    70: "Swiss LNA",
    7: "Turkish BSL",
    122: "Turkish Cup",
    56: "Turkish TBL",
    57: "Ukrainian Superleague",
    162: "ULM Tournament (ANGT)",
    82: "Venezuelan SLB",
    144: "VTB SuperCup",
    35: "VTB United League",
    119: "VTB Youth United League",
    150: "Youth Basketball Champions League",
    # Major leagues (these use different URL patterns)
    163: "NBA",
    164: "WNBA"
}

# Reverse lookup dictionary (name to ID)
LEAGUE_NAME_TO_ID = {name: league_id for league_id, name in BASKETBALL_LEAGUES.items()}

def find_league_by_regex(pattern: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
    """
    Find leagues by regex pattern matching on league names.
    
    Args:
        pattern (str): Regex pattern to search for
        case_sensitive (bool): Whether the search should be case sensitive
        
    Returns:
        List[Tuple[int, str]]: List of tuples containing (league_id, league_name)
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled_pattern = re.compile(pattern, flags)
    
    matches = []
    for league_id, league_name in BASKETBALL_LEAGUES.items():
        if compiled_pattern.search(league_name):
            matches.append((league_id, league_name))
    
    return matches

def get_league_by_id(league_id: int) -> Optional[str]:
    """
    Get league name by ID.
    
    Args:
        league_id (int): The league ID
        
    Returns:
        Optional[str]: League name if found, None otherwise
    """
    return BASKETBALL_LEAGUES.get(league_id)

def get_league_id_by_name(league_name: str, exact_match: bool = True) -> Optional[int]:
    """
    Get league ID by name.
    
    Args:
        league_name (str): The league name
        exact_match (bool): Whether to require exact match or fuzzy search
        
    Returns:
        Optional[int]: League ID if found, None otherwise
    """
    if exact_match:
        return LEAGUE_NAME_TO_ID.get(league_name)
    else:
        # Fuzzy search using regex
        matches = find_league_by_regex(re.escape(league_name))
        return matches[0][0] if matches else None

def search_leagues(query: str) -> List[Tuple[int, str]]:
    """
    Search for leagues containing the query string.
    
    Args:
        query (str): Search query
        
    Returns:
        List[Tuple[int, str]]: List of matching leagues
    """
    return find_league_by_regex(re.escape(query), case_sensitive=False)

# Example usage and testing
if __name__ == "__main__":
    # Test the functions
    print("=== Basketball League Lookup Functions ===\n")
    
    # Find leagues by regex
    print("1. Find leagues containing 'Spanish':")
    spanish_leagues = find_league_by_regex(r"spanish", case_sensitive=False)
    for league_id, name in spanish_leagues:
        print(f"   ID: {league_id} - {name}")
    
    print("\n2. Find leagues containing 'Cup':")
    cup_leagues = find_league_by_regex(r"cup", case_sensitive=False)
    for league_id, name in cup_leagues:
        print(f"   ID: {league_id} - {name}")
    
    print("\n3. Find European leagues (containing 'Euro'):")
    euro_leagues = find_league_by_regex(r"euro", case_sensitive=False)
    for league_id, name in euro_leagues:
        print(f"   ID: {league_id} - {name}")
    
    print("\n4. Get league by ID:")
    print(f"   League ID 31: {get_league_by_id(31)}")
    print(f"   League ID 1: {get_league_by_id(1)}")
    
    print("\n5. Get ID by league name:")
    print(f"   'Romanian Divizia A': {get_league_id_by_name('Romanian Divizia A')}")
    print(f"   'Euroleague': {get_league_id_by_name('Euroleague')}")
    
    print("\n6. Search for leagues:")
    nba_search = search_leagues("NBA")
    print(f"   Search 'NBA': {nba_search}")
    
    turkish_search = search_leagues("Turkish")
    print(f"   Search 'Turkish': {turkish_search}")
    
    print(f"\n7. Total leagues in database: {len(BASKETBALL_LEAGUES)}")