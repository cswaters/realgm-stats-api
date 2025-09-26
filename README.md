# RealGM Stats API

A Python package that provides a clean API interface for accessing RealGM basketball statistics, replicating the filtering functionality of the RealGM stats pages.

## Features

- ✅ Fetch basketball statistics for any league on RealGM
- ✅ Filter by season, stat type, position, team, prospects, and more
- ✅ Export data to CSV, JSON, or pandas DataFrame
- ✅ Command-line interface for quick access
- ✅ Support for all RealGM international leagues (100+ leagues)
- ✅ **NBA and WNBA support**
- ✅ **Boxscore data scraping with intelligent game filtering**
- ✅ **Team scraping utilities**
- ✅ **Player profile and stats scraping**
- ✅ **League discovery and search functionality**
- ✅ Respectful scraping with built-in delays
- ✅ Depth chart data for teams and leagues
- ✅ Team roster data for teams and leagues
- ✅ **Automatic skipping of preview/unplayed games**
- ✅ **Robust error handling and retry logic**

## Installation

```bash
pip install realgm-stats-api
```

Or install from source:
```bash
git clone https://github.com/yourusername/realgm-stats-api.git
cd realgm-stats-api
pip install -e .
```

## Project Structure

```
realgm-stats-api/
├── realgm_stats_api/          # Main package
├── examples/                  # Usage examples and demo scripts
├── tests/                     # Test scripts
├── data/                      # Data output directory
└── README.md                  # This file
```

## Supported Leagues

The API supports **102 basketball leagues** worldwide, including:

**Major Leagues:**
- NBA (League ID: 163)
- WNBA (League ID: 164)

**Popular International Leagues:**
- Euroleague (ID: 1)
- Spanish ACB (ID: 4)
- Italian Serie A (ID: 6)
- German BBL (ID: 15)
- French LNB Pro A (ID: 12)
- French LNB Pro B (ID: 50)
- Italian Serie A2 Basket (ID: 54)
- Turkish BSL (ID: 7)
- Greek HEBA A1 (ID: 8)
- And many more...

Use `api.get_leagues()` to see all available leagues or `api.get_leagues("search_term")` to find specific leagues.

## Quick Start

### Python API

#### League Discovery
```python
from realgm_stats_api import RealGMStatsAPI

# Create API client
api = RealGMStatsAPI()

# Get all available leagues
all_leagues = api.get_leagues()
print(f"Total leagues: {len(all_leagues)}")

# Search for specific leagues
italian_leagues = api.get_leagues("Italian")
for league in italian_leagues:
    print(f"ID: {league['id']}, Name: {league['name']}")

# Get specific league info
from realgm_stats_api import get_league_by_id
league_name = get_league_by_id(54)
print(f"League 54: {league_name}")
```

#### International Leagues
```python
from realgm_stats_api import create_api_client

# Create API client
api = create_api_client()

# Get Romanian Divizia A stats
stats_df = api.get_league_stats(
    league_id=31,
    league_name="Romanian-Divizia-A",
    season="2025",
    stat_type="Averages",
    position="PG"  # Point guards only
)

print(stats_df.head())
```

#### NBA and WNBA
```python
from realgm_stats_api import RealGMStatsAPI

api = RealGMStatsAPI()

# Get NBA stats
nba_stats = api.get_league_stats(
    league_name="nba",
    season="2025",
    stat_type="Averages",
    team="All"  # or specific team like "Boston Celtics"
)

# Get WNBA team stats
wnba_team_stats = api.get_league_stats(
    league_name="wnba",
    season="2025",
    stat_type="Averages",
    team="Golden State Valkyries"  # Use display name
)

# Get WNBA roster
roster = api.get_team_roster(
    league_name="wnba",
    team_id=7,
    team_name="Golden-State-Valkyries",  # Use slug
    season="2025"
)

# Get all WNBA teams info
teams = api.scrape_league_teams("wnba")
for name, info in teams.items():
    print(f"{name}: ID={info['id']}, Slug={info['slug']}")
```

