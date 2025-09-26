from realgm_stats_api import RealGMStatsAPI
import json
from datetime import datetime, timedelta

def main():
    # Initialize API
    api = RealGMStatsAPI()
    
    print("=== Testing Major League Boxscores with Real Data ===\n")
    
    # Test NBA with recent dates
    print("1. NBA Testing:")
    print("-" * 50)
    
    try:
        # Get NBA game dates
        nba_dates = api.get_game_dates(league_id=163, league_name="nba")
        print(f"Found {len(nba_dates)} NBA game dates")
        
        # Find recent dates with actual games (not future dates)
        today = datetime.now()
        recent_nba_dates = []
        for date_str in nba_dates[-20:]:  # Check last 20 dates
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj < today:
                recent_nba_dates.append(date_str)
        
        print(f"Found {len(recent_nba_dates)} recent NBA dates with games")
        
        if recent_nba_dates:
            # Test with the most recent date that has games
            test_date = recent_nba_dates[-1]
            print(f"Testing NBA boxscores for {test_date}...")
            
            nba_boxscore_links = api.get_boxscore_links(league_id=163, date=test_date, league_name="nba")
            print(f"Found {len(nba_boxscore_links)} NBA games for {test_date}")
            
            if nba_boxscore_links:
                for i, game_info in enumerate(nba_boxscore_links[:2]):  # Test first 2 games
                    print(f"\nGame {i+1}: {game_info['away_team']} @ {game_info['home_team']}")
                    print(f"Score: {game_info['away_score']}-{game_info['home_score']}")
                    
                    # Get detailed boxscore
                    print("Downloading detailed boxscore...")
                    boxscore = api.get_boxscore(game_info)
                    
                    print(f"Game ID: {boxscore['game_id']}")
                    print(f"URL: {boxscore['url']}")
                    
                    if 'scores' in boxscore and 'final' in boxscore['scores']:
                        final = boxscore['scores']['final']
                        print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
                    
                    if 'player_stats' in boxscore:
                        for team_key, team_stats in boxscore['player_stats'].items():
                            print(f"{team_key.upper()} team has {len(team_stats.get('players', []))} players")
                            if team_stats.get('players'):
                                top_scorer = max(team_stats['players'], key=lambda p: p.get('points', 0))
                                print(f"  Top scorer: {top_scorer.get('name', 'N/A')} - {top_scorer.get('points', 0)} pts")
                    
                    print("-" * 30)
            else:
                print(f"No NBA games found for {test_date}")
        else:
            print("No recent NBA dates with games found")
            
    except Exception as e:
        print(f"Error testing NBA: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")
    
    # Test WNBA with recent dates
    print("2. WNBA Testing:")
    print("-" * 50)
    
    try:
        # Get WNBA game dates
        wnba_dates = api.get_game_dates(league_id=164, league_name="wnba")
        print(f"Found {len(wnba_dates)} WNBA game dates")
        
        # Find recent dates with actual games (not future dates)
        today = datetime.now()
        recent_wnba_dates = []
        for date_str in wnba_dates[-20:]:  # Check last 20 dates
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj < today:
                recent_wnba_dates.append(date_str)
        
        print(f"Found {len(recent_wnba_dates)} recent WNBA dates with games")
        
        if recent_wnba_dates:
            # Test with the most recent date that has games
            test_date = recent_wnba_dates[-1]
            print(f"Testing WNBA boxscores for {test_date}...")
            
            wnba_boxscore_links = api.get_boxscore_links(league_id=164, date=test_date, league_name="wnba")
            print(f"Found {len(wnba_boxscore_links)} WNBA games for {test_date}")
            
            if wnba_boxscore_links:
                for i, game_info in enumerate(wnba_boxscore_links[:2]):  # Test first 2 games
                    print(f"\nGame {i+1}: {game_info['away_team']} @ {game_info['home_team']}")
                    print(f"Score: {game_info['away_score']}-{game_info['home_score']}")
                    
                    # Get detailed boxscore
                    print("Downloading detailed boxscore...")
                    boxscore = api.get_boxscore(game_info)
                    
                    print(f"Game ID: {boxscore['game_id']}")
                    print(f"URL: {boxscore['url']}")
                    
                    if 'scores' in boxscore and 'final' in boxscore['scores']:
                        final = boxscore['scores']['final']
                        print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
                    
                    if 'player_stats' in boxscore:
                        for team_key, team_stats in boxscore['player_stats'].items():
                            print(f"{team_key.upper()} team has {len(team_stats.get('players', []))} players")
                            if team_stats.get('players'):
                                top_scorer = max(team_stats['players'], key=lambda p: p.get('points', 0))
                                print(f"  Top scorer: {top_scorer.get('name', 'N/A')} - {top_scorer.get('points', 0)} pts")
                    
                    print("-" * 30)
            else:
                print(f"No WNBA games found for {test_date}")
        else:
            print("No recent WNBA dates with games found")
            
    except Exception as e:
        print(f"Error testing WNBA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 