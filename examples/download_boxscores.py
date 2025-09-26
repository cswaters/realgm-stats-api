from realgm_stats_api import RealGMStatsAPI, find_league_by_regex
import duckdb
from datetime import datetime, timedelta
import argparse
import json
import time
import random
from typing import Optional, List, Dict, Any

def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """Add a random delay between requests to avoid rate limiting"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def get_boxscore_links_with_retry(api: RealGMStatsAPI, league_id: int, date: str, league_name: str = None, max_retries: int = 3) -> List[Dict[str, Any]]:
    """Get boxscore links with retry logic"""
    for attempt in range(max_retries):
        try:
            random_delay()
            return api.get_boxscore_links(league_id, date, league_name)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"    Failed to get boxscore links after {max_retries} attempts: {e}")
                return []
            print(f"    Attempt {attempt + 1} failed, retrying...")
            random_delay(min_seconds=2.0, max_seconds=5.0)  # Longer delay on retry
    return []

def get_boxscore_with_retry(api: RealGMStatsAPI, game_info: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Get boxscore with retry logic"""
    for attempt in range(max_retries):
        try:
            random_delay()
            return api.get_boxscore(game_info)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"    Failed to get boxscore after {max_retries} attempts: {e}")
                return None
            print(f"    Attempt {attempt + 1} failed, retrying...")
            random_delay(min_seconds=2.0, max_seconds=5.0)  # Longer delay on retry
    return None