#### Boxscore Data
```python
# Get boxscore links for a date (automatically skips preview games)
links = api.get_boxscore_links(54, "2025-09-21", "Italian-Serie-A2-Basket")
print(f"Found {len(links)} completed games")

# Get boxscore for a specific game
boxscore = api.get_boxscore({
    'game_id': '2121',
    'date': '2015-06-14',
    'url': 'https://basketball.realgm.com/wnba/boxscore/2015-06-14/Seattle-at-LA-Sparks/2121',
    'away_team': 'Seattle',
    'home_team': 'L.A. Sparks'
})

# Get all boxscores for a date (only completed games)
boxscores = api.get_boxscores_for_date(
    league_id=54,
    date="2025-09-21",
    league_name="Italian-Serie-A2-Basket"
)

# Get boxscores for a date range
boxscores = api.get_boxscores_for_date_range(
    league_id=54,
    start_date="2025-09-14",
    end_date="2025-09-26",
    league_name="Italian-Serie-A2-Basket"
)
```

#### Player Data
```python
from realgm_stats_api import RealGMStatsAPI

api = RealGMStatsAPI()

# Get player profile only
profile = api.get_player_profile("80999", "Elijah-Stewart")
print(f"Name: {profile['name']}")
print(f"Position: {profile['position']}")
print(f"Height: {profile['height_imperial']} ({profile['height_metric']}cm)")

# Get player stats for specific league
stats = api.get_player_stats("80999", "Elijah-Stewart", "International")
print(f"International seasons: {len(stats)}")

# Get complete player data for multiple leagues
player_data = api.get_player("80999", "Elijah-Stewart", ["International", "NBA"])
print(f"Player: {player_data['name']}")
print(f"Available stats: {list(player_data['stats'].keys())}")

# Get WNBA player data
wnba_player = api.get_player("3000070", "Allisha-Gray", ["WNBA"])
print(f"WNBA seasons: {len(wnba_player['stats']['WNBA'])}")
```

### Command Line

#### International Leagues
```bash
# Get stats for Romanian Divizia A
realgm-stats --league-id 31 --league-name "Romanian-Divizia-A"

# Filter by position
realgm-stats --league-id 31 --league-name "Romanian-Divizia-A" --position PG

# Export to CSV
realgm-stats --league-id 31 --league-name "Romanian-Divizia-A" --output stats.csv

# List available teams
realgm-stats --league-id 31 --league-name "Romanian-Divizia-A" --list-teams

# Get depth chart for a specific team
realgm-stats --league-id 62 --league-name "Puerto-Rican-BSN" --team-id 327 --team-name "Mets-de-Guaynabo" --depth-chart

# Get depth charts for all teams in a league
realgm-stats --league-id 62 --league-name "Puerto-Rican-BSN" --all-depth-charts --output depth_charts.json

# Get depth charts for all teams using teams page and auto-save
realgm-stats --league-id 15 --league-name "German-BBL" --league-depth-charts

# List all teams from the teams page
realgm-stats --league-id 15 --league-name "German-BBL" --list-league-teams

# Get rosters for all teams using teams page and auto-save
realgm-stats --league-id 15 --league-name "German-BBL" --league-rosters

# Get roster for a specific team
realgm-stats --league-id 15 --league-name "German-BBL" --team-id 142 --team-name "ALBA-Berlin" --roster

# Get rosters for all teams using teams page and auto-save
realgm-stats --league-id 15 --league-name "German-BBL" --league-rosters

# Get player profile only
realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player-profile

# Get complete player data for specific leagues
realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player --leagues "International,NBA"

# Get WNBA player stats
realgm-stats --player-id 3000070 --player-name "Allisha-Gray" --player --leagues "WNBA"
```

#### NBA and WNBA
```bash
# Get NBA stats
realgm-stats --league-name nba --season 2025 --stat-type Averages

# Get WNBA team stats
realgm-stats --league-name wnba --season 2025 --team "Golden State Valkyries"

# Get WNBA roster
realgm-stats --league-name wnba --team-id 7 --team-name "Golden-State-Valkyries" --roster

# Get WNBA boxscores for a date
realgm-stats --league-name wnba --date 2015-06-14 --boxscores
```

### Player Examples
```bash
# Get player profile only
realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player-profile

# Get complete player data for specific leagues
realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player --leagues "International,NBA"

# Get WNBA player stats
realgm-stats --player-id 3000070 --player-name "Allisha-Gray" --player --leagues "WNBA"

# Export player data to JSON
realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player --leagues "International,NBA" --output player_data.json

# Get player data in JSON format
realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player --leagues "International" --format json
```

## API Reference

### RealGMStatsAPI

The main class for interacting with RealGM statistics.

#### Methods

##### `get_leagues()`

```python
get_leagues(search_query: str = None) -> List[Dict[str, Union[int, str]]]
```

Get list of all available basketball leagues or search for specific leagues.

**Parameters:**
- `search_query`: Optional search query to filter leagues

**Returns:**
List of dictionaries containing league information:
```python
[
    {'id': 54, 'name': 'Italian Serie A2 Basket'},
    {'id': 50, 'name': 'French LNB Pro B'},
    ...
]
```

**Examples:**
```python
# Get all leagues
all_leagues = api.get_leagues()

# Search for Italian leagues
italian_leagues = api.get_leagues("Italian")

# Search for Cup competitions
cup_leagues = api.get_leagues("Cup")
```

##### `get_league_stats()`

```python
get_league_stats(
    league_id: int = 31,
    league_name: str = "Romanian-Divizia-A",
    season: str = "2025",
    stat_type: str = "Averages",
    qualified: bool = True,
    prospects: str = "All",
    team: str = "All", 
    position: str = "All",
    sort_column: str = "points",
    sort_order: str = "desc",
    page: int = 1,
    season_type: str = "Regular_Season"
) -> pd.DataFrame
```

**Parameters:**
- `league_id`: League ID number (not required for NBA/WNBA)
- `league_name`: URL-friendly league name (e.g., "nba", "wnba", "Romanian-Divizia-A")
- `season`: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)
- `stat_type`: One of "Averages", "Totals", "Per_48", "Per_40", "Per_36", "Per_Minute", "Minute_Per", "Misc_Stats", "Advanced_Stats"
- `qualified`: Whether to show only qualified players
- `prospects`: One of "All", "Pro", "Draft"
- `team`: Team filter ("All" or specific team name)
- `position`: One of "All", "PG", "SG", "SF", "PF", "C"
- `sort_column`: Column name to sort by
- `sort_order`: "desc" or "asc"

##### `scrape_league_teams()`

```python
scrape_league_teams(league_name: str) -> Dict[str, Dict]
```

Get all team information (names, IDs, slugs) for a league.

**Parameters:**
- `league_name`: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")

**Returns:**
```python
{
    "Golden State Valkyries": {
        "id": "7",
        "slug": "Golden-State-Valkyries",
        "url": "/wnba/teams/Golden-State-Valkyries/7/Home"
    },
    ...
}
```

##### `print_league_teams()`

```python
print_league_teams(league_name: str)
```

Print all teams for a league in a formatted way.

##### `get_team_mapping_for_code()`

```python
get_team_mapping_for_code(league_name: str) -> str
```

Generate Python code for team ID mapping that can be used in the API.

**Returns:**
```python
# WNBA team mapping
wnba_team_ids = {
    "Golden State Valkyries": 7,
    "Seattle Storm": 18,
    ...
}
```

##### `get_boxscore()`

```python
get_boxscore(game_info: Dict[str, str]) -> Dict
```

Get boxscore data for a specific game.

**Parameters:**
- `game_info`: Dictionary containing game information:
  - `game_id`: Game ID
  - `date`: Game date
  - `url`: Boxscore URL
  - `away_team`: Away team name
  - `home_team`: Home team name

**Returns:**
```python
{
    'game_id': str,
    'date': str,
    'url': str,
    'away_team': str,
    'home_team': str,
    'scraped_at': str,
    'scores': {
        'quarters': {'Q1_away': int, 'Q1_home': int, ...},
        'final': {'away': int, 'home': int},
        'away_abbr': str,
        'home_abbr': str
    },
    'advanced_stats': {
        'possessions': int,
        'away_offensive_rating': float,
        'away_defensive_rating': float,
        'home_offensive_rating': float,
        'home_defensive_rating': float
    },
    'four_factors': {
        'away_efg_pct': float,
        'away_to_pct': float,
        'away_or_pct': float,
        'away_ftr': float,
        'home_efg_pct': float,
        'home_to_pct': float,
        'home_or_pct': float,
        'home_ftr': float
    },
    'player_stats': {
        'away': {
            'players': [{'name': str, 'position': str, 'points': int, ...}],
            'totals': {'points': int, 'rebounds': int, ...}
        },
        'home': {...}
    },
    'depth_charts': {
        'away': {
            'starters': {'PG': {'name': str, 'player_id': str}, ...},
            'rotation': {...},
            'lim_pt': {...}
        },
        'home': {...}
    },
    'metadata': {
        'attendance': int,
        'officials': str
    }
}
```

##### `get_boxscores_for_date()`

```python
get_boxscores_for_date(
    league_id: int,
    date: str,
    league_name: str = None
) -> List[Dict]
```