def save_boxscore_to_db(conn, boxscore, league_id, country):
    """Save a boxscore to the database"""
    try:
        # Insert game info
        conn.execute("""
        INSERT INTO games (game_id, league_id, country, date, venue, attendance, officials, url, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            boxscore['game_id'],
            league_id,
            country,
            boxscore['date'],
            boxscore.get('metadata', {}).get('venue'),
            boxscore.get('metadata', {}).get('attendance'),
            boxscore.get('metadata', {}).get('officials'),
            boxscore['url'],
            boxscore['scraped_at']
        ))
        
        # Insert team info
        for team_type in ['away', 'home']:
            conn.execute("""
            INSERT INTO game_teams (game_id, team_type, team_name, team_record, team_score, team_abbr, quarters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                boxscore['game_id'],
                team_type,
                boxscore[f'{team_type}_team'],
                boxscore['scores'][f'{team_type}_record'],
                boxscore['scores']['final'][team_type],
                boxscore['scores'][f'{team_type}_abbr'],
                json.dumps(boxscore['scores']['quarters'])
            ))
        
        # Insert advanced stats
        for team_type in ['away', 'home']:
            conn.execute("""
            INSERT INTO game_advanced_stats (game_id, team_type, possessions, offensive_rating, defensive_rating, 
                                           efg_pct, to_pct, or_pct, ftr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                boxscore['game_id'],
                team_type,
                boxscore['advanced_stats']['possessions'],
                boxscore['advanced_stats'][f'{team_type}_offensive_rating'],
                boxscore['advanced_stats'][f'{team_type}_defensive_rating'],
                boxscore['four_factors'][f'{team_type}_efg_pct'],
                boxscore['four_factors'][f'{team_type}_to_pct'],
                boxscore['four_factors'][f'{team_type}_or_pct'],
                boxscore['four_factors'][f'{team_type}_ftr']
            ))
        
        # Insert team totals
        for team_type in ['away', 'home']:
            totals = boxscore['player_stats'][team_type]['totals']
            conn.execute("""
            INSERT INTO game_team_totals (game_id, team_type, minutes, fg_made, fg_attempted, three_made, three_attempted,
                                        ft_made, ft_attempted, fg_percentage, three_percentage, ft_percentage,
                                        offensive_rebounds, defensive_rebounds, total_rebounds, assists, personal_fouls,
                                        steals, turnovers, blocks, points, fic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                boxscore['game_id'],
                team_type,
                totals['minutes'],
                *[int(x) for x in totals['fgm_a'].split('-')],
                *[int(x) for x in totals['three_pm_a'].split('-')],
                *[int(x) for x in totals['ftm_a'].split('-')],
                float(totals['fg_percentage'].strip('%')),
                float(totals['three_percentage'].strip('%')),
                float(totals['ft_percentage'].strip('%')),
                totals['offensive_rebounds'],
                totals['defensive_rebounds'],
                totals['total_rebounds'],
                totals['assists'],
                totals['personal_fouls'],
                totals['steals'],
                totals['turnovers'],
                totals['blocks'],
                totals['points'],
                totals['fic']
            ))
        
        # Insert player stats
        for team_type in ['away', 'home']:
            for player in boxscore['player_stats'][team_type]['players']:
                conn.execute("""
                INSERT INTO game_player_stats (game_id, team_type, player_id, player_name, number, position, is_starter,
                                             minutes, fg_made, fg_attempted, three_made, three_attempted, ft_made,
                                             ft_attempted, offensive_rebounds, defensive_rebounds, total_rebounds,
                                             assists, personal_fouls, steals, turnovers, blocks, points, fic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    boxscore['game_id'],
                    team_type,
                    player.get('player_id'),
                    player['name'],
                    player.get('number'),
                    player.get('position'),
                    player.get('is_starter', False),
                    player.get('minutes'),
                    player.get('fg_made'),
                    player.get('fg_attempted'),
                    player.get('three_made'),
                    player.get('three_attempted'),
                    player.get('ft_made'),
                    player.get('ft_attempted'),
                    player.get('offensive_rebounds'),
                    player.get('defensive_rebounds'),
                    player.get('total_rebounds'),
                    player.get('assists'),
                    player.get('personal_fouls'),
                    player.get('steals'),
                    player.get('turnovers'),
                    player.get('blocks'),
                    player.get('points'),
                    player.get('fic')
                ))
        
        # Insert depth charts
        for team_type in ['away', 'home']:
            if team_type in boxscore['depth_charts']:
                for role, positions in boxscore['depth_charts'][team_type].items():
                    for pos, player_info in positions.items():
                        conn.execute("""
                        INSERT INTO game_depth_charts (game_id, team_type, position, role, player_id, player_name, season_stats)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            boxscore['game_id'],
                            team_type,
                            pos,
                            role,
                            player_info.get('player_id'),
                            player_info['name'],
                            player_info.get('season_stats')
                        ))
        return True
    except Exception as e:
        print(f"    Error saving boxscore to database: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download boxscores for a date range')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--league', required=True, help='League name regex pattern or exact name (nba, wnba)')
    parser.add_argument('--min-delay', type=float, default=1.0, help='Minimum delay between requests in seconds')
    parser.add_argument('--max-delay', type=float, default=3.0, help='Maximum delay between requests in seconds')
    args = parser.parse_args()
    
    # Initialize API and database
    api = RealGMStatsAPI()
    conn = duckdb.connect('realgm.db')
    
    # Handle major leagues (NBA, WNBA) vs international leagues
    league_name = None
    country = "Unknown"
    
    if args.league.lower() in ['nba', 'wnba']:
        # Major league - use exact league name
        league_name = args.league.lower()
        if league_name == 'nba':
            league_id = 163
            country = "USA"
        else:  # wnba
            league_id = 164
            country = "USA"
        print(f"Using major league: {league_name.upper()} (ID: {league_id})")
    else:
        # International league - find by regex
        leagues = find_league_by_regex(args.league)
        if not leagues:
            print(f"Could not find league matching pattern: {args.league}")
            return
        
        # Get the first matching league
        league_id, league_name = leagues[0]
        print(f"Found international league: {league_name} (ID: {league_id})")
        country = "International"  # You can make this more specific based on league
    
    # Insert league info if not exists
    conn.execute("""
    INSERT OR IGNORE INTO leagues (league_id, league_name, country, slug)
    VALUES (?, ?, ?, ?)
    """, (league_id, league_name, country, league_name.lower().replace(" ", "-")))
    
    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else datetime.now()
    
    # Get all dates with games
    all_dates = api.get_game_dates(league_id, league_name)
    dates_to_process = [
        date for date in all_dates 
        if start_date <= datetime.strptime(date, "%Y-%m-%d") <= end_date
    ]
    
    print(f"Found {len(dates_to_process)} dates with games in range")
    
    # Process each date
    for date in dates_to_process:
        print(f"\nProcessing {date}...")
        boxscore_links = get_boxscore_links_with_retry(api, league_id, date, league_name)
        
        if not boxscore_links:
            print(f"  No boxscore links found for {date}, skipping...")
            continue
        
        for game_info in boxscore_links:
            print(f"  - {game_info['away_team']} @ {game_info['home_team']}")
            try:
                # Check if game already exists
                result = conn.execute("""
                SELECT 1 FROM games WHERE game_id = ?
                """, (game_info['game_id'],)).fetchone()
                
                if result:
                    print(f"    Game {game_info['game_id']} already exists, skipping")
                    continue
                
                boxscore = get_boxscore_with_retry(api, game_info)
                if boxscore:
                    if save_boxscore_to_db(conn, boxscore, league_id, country):
                        print(f"    Saved game {boxscore['game_id']}")
                    else:
                        print(f"    Failed to save game {game_info['game_id']}")
                else:
                    print(f"    Failed to get boxscore for game {game_info['game_id']}")
            except Exception as e:
                print(f"    Error processing game: {e}")
                continue
    
    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    main() 