Get all boxscores for a specific date.

##### `get_boxscores_for_date_range()`

```python
get_boxscores_for_date_range(
    league_id: int,
    start_date: str,
    end_date: str,
    league_name: str = None
) -> List[Dict]
```

Get all boxscores for a date range.

##### `get_available_filters()`

Get all available filter options for a league.

##### `get_team_list()`

Get list of teams in a league.

##### `get_depth_chart()`

```python
get_depth_chart(
    league_id: int = None,
    league_name: str = None,
    team_id: int = None,
    team_name: str = None,
    season: str = "2025"
) -> Dict
```

Get depth chart for a specific team.

**Parameters:**
- `league_id`: League ID number (not required for NBA/WNBA)
- `league_name`: URL-friendly league name
- `team_id`: Team ID number
- `team_name`: URL-friendly team name
- `season`: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)

**Returns:**
Dictionary containing depth chart data with the following structure:
```python
{
    'league_id': int,
    'league_name': str,
    'team_id': int,
    'team_name': str,
    'season': str,
    'scraped_at': str,
    'depth_chart': {
        'starters': {
            'PG': {'name': str, 'player_id': str, 'season_stats': Dict},
            'SG': {...},
            'SF': {...},
            'PF': {...},
            'C': {...}
        },
        'rotation': {...},
        'lim_pt': {...}
    },
    'team_leaders': {
        'MPG': {'player_name': str, 'player_id': str, 'value': str},
        'PPG': {...},
        'RPG': {...},
        # ... other stats
    },
    'metadata': Dict
}
```

##### `get_team_depth_charts()`

```python
get_team_depth_charts(
    league_id: int,
    league_name: str,
    season: str = "2025"
) -> Dict[str, Dict]
```

Get depth charts for all teams in a league.

**Parameters:**
- `league_id`: League ID number (not required for NBA/WNBA)
- `league_name`: URL-friendly league name
- `season`: Season year

**Returns:**
Dictionary mapping team names to their depth charts.

##### `get_league_depth_charts()`

```python
get_league_depth_charts(
    league_id: int,
    league_name: str,
    season: str = "2025",
    output_file: Optional[str] = None
) -> Dict
```

Get depth charts for all teams in a league and optionally save to file.

**Parameters:**
- `league_id`: League ID number (not required for NBA/WNBA)
- `league_name`: URL-friendly league name
- `season`: Season year
- `output_file`: Optional output file path for JSON export

**Returns:**
Dictionary containing league info and all team depth charts.

##### `get_team_roster()`

```python
get_team_roster(
    league_id: int = None,
    league_name: str = None,
    team_id: int = None,
    team_name: str = None,
    season: str = "2025"
) -> Dict
```

Get roster for a specific team.

**Parameters:**
- `league_id`: League ID number (not required for NBA/WNBA)
- `league_name`: URL-friendly league name
- `team_id`: Team ID number
- `team_name`: URL-friendly team name (slug)
- `season`: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)

**Returns:**
Dictionary containing roster data with the following structure:
```python
{
    'league_id': int,
    'league_name': str,
    'team_id': int,
    'team_name': str,
    'season': str,
    'scraped_at': str,
    'roster': [
        {
            'name': str,
            'position': str,
            'height': str,
            'weight': str,
            'birth_date': str,
            'college': str,
            'player_id': str
        },
        ...
    ],
    'metadata': Dict
}
```

##### `get_league_rosters()`

```python
get_league_rosters(
    league_id: int,
    league_name: str,
    season: str = "2025",
    output_file: Optional[str] = None
) -> Dict
```

Get rosters for all teams in a league and optionally save to file.

**Parameters:**
- `league_id`: League ID number (not required for NBA/WNBA)
- `league_name`: URL-friendly league name
- `season`: Season year
- `output_file`: Optional output file path for JSON export

**Returns:**
Dictionary containing league info and all team rosters.

##### `get_teams_from_teams_page()`

```python
get_teams_from_teams_page(
    league_id: int,
    league_name: str
) -> List[Dict]
```

Get list of teams from the league teams page.

**Returns:**
List of team dictionaries with id, name, name_slug, and url.

##### `get_player_profile()`

```python
get_player_profile(
    player_id: str,
    player_name: str
) -> Dict
```

Get player profile information from the Summary page.

**Parameters:**
- `player_id`: Player ID from RealGM
- `player_name`: Player name slug (e.g., "Elijah-Stewart")

**Returns:**
```python
{
    'name': str,
    'position': str,
    'jersey': Optional[str],
    'height_imperial': str,
    'height_metric': str,
    'weight_imperial': str,
    'weight_metric': str,
    'date_of_birth': str,
    'age': str,
    'hometown': str,
    'nationality': str
}
```

##### `get_player_stats()`

```python
get_player_stats(
    player_id: str,
    player_name: str,
    league: str
) -> pd.DataFrame
```

Get player stats for a specific league.

**Parameters:**
- `player_id`: Player ID from RealGM
- `player_name`: Player name slug (e.g., "Elijah-Stewart")
- `league`: League name (International, NBA, WNBA, D-League, NCAA)

**Returns:**
pandas DataFrame containing player statistics with columns:
- Season, Team, GP, GS, MIN, PTS, FGM, FGA, FG%, 3PM, 3PA, 3P%, FTM, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF
- NCAA includes additional columns: School, Class

##### `get_player()`

```python
get_player(
    player_id: str,
    player_name: str,
    leagues: List[str] = ["International"]
) -> Dict
```

Get complete player information including profile and stats for specified leagues.

**Parameters:**
- `player_id`: Player ID from RealGM
- `player_name`: Player name slug (e.g., "Elijah-Stewart")
- `leagues`: List of leagues to fetch stats for (default: ["International"])
  Supported leagues: ["International", "NBA", "WNBA", "D-League", "NCAA"]

**Returns:**
```python
{
    'player_id': str,
    'name': str,
    'profile': Dict,  # Same structure as get_player_profile()
    'stats': {
        'International': pd.DataFrame,
        'NBA': pd.DataFrame,
        'WNBA': pd.DataFrame,
        'D-League': pd.DataFrame,
        'NCAA': pd.DataFrame
    }
}
```

## Examples

### Get WNBA Team Stats
```python
from realgm_stats_api import RealGMStatsAPI

api = RealGMStatsAPI()

# Get stats for Golden State Valkyries
stats = api.get_league_stats(
    league_name="wnba",
    season="2025",
    stat_type="Averages",
    team="Golden State Valkyries"  # Use display name
)

print(stats.head())
```

### Get WNBA Roster
```python
# Get roster for Golden State Valkyries
roster = api.get_team_roster(
    league_name="wnba",
    team_id=7,
    team_name="Golden-State-Valkyries",  # Use slug
    season="2025"
)

for player in roster.get("roster", []):
    print(f"{player['name']} - {player['position']}")
```

### Get All WNBA Teams
```python
# Get all WNBA teams info
teams = api.scrape_league_teams("wnba")

for name, info in teams.items():
    print(f"{name}: ID={info['id']}, Slug={info['slug']}")

# Generate Python code for team mapping
code = api.get_team_mapping_for_code("wnba")
print(code)
```

### Get Boxscore Data
```python
# Get boxscore for a specific game
boxscore = api.get_boxscore({
    'game_id': '2121',
    'date': '2015-06-14',
    'url': 'https://basketball.realgm.com/wnba/boxscore/2015-06-14/Seattle-at-LA-Sparks/2121',
    'away_team': 'Seattle',
    'home_team': 'L.A. Sparks'
})

# Print player stats
for team_key, team_stats in boxscore['player_stats'].items():
    print(f"\n{team_key.upper()} TEAM:")
    for player in team_stats.get('players', []):
        print(f"  {player['name']}: {player.get('points', 0)} points")
```

### Download All WNBA Rosters
```python
# Download all WNBA rosters
rosters = api.get_league_rosters(
    league_id=1,  # Not used for WNBA
    league_name="wnba",
    season="2025",
    output_file="wnba_rosters_2025.json"
)
```

### Get Player Data
```python
from realgm_stats_api import RealGMStatsAPI

api = RealGMStatsAPI()

# Get player profile only
profile = api.get_player_profile("80999", "Elijah-Stewart")
print(f"Name: {profile['name']}")
print(f"Position: {profile['position']}")
print(f"Height: {profile['height_imperial']} ({profile['height_metric']}cm)")
print(f"Weight: {profile['weight_imperial']} ({profile['weight_metric']}kg)")
print(f"Born: {profile['date_of_birth']} ({profile['age']})")
print(f"Hometown: {profile['hometown']}")
print(f"Nationality: {profile['nationality']}")

# Get player stats for specific league
stats = api.get_player_stats("80999", "Elijah-Stewart", "International")
print(f"International seasons: {len(stats)}")
if not stats.empty:
    print(stats.head())

# Get complete player data for multiple leagues
player_data = api.get_player("80999", "Elijah-Stewart", ["International", "NBA"])
print(f"Player: {player_data['name']}")
print(f"Available stats: {list(player_data['stats'].keys())}")

for league, df in player_data['stats'].items():
    if not df.empty:
        print(f"{league}: {len(df)} seasons")
        print(df[['Season', 'Team', 'GP', 'PTS', 'AST']].head())

# Get WNBA player data
wnba_player = api.get_player("3000070", "Allisha-Gray", ["WNBA"])
print(f"WNBA Player: {wnba_player['name']}")
print(f"WNBA seasons: {len(wnba_player['stats']['WNBA'])}")
if not wnba_player['stats']['WNBA'].empty:
    print(wnba_player['stats']['WNBA'][['Season', 'Team', 'GP', 'PTS', 'AST']].head())
```

## Command Line Examples

### WNBA Examples
```bash
# Get WNBA league stats
realgm-stats --league-name wnba --season 2025 --stat-type Averages

# Get specific team stats
realgm-stats --league-name wnba --season 2025 --team "Golden State Valkyries"

# Get team roster
realgm-stats --league-name wnba --team-id 7 --team-name "Golden-State-Valkyries" --roster

# Get boxscores for a date
realgm-stats --league-name wnba --date 2015-06-14 --boxscores

# List all WNBA teams
realgm-stats --league-name wnba --list-league-teams
```

### NBA Examples
```bash
# Get NBA league stats
realgm-stats --league-name nba --season 2025 --stat-type Averages

# Get specific team stats
realgm-stats --league-name nba --season 2025 --team "Boston Celtics"

# Get team roster
realgm-stats --league-name nba --team-id 2 --team-name "Boston-Celtics" --roster
```

## Team Name Mapping

For NBA and WNBA, you need to use the correct team names and IDs:

### WNBA Teams
- Use display names for stats: `"Golden State Valkyries"`
- Use slugs for rosters: `"Golden-State-Valkyries"`
- Use correct team IDs: `7` for Golden State Valkyries

### Getting Team Info
```python
# Get all team info for any league
teams = api.scrape_league_teams("wnba")  # or "nba"
for name, info in teams.items():
    print(f"{name}: ID={info['id']}, Slug={info['slug']}")
```

## Recent Improvements

### v0.2.0 - Enhanced Boxscore Handling & League Discovery

- **🎯 Smart Game Filtering**: Automatically skips "PREVIEW" games and only processes completed games with boxscores
- **🔍 League Discovery**: New `get_leagues()` method to search and discover all 102+ available leagues
- **🛠️ Enhanced Error Handling**: Robust parsing that gracefully handles missing or malformed data
- **📁 Better Project Structure**: Organized examples, tests, and documentation
- **🌍 Expanded League Support**: Added French LNB Pro B and Italian Serie A2 Basket support
- **⚡ Improved Reliability**: Better retry logic and error recovery

### Key Features Added:
```python
# League discovery
leagues = api.get_leagues("Italian")  # Search functionality
all_leagues = api.get_leagues()       # Get all leagues

# Smart boxscore filtering (skips unplayed games automatically)
links = api.get_boxscore_links(54, "2025-09-21", "Italian-Serie-A2-Basket")
```

## Error Handling

The API includes comprehensive error handling for common issues:

- **Invalid league/team combinations**: Clear error messages
- **Network issues**: Automatic retry with exponential backoff
- **Rate limiting**: Built-in delays to respect RealGM's servers
- **Missing data**: Graceful handling of empty results
- **Preview games**: Automatic detection and skipping of unplayed games
- **Malformed data**: Robust parsing that handles edge cases

## Examples Directory

The `examples/` directory contains comprehensive usage examples:

- **Basic Usage**: `example_get_league_stats.py`, `example_all_leagues.py`
- **NBA/WNBA**: `example_major_leagues.py`
- **Boxscores**: `example_boxscores.py`, `download_boxscores.py`
- **Team Data**: `example_rosters.py`, `example_depth_charts.py`
- **WNBA Specific**: `download_wnba_rosters.py`, `download_wnba_team_stats.py`

Run any example:
```bash
python examples/example_get_league_stats.py
```

## Testing

Run tests from the project root:
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_boxscores_major.py
```
## License

The Unlicense 